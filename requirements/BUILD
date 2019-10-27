package(default_visibility = ["//visibility:public"])

load("@bazel_tools//tools/python:toolchain.bzl", "py_runtime_pair")

# local macos environment
py_runtime(
    name = "brew_fake_py2_runtime",
    interpreter_path = "/usr/local/bin/python3",
    python_version = "PY2",
)
py_runtime(
    name = "brew_py3_runtime",
    interpreter_path = "/usr/local/bin/python3",
    python_version = "PY3",
)
py_runtime_pair(
    name = "brew_py_runtime_pair",
    py2_runtime = ":brew_fake_py2_runtime",
    py3_runtime = ":brew_py3_runtime",
)
toolchain(
    name = "homebrew_toolchain",
    target_compatible_with = [
        "@platforms//os:osx",
    ],
    toolchain = ":brew_py_runtime_pair",
    toolchain_type = "@bazel_tools//tools/python:toolchain_type",
)

# travis environment
py_runtime(
    name = "ubuntu_fake_py2_runtime",
    interpreter_path = "/opt/pyenv/shims/python3",
    python_version = "PY2",
)
py_runtime(
    name = "ubuntu_py3_runtime",
    interpreter_path = "/opt/pyenv/shims/python3",
    python_version = "PY3",
)
py_runtime_pair(
    name = "ubuntu_py_runtime_pair",
    py2_runtime = ":ubuntu_fake_py2_runtime",
    py3_runtime = ":ubuntu_py3_runtime",
)
toolchain(
    name = "travis_toolchain",
    target_compatible_with = [
        "@platforms//os:linux",
    ],
    toolchain = ":ubuntu_py_runtime_pair",
    toolchain_type = "@bazel_tools//tools/python:toolchain_type",
)
