# The Velociraptor Python bindings.

Velociraptor is an open source DFIR tool. Read more about it at
https://docs.velociraptor.app/

Velociraptor has an API which allows an external program to interface
with it. The API presents a simple GRPC connection with the following endpoints:


1. Query: Allows running arbitrary VQL queries - this can be used to
   automate Velociraptor's collection, analysis and receive JSON
   encoded results.

   Example script: client_example.py

2. VFSGetBuffer: This API allows to read arbitrary buffers from the
   Velociraptor file store. This allows a client program to fetch bulk
   collected data.

   Example script: fetch.py

You can use these API endpoint to:

* Control collection from Velociraptor: Start hunts, collections,
  trigger exports etc.. All with VQL queries over the Query() API
  endpoint.

* Perform administive tasks: Spawn new orgs, add users, adjust
  permissions, create periodic tasks etc.

* Read results from collected data using the VFSGetBuffer() endpoint.

and much more!

To read more about the Velociraptor API see
https://docs.velociraptor.app/docs/server_automation/server_api/

## Sample programs

You will find some sample programs in the pyvelociraptor directory:

* **client_example.py**: This is a simple client program that allows
  calling the server to run a query. It demonstrates how to prepare
  the request and collect the resulting JSON data for display
  including viewing the query logs.

* **fetch.py**: This program demonstrates how to fetch a file from the
  server's file store - the file is fetched in chunks using the
  `VFSGetBuffer` API.

* **fetch_flow_uploads.py**: This example demonstrates how to combine
  `Query` and `VFSGetBuffer` to both create a flow's export download
  then fetch it from the server. The flow download is a ZIP file
  containing all the flow data.

## Licensing

Note that Velociraptor itself is licensed under the AGPL, however use
of the API is permitted and does not fall under the `derived work`
definition. Therefore, using the `.proto` file in this repository
falls under the MIT license which covers this repository, including
sample programs in python.

Since GRPC protobuf is a portable API definition language you can use
the `.proto` file to generate interfaces in many other languages. We
use python here as an example to demonstrate the use of the API but
any language will work.

You can even use shell scripting as the Velociraptor binary itself can
use the API to call into the server. For details, see
https://docs.velociraptor.app/docs/server_automation/server_api/#using-the-built-in-api-client
