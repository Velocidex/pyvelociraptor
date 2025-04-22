#!/usr/bin/python

"""Example Velociraptor api client.

This example demonstrates how to connect to the Velociraptor server
and write an event to a single Artifact queue.

NOTE: This API will be available in the next release. It is presented
here for testing until then (will work with any Velociraptor server
built after 0.74.2)

NOTE: The API user **must** have permissions to send to the specific
queue. You must grant the user this permission. Currently this is not
possibly to do via the GUI so you will have to use the following VQL
in a notebook.

For example the following will grant the user 'mic' the permission to
send to the `Server.Audit.Logs` queue. Note that no other permission
is needed other than `publish_queues`.

```
LET _GetPolicy(User) = SELECT _policy
  FROM gui_users()
  WHERE name = User

LET GetPolicy(User) = _GetPolicy(User=User)[0]._policy

// Preserve the existing policy and just replace the publish_queues
// field.
LET _ <= user_grant(user="mic",
                    policy=GetPolicy(User="mic") +
                      dict(publish_queues=["Server.Audit.Logs", ]))

SELECT GetPolicy(User="mic") AS Policy
FROM scope()
```

The result will be something like
```
  {
    "Policy": {
      "publish_queues": [
        "Server.Audit.Logs"
      ],
      "roles": [
        "reader"
      ]
    }
  }
```

"""
import argparse
import collections
import json
import grpc
import yaml

from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc

def run(config, queue, org_id, client_id, event):
    serialized = ""
    count = 0
    for line in event:
        serialized += json.dumps(line) + "\n"
        count += 1

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

        request = api_pb2.PushEventRequest(
            artifact=queue,
            client_id=client_id,
            jsonl=serialized.encode("utf8"),
            rows=count,
            org_id=org_id,
        )

        err = stub.PushEvents(request)
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

    parser.add_argument('--client_id', type=str, default="server",
                        help='The Client Id of the queue.')

    parser.add_argument('event', type=str, help='A JSON formatted event to send')

    parser.add_argument("--org", type=str,
                        help="Org ID to use")

    args = parser.parse_args()

    # Parse the event to determine the columns
    event_data = json.loads(args.event, object_pairs_hook=collections.OrderedDict)
    event = args.event

    # Let the user just supply one event if they want
    if not isinstance(event_data, list):
        event_data = [event_data,]

    config = yaml.safe_load(open(args.config).read())
    run(config, args.queue, args.org, args.client_id, event_data)

if __name__ == '__main__':
    main()
