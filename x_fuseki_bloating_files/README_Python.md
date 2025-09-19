# Python XML Upload Monitor

Python rewrite of `xmlupload_size_increase.sh` that monitors Fuseki database size changes during XML uploads with compression tracking.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage (default project.json, files/ directory)
./xmlupload_monitor.py

# Custom project file
./xmlupload_monitor.py my_project.json

# Custom XML directory and output
./xmlupload_monitor.py --xml-dir my_files --output-csv my_results.csv

# Verbose logging
./xmlupload_monitor.py --verbose
```

## Key Improvements over Shell Script

### **Reliability**
- **Structured error handling** with custom exception hierarchy
- **Better timeout management** with configurable intervals
- **Robust HTTP client** with automatic retries and connection pooling
- **Native Docker API** integration (no subprocess calls)

### **Maintainability**
- **Object-oriented design** with clear separation of concerns
- **Full type hints** for better IDE support and catch errors
- **Modular architecture** - easy to extend or modify individual components
- **Comprehensive logging** with colored output and debug levels

### **Functionality**
- **Better progress monitoring** with detailed status updates
- **Configurable timeouts** and retry attempts
- **Graceful error recovery** - continues processing other files if one fails
- **CSV output validation** with structured data models

## Architecture

```
xmlupload_monitor.py
├── MonitorConfig        # Configuration management
├── ProcessingResult     # CSV data structure
├── DockerClient         # Docker container operations
├── ProcessManager       # DSP-tools subprocess management  
├── FusekiAPIClient      # Fuseki HTTP API operations
├── CSVReporter          # CSV file output
└── FusekiMonitor        # Main orchestration class
```

## Error Handling

The script includes comprehensive error handling:

- **MonitorError** - Base exception for monitor operations
- **DockerError** - Docker-related errors (container not found, size measurement failures)
- **FusekiError** - Fuseki API errors (compression failures, connection issues)
- **DSPToolsError** - DSP-tools command execution errors
- **CompressionTimeoutError** - Database compression timeout

## Timing Improvements

The Python version incorporates the timing fixes from the updated shell script:

- **Fuseki readiness**: Up to 10 minutes wait time (60 attempts × 10s intervals)
- **Post-detection wait**: 15 seconds for full service readiness
- **Compression timeout**: 2 hours maximum
- **Compression polling**: 60-second intervals (less frequent than shell script)
- **Operation buffers**: 10s after project creation, 15s after XML upload

## Output

Results are written to `fuseki_size.csv` with columns:
- `Timestamp` - Processing start time
- `DB_Before` - Database size before XML upload
- `Filename` - XML file being processed
- `DB_After_Upload` - Database size after XML upload (before compression)
- `DB_Before_Compression` - Database size when compression starts
- `Compression_Duration` - Time taken for compression (seconds, or ERROR/TIMEOUT/FAILED)
- `DB_After_Compression` - Database size after compression completes

## Requirements

- Python 3.7+ (for dataclasses)
- Docker daemon running
- DSP-tools available in PATH
- Dependencies listed in `requirements.txt`

## Migration from Shell Script

The Python version maintains full compatibility with the shell script's functionality while providing significant improvements in reliability and maintainability. It can be used as a drop-in replacement with the same command-line interface.