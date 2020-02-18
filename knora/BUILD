# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

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
    imports = ["."],
)

py_binary(
    name = "create_ontology",
    visibility = ["//visibility:public"],
    srcs = ["create_ontology.py"],
    deps = [
        ":knora",
        requirement("jsonschema"),
        requirement("pprint"),
    ],
    data = [
        "knora-schema.json",
        "knora-schema-lists.json",
    ],
    python_version = "PY3",
)

py_binary(
    name = "xml2knora",
    visibility = ["//visibility:public"],
    srcs = ["xml2knora.py"],
    deps = [
        ":knora",
        requirement("lxml"),
        requirement("rdflib"),
        requirement("pprint"),
    ],
    data = [
        "knora-data-schema.xsd"
    ],
    python_version = "PY3",
)

py_binary(
    name = "reset_triplestore",
    visibility = ["//visibility:public"],
    srcs = ["reset_triplestore.py"],
    deps = [":knora"],
    python_version = "PY3",
)

py_binary(
    name = "knoraConsole",
    visibility = ["//visibility:public"],
    srcs = ["knoraConsole.py"],
    deps = [":knora"],
    python_version = "PY3",
)

py_binary(
    name = "knoractl",
    visibility = ["//visibility:public"],
    srcs = ["knoractl.py"],
    deps = [":knora"],
    python_version = "PY3",
)
