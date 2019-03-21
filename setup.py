import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='knora',
    version='0.0.3',
    description='A Python library and tools for the Knora-API',
    url='https://github.com/dhlab-basel/knora-py',
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
        'validators'
    ],
    entry_points={
          'console_scripts': ['knora-create-ontology=knora.create_ontology:main'],
    },
    include_package_data=True,
    zip_safe=False
)
