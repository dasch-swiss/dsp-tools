workspace(name = "knora_py")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# register our custom toolchains for the different platforms
#register_toolchains("//:homebrew_toolchain", "//:travis_toolchain")

# use rules_python version 0.1.0
http_archive(
    name = "rules_python",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.1.0/rules_python-0.1.0.tar.gz",
    sha256 = "b6d46438523a3ec0f3cead544190ee13223a52f6a6765a29eae7b7cc24cc83a0",
)

# allows to use requirements.txt for loading the dependencies
load("@rules_python//python:pip.bzl", "pip_install")

# Create a central repo that knows about the dependencies needed for
# requirements.txt.
pip_install(
   name = "knora_py_deps",
   requirements = "//:requirements.txt",
   python_interpreter = "python3",
)
