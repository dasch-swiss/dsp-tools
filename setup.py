from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dsp-tools',
    version='1.14.0',
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
    install_requires=['argparse==1.4.0', "attrs==21.4.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'", 'certifi==2021.10.8', "charset-normalizer==2.0.12; python_version >= '3'", 'click==8.1.2', "decorator==5.1.1; python_version >= '3.5'", "et-xmlfile==1.1.0; python_version >= '3.6'", "idna==3.3; python_version >= '3'", 'isodate==0.6.1', 'jsonpath-ng==1.5.3', 'jsonschema==4.4.0', 'lxml==4.8.0', 'openpyxl==3.0.9', 'ply==3.11', 'pyparsing==2.4.7', "pyrsistent==0.18.1; python_version >= '3.7'", 'pystrict==1.2', 'rdflib==6.1.1', 'requests==2.27.1', 'rfc3987==1.3.8', "setuptools==62.1.0; python_version >= '3.7'", "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2'", "urllib3==1.26.9; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'", 'validators==0.18.2'
                      ],
    entry_points={
        'console_scripts': [
            'dsp-tools=knora.dsp_tools:main'
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
