# Workflow

- dsp-tools start-stack
- dsp-tools create fuseki_bloating/project.json
- CID=$(docker ps -q --filter "ancestor=daschswiss/apache-jena-fuseki:5.5.0-1") && docker exec -it $CID du -sh /fuseki
- dsp-tools xmlupload --skip-validation fuseki_bloating/
- CID=$(docker ps -q --filter "ancestor=daschswiss/apache-jena-fuseki:5.5.0-1") && docker exec -it $CID du -sh /fuseki

# TODO:

- Upload the file with every type once, several times without re-starting the stack to see the increase
- To compare fuseki triple size, upload one resource without values and see the val increase
- Create average GB growth per triple for each value type, for that you need to upload 13 values for a resource so it can be compared to the every once
- add plot for filesize vs db growth

## Further but out of scope

- stash
- do it on a server to compare?
- Richtext with standoff link to resource or URI or XML mark-up

# Analysis

## Considerations about the data

- Multiple Values per Resource
  - apart from boolean (where 0-1) every value uses the same property
  - Int Values contain a different number (0-n), this may have affected the result
- Type Comparison
  - apart from boolean (where 0-1) every value uses the same property
  - All the values contain the identical content (duplicate check disabled)
  - All text values tested separately, the content of the text value is identical

## Observations

- Change in computer did not make a difference
- The uploads where the number of resources / values increased have a vastly different DB size than the ones where
  we compare the value types. While the number of values is not identical, therefore an exact comparison cannot be done
  I cannot explain the difference.
- To ensure that the multiple uploads do not differ too much, we need to run it multiple times and compare.
- 

## Local Mac Docker Resources

- CPU Limit: 9
- Memory Limit 16 GB
- Swap: 1 GB
- Disk: 1.37 TB

## Cheesgrater Docker Resources

- CPU Limit: 32
- Memory Limit 78.3 GB
- Swap: 0 GB
- Disk: 17 TB


# Queries

## Number of triples

```
SELECT (COUNT(*) AS ?numberOfTriples)
WHERE {
  ?s ?p ?o .
}
```

http://127.0.0.1:3030/#/dataset/knora-test/query?query=SELECT%20%28COUNT%28%2A%29%20AS%20%3FnumberOfTriples%29%0AWHERE%20%7B%0A%20%20%3Fs%20%3Fp%20%3Fo%20.%0A%7D


Response:

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

Give all the dtypes of objects

http://127.0.0.1:3030/#/dataset/knora-test/query?query=SELECT%20%3Fdtype%20%28COUNT%28%2A%29%20AS%20%3Fcount%29%0AWHERE%20%7B%0A%20%20%3Fx%20%3Fy%20%3Fz.%0A%20%20FILTER%20%28%20isLiteral%28%3Fz%29%29%0A%20%20BIND%28DATATYPE%28%3Fz%29%20AS%20%3Fdtype%20%29%0A%7D%0AGROUP%20BY%20%3Fdtype

```
SELECT ?dtype (COUNT(*) AS ?count)
WHERE {
  ?x ?y ?z.
  FILTER ( isLiteral(?z))
  BIND(DATATYPE(?z) AS ?dtype )
}
GROUP BY ?dtype
```

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