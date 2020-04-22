# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "connection",
    visibility = ["//visibility:public"],
    srcs = ["connection.py"],
    deps = [
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "group",
    visibility = ["//visibility:public"],
    srcs = ["group.py"],
    deps = [
        ":helpers",
        ":connection",
        ":langstring",
        ":project",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "helpers",
    visibility = ["//visibility:public"],
    srcs = ["helpers.py"],
    deps = [
        requirement("pprint"),
    ],
    imports = [".", ".."],
)

py_library(
    name = "langstring",
    visibility = ["//visibility:public"],
    srcs = ["langstring.py"],
    deps = [
        ":helpers",
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "listnode",
    visibility = ["//visibility:public"],
    srcs = ["listnode.py"],
    deps = [
        ":connection",
        ":helpers",
        ":langstring",
        ":project",
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "project",
    visibility = ["//visibility:public"],
    srcs = ["project.py"],
    deps = [
        ":helpers",
        ":langstring",
        ":connection",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "user",
    visibility = ["//visibility:public"],
    srcs = ["user.py"],
    deps = [
        ":connection",
        ":helpers",
        ":group",
        ":project",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "ontology",
    visibility = ["//visibility:public"],
    srcs = ["ontology.py"],
    deps = [
        ":connection",
        ":helpers",
        ":project",
        ":resourceclass",
        ":propertyclass",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "resourceclass",
    visibility = ["//visibility:public"],
    srcs = ["resourceclass.py"],
    deps = [
        ":connection",
        ":helpers",
        ":langstring",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)

py_library(
    name = "propertyclass",
    visibility = ["//visibility:public"],
    srcs = ["propertyclass.py"],
    deps = [
        ":connection",
        ":helpers",
        ":langstring",
        requirement("requests"),
        requirement("pprint"),
    ],
    imports = [".."],
)
