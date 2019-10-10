py_library(
    name = "knora",
    srcs = glob(["knora/knora.py"]),
)

py_binary(
    name = "knora_create_ontology",
    srcs = ["knora/create_ontology.py"],
    deps = ["knora"]
)

py_binary(
    name = "knora-xml-import",
    srcs = ["knora/xml2knora.py"],
    deps = ["knora"]
)

py_binary(
    name = "knora-reset-triplestore",
    srcs = ["knora/reset_triplestore.py"],
    deps = ["knora"]
)

py_binary(
    name = "knoractl",
    srcs = ["knora/knoractl.py"],
    deps = ["knora"]
)

py_test(
    name = "test_knora",
    srcs = ["tests/test_knora.py"],
    deps = ["knora"],
)

test_suite(
    name = "all_tests",
    tests = [
        "test_knora",
    ],
)
