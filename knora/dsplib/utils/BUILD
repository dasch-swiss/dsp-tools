# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "onto_commons",
    visibility = ["//visibility:public"],
    srcs = ["onto_commons.py"],
    deps = [
        ":helpers",
        ":listnode",
        ":project",
    ],
    imports = [".."],
)

py_library(
    name = "onto_create_lists",
    visibility = ["//visibility:public"],
    srcs = ["onto_create_lists.py"],
    deps = [
        ":helpers",
        ":connection"
        ":listnode",
        ":project",
        ":onto_commons",
        requirement("jsonschema"),
    ],
    imports = [".", ".."],
)

py_library(
    name = "onto_create_ontology",
    visibility = ["//visibility:public"],
    srcs = ["onto_create_ontology.py"],
    deps = [
        ":helpers",
        ":langstring",
        ":group",
        ":user",
        ":ontology",
        ":propertyclass",
        ":resourceclass"
        ":connection"
        ":listnode",
        ":project",
        ":onto_commons",
        requirement("jsonschema"),
    ],
    imports = [".", ".."],
)

py_library(
    name = "onto_get",
    visibility = ["//visibility:public"],
    srcs = ["onto_get.py"],
    deps = [
        ":connection",
        ":project",
        ":listnode",
        ":ontology"
    ],
    imports = [".", ".."],
)

py_library(
    name = "onto_get",
    visibility = ["//visibility:public"],
    srcs = ["onto_get.py"],
    deps = [
        requirement("jsonschema"),
    ],
    imports = ["."],
)

