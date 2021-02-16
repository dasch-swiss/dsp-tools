# make the python rules available
#load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
#load("@knora_py_deps//:requirements.bzl", "requirement")

filegroup(
    name = "testdata",
    visibility = ["//visibility:public"],
    srcs = [
        "anything.json",
        "list-as-excel.xlsx",
        "test-data.xml",
        "test-onto.json",
    ],
)

