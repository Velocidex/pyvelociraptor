#!/usr/bin/python

"""Example Velociraptor api client.

This example demonstrates how to connect to the Velociraptor API
server and fetch all uploaded files from a single flow.

We first make a query to the server to find all the uploads in a flow,
then for each upload we fetch the data and store it in a directory.

"""
import argparse
import json
import grpc
import time
import yaml
import sys
import os.path

import pyvelociraptor
from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc


def fetch_file(stub, components, outfd, org_id):
    """ Use the stub to fetch data from the server.

    Write the data to the out fd.
    """
    offset = 0
    while 1:
        request = api_pb2.VFSFileBuffer(
            org_id=org_id,
            components=components,

            # This should be between 1 mb to 4mb for optimum
            # performance.
            length=1024 * 1024,
            offset=offset,
        )

        res = stub.VFSGetBuffer(request)
        if len(res.data) == 0:
            break

        outfd.write(res.data)
        offset+=len(res.data)


def run(config, client_id, flow_id, output_path, export_zip, org_id):
    # Fill in the SSL params from the api_client config file. You can
    # get such a file:
    # velociraptor --config server.config.yaml config api_client > api_client.conf.yaml
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8"))

    # This option is required to connect to the grpc server by IP - we
    # use self signed certs.
    options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

    query = '''
    SELECT Upload.Components AS Components
    FROM uploads(flow_id=FlowId, client_id=ClientId)
    '''

    if export_zip:
        query = '''
        SELECT create_flow_download(
            client_id=ClientId, flow_id=FlowId).Components AS Components
        FROM scope()
        '''

    # The first step is to open a gRPC channel to the server..
    with grpc.secure_channel(config["api_connection_string"],
                             creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)

        # The request consists of one or more VQL queries. Note that
        # you can collect artifacts by simply naming them using the
        # "Artifact" plugin.
        request = api_pb2.VQLCollectorArgs(
            org_id=org_id,
            max_wait=1,
            max_row=100,
            Query=[api_pb2.VQLRequest(
                Name="Test",
                VQL=query,
            )],
            env=[api_pb2.VQLEnv(key="FlowId", value=flow_id),
                 api_pb2.VQLEnv(key="ClientId", value=client_id),
                 ],
        )

        # This will block as responses are streamed from the
        # server. If the query is an event query we will run this loop
        # forever.
        for response in stub.Query(request):
            if response.Response:
                package = json.loads(response.Response)

                for row in package:
                    components = row.get("Components", [])
                    output_file = os.path.join(output_path, components[-1])
                    print ("Fetching file %s to %s" % (components, output_file))

                    with open(output_file, "wb") as outfd:
                        fetch_file(stub, components, outfd, org_id)


def main():
    parser = argparse.ArgumentParser(
        description="Sample Velociraptor fetch client.",
        epilog='Example: fetch.py --config api_client.yaml /downloads/C.b9bdf1fba596d686/F.BQK1O12VLHH04/F.BQK1O12VLHH04.zip')

    parser.add_argument('--config', type=str,
                        help='Path to the api_client config. You can generate such '
                        'a file with "velociraptor config api_client"')

    parser.add_argument("--org", type=str, help="Org ID to use")
    parser.add_argument('client_id', type=str, help='The path to get.')
    parser.add_argument('flow_id', type=str, help='The path to get.')
    parser.add_argument('--zip', action=argparse.BooleanOptionalAction,
                        help='If set we upload a zip file.')
    parser.add_argument('--output', type=str, default="/tmp/", help='The output directory to write.')

    args = parser.parse_args()

    config = pyvelociraptor.LoadConfigFile(args.config)
    run(config, args.client_id, args.flow_id, args.output, args.zip, args.org)

if __name__ == '__main__':
    main()
