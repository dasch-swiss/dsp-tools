# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "doublepassword",
    visibility = ["//visibility:public"],
    srcs = ["doublepassword.py"],
    deps = [
        requirement("wx"),
    ],
    imports = ["."],
)
