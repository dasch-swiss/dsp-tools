"""
Expected response text for OntologyClientLive.post_resource_cardinalities()

{
    "status_code": 200,
    "headers": {
        "Server": "webapi/v32.3.2",
        "Date": "Tue, 14 Oct 2025 13:23:48 GMT",
        "Content-Type": "application/ld+json",
        "Content-Length": "6760"
    },
    "content": {
        "knora-api:lastModificationDate": {
            "@value": "2025-10-14T13:23:48.751237753Z",
            "@type": "xsd:dateTimeStamp"
        },
        "rdfs:label": "Second test ontology",
        "@graph": [
            {
                "knora-api:isResourceClass": true,
                "rdfs:label": {
                    "@value": "Resource with a property from first ontology",
                    "@language": "en"
                },
                "knora-api:canBeInstantiated": true,
                "rdfs:subClassOf": [
                    {
                        "@id": "knora-api:Resource"
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "e2e-testonto:hasText"
                        },
                        "owl:maxCardinality": 1
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:arkUrl"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:attachedToProject"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:attachedToUser"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:creationDate"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:deleteComment"
                        },
                        "owl:maxCardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:deleteDate"
                        },
                        "owl:maxCardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:deletedBy"
                        },
                        "owl:maxCardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:hasIncomingLinkValue"
                        },
                        "owl:minCardinality": 0,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:hasPermissions"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:hasStandoffLinkTo"
                        },
                        "owl:minCardinality": 0,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:hasStandoffLinkToValue"
                        },
                        "owl:minCardinality": 0,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:isDeleted"
                        },
                        "owl:maxCardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:lastModificationDate"
                        },
                        "owl:maxCardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:userHasPermission"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:versionArkUrl"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "knora-api:versionDate"
                        },
                        "owl:maxCardinality": 1,
                        "knora-api:isInherited": true
                    },
                    {
                        "@type": "owl:Restriction",
                        "owl:onProperty": {
                            "@id": "rdfs:label"
                        },
                        "owl:cardinality": 1,
                        "knora-api:isInherited": true
                    }
                ],
                "@type": "owl:Class",
                "@id": "second-onto:ResourceWithPropFromFirstOnto"
            }
        ],
        "knora-api:attachedToProject": {
            "@id": "http://rdfh.ch/projects/FxKUFS6bQFKgDv2v9-S9tw"
        },
        "@type": "owl:Ontology",
        "@id": "http://0.0.0.0:3333/ontology/4125/second-onto/v2",
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "e2e-testonto": "http://0.0.0.0:3333/ontology/4125/e2e-testonto/v2#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "second-onto": "http://0.0.0.0:3333/ontology/4125/second-onto/v2#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
    }
}



"""
