#!/bin/bash

# Multiple Upload DSP-Tools Fuseki Monitoring Script
# This script uploads the same XML file multiple times without restarting the stack
# and monitors Fuseki database size changes between each upload

set -e  # Exit on any error

# Configuration - Fixed paths within x_fuseki_bloating_files directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_FILE="$SCRIPT_DIR/project.json"
UPLOAD_COUNT="${1:-5}"
OUTPUT_DIR="$SCRIPT_DIR"
OUTPUT_CSV="$OUTPUT_DIR/fuseki_multiple_uploads.csv"

# Function to find XML file in files directory
find_xml_file() {
    local xml_files=$(find "$SCRIPT_DIR/files" -name "*.xml" -type f 2>/dev/null | head -1)
    if [ -z "$xml_files" ]; then
        print_error "No XML files found in $SCRIPT_DIR/files directory"
        exit 1
    fi
    echo "$xml_files"
}

XML_FILE=$(find_xml_file)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get Fuseki container ID
get_fuseki_container_id() {
    local cid=$(docker ps -q --filter "ancestor=daschswiss/apache-jena-fuseki:5.2.0")
    if [ -z "$cid" ]; then
        print_error "No Fuseki container found running"
        return 1
    fi
    echo "$cid"
}

# Function to get Fuseki database size
get_fuseki_size() {
    local cid=$(get_fuseki_container_id)
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    local size=$(docker exec "$cid" du -sh /fuseki 2>/dev/null | awk '{print $1}')
    if [ -z "$size" ]; then
        print_error "Failed to get Fuseki database size"
        return 1
    fi
    echo "$size"
}

# Function to validate required files
validate_inputs() {
    if [ ! -f "$PROJECT_FILE" ]; then
        print_error "Project file '$PROJECT_FILE' not found"
        exit 1
    fi
    
    if [ ! -d "$SCRIPT_DIR/files" ]; then
        print_error "Files directory '$SCRIPT_DIR/files' not found"
        exit 1
    fi
    
    if [ ! -f "$XML_FILE" ]; then
        print_error "XML file '$XML_FILE' not found"
        exit 1
    fi
    
    if ! [[ "$UPLOAD_COUNT" =~ ^[1-9][0-9]*$ ]]; then
        print_error "Upload count must be a positive integer, got: $UPLOAD_COUNT"
        exit 1
    fi
    
    print_status "Script directory: $SCRIPT_DIR"
    print_status "Project file: $PROJECT_FILE"
    print_status "XML file: $XML_FILE"
    print_status "Upload count: $UPLOAD_COUNT"
}

# Function to initialize CSV file
initialize_csv() {
    echo "Run,Timestamp,DB_Before,DB_After" > "$OUTPUT_CSV"
    print_status "Created new CSV file: $OUTPUT_CSV"
}

# Function to wait for Fuseki to be ready
wait_for_fuseki() {
    print_status "Waiting for Fuseki to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if get_fuseki_container_id > /dev/null 2>&1; then
            # Wait a bit more for the service to be fully ready
            sleep 5
            print_status "Fuseki is ready"
            return 0
        fi
        print_status "Attempt $attempt/$max_attempts: Waiting for Fuseki..."
        sleep 5
        ((attempt++))
    done
    
    print_error "Fuseki did not become ready within expected time"
    return 1
}

# Function to perform a single upload run
perform_upload_run() {
    local run_number="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    print_status "=== UPLOAD RUN $run_number/$UPLOAD_COUNT ==="
    
    # Get DB size before upload
    print_status "Getting Fuseki database size before upload..."
    local db_before=$(get_fuseki_size)
    if [ $? -ne 0 ]; then
        print_warning "Failed to get database size before upload"
        db_before="ERROR"
    else
        print_status "DB Before: $db_before"
    fi
    
    # Perform xmlupload with skip validation
    local filename=$(basename "$XML_FILE")
    print_status "Starting XML upload for $filename (run $run_number)..."
    dsp-tools xmlupload --skip-validation "$XML_FILE"
    
    # Get DB size after upload
    print_status "Getting Fuseki database size after upload..."
    local db_after=$(get_fuseki_size)
    if [ $? -ne 0 ]; then
        print_warning "Failed to get database size after upload"
        db_after="ERROR"
    else
        print_status "DB After: $db_after"
    fi
    
    # Write results to CSV
    echo "$run_number,$timestamp,$db_before,$db_after" >> "$OUTPUT_CSV"
    print_status "Results for run $run_number written to $OUTPUT_CSV"
    
    echo "========================================"
    
    return 0
}

# Main execution function
main() {
    print_status "Starting Multiple Upload DSP-Tools Fuseki Monitoring Script"
    
    # Validate inputs
    validate_inputs
    
    # Initialize CSV
    initialize_csv
    
    # Stop and start DSP stack once at the beginning
    print_status "Stopping DSP stack..."
    dsp-tools stop-stack
    
    print_status "Starting DSP stack with prune..."
    dsp-tools start-stack --prune
    
    # Wait for Fuseki to be ready
    wait_for_fuseki
    
    # Create project once at the beginning
    print_status "Creating project from $PROJECT_FILE..."
    dsp-tools create "$PROJECT_FILE"
    
    # Perform multiple uploads
    for ((run=1; run<=UPLOAD_COUNT; run++)); do
        perform_upload_run "$run"
    done
    
    # Final cleanup - stop the stack
    print_status "Stopping DSP stack after all uploads..."
    dsp-tools stop-stack
    
    print_status "All $UPLOAD_COUNT upload runs completed successfully"
    print_status "All results written to $OUTPUT_CSV"
}

# Usage function
usage() {
    echo "Usage: $0 [UPLOAD_COUNT]"
    echo
    echo "Arguments:"
    echo "  UPLOAD_COUNT      Number of times to upload the XML file (default: 5)"
    echo
    echo "Examples:"
    echo "  $0                # Upload 5 times (default)"
    echo "  $0 10             # Upload 10 times"
    echo
    echo "Features:"
    echo "  - Uses fixed project.json from script directory"
    echo "  - Automatically finds first XML file in files/ subdirectory"
    echo "  - Starts DSP stack once and creates project once"
    echo "  - Uploads the same XML file multiple times without restarting stack"
    echo "  - Records database size before and after each upload"
    echo "  - Tracks size growth across multiple uploads"
    echo
    echo "Output:"
    echo "  Results are written to fuseki_multiple_uploads.csv with columns: Run,Timestamp,DB_Before,DB_After"
    echo
    echo "Note: Script must be run from or contain x_fuseki_bloating_files/project.json and files/ directory"
}

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Simple argument handling
if [ $# -gt 1 ]; then
    print_error "Too many arguments."
    usage
    exit 1
fi

# Validate upload count argument if provided
if [ $# -eq 1 ] && [ ! -z "$1" ]; then
    if ! [[ "$1" =~ ^[1-9][0-9]*$ ]]; then
        print_error "Argument '$1' must be a positive integer"
        exit 1
    fi
fi

# Run main function
main