#!/usr/bin/env python

"""PyVelociraptor are the python bindings for talking with Velociraptor."""

__author__ = "Velocidex <support@velocidex.com>"

import io
from distutils.core import setup

setup(
    name="pyvelociraptor",
    version="0.1",
    packages=['pyvelociraptor'],
    description="PyVelociraptor is the python binding for the Velociraptor API",
    long_description=io.open("README.md", "rt", encoding='utf8').read(),
    license="GPL",
    url="https://github.com/Velocidex/pyvelociraptor",
    author="The Velociraptor Team",
    author_email="support@velocidex.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
