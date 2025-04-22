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

# Licensing

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
https://docs.velociraptor.app/docs/server_automation/server_api/#using-the-shell-for-automation
