import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='knora',
    version='0.0.1',
    description='A Python library and tools for the Knora-API',
    url='https://github.com/dhlab-basel/knora-py',
    author='Lukas Rosenthaler',
    author_email='lukas.rosenthaler@unibas.ch',
    license='GPLv3',
    zip_safe=False,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
)
