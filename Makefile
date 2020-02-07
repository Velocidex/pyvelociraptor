all:
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pyvelociraptor/api.proto

clean:
	rm -f pyvelociraptor/api_pb2_grpc.py pyvelociraptor/api_pb2.py
