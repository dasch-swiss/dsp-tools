workspace(name = "knora_py")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

# register our custom toolchains for the different platforms
register_toolchains("//requirements:homebrew_toolchain", "//requirements:travis_toolchain")

# using custom repo with a (quick and dirty) fix because of https://github.com/bazelbuild/rules_python/issues/220
git_repository(
    name = "rules_python",
    remote = "https://github.com/subotic/rules_python.git",
    commit = "d34f2a6957b64d0af1fbc33100ca85ff496bac22",
    shallow_since = "1572180622 +0100"
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

load("@rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()

# allows to use requirements.txt for loading the dependencies
load("@rules_python//python:pip.bzl", "pip_import")

# This rule translates the specified requirements.txt into
# @knora_py_deps//:requirements.bzl, which itself exposes a pip_install method.
pip_import(
   name = "knora_py_deps",
   requirements = "//requirements:requirements.txt",
)

# Load the pip_install symbol for knora_py_deps, and create the dependencies'
# repositories.
load("@knora_py_deps//:requirements.bzl", "pip_install")
pip_install()
