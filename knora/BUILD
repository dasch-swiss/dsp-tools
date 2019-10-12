load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "knora",
    srcs = ["knora.py"],
    deps = [
        requirement("rdflib"),
        requirement("lxml"),
        requirement("validators"),
        requirement("requests"),
        requirement("jsonschema"),
        requirement("click"),
        requirement("rfc3987"),
        requirement("pprint"),
    ],
    imports = ["."],
    visibility = ["//knora_py/knora:__pkg__"],
)

py_binary(
    name = "knora_create_ontology",
    srcs = ["create_ontology.py"],
    deps = [
        "knora",
        requirement("jsonschema"),
        requirement("pprint"),
    ],
    imports = ["."],
    visibility = ["//knora_py/knora:__pkg__"],
)

py_binary(
    name = "knora_xml_import",
    srcs = ["xml2knora.py"],
    deps = [
        "knora",
        requirement("lxml"),
        requirement("pprint"),
    ],
    imports = ["."],
    visibility = ["//knora_py/knora:__pkg__"],
)

py_binary(
    name = "knora_reset_triplestore",
    srcs = ["reset_triplestore.py"],
    deps = [":knora"],
    imports = ["."],
    visibility = ["//knora_py/knora:__pkg__"],
)

py_binary(
    name = "knoractl",
    srcs = ["knoractl.py"],
    deps = [":knora"],
    imports = ["."],
    visibility = ["//knora_py/knora:__pkg__"],
)
