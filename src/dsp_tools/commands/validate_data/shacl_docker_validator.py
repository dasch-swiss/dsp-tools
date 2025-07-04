"""
Docker-based SHACL validation utility for external SHACL validation.

This module provides functionality to run SHACL validation using the
daschswiss/shacl-cli Docker container.
"""

import subprocess
from pathlib import Path
from typing import Optional

from loguru import logger


class ShaclDockerValidator:
    """
    A utility class for running SHACL validation using Docker.
    
    This class manages the lifecycle of a Docker container for SHACL validation,
    including pulling the image, starting the container, running validations,
    and stopping the container.
    """
    
    DOCKER_IMAGE = "daschswiss/shacl-cli:latest"
    
    def __init__(self, results_dir: Optional[Path] = None):
        """
        Initialize the SHACL Docker validator.
        
        Args:
            results_dir: Directory to save validation results. If None, uses current directory.
        """
        self.results_dir = results_dir or Path.cwd()
        self.container_id: Optional[str] = None
        
    def pull_image(self) -> bool:
        """
        Pull the SHACL CLI Docker image if it doesn't exist.
        
        Returns:
            True if image was pulled successfully or already exists, False otherwise.
        """
        try:
            logger.info(f"Pulling Docker image: {self.DOCKER_IMAGE}")
            result = subprocess.run(
                ["docker", "pull", self.DOCKER_IMAGE],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Docker image pulled successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull Docker image: {e.stderr}")
            return False
    
    def start_container(self) -> bool:
        """
        Start the Docker container for SHACL validation.
        
        Returns:
            True if container started successfully, False otherwise.
        """
        try:
            # Check if image exists, pull if not
            if not self._image_exists():
                if not self.pull_image():
                    return False
            
            logger.info("Starting SHACL validation container")
            result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "-v", f"{self.results_dir.absolute()}:/data",
                    "--name", "shacl-validator",
                    self.DOCKER_IMAGE,
                    "tail", "-f", "/dev/null"  # Keep container running
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.container_id = result.stdout.strip()
            logger.info(f"Container started with ID: {self.container_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start container: {e.stderr}")
            return False
    
    def validate(self, shacl_file: Path, data_file: Path, report_file: Path) -> bool:
        """
        Run SHACL validation on the provided files.
        
        Args:
            shacl_file: Path to the SHACL shapes file
            data_file: Path to the RDF data file
            report_file: Path where validation report should be saved
            
        Returns:
            True if validation completed successfully, False otherwise.
        """
        if not self.container_id:
            logger.error("Container not started. Call start_container() first.")
            return False
        
        try:
            # Ensure files exist
            if not shacl_file.exists():
                logger.error(f"SHACL file not found: {shacl_file}")
                return False
            if not data_file.exists():
                logger.error(f"Data file not found: {data_file}")
                return False
            
            # Get relative paths within the container
            shacl_path = f"/data/{shacl_file.name}"
            data_path = f"/data/{data_file.name}"
            report_path = f"/data/{report_file.name}"
            
            logger.info(f"Running SHACL validation: {shacl_file.name} -> {data_file.name}")
            
            result = subprocess.run(
                [
                    "docker", "exec", self.container_id,
                    "validate",
                    "--shacl", shacl_path,
                    "--data", data_path,
                    "--report", report_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Validation completed. Report saved to: {report_file}")
            if result.stdout:
                logger.debug(f"Validation output: {result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"SHACL validation failed: {e.stderr}")
            if e.stdout:
                logger.debug(f"Validation stdout: {e.stdout}")
            return False
    
    def run_multiple_validations(self, validation_configs: list[dict]) -> list[bool]:
        """
        Run multiple SHACL validations without restarting the container.
        
        Args:
            validation_configs: List of dictionaries with keys:
                - shacl_file: Path to SHACL shapes file
                - data_file: Path to RDF data file  
                - report_file: Path for validation report
                
        Returns:
            List of boolean results for each validation.
        """
        results = []
        for i, config in enumerate(validation_configs, 1):
            logger.info(f"Running validation {i}/{len(validation_configs)}")
            success = self.validate(
                shacl_file=config["shacl_file"],
                data_file=config["data_file"],
                report_file=config["report_file"]
            )
            results.append(success)
        
        return results
    
    def stop_container(self) -> bool:
        """
        Stop and remove the Docker container.
        
        Returns:
            True if container was stopped successfully, False otherwise.
        """
        if not self.container_id:
            logger.warning("No container to stop")
            return True
        
        try:
            logger.info(f"Stopping container: {self.container_id}")
            subprocess.run(
                ["docker", "stop", self.container_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            subprocess.run(
                ["docker", "rm", self.container_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Container stopped and removed")
            self.container_id = None
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop container: {e.stderr}")
            return False
    
    def _image_exists(self) -> bool:
        """Check if the Docker image exists locally."""
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", self.DOCKER_IMAGE],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def __enter__(self):
        """Context manager entry - start the container."""
        if not self.start_container():
            raise RuntimeError("Failed to start SHACL validation container")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop the container."""
        self.stop_container()