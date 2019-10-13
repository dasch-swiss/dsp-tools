# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

# make the dependencies from requirements.txt available
load("@my_deps//:requirements.bzl", "requirement")

py_test(
    name = "test_create_ontology",
    srcs = ["test_create_ontology.py"],
    deps = ["//knora:knora"],
    data = ["test-onto.json"],
)

py_test(
    name = "test_create_resource",
    srcs = ["test_create_resource.py"],
    deps = [
        "//knora:knora",
        requirement("pprint"),
    ],
    data = [
        "test-onto.json",
        "test.tif"
    ],
)

py_test(
    name = "test_knora",
    srcs = ["test_knora.py"],
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
    srcs = glob(["*.py"]),
    deps = [
        "//knora:knora",
    ],
)

py_binary(
    name = "run_tests",
    main = "test/run.py",
    srcs = ["test/run.py"],
    deps = ["test_lib"],
)
