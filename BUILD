load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

load("@knora_py_deps//:requirements.bzl", "requirement")

py_test(
    name = "test_create_ontology",
    srcs = ["test/test_create_ontology.py"],
    deps = ["//knora_py/knora/knora"],
)

py_test(
    name = "test_create_resource",
    srcs = ["test/test_create_resource.py"],
    deps = [
        "//knora/knora",
        requirement("pprint"),
    ],
)

py_test(
    name = "test_knora",
    srcs = ["test/test_knora.py"],
    deps = ["//knora:knora"],
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
        "//knora_py/knora/knora",
    ],
)

py_binary(
    name = "run_tests",
    main = "test/run.py",
    srcs = ["test/run.py"],
    deps = ["test_lib"],
)
