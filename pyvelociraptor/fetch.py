#!/usr/bin/python

"""Example Velociraptor api client.

This example demonstrates how to connect to the Velociraptor server
and fetch a file from the filestore.

"""
import argparse
import json
import grpc
import time
import yaml
import sys

import pyvelociraptor
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc


def run(config, vfs_path):
    # Fill in the SSL params from the api_client config file. You can get such a file:
    # velociraptor --config server.config.yaml config api_client > api_client.conf.yaml
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8"))

    # This option is required to connect to the grpc server by IP - we
    # use self signed certs.
    options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

    # The first step is to open a gRPC channel to the server..
    with grpc.secure_channel(config["api_connection_string"],
                             creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)

        # The request consists of one or more VQL queries. Note that
        # you can collect artifacts by simply naming them using the
        # "Artifact" plugin.
        offset = 0
        while 1:
            request = api_pb2.VFSFileBuffer(
                vfs_path=vfs_path,

                # For demonstration we set a small buffer but you
                # should use a larger one in practice.
                length=1024,
                offset=offset,
            )

            res = stub.VFSGetBuffer(request)
            if len(res.data) == 0:
                break

            sys.stdout.buffer.write(res.data)
            offset+=len(res.data)

def main():
    parser = argparse.ArgumentParser(
        description="Sample Velociraptor fetch client.",
        epilog='Example: fetch.py api_client.yaml /downloads/C.b9bdf1fba596d686/F.BQK1O12VLHH04/F.BQK1O12VLHH04.zip')

    parser.add_argument('--config', type=str,
                        help='Path to the api_client config. You can generate such '
                        'a file with "velociraptor config api_client"')
    parser.add_argument('vfs_path', type=str, help='The path to get.')

    args = parser.parse_args()

    config = pyvelociraptor.LoadConfigFile(args.config)
    run(config, args.vfs_path)

if __name__ == '__main__':
    main()
