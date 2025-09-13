#!/bin/bash

# Automated DSP-Tools Fuseki Monitoring Script
# This script performs DSP stack operations and monitors Fuseki database size changes

set -e  # Exit on any error

# Configuration
PROJECT_FILE="${1:-project.json}"
XML_DIR="$(pwd)/files"  # Always use files subdirectory
XML_FILE=""
OUTPUT_CSV="fuseki_size.csv"

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
    local cid=$(docker ps -q --filter "ancestor=daschswiss/apache-jena-fuseki:5.5.0-1")
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

# Function to kick off database compression
kick_off_compression() {
    print_status "Kicking off database compression..."
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        local response=$(curl -s -w "%{http_code}" -X POST \
            "http://localhost:3030/\$/compact/dsp-repo?deleteOld=true" \
            -u "admin:test" \
            --connect-timeout 30 \
            --max-time 60 2>/dev/null)
        
        local http_code="${response: -3}"
        local response_body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            # Extract taskId from JSON response
            local task_id=$(echo "$response_body" | grep -o '"taskId"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)".*/\1/')
            if [ -n "$task_id" ]; then
                print_status "Database compression initiated with task ID: $task_id"
                echo "$task_id"
                return 0
            else
                print_warning "Failed to extract task ID from response: $response_body"
            fi
        else
            print_warning "Compression request failed (attempt $attempt/$max_attempts): HTTP $http_code - $response_body"
        fi
        
        sleep 20  # Increased from 10 to 20 seconds between attempts
        ((attempt++))
    done
    
    print_error "Failed to kick off database compression after $max_attempts attempts"
    return 1
}

# Function to wait for compression to complete
wait_for_compression() {
    local task_id="$1"
    print_status "Waiting for database compression to complete (task ID: $task_id)..."
    
    local max_wait_time=7200  # Increased to 2 hours timeout
    local elapsed_time=0
    local check_interval=60   # Increased from 30 to 60 seconds
    
    while [ $elapsed_time -lt $max_wait_time ]; do
        local response=$(curl -s -w "%{http_code}" \
            "http://localhost:3030/\$/tasks/$task_id" \
            -u "admin:test" \
            --connect-timeout 30 \
            --max-time 60 2>/dev/null)
        
        local http_code="${response: -3}"
        local response_body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            # Check if task is finished
            local finished=$(echo "$response_body" | grep -o '"finished"[[:space:]]*:[[:space:]]*[a-z]*' | sed 's/.*:\s*//')
            
            if [ "$finished" = "true" ]; then
                print_status "Database compression completed successfully"
                return 0
            else
                print_status "Database compression in progress... (elapsed: ${elapsed_time}s)"
            fi
        else
            print_warning "Failed to check compression status: HTTP $http_code - $response_body"
        fi
        
        sleep $check_interval
        elapsed_time=$((elapsed_time + check_interval))
    done
    
    print_error "Database compression timed out after ${max_wait_time}s"
    return 1
}

# Function to validate required files
validate_inputs() {
    if [ ! -f "$PROJECT_FILE" ]; then
        print_error "Project file '$PROJECT_FILE' not found in current directory"
        exit 1
    fi
    
    # Check if files directory exists
    if [ ! -d "$XML_DIR" ]; then
        print_error "Files directory '$XML_DIR' not found"
        exit 1
    fi
    
    print_status "Looking for XML files in: $XML_DIR"
}

# Function to get all XML files from directory
get_xml_files() {
    local dir="$1"
    find "$dir" -name "*.xml" -type f | sort
}

# Function to initialize CSV file
initialize_csv() {
    if [ ! -f "$OUTPUT_CSV" ]; then
        echo "Timestamp,DB_Before,Filename,DB_After_Upload,DB_Before_Compression,Compression_Duration,DB_After_Compression" > "$OUTPUT_CSV"
        print_status "Created new CSV file: $OUTPUT_CSV"
    fi
}

# Function to wait for Fuseki to be ready
wait_for_fuseki() {
    print_status "Waiting for Fuseki to be ready..."
    local max_attempts=60  # Increased from 30 to 60 attempts
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if get_fuseki_container_id > /dev/null 2>&1; then
            # Wait longer for the service to be fully ready and stable
            print_status "Fuseki container detected, waiting for full readiness..."
            sleep 15  # Increased from 5 to 15 seconds
            print_status "Fuseki is ready"
            return 0
        fi
        print_status "Attempt $attempt/$max_attempts: Waiting for Fuseki..."
        sleep 10  # Increased from 5 to 10 seconds between attempts
        ((attempt++))
    done
    
    print_error "Fuseki did not become ready within expected time"
    return 1
}

# Function to process a single XML file
process_xml_file() {
    local xml_file="$1"
    local initial_db_size="$2"
    
    local filename=$(basename "$xml_file")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    print_status "Processing XML file: $filename"
    
    # Perform xmlupload with skip validation
    print_status "Starting XML upload for $filename..."
    dsp-tools xmlupload --skip-validation "$xml_file"
    
    # Wait for XML upload to fully complete before measuring size
    print_status "Waiting for XML upload to fully complete..."
    sleep 15
    
    # Get DB size after upload (before compression)
    print_status "Getting Fuseki database size after upload (before compression)..."
    local db_after_upload=$(get_fuseki_size)
    if [ $? -ne 0 ]; then
        print_warning "Failed to get database size after upload"
        db_after_upload="ERROR"
    else
        print_status "DB After Upload: $db_after_upload"
    fi
    
    # Start compression process
    local compression_start_time=$(date +%s)
    local task_id=$(kick_off_compression)
    local compression_success=false
    local db_before_compression="N/A"
    local compression_duration="ERROR"
    local db_after_compression="ERROR"
    
    if [ $? -eq 0 ] && [ -n "$task_id" ]; then
        # Get DB size before compression (should be same as after upload, but measure again for accuracy)
        db_before_compression=$(get_fuseki_size)
        if [ $? -ne 0 ]; then
            print_warning "Failed to get database size before compression"
            db_before_compression="ERROR"
        fi
        
        # Wait for compression to complete
        if wait_for_compression "$task_id"; then
            local compression_end_time=$(date +%s)
            compression_duration=$((compression_end_time - compression_start_time))
            compression_success=true
            
            # Get DB size after compression
            print_status "Getting Fuseki database size after compression..."
            db_after_compression=$(get_fuseki_size)
            if [ $? -ne 0 ]; then
                print_warning "Failed to get database size after compression"
                db_after_compression="ERROR"
            else
                print_status "DB After Compression: $db_after_compression"
                print_status "Compression took ${compression_duration} seconds"
            fi
        else
            print_error "Compression failed or timed out"
            compression_duration="TIMEOUT"
        fi
    else
        print_error "Failed to initiate compression"
    fi
    
    # Write results to CSV
    echo "$timestamp,$initial_db_size,$filename,$db_after_upload,$db_before_compression,$compression_duration,$db_after_compression" >> "$OUTPUT_CSV"
    print_status "Results for $filename written to $OUTPUT_CSV"
    
    return 0
}

# Main execution function
main() {
    print_status "Starting DSP-Tools Fuseki Monitoring Script"
    print_status "Project file: $PROJECT_FILE"
    print_status "Searching for XML files in files directory: $XML_DIR"
    
    # Validate inputs
    validate_inputs
    
    # Initialize CSV
    initialize_csv
    
    # Get XML files for loop processing
    local xml_files=$(get_xml_files "$XML_DIR")
    local file_count=0
    
    if [ -n "$xml_files" ] && [ "$xml_files" != "" ]; then
        file_count=$(echo "$xml_files" | wc -l)
    fi
    
    if [ $file_count -eq 0 ]; then
        print_warning "No XML files found in files directory: $XML_DIR"
        exit 1
    fi
    
    print_status "Found $file_count XML files to process in loop"
    
    # Process each XML file in a complete DSP stack cycle
    local current_file_num=1
    while IFS= read -r xml_file; do
        local filename=$(basename "$xml_file")
        print_status "=== PROCESSING CYCLE $current_file_num/$file_count: $filename ==="
        
        # Stop and start DSP stack
        print_status "Stopping DSP stack..."
        dsp-tools stop-stack
        
        print_status "Starting DSP stack with prune..."
        dsp-tools start-stack --prune
        
        # Wait for Fuseki to be ready
        wait_for_fuseki
        
        # Create project
        print_status "Creating project from $PROJECT_FILE..."
        dsp-tools create "$PROJECT_FILE"
        
        # Wait for project creation to fully complete
        print_status "Waiting for project creation to stabilize..."
        sleep 10
        
        # Get DB size before XML upload
        print_status "Getting Fuseki database size before XML upload..."
        local db_before=$(get_fuseki_size)
        if [ $? -ne 0 ]; then
            print_warning "Failed to get database size before processing $xml_file"
            db_before="ERROR"
        fi
        print_status "DB Before XML upload: $db_before"
        
        # Process the XML file
        process_xml_file "$xml_file" "$db_before"
        
        print_status "Completed cycle $current_file_num/$file_count for $filename"
        echo "========================================"
        
        ((current_file_num++))
    done <<< "$xml_files"
    
    # Final cleanup - stop the stack
    print_status "Stopping DSP stack after all processing..."
    dsp-tools stop-stack
    
    print_status "All cycles completed successfully"
    print_status "All results written to $OUTPUT_CSV"
}

# Usage function
usage() {
    echo "Usage: $0 [PROJECT_FILE]"
    echo
    echo "Arguments:"
    echo "  PROJECT_FILE      Path to the project.json file (default: project.json)"
    echo
    echo "Examples:"
    echo "  $0                                    # Use default project.json"
    echo "  $0 my_project.json                   # Use custom project file"
    echo
    echo "Features:"
    echo "  - Automatically processes all .xml files in the 'files' subdirectory"
    echo "  - Files are processed in alphabetical order"
    echo "  - Records database size before and after each XML upload"
    echo "  - Performs database compression after each XML upload"
    echo "  - Monitors compression progress with timeout protection"
    echo "  - Records database size before and after compression"
    echo "  - Restarts DSP stack and creates project before processing XML files"
    echo
    echo "Output:"
    echo "  Results are written to fuseki_size.csv with columns:"
    echo "  Timestamp,DB_Before,Filename,DB_After_Upload,DB_Before_Compression,Compression_Duration,DB_After_Compression"
    echo
    echo "Note: The script must be run from a directory containing project.json and a 'files' subdirectory with XML files."
}

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Simple argument handling: only accept PROJECT_FILE as optional argument
if [ $# -eq 1 ]; then
    if [ -f "$1" ] && [[ "$1" == *.json ]]; then
        # Single argument is a JSON file - use as project file
        PROJECT_FILE="$1"
    else
        print_error "Argument '$1' must be a JSON project file"
        exit 1
    fi
elif [ $# -gt 1 ]; then
    print_error "Too many arguments. Only PROJECT_FILE is accepted."
    usage
    exit 1
fi

# Run main function
main