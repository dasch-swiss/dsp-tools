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
        echo "Timestamp,DB_Before,Filename,DB_After" > "$OUTPUT_CSV"
        print_status "Created new CSV file: $OUTPUT_CSV"
    fi
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
    
    # Get final DB size
    print_status "Getting Fuseki database size after upload..."
    local db_after=$(get_fuseki_size)
    if [ $? -ne 0 ]; then
        print_warning "Failed to get database size after upload"
        db_after="ERROR"
    else
        print_status "DB After: $db_after"
    fi
    
    # Write results to CSV
    echo "$timestamp,$initial_db_size,$filename,$db_after" >> "$OUTPUT_CSV"
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
    
    # Get initial DB size (after project creation)
    print_status "Getting initial Fuseki database size..."
    local db_before=$(get_fuseki_size)
    if [ $? -ne 0 ]; then
        print_error "Failed to get initial database size"
        exit 1
    fi
    print_status "DB Before (after project creation): $db_before"
    
    # Process XML files from current directory
    local xml_files=$(get_xml_files "$XML_DIR")
    local file_count=0
    
    if [ -n "$xml_files" ] && [ "$xml_files" != "" ]; then
        file_count=$(echo "$xml_files" | wc -l)
    fi
    
    if [ $file_count -eq 0 ]; then
        print_warning "No XML files found in files directory: $XML_DIR"
        # Still record the baseline
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp,$db_before,NO_XML_FILES,N/A" >> "$OUTPUT_CSV"
    else
        print_status "Found $file_count XML files to process"
        
        local current_file_num=1
        while IFS= read -r xml_file; do
            print_status "Processing file $current_file_num/$file_count: $(basename "$xml_file")"
            
            # Use the current database size as the "before" size for this file
            local current_db_before=$(get_fuseki_size)
            if [ $? -ne 0 ]; then
                print_warning "Failed to get database size before processing $xml_file"
                current_db_before="ERROR"
            fi
            
            process_xml_file "$xml_file" "$current_db_before"
            
            print_status "Completed file $current_file_num/$file_count"
            echo "----------------------------------------"
            
            ((current_file_num++))
        done <<< "$xml_files"
    fi
    
    # Get final summary
    local final_db_size=$(get_fuseki_size)
    
    # Display summary
    echo
    print_status "=== FINAL SUMMARY ==="
    echo "Initial DB size (after project creation): $db_before"
    echo "Final DB size: $final_db_size"
    print_status "All results written to $OUTPUT_CSV"
    
    print_status "Script completed successfully"
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
    echo "  - Restarts DSP stack and creates project before processing XML files"
    echo
    echo "Output:"
    echo "  Results are written to fuseki_size.csv with columns: Timestamp,DB_Before,Filename,DB_After"
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