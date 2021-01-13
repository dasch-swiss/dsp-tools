import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dsp-tools',
    version='0.9.12',
    description='A Python library and tools for the DaSCH Service Platform',
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
    python_requires='>=3.9.0',
    install_requires=[
        'argparse',
        'rdflib',
        'lxml',
        'validators',
        'requests',
        'jsonschema',
        'click',
        'rfc3987',
        'pystrict'
    ],
    entry_points={
          'console_scripts': [
              'dsp-tools=knora.dsp_tools:main'
          ],
    },
    include_package_data=True,
    zip_safe=False,
)
