#!/usr/bin/env python3
"""
Fuseki XML Upload Monitor

Python rewrite of xmlupload_size_increase.sh that monitors Fuseki database size
changes during XML uploads with compression tracking.

This script processes XML files sequentially, restarting the DSP stack for each file,
and records database size metrics before and after operations.
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from loguru import logger
import docker
import requests
from requests.auth import HTTPBasicAuth


# Phase 1: Configuration and Data Structures
@dataclass
class MonitorConfig:
    """Configuration for the Fuseki monitor."""
    project_file: Path
    xml_dir: Path
    output_csv: Path
    fuseki_image: str = "daschswiss/apache-jena-fuseki:5.5.0-1"
    fuseki_url: str = "http://localhost:3030"
    fuseki_auth: tuple[str, str] = ("admin", "test")
    max_compression_timeout: int = 7200  # 2 hours
    compression_check_interval: int = 60  # 1 minute
    fuseki_wait_attempts: int = 60
    fuseki_wait_interval: int = 10


@dataclass
class ProcessingResult:
    """Result data structure for CSV output."""
    timestamp: str
    db_before: str
    filename: str
    db_after_upload: str
    db_before_compression: str
    compression_duration: Union[int, str]
    db_after_compression: str

    def to_csv_row(self) -> list[str]:
        """Convert to CSV row format."""
        return [
            self.timestamp,
            self.db_before,
            self.filename,
            self.db_after_upload,
            self.db_before_compression,
            str(self.compression_duration),
            self.db_after_compression
        ]


# Exception Hierarchy
class MonitorError(Exception):
    """Base exception for monitor operations."""
    pass


class DockerError(MonitorError):
    """Docker-related errors."""
    pass


class FusekiError(MonitorError):
    """Fuseki-related errors."""
    pass


class DSPToolsError(MonitorError):
    """DSP-tools command errors."""
    pass


class CompressionTimeoutError(FusekiError):
    """Database compression timeout error."""
    pass



def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Monitor Fuseki database size during XML uploads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default project.json
  %(prog)s my_project.json                   # Use custom project file

Features:
  - Automatically processes all .xml files in the 'files' subdirectory
  - Files are processed in alphabetical order
  - Records database size before and after each XML upload
  - Performs database compression after each XML upload
  - Monitors compression progress with timeout protection
  - Records database size before and after compression
  - Restarts DSP stack and creates project before processing XML files

Output:
  Results are written to fuseki_size.csv with columns:
  Timestamp,DB_Before,Filename,DB_After_Upload,DB_Before_Compression,Compression_Duration,DB_After_Compression

Note: The script must be run from a directory containing project.json and a 'files' subdirectory with XML files.
        """
    )
    
    parser.add_argument(
        'project_file',
        nargs='?',
        default='project.json',
        help='Path to the project.json file (default: project.json)'
    )
    
    parser.add_argument(
        '--xml-dir',
        type=Path,
        default=Path('files'),
        help='Directory containing XML files (default: files)'
    )
    
    parser.add_argument(
        '--output-csv',
        type=Path,
        default=Path('fuseki_size.csv'),
        help='Output CSV file (default: fuseki_size.csv)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


class DockerClient:
    """Docker container interaction client."""
    
    def __init__(self, image_name: str):
        self.image_name = image_name
        self.client = docker.from_env()
    
    def get_fuseki_container(self) -> docker.models.containers.Container:
        """Get the running Fuseki container."""
        try:
            containers = self.client.containers.list(
                filters={"ancestor": self.image_name}
            )
            if not containers:
                raise DockerError(f"No Fuseki container found running with image: {self.image_name}")
            
            if len(containers) > 1:
                logger.warning(f"Multiple Fuseki containers found, using first one")
            
            return containers[0]
        except docker.errors.DockerException as e:
            raise DockerError(f"Docker API error: {e}") from e
    
    def get_database_size(self) -> str:
        """Get Fuseki database size using docker exec du command."""
        try:
            container = self.get_fuseki_container()
            
            # Execute du -sh /fuseki inside container
            result = container.exec_run("du -sb /fuseki")
            if result.exit_code != 0:
                raise DockerError(f"Failed to get database size: {result.output.decode()}")
            
            # Parse output (format: "SIZE /fuseki")
            output = result.output.decode().strip()
            size = output.split()[0] if output else "0B"
            
            logger.debug(f"Database size: {size}")
            return size
            
        except docker.errors.DockerException as e:
            raise DockerError(f"Failed to get database size: {e}") from e
        except Exception as e:
            raise DockerError(f"Unexpected error getting database size: {e}") from e
    
    def wait_for_container(self, max_attempts: int = 60, wait_interval: int = 10) -> bool:
        """Wait for Fuseki container to be running and ready."""
        logger.info("Waiting for Fuseki container to be ready...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                container = self.get_fuseki_container()
                if container.status == "running":
                    # Additional wait for service to be fully ready
                    logger.info("Fuseki container detected, waiting for full readiness...")
                    time.sleep(15)
                    logger.info("Fuseki is ready")
                    return True
                else:
                    logger.debug(f"Container status: {container.status}")
            except DockerError:
                pass  # Container not found yet
            
            logger.info(f"Attempt {attempt}/{max_attempts}: Waiting for Fuseki...")
            time.sleep(wait_interval)
        
        logger.error("Fuseki did not become ready within expected time")
        return False


class ProcessManager:
    """Manager for DSP-tools subprocess operations."""

    def _run_command(self, cmd: list[str], timeout: int = 300, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with logging and error handling."""
        cmd_str = " ".join(cmd)
        logger.info(f"Executing: {cmd_str}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            
            if result.stdout:
                logger.debug(f"stdout: {result.stdout}")
            if result.stderr:
                logger.debug(f"stderr: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired as e:
            raise DSPToolsError(f"Command timed out after {timeout}s: {cmd_str}") from e
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}: {cmd_str}"
            if e.stderr:
                error_msg += f"\nstderr: {e.stderr}"
            raise DSPToolsError(error_msg) from e
        except Exception as e:
            raise DSPToolsError(f"Unexpected error running command {cmd_str}: {e}") from e
    
    def start_stack(self, prune: bool = True) -> None:
        """Start DSP stack with optional pruning."""
        cmd = ["dsp-tools", "start-stack"]
        if prune:
            cmd.append("--prune")
        
        self._run_command(cmd, timeout=600)
        logger.info("DSP stack started successfully")
    
    def stop_stack(self) -> None:
        """Stop DSP stack."""
        self._run_command(["dsp-tools", "stop-stack"], timeout=900)  # Increased to 15 minutes
        logger.info("DSP stack stopped successfully")
    
    def create_project(self, project_file: Path) -> None:
        """Create project from JSON file."""
        if not project_file.exists():
            raise DSPToolsError(f"Project file not found: {project_file}")
        
        self._run_command(["dsp-tools", "create", str(project_file)], timeout=600)
        logger.info(f"Project created successfully from {project_file}")
        
        # Wait for project creation to stabilize
        logger.info("Waiting for project creation to stabilize...")
        time.sleep(10)
    
    def xmlupload(self, xml_file: Path) -> None:
        """Upload XML file to DSP server."""
        if not xml_file.exists():
            raise DSPToolsError(f"XML file not found: {xml_file}")
        
        self._run_command([
            "dsp-tools", "xmlupload", 
            "--skip-validation", 
            str(xml_file)
        ], timeout=1800)  # 30 minutes timeout for large uploads
        
        logger.info(f"XML upload completed for {xml_file.name}")
        
        # Wait for upload to fully complete
        logger.info("Waiting for XML upload to fully complete...")
        time.sleep(15)


class FusekiAPIClient:
    """Client for Fuseki HTTP API operations."""
    
    def __init__(self, base_url: str, auth: tuple[str, str]):
        self.base_url = base_url.rstrip('/')
        self.logger = logger
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(*auth)
        # Set timeouts for all requests
        self.session.timeout = (30, 60)  # connect, read timeout
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"{method} {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout as e:
            raise FusekiError(f"Request timeout to {url}: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise FusekiError(f"Connection error to {url}: {e}") from e
        except requests.exceptions.HTTPError as e:
            raise FusekiError(f"HTTP error {e.response.status_code} from {url}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise FusekiError(f"Request error to {url}: {e}") from e
    
    def start_compression(self, dataset: str = "dsp-repo", max_attempts: int = 3) -> str:
        """Start database compression and return task ID."""
        endpoint = f"/$/compact/{dataset}"
        params = {"deleteOld": "true"}
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Starting database compression (attempt {attempt}/{max_attempts})...")
                response = self._make_request("POST", endpoint, params=params)
                
                # Parse JSON response to extract task ID
                data = response.json()
                task_id = data.get("taskId")
                
                if not task_id:
                    raise FusekiError(f"No taskId in response: {data}")
                
                logger.info(f"Database compression initiated with task ID: {task_id}")
                return task_id
                
            except FusekiError as e:
                logger.warning(f"Compression start attempt {attempt} failed: {e}")
                if attempt < max_attempts:
                    logger.info(f"Retrying in 20 seconds...")
                    time.sleep(20)
                else:
                    raise FusekiError(f"Failed to start compression after {max_attempts} attempts") from e
    
    def check_compression_status(self, task_id: str) -> dict:
        """Check compression task status."""
        endpoint = f"/$/tasks/{task_id}"
        
        try:
            response = self._make_request("GET", endpoint)
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to check compression status: {e}")
            return {"finished": False, "success": False}
    
    def wait_for_compression(self, task_id: str, timeout: int = 7200, check_interval: int = 60) -> bool:
        """Wait for compression to complete with progress monitoring."""
        logger.info(f"Waiting for database compression to complete (task ID: {task_id})...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            
            status = self.check_compression_status(task_id)
            finished = status.get("finished", False)
            
            if finished:
                success = status.get("success", True)  # Assume success if not specified
                if success:
                    logger.info("Database compression completed successfully")
                    return True
                else:
                    logger.error(f"Database compression failed: {status}")
                    return False
            
            logger.info(f"Database compression in progress... (elapsed: {elapsed}s)")
            time.sleep(check_interval)
        
        raise CompressionTimeoutError(f"Database compression timed out after {timeout}s")


class CSVReporter:
    """CSV file output manager."""
    
    CSV_HEADERS = [
        "Timestamp",
        "DB_Before", 
        "Filename",
        "DB_After_Upload",
        "DB_Before_Compression",
        "Compression_Duration",
        "DB_After_Compression"
    ]
    
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.logger = logger
        self._initialize_csv()
    
    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADERS)
            logger.info(f"Created new CSV file: {self.csv_path}")
        else:
            logger.info(f"Using existing CSV file: {self.csv_path}")
    
    def write_result(self, result: ProcessingResult) -> None:
        """Write processing result to CSV file."""
        try:
            with open(self.csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(result.to_csv_row())
            
            logger.info(f"Results for {result.filename} written to {self.csv_path}")
        
        except Exception as e:
            logger.error(f"Failed to write to CSV: {e}")
            raise MonitorError(f"CSV write error: {e}") from e


class FusekiMonitor:
    """Main orchestrator class for Fuseki monitoring operations."""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.logger = logger
        
        # Initialize components
        self.docker_client = DockerClient(config.fuseki_image)
        self.process_manager = ProcessManager()
        self.fuseki_client = FusekiAPIClient(config.fuseki_url, config.fuseki_auth)
        self.csv_reporter = CSVReporter(config.output_csv)
    
    def validate_inputs(self) -> None:
        """Validate required files and directories exist."""
        if not self.config.project_file.exists():
            raise MonitorError(f"Project file not found: {self.config.project_file}")
        
        if not self.config.xml_dir.exists():
            raise MonitorError(f"XML directory not found: {self.config.xml_dir}")
        
        logger.info(f"Looking for XML files in: {self.config.xml_dir}")
    
    def get_xml_files(self) -> list[Path]:
        """Get all XML files from the XML directory, sorted alphabetically."""
        xml_files = sorted(self.config.xml_dir.glob("*.xml"))
        
        if not xml_files:
            raise MonitorError(f"No XML files found in directory: {self.config.xml_dir}")
        
        logger.info(f"Found {len(xml_files)} XML files to process")
        return xml_files
    
    def process_xml_file(self, xml_file: Path, initial_db_size: str) -> ProcessingResult:
        """Process a single XML file and return results."""
        filename = xml_file.name
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"Processing XML file: {filename}")
        
        # Upload XML file
        logger.info(f"Starting XML upload for {filename}...")
        self.process_manager.xmlupload(xml_file)
        
        # Get DB size after upload (before compression)
        logger.info("Getting Fuseki database size after upload (before compression)...")
        try:
            db_after_upload = self.docker_client.get_database_size()
            logger.info(f"DB After Upload: {db_after_upload}")
        except DockerError as e:
            logger.warning(f"Failed to get database size after upload: {e}")
            db_after_upload = "ERROR"
        
        # Initialize compression variables
        compression_success = False
        db_before_compression = "N/A"
        compression_duration = "ERROR"
        db_after_compression = "ERROR"
        
        # Start compression process
        try:
            compression_start_time = time.time()
            task_id = self.fuseki_client.start_compression()
            
            # Get DB size before compression (should be same as after upload)
            try:
                db_before_compression = self.docker_client.get_database_size()
            except DockerError as e:
                logger.warning(f"Failed to get database size before compression: {e}")
                db_before_compression = "ERROR"
            
            # Wait for compression to complete
            if self.fuseki_client.wait_for_compression(
                task_id, 
                self.config.max_compression_timeout, 
                self.config.compression_check_interval
            ):
                compression_end_time = time.time()
                compression_duration = int(compression_end_time - compression_start_time)
                compression_success = True
                
                # Get DB size after compression
                logger.info("Getting Fuseki database size after compression...")
                try:
                    db_after_compression = self.docker_client.get_database_size()
                    logger.info(f"DB After Compression: {db_after_compression}")
                    logger.info(f"Compression took {compression_duration} seconds")
                except DockerError as e:
                    logger.warning(f"Failed to get database size after compression: {e}")
                    db_after_compression = "ERROR"
            else:
                logger.error("Compression failed")
                compression_duration = "FAILED"
                
        except CompressionTimeoutError:
            logger.error("Compression timed out")
            compression_duration = "TIMEOUT"
        except FusekiError as e:
            logger.error(f"Failed to initiate compression: {e}")
            compression_duration = "ERROR"
        
        # Create and return result
        result = ProcessingResult(
            timestamp=timestamp,
            db_before=initial_db_size,
            filename=filename,
            db_after_upload=db_after_upload,
            db_before_compression=db_before_compression,
            compression_duration=compression_duration,
            db_after_compression=db_after_compression
        )
        
        # Write to CSV
        self.csv_reporter.write_result(result)
        
        return result
    
    def run(self) -> None:
        """Main execution method."""
        try:
            logger.info("Starting DSP-Tools Fuseki Monitoring Script")
            logger.info(f"Project file: {self.config.project_file}")
            logger.info(f"Searching for XML files in directory: {self.config.xml_dir}")
            
            # Validate inputs
            self.validate_inputs()
            
            # Get XML files to process
            xml_files = self.get_xml_files()
            
            # Process each XML file in a complete DSP stack cycle
            for current_file_num, xml_file in enumerate(xml_files, 1):
                filename = xml_file.name
                logger.info(f"=== PROCESSING CYCLE {current_file_num}/{len(xml_files)}: {filename} ===")
                
                try:
                    # Stop and start DSP stack
                    logger.info("Stopping DSP stack...")
                    self.process_manager.stop_stack()
                    
                    logger.info("Starting DSP stack with prune...")
                    self.process_manager.start_stack(prune=True)
                    
                    # Wait for Fuseki to be ready
                    if not self.docker_client.wait_for_container(
                        self.config.fuseki_wait_attempts,
                        self.config.fuseki_wait_interval
                    ):
                        raise MonitorError("Fuseki failed to become ready")
                    
                    # Create project
                    logger.info(f"Creating project from {self.config.project_file}...")
                    self.process_manager.create_project(self.config.project_file)
                    
                    # Get DB size before XML upload
                    logger.info("Getting Fuseki database size before XML upload...")
                    try:
                        db_before = self.docker_client.get_database_size()
                        logger.info(f"DB Before XML upload: {db_before}")
                    except DockerError as e:
                        logger.warning(f"Failed to get database size before processing {xml_file}: {e}")
                        db_before = "ERROR"
                    
                    # Process the XML file
                    self.process_xml_file(xml_file, db_before)
                    
                    logger.info(f"Completed cycle {current_file_num}/{len(xml_files)} for {filename}")
                    
                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")
                    # Continue with next file rather than stopping entirely
                    continue
                
                logger.info("=" * 72)
            
            # Final cleanup - stop the stack
            logger.info("Stopping DSP stack after all processing...")
            self.process_manager.stop_stack()
            
            logger.info("All cycles completed successfully")
            logger.info(f"All results written to {self.config.output_csv}")
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)


def main() -> None:
    """Main entry point."""
    args = parse_args()

    
    # Create configuration
    config = MonitorConfig(
        project_file=Path(args.project_file),
        xml_dir=args.xml_dir,
        output_csv=args.output_csv
    )
    
    # Create and run monitor
    monitor = FusekiMonitor(config)
    monitor.run()


if __name__ == "__main__":
    main()
