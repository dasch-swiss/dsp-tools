# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "Connection",
    visibility = ["//visibility:public"],
    srcs = ["Connection.py"],
    deps = [
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = ["."],
)

py_library(
    name = "Group",
    visibility = ["//visibility:public"],
    srcs = ["Group.py"],
    deps = [
        ":Helpers",
        ":Connection",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = ["."],
)

py_library(
    name = "Helpers",
    visibility = ["//visibility:public"],
    srcs = ["Helpers.py"],
    deps = [
        requirement("pprint"),
    ],
    imports = ["."],
)

py_library(
    name = "ListNode",
    visibility = ["//visibility:public"],
    srcs = ["ListNode.py"],
    deps = [
        ":Connection",
        ":Helpers",
        ":Project",
        requirement("pprint"),
    ],
    imports = ["."],
)

py_library(
    name = "Project",
    visibility = ["//visibility:public"],
    srcs = ["Project.py"],
    deps = [
        ":Helpers",
        ":Connection",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = ["."],
)

py_library(
    name = "User",
    visibility = ["//visibility:public"],
    srcs = ["User.py"],
    deps = [
        ":Connection",
        ":Helpers",
        ":Group",
        ":Project",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = ["."],
)
