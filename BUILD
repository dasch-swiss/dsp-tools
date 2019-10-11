load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python:defs.bzl", "py_library")
load("@rules_python//python:defs.bzl", "py_test")

load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "knora",
    srcs = glob(["knora/knora.py"]),
    deps = [
        requirement("rdflib"),
        requirement("lxml"),
        requirement("validators"),
        requirement("requests"),
        requirement("jsonschema"),
        requirement("click"),
        requirement("rfc3987"),
        requirement("pprint"),
    ]
)

py_binary(
    name = "knora_create_ontology",
    srcs = ["knora/create_ontology.py"],
    deps = [
        "knora",
        requirement("jsonschema"),
        requirement("pprint"),
    ]
)

py_binary(
    name = "knora_xml_import",
    srcs = ["knora/xml2knora.py"],
    deps = [
        "knora",
        requirement("lxml"),
        requirement("pprint"),
    ],
)

py_binary(
    name = "knora_reset_triplestore",
    srcs = ["knora/reset_triplestore.py"],
    deps = [":knora"],
)

py_binary(
    name = "knoractl",
    srcs = ["knora/knoractl.py"],
    deps = [":knora"],
)

py_test(
    name = "test_create_ontology",
    srcs = ["test/test_create_ontology.py"],
    deps = [":knora"],
)

py_test(
    name = "test_create_resource",
    srcs = ["test/test_create_resource.py"],
    deps = [
        ":knora",
        requirement("pprint"),
    ],
)

py_test(
    name = "test_knora",
    srcs = ["test/test_knora.py"],
    deps = [":knora"],
)

test_suite(
    name = "all_tests",
    tests = [
        "test_create_ontology",
        "test_create_resource",
        "test_knora",
    ],
)

py_library(
    name = "test_lib",
    srcs = glob(["test/*.py"]),
    deps = [
        ":knora",
    ],
)

py_binary(
    name = "run_tests",
    main = "test/run.py",
    srcs = ["test/run.py"],
    deps = ["test_lib"],
)
