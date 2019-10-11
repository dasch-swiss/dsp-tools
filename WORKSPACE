workspace(name = "knora_py")

# use bazel federation (set of rule versions known to work well together)
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name = "bazel_federation",
    url = "https://github.com/bazelbuild/bazel-federation/releases/download/0.0.1/bazel_federation-0.0.1.tar.gz",
    sha256 = "506dfbfd74ade486ac077113f48d16835fdf6e343e1d4741552b450cfc2efb53",
)

# load the initializer methods for all the rules we want to use in this workspace
load("@bazel_federation//:repositories.bzl",
     "rules_python",
)

# run any rule specific setups
rules_python()
load("@bazel_federation//setup:rules_python.bzl", "rules_python_setup")
rules_python_setup()

# load py_repositories from rules_python
load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

# load pip_repositories from rules_python
load("@rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

# allows to use requirements.txt for loading the dependencies
load("@rules_python//python:pip.bzl", "pip_import")

# This rule translates the specified requirements.txt into
# @knora_py_deps//:requirements.bzl, which itself exposes a pip_install method.
pip_import(
   name = "knora_py_deps",
   requirements = "//:requirements.txt",
)

# Load the pip_install symbol for knora_py_deps, and create the dependencies'
# repositories.
load("@knora_py_deps//:requirements.bzl", "pip_install")
pip_install()
