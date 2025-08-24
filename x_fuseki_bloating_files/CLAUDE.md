# Workflow

Adjust this file: x_fuseki_bloating_files/xmlupload_with_restart_stack.sh

Database User: "admin", Password "test"

I want:

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