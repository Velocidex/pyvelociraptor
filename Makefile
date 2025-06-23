all:
	protoc -I/usr/local/include/ -I.g --python_out=.  pyvelociraptor/api.proto
	python3 -m grpc_tools.protoc -I. --grpc_python_out=. pyvelociraptor/api.proto

clean:
	rm -f pyvelociraptor/api_pb2_grpc.py pyvelociraptor/api_pb2.py
