# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

py_library(
    name = "onto_commons",
    visibility = ["//visibility:public"],
    srcs = ["onto_commons.py"],
    deps = [
        "//knora/dsplib/models:helpers",
        "//knora/dsplib/models:listnode",
        "//knora/dsplib/models:project",
    ],
    imports = [".."],
)

py_library(
    name = "onto_create_lists",
    visibility = ["//visibility:public"],
    srcs = ["onto_create_lists.py"],
    deps = [
        "//knora/dsplib/models:helpers",
        "//knora/dsplib/models:connection",
        "//knora/dsplib/models:listnode",
        "//knora/dsplib/models:project",
        ":onto_commons",
        requirement("jsonschema"),
    ],
    imports = [".", ".."],
)

py_library(
    name = "onto_validate",
    visibility = ["//visibility:public"],
    srcs = ["onto_validate.py"],
    deps = [
        ":onto_commons",
    ],
    imports = [".", ".."],
)


py_library(
    name = "onto_create_ontology",
    visibility = ["//visibility:public"],
    srcs = ["onto_create_ontology.py"],
    deps = [
        "//knora/dsplib/models:helpers",
        "//knora/dsplib/models:langstring",
        "//knora/dsplib/models:group",
        "//knora/dsplib/models:user",
        "//knora/dsplib/models:ontology",
        "//knora/dsplib/models:propertyclass",
        "//knora/dsplib/models:resourceclass",
        "//knora/dsplib/models:connection",
        "//knora/dsplib/models:listnode",
        "//knora/dsplib/models:project",
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
        "//knora/dsplib/models:connection",
        "//knora/dsplib/models:project",
        "//knora/dsplib/models:listnode",
        "//knora/dsplib/models:ontology",
        requirement("jsonschema"),
    ],
    imports = [".", ".."],
)

py_library(
    name = "xml_upload",
    visibility = ["//visibility:public"],
    srcs = ["xml_upload.py"],
    deps = [
        "//knora/dsplib/models:connection",
        "//knora/dsplib/models:group",
        "//knora/dsplib/models:project",
        "//knora/dsplib/models:resource",
        "//knora/dsplib/models:value",
        "//knora/dsplib/models:permission",
        "//knora/dsplib/models:sipi",
        "//knora/dsplib/models:listnode",
        "//knora/dsplib/models:ontology",
        requirement("jsonschema"),
    ],
    imports = [".", ".."],
)

