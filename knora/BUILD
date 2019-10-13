# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@my_deps//:requirements.bzl", "requirement")

py_library(
    name = "knora",
    visibility = ["//visibility:public"],
    srcs = ["knora.py"],
    deps = [
        requirement("rdflib"),
        requirement("lxml"),
        requirement("validators"),
        requirement("requests"),
        requirement("jsonschema"),
        requirement("click"),
        requirement("rfc3987"),
        requirement("pprint"),
    ],
    data = ["__init__.py"],
)

py_binary(
    name = "knora_create_ontology",
    visibility = ["//visibility:public"],
    srcs = ["create_ontology.py"],
    deps = [
        "knora",
        requirement("jsonschema"),
        requirement("pprint"),
    ],
    data = [
        "knora-schema.json",
        "knora-schema-lists.json",
    ],
)

py_binary(
    name = "knora_xml_import",
    visibility = ["//visibility:public"],
    srcs = ["xml2knora.py"],
    deps = [
        "knora",
        requirement("lxml"),
        requirement("pprint"),
    ],
    data = [
        "knora-data-schema.xsd"
    ],
)

py_binary(
    name = "knora_reset_triplestore",
    visibility = ["//visibility:public"],
    srcs = ["reset_triplestore.py"],
    deps = [":knora"],
)

py_binary(
    name = "knoractl",
    visibility = ["//visibility:public"],
    srcs = ["knoractl.py"],
    deps = [":knora"],
)
