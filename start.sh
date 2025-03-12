proto_dir=protos
py_out=.
pyi_out=.
grpc_out=.
proto_files=$proto_dir/**.proto


python -m grpc_tools.protoc -I$proto_dir --python_out=$py_out --pyi_out=$pyi_out --grpc_python_out=$grpc_out $proto_files
