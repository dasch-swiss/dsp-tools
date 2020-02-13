# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "KnoraConnection",
    visibility = ["//visibility:public"],
    srcs = ["KnoraConnection.py"],
    deps = [
        requirement("requests"),
        requirement("pprint"),
    ],
    data = ["__init__.py"],
)

py_library(
    name = "KnoraGroup",
    visibility = ["//visibility:public"],
    srcs = ["KnoraGroup.py"],
    deps = [
        requirement("requests"),
        requirement("pprint"),
        ":KnoraHelpers",
        ":KnoraConnection",
    ],
    data = ["__init__.py"],
)

py_library(
    name = "KnoraHelpers",
    visibility = ["//visibility:public"],
    srcs = ["KnoraHelpers.py"],
    deps = [
        requirement("pprint"),
    ],
    data = ["__init__.py"],
)

py_library(
    name = "KnoraProject",
    visibility = ["//visibility:public"],
    srcs = ["KnoraProject.py"],
    deps = [
        requirement("requests"),
        requirement("pprint"),
        ":KnoraHelpers",
        ":KnoraConnection"
    ],
    data = ["__init__.py"],
)

py_library(
    name = "KnoraUser",
    visibility = ["//visibility:public"],
    srcs = ["KnoraUser.py"],
    deps = [
        requirement("requests"),
        requirement("pprint"),
        ":KnoraConnection",
        ":KnoraHelpers",
        ":KnoraGroup",
        ":KnoraProject"
    ],
    data = ["__init__.py"],
)
