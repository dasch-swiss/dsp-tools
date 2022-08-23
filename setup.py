from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dsp-tools',
    version='1.17.1',
    description='A Python library and tools for the DaSCH Service Platform',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/dasch-swiss/dsp-tools',
    author='DaSCH - Swiss National Data and Service Center for the Humanities',
    author_email='support@dasch.swiss',
    license='GPLv3',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9.0',
    install_requires=['argparse~=1.4.0', "attrs~=22.1.0; python_version >= '3.5'", "certifi~=2022.6.15; python_full_version >= '3.6.0'", "charset-normalizer~=2.1.1; python_full_version >= '3.6.0'", 'click~=8.1.3', "decorator~=5.1.1; python_version >= '3.5'", "et-xmlfile~=1.1.0; python_full_version >= '3.6.0'", "idna~=3.3; python_version >= '3.5'", 'isodate~=0.6.1', 'jsonpath-ng~=1.5.3', 'jsonschema~=4.14.0', 'lxml~=4.9.1', 'networkx~=2.8.5', "numpy~=1.23.2; python_version < '3.10' and platform_machine != 'aarch64' and platform_machine != 'arm64'", 'openpyxl~=3.0.10', 'pandas~=1.4.3', 'ply~=3.11', 'pyparsing~=2.4.7', "pyrsistent~=0.18.1; python_version >= '3.7'", 'pystrict~=1.3', "python-dateutil~=2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", 'pytz~=2022.2.1', 'rdflib~=6.2.0', 'requests~=2.28.1', 'rfc3987~=1.3.8', "setuptools~=65.2.0; python_version >= '3.7'", "six~=1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'", "urllib3~=1.26.11; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5' and python_version < '4'", 'validators~=0.20.0'
                      ],
    entry_points={
        'console_scripts': [
            'dsp-tools=knora.dsp_tools:main'
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
