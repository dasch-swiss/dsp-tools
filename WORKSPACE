workspace(name = "knora_py")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

# register our custom toolchains for the different platforms
#register_toolchains("//:homebrew_toolchain", "//:travis_toolchain")

# using certain commit that includes fix: https://github.com/bazelbuild/rules_python/issues/220
git_repository(
    name = "rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "94677401bc56ed5d756f50b441a6a5c7f735a6d4",
    shallow_since = "1573842889 -0500"
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

load("@rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

# allows to use requirements.txt for loading the dependencies
load("@rules_python//python:pip.bzl", "pip3_import")

# This rule translates the specified requirements.txt into
# @knora_py_deps//:requirements.bzl, which itself exposes a pip_install method.
pip3_import(
   name = "knora_py_deps",
   requirements = "//:requirements.txt",
)

# Load the pip_install symbol for knora_py_deps, and create the dependencies'
# repositories.
load("@knora_py_deps//:requirements.bzl", "pip_install")
pip_install()
