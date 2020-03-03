"""Helper functions to deal with pandas.

# How to use this code in a jupyter notebook

First initialize pandas options to prevent eliding output or rows.

1. Create an api config with the velociraptor server:

$ velociraptor --config server.config.yaml config api_config --name Mike

2. Grant the API user all query permissions

$ velociraptor --config server.config.yaml acl grant '{"all_query": true}'

3. Export the API service or port forward using SSH to the server

$ ssh -L 8001:127.0.0.1:8001 velociraptor.example.com

4. On your workstation copy the API config to ~/.pyvelociraptorrc or

$ export VELOCIRAPTOR_API_FILE=/path/to/api/file.yaml

5. Install Jupyter, Pandas and pyvelociraptor (preferably inside a virtualenv)

$ pip install jupyter pandas pyvelociraptor

6. Start jupyter

$ jupyter notebook


In the first cell initialize the pandas options

```
import pandas
from pyvelociraptor import velo_pandas

pandas.set_option('display.max_colwidth', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.max_rows', None)
```

Calling velo_pandas.DataFrameQuery(vql) will connect to the API server
specified in the api config file (either from ~/.pyvelociraptorrc or the
VELOCIRAPTOR_API_FILE environment ) and run the VQL query
specified. The result is a python dict structured in a way that can
initialize a pandas DataFrame directly. You can then use regular
pandas visualization or plotting functions to explore the data (see
any pandas tutorial or book).

Each cell in the notebook can create a new data frame and explore it.

```
df = pandas.DataFrame(velo_pandas.DataFrameQuery(```
  SELECT ConsumerDetails, FilterDetails, Fqdn FROM hunt_results(hunt_id='H.380432d0',
 artifact='Windows.Persistence.PermanentWMIEvents')
 WHERE NOT ConsumerDetails.Name =~ '(SCM Event Log Consumer|DellCommandPowerManager.*EventConsumer)'
 LIMIT 50 ```))
df.head(500)
```

You can also add query parameters as keyword args:

```
HuntId = 'H.380432d0'
df = pandas.DataFrame(velo_pandas.DataFrameQuery(```
  SELECT ConsumerDetails, FilterDetails, Fqdn FROM hunt_results(hunt_id=HuntId,
 artifact='Windows.Persistence.PermanentWMIEvents')
 WHERE NOT ConsumerDetails.Name =~ '(SCM Event Log Consumer|DellCommandPowerManager.*EventConsumer)'
 LIMIT 50 ```, HuntId=HuntId))
df.head(500)
```

"""
import json
import grpc
import os
import os.path

import pyvelociraptor

from pyvelociraptor import api_pb2
from pyvelociraptor import api_pb2_grpc


def DataFrameQuery(query, timeout=600, config=None, **kw):
    if config is None:
        config = pyvelociraptor.LoadConfigFile()

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
        # you can collect server artifacts by simply naming them using the
        # "Artifact" plugin (i.e. `SELECT * FROM Artifact.Server.Hunts.List()` )
        request = api_pb2.VQLCollectorArgs(
            max_wait=1,
            env=[api_pb2.VQLEnv(key=k, value=v) for k,v in kw.items()],
            Query=[api_pb2.VQLRequest(
                Name="Query",
                VQL=query,
            )])

        result = {}
        for response in stub.Query(request):
            for row in json.loads(response.Response):
                for c in response.Columns:
                    result.setdefault(c, []).append(row.get(c))

        return result
