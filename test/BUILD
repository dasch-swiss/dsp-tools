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
    name = "test_Connection",
    srcs = ["test_Connection.py"],
    deps = [
        "//knora/models:Connection",
        requirement("pprint"),
    ],
)

py_test(
    name = "test_Group",
    srcs = ["test_Group.py"],
    deps = [
        "//knora/models:Connection",
        "//knora/models:Group",
        "//knora/models:Helpers",
        requirement("pprint"),
        requirement("requests"),
        requirement("pystrict"),
    ],
    imports = ["."],
)

py_test(
    name = "test_Project",
    srcs = ["test_Project.py"],
    deps = [
        "//knora/models:Connection",
        "//knora/models:Helpers",
        "//knora/models:Project",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_User",
    srcs = ["test_User.py"],
    deps = [
        "//knora/models:Connection",
        "//knora/models:Helpers",
        "//knora/models:User",
        requirement("pystrict"),
    ],
)

py_test(
    name = "test_ListNode",
    srcs = ["test_ListNode.py"],
    deps = [
        "//knora/models:Connection",
        "//knora/models:Helpers",
        "//knora/models:ListNode",
        "//knora/models:Project",
        requirement("pystrict"),
    ],
)


