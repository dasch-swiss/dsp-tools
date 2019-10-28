import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='knora',
    version='1.2.1a1',
    description='A Python library and tools for the Knora-API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/dasch-swiss/knora-py',
    author='Lukas Rosenthaler',
    author_email='lukas.rosenthaler@unibas.ch',
    license='GPLv3',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'rdflib',
        'lxml',
        'validators',
        'requests',
        'jsonschema',
        'click',
        'rfc3987',
        'pprint',
    ],
    entry_points={
          'console_scripts': [
              'knora-create-ontology=knora.create_ontology:main',
              'knora-xml-import=knora.xml2knora:main',
              'knora-reset-triplestore=knora.reset_triplestore:main',
              'knoractl=knoractl:main',
          ],
    },
    include_package_data=True,
    zip_safe=False,
)
