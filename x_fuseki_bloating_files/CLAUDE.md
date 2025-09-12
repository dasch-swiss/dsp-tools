# Fuseki Bloating Analysis Scripts

This directory contains three shell scripts for analyzing Fuseki database size changes during XML uploads:

## Scripts Overview

### 1. `xmlupload_multiple_runs.sh`
**Purpose**: Performs multiple uploads of the same XML file without restarting the DSP stack between uploads.
- Uploads the same XML file N times (default: 5) to measure cumulative disk usage
- Restarts DSP stack only once at the beginning
- Creates project once at the beginning
- Records database size before and after each upload
- Outputs results to `fuseki_multiple_uploads.csv`

### 2. `xmlupload_size_increase.sh` 
**Purpose**: Processes multiple XML files sequentially, restarting the DSP stack for each file.
- Processes all XML files in the `files/` directory in alphabetical order
- Performs complete DSP stack restart cycle for each XML file
- Creates fresh project for each file
- Records database size before and after each XML upload
- Outputs results to `fuseki_size.csv`

### 3. `xmlupload_with_triple_count.sh`
**Purpose**: Enhanced version that tracks detailed triple statistics along with database size.
- Similar workflow to `xmlupload_size_increase.sh` but with additional SPARQL queries
- Records database size, total triple count, and triple type counts
- Uses SPARQL queries to count triples by data type (string, integer, dateTime, etc.)
- Dynamically generates CSV columns based on discovered data types
- Outputs comprehensive results to `fuseki_size.csv` with extended metrics

## Database Configuration
Database User: "admin", Password "test"

## Original Workflow Requirements

The initial workflow specification was:

1. Stop stack (same as now)
2. Start stack (same as now) & create project
3. Fuseki health (same as now)
4. Fuseki size (same as now)
5. Triple number (new!)

use the cURL exactly as written
cURL: http://127.0.0.1:3030/#/dataset/knora-test/query?query=SELECT%20%28COUNT%28%2A%29%20AS%20%3FnumberOfTriples%29%0AWHERE%20%7B%0A%20%20%3Fs%20%3Fp%20%3Fo%20.%0A%7D
response is in style 

```json
{
  "head": {
    "vars": [
      "numberOfTriples"
    ]
  },
  "results": {
    "bindings": [
      {
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "3353"
        }
      }
    ]
  }
}
```

Add to the csv new column: numberOfTriples_Before with the result in 3353

6. Triple types (new!)

   use the cURL exactly as written
   cURL: http://127.0.0.1:3030/#/dataset/knora-test/query?query=SELECT%20%3Fdtype%20%28COUNT%28%2A%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%20%20%3Fx%20%3Fy%20%3Fz.%0A%20%20FILTER%20%28%20isLiteral%28%3Fz%29%29%0A%20%20BIND%28DATATYPE%28%3Fz%29%20AS%20%3Fdtype%20%29%0A%7D%0AGROUP%20BY%20%3Fdtype

   result format

```json
{
  "head": {
    "vars": [
      "dtype",
      "count"
    ]
  },
  "results": {
    "bindings": [
      {
        "dtype": {
          "type": "uri",
          "value": "http://www.w3.org/2001/XMLSchema#string"
        },
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "286"
        }
      },
      {
        "dtype": {
          "type": "uri",
          "value": "http://www.w3.org/2001/XMLSchema#integer"
        },
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "6"
        }
      },
      {
        "dtype": {
          "type": "uri",
          "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
        },
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "654"
        }
      },
      {
        "dtype": {
          "type": "uri",
          "value": "http://www.w3.org/2001/XMLSchema#boolean"
        },
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "131"
        }
      },
      {
        "dtype": {
          "type": "uri",
          "value": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
        },
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "242"
        }
      },
      {
        "dtype": {
          "type": "uri",
          "value": "http://www.w3.org/2001/XMLSchema#dateTime"
        },
        "count": {
          "type": "literal",
          "datatype": "http://www.w3.org/2001/XMLSchema#integer",
          "value": "5"
        }
      }
    ]
  }
}
```

   make new csv columns for all in the format: "http://www.w3.org/2001/XMLSchema#integer _Before" value: "5"

7. xmlupload (same as now)
8. Fuseki size (same as now)
9. Triple number (new!) SAME AS POINT 5. now column called "numberOfTriples_After"
10. Triple types (new!) SAME AS POINT 6. now column called "http://www.w3.org/2001/XMLSchema#integer _After"
11. start again from 1.