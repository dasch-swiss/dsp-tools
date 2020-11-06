import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='knora',
    version='1.3.2',
    description='A Python library and tools for the Knora-API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/dasch-swiss/knora-py',
    author='Lukas Rosenthaler',
    author_email='lukas.rosenthaler@dasch.swiss',
    license='GPLv3',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
    install_requires=[
        'rdflib',
        'lxml',
        'validators',
        'requests',
        'jsonschema',
        'click',
        'rfc3987',
        'pystrict',
        'wxpython'
    ],
    entry_points={
          'console_scripts': [
              'dsp-tools=knora.dsp_tools:main',
              'knora-console=knora.knoraConsole:main'
              'knora-reset-triplestore=knora.reset_triplestore:main',
          ],
    },
    include_package_data=True,
    zip_safe=False,
)
