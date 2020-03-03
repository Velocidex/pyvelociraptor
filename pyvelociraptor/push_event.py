#!/usr/bin/python

"""Example Velociraptor api client.

This example demonstrates how to connect to the Velociraptor server
and write an event to a single Artifact queue.
"""
import argparse
import collections
import json
import grpc
import yaml

from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc

def run(config, queue, event, columns):
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
        request = api_pb2.VQLResponse(
            Response=event,
            Columns=columns,
            Query=api_pb2.VQLRequest(Name=queue))

        err = stub.WriteEvent(request)
        print(err)

def main():
    parser = argparse.ArgumentParser(
        description="Sample Velociraptor query client.",
        epilog='Example: pyvelociraptor_push_event api_client.yaml Windows.Event.Monitor'
        "'{\"Time\": ....}'")

    parser.add_argument('config', type=str,
                        help='Path to the api_client config. You can generate such '
                        'a file with "velociraptor config api_client"')
    parser.add_argument('queue', type=str, help='The artifact name this event will go to.')
    parser.add_argument('event', type=str, help='A JSON formatted event to send')
    args = parser.parse_args()

    # Parse the event to determine the columns
    event_data = json.loads(args.event, object_pairs_hook=collections.OrderedDict)
    event = args.event

    # Let the user just supply one event if they want
    if not isinstance(event_data, list):
        event_data = [event_data,]
        event = json.dumps(event_data)

    columns = event_data[0].keys()

    config = yaml.safe_load(open(args.config).read())
    run(config, args.queue, event, columns)

if __name__ == '__main__':
    main()
