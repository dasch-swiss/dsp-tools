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
    # Try multiple possible Fuseki container patterns
    local cid=$(docker ps -q --filter "ancestor=daschswiss/apache-jena-fuseki:5.5.0-1")
    if [ -z "$cid" ]; then
        # Try other possible Fuseki containers
        cid=$(docker ps -q --filter "name=fuseki")
        if [ -z "$cid" ]; then
            cid=$(docker ps -q --filter "name=db")
            if [ -z "$cid" ]; then
                print_error "No Fuseki container found running. Available containers:"
                docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
                return 1
            fi
        fi
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

# Function to get number of triples from Fuseki
get_triple_count() {
    local query="SELECT (COUNT(*) AS ?numberOfTriples) WHERE { ?s ?p ?o . }"
    local response=$(curl -s -X POST "http://localhost:3030/dsp-repo/sparql" \
        -u "admin:test" \
        -H "Accept: application/sparql-results+json" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "query=${query}")
    
    if [ -z "$response" ]; then
        print_error "Failed to get triple count from Fuseki - empty response"
        return 1
    fi
    
    # Check if response contains error
    if echo "$response" | grep -q "error\|Error\|ERROR"; then
        print_error "Fuseki returned error: $(echo "$response" | head -1)"
        return 1
    fi
    
    # Extract the count value from JSON response
    local count=$(echo "$response" | grep -o '"value"[[:space:]]*:[[:space:]]*"[^"]*"' | tail -1 | sed 's/.*"\([^"]*\)".*/\1/')
    
    if [ -z "$count" ]; then
        print_error "Failed to parse triple count from response: $(echo "$response" | head -100)"
        return 1
    fi
    
    echo "$count"
}

# Function to get triple types from Fuseki
get_triple_types() {
    local query="SELECT ?dtype (COUNT(*) AS ?count) WHERE { ?x ?y ?z. FILTER ( isLiteral(?z)) BIND(DATATYPE(?z) AS ?dtype ) } GROUP BY ?dtype"
    local response=$(curl -s -X POST "http://localhost:3030/dsp-repo/sparql" \
        -u "admin:test" \
        -H "Accept: application/sparql-results+json" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "query=${query}")
    
    if [ -z "$response" ]; then
        print_error "Failed to get triple types from Fuseki"
        return 1
    fi
    
    # Check if response contains error
    if echo "$response" | grep -q "error\|Error\|ERROR"; then
        print_error "Fuseki returned error for triple types: $(echo "$response" | head -1)"
        return 1
    fi
    
    echo "$response"
}

# Function to parse triple types from JSON response
parse_triple_types() {
    local json_response="$1"
    
    # Extract all values in order: dtype1, count1, dtype2, count2, ...
    local values=$(echo "$json_response" | grep -o '"value"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)".*/\1/')
    
    # Convert to dtype,count pairs
    local result=""
    local line_num=0
    local current_dtype=""
    
    while IFS= read -r value; do
        if [ $((line_num % 2)) -eq 0 ]; then
            # Even line numbers are dtypes
            current_dtype="$value"
        else
            # Odd line numbers are counts
            if [ -n "$result" ]; then
                result="${result}\n${current_dtype},${value}"
            else
                result="${current_dtype},${value}"
            fi
        fi
        ((line_num++))
    done <<< "$values"
    
    echo -e "$result"
}

# Function to get all unique data types from initial query
get_unique_dtypes() {
    local triple_types_response=$(get_triple_types)
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    parse_triple_types "$triple_types_response" | cut -d',' -f1 | sort -u
}

# Function to get triple type counts as CSV values
get_triple_type_counts_csv() {
    local dtypes="$1"
    local triple_types_response=$(get_triple_types)
    local csv_values=""
    
    if [ $? -ne 0 ]; then
        # Return empty values if we can't get the data
        while IFS= read -r dtype; do
            csv_values="${csv_values},ERROR"
        done <<< "$dtypes"
        echo "$csv_values"
        return 1
    fi
    
    local parsed_types=$(parse_triple_types "$triple_types_response")
    
    while IFS= read -r dtype; do
        local count=$(echo "$parsed_types" | grep "^${dtype}," | cut -d',' -f2)
        if [ -z "$count" ]; then
            count="0"
        fi
        csv_values="${csv_values},${count}"
    done <<< "$dtypes"
    
    echo "$csv_values"
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

# Function to initialize CSV file with dynamic headers
initialize_csv() {
    if [ ! -f "$OUTPUT_CSV" ]; then
        # Start with base columns
        local header="Timestamp,DB_Before,numberOfTriples_Before"
        
        # Get unique data types for column headers (Fuseki should already be running)
        local dtypes=$(get_unique_dtypes)
        if [ $? -eq 0 ] && [ -n "$dtypes" ]; then
            while IFS= read -r dtype; do
                # Convert URL to column name format (add _Before suffix)
                local col_name="${dtype}_Before"
                header="${header},${col_name}"
            done <<< "$dtypes"
        fi
        
        # Add middle columns
        header="${header},Filename"
        
        # Add After columns
        header="${header},DB_After,numberOfTriples_After"
        
        # Add dtype After columns
        if [ $? -eq 0 ] && [ -n "$dtypes" ]; then
            while IFS= read -r dtype; do
                # Convert URL to column name format (add _After suffix)
                local col_name="${dtype}_After"
                header="${header},${col_name}"
            done <<< "$dtypes"
        fi
        
        echo "$header" > "$OUTPUT_CSV"
        print_status "Created new CSV file: $OUTPUT_CSV"
    fi
}

# Function to wait for Fuseki to be ready
wait_for_fuseki() {
    print_status "Waiting for Fuseki to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        # Check if Fuseki responds on localhost:3030
        local ping_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:3030/$/ping" 2>/dev/null || echo "000")
        if [ "$ping_response" = "200" ]; then
            print_status "Fuseki is ready on localhost:3030"
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
    local initial_triple_count="$3"
    local initial_triple_types_csv="$4"
    local dtypes="$5"
    
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
    
    # Get final triple count
    print_status "Getting triple count after upload..."
    local triple_count_after=$(get_triple_count)
    if [ $? -ne 0 ]; then
        print_warning "Failed to get triple count after upload"
        triple_count_after="ERROR"
    else
        print_status "Triple count after: $triple_count_after"
    fi
    
    # Get final triple types
    print_status "Getting triple types after upload..."
    local triple_types_after_csv=$(get_triple_type_counts_csv "$dtypes")
    if [ $? -ne 0 ]; then
        print_warning "Failed to get triple types after upload"
    fi
    
    # Write results to CSV
    local csv_line="$timestamp,$initial_db_size,$initial_triple_count$initial_triple_types_csv,$filename,$db_after,$triple_count_after$triple_types_after_csv"
    echo "$csv_line" >> "$OUTPUT_CSV"
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
    
    # Start stack initially for CSV header initialization
    print_status "Starting DSP stack for initial setup..."
    dsp-tools start-stack --prune
    
    # Wait for Fuseki to be ready
    wait_for_fuseki
    
    # Create project for initial data type discovery
    print_status "Creating project from $PROJECT_FILE for initial setup..."
    dsp-tools create "$PROJECT_FILE"
    
    # Initialize CSV with proper headers
    initialize_csv
    
    # Stop stack after initialization
    print_status "Stopping stack after initialization..."
    dsp-tools stop-stack
    
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
        
        # Get DB size before XML upload
        print_status "Getting Fuseki database size before XML upload..."
        local db_before=$(get_fuseki_size)
        if [ $? -ne 0 ]; then
            print_warning "Failed to get database size before processing $xml_file"
            db_before="ERROR"
        fi
        print_status "DB Before XML upload: $db_before"
        
        # Get triple count before XML upload
        print_status "Getting triple count before XML upload..."
        local triple_count_before=$(get_triple_count)
        if [ $? -ne 0 ]; then
            print_warning "Failed to get triple count before processing $xml_file"
            triple_count_before="ERROR"
        fi
        print_status "Triple count before: $triple_count_before"
        
        # Get unique data types for consistent column ordering
        local dtypes=$(get_unique_dtypes)
        
        # Get triple types before XML upload
        print_status "Getting triple types before XML upload..."
        local triple_types_before_csv=$(get_triple_type_counts_csv "$dtypes")
        if [ $? -ne 0 ]; then
            print_warning "Failed to get triple types before processing $xml_file"
        fi
        
        # Process the XML file
        process_xml_file "$xml_file" "$db_before" "$triple_count_before" "$triple_types_before_csv" "$dtypes"
        
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
    echo "  - Records triple count before and after each XML upload"
    echo "  - Records triple types and counts before and after each XML upload"
    echo "  - Restarts DSP stack and creates project before processing XML files"
    echo
    echo "Output:"
    echo "  Results are written to fuseki_size.csv with columns:"
    echo "  Timestamp,DB_Before,numberOfTriples_Before,[dtype_Before columns],Filename,DB_After,numberOfTriples_After,[dtype_After columns]"
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