# make the python rules available
load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

# make the dependencies from requirements.txt available
load("@knora_py_deps//:requirements.bzl", "requirement")

#py_test(
#    name = "test_create_ontology",
#    srcs = ["test_create_ontology.py"],
#    deps = [
#        "//knora:knora"
#    ],
#    data = [
#        "test-onto.json"
#    ],
#)

#py_test(
#    name = "test_create_resource",
#    srcs = ["test_create_resource.py"],
#    deps = [
#        "//knora:knora",
#    ],
#    data = [
#        "test-onto.json",
#        "test.tif"
#    ],
#)

py_test(
    name = "test_connection",
    srcs = ["test_connection.py"],
    deps = [
        "//knora/knora/models:connection",
#        requirement("pprint"),
    ],
)

py_test(
    name = "test_langstring",
    srcs = ["test_langstring.py"],
    deps = [
        "//knora/knora/models:helpers",
        "//knora/knora/models:langstring",
#        requirement("pprint"),
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_group",
    srcs = ["test_group.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:group",
        "//knora/knora/models:langstring",
#        requirement("pprint"),
        requirement("requests"),
        requirement("pystrict"),
    ],
    imports = ["."],
)

py_test(
    name = "test_project",
    srcs = ["test_project.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:langstring",
        "//knora/knora/models:project",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_user",
    srcs = ["test_user.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:user",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_listnode",
    srcs = ["test_listnode.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:langstring",
        "//knora/knora/models:listnode",
        "//knora/knora/models:project",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_ontology",
    srcs = ["test_ontology.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:ontology",
        "//knora/knora/models:listnode",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_resourceclass",
    srcs = ["test_resourceclass.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:ontology",
        "//knora/knora/models:resourceclass",
        "//knora/knora/models:listnode",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_propertyclass",
    srcs = ["test_propertyclass.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:ontology",
        "//knora/knora/models:propertyclass",
        "//knora/knora/models:listnode",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_all",
    srcs = ["test_all.py"],
    deps = [
        "//knora/knora/models:connection",
        "//knora/knora/models:helpers",
        "//knora/knora/models:ontology",
        "//knora/knora/models:resourceclass",
        "//knora/knora/models:propertyclass",
        "//knora/knora/models:listnode",
        requirement("pystrict"),
    ],
)

