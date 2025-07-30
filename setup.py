#!/usr/bin/env python

"""PyVelociraptor are the python bindings for talking with Velociraptor."""

__author__ = "Velocidex <support@velocidex.com>"

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvelociraptor",
    version="0.1.11",
    author="The Velociraptor Team",
    author_email="support@velocidex.com",
    description="PyVelociraptor is the python binding for the Velociraptor API",
    long_description=long_description,
    long_description_content_type="text/markdown",

    license="MIT",
    url="https://github.com/Velocidex/pyvelociraptor",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        "grpcio==1.73.0",
        "grpcio-tools==1.73.0",
        "pyyaml==6.0.2",
        "cryptography==45.0.4",
    ],
    entry_points="""

    [console_scripts]
    pyvelociraptor = pyvelociraptor.client_example:main
    pyvelociraptor_push_event = pyvelociraptor.push_event:main
    """,
    packages=setuptools.find_packages(),
)
