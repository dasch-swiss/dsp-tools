# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "KnDialogControl",
    visibility = ["//visibility:public"],
    srcs = ["KnDialogControl.py"],
    deps = [
        requirement("pprint"),
        "//knora:knora",
    ],
    data = ["__init__.py"],
)

py_library(
    name = "ProjectPanel",
    visibility = ["//visibility:public"],
    srcs = ["ProjectPanel.py"],
    deps = [
        requirement("pprint"),
        "//knora/models:Connection",
        "//knora/models:Group",
        "//knora/models:Helpers",
        "//knora/models:Project",
        "//knora/models:User",
        ":KnDialogControl"
    ],
    data = ["__init__.py"],
)

py_library(
    name = "UserPanel",
    visibility = ["//visibility:public"],
    srcs = ["UserPanel.py"],
    deps = [
        requirement("pprint"),
        "//knora:knora",
        "//knora/models:Connection",
        "//knora/models:Group",
        "//knora/models:Helpers",
        "//knora/models:Project",
        "//knora/models:User",
        ":KnDialogControl"
    ],
    data = ["__init__.py"],
)
