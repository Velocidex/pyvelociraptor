#!/usr/bin/env python

"""PyVelociraptor are the python bindings for talking with Velociraptor."""

__author__ = "Velocidex <support@velocidex.com>"

import io
from distutils.core import setup

setup(
    name="pyvelociraptor",
    version="0.1.2",
    packages=['pyvelociraptor'],
    description="PyVelociraptor is the python binding for the Velociraptor API",
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
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "pyyaml",
    ],
    entry_points="""

    [console_scripts]
    pyvelociraptor = pyvelociraptor.client_example:main
    pyvelociraptor_push_event = pyvelociraptor.push_event:main
    """,
)
