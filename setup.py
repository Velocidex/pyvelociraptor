#!/usr/bin/env python

"""PyVelociraptor are the python bindings for talking with Velociraptor."""

__author__ = "Velocidex <support@velocidex.com>"

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvelociraptor",
    version="0.1.9",
    author="The Velociraptor Team",
    author_email="support@velocidex.com",
    description="PyVelociraptor is the python binding for the Velociraptor API",
    long_description=long_description,
    long_description_content_type="text/markdown",

    license="GPL",
    url="https://github.com/Velocidex/pyvelociraptor",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "pyyaml",
        "cryptography",
    ],
    entry_points="""

    [console_scripts]
    pyvelociraptor = pyvelociraptor.client_example:main
    pyvelociraptor_push_event = pyvelociraptor.push_event:main
    """,
    packages=setuptools.find_packages(),
)
