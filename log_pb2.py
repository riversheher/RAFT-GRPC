# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: log.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'log.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tlog.proto\x12\x03log\"F\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\r\n\x05index\x18\x02 \x01(\x05\x12\x0f\n\x07\x63ommand\x18\x03 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\t\"\x1a\n\x0bLogResponse\x12\x0b\n\x03\x61\x63k\x18\x01 \x01(\x05\"+\n\x0cIndexRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\r\n\x05index\x18\x02 \x01(\x05\",\n\rIndexResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\r\n\x05index\x18\x02 \x01(\x05\x32m\n\x06Logger\x12+\n\x08WriteLog\x12\r.log.LogEntry\x1a\x10.log.LogResponse\x12\x36\n\rRetrieveIndex\x12\x11.log.IndexRequest\x1a\x12.log.IndexResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'log_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_LOGENTRY']._serialized_start=18
  _globals['_LOGENTRY']._serialized_end=88
  _globals['_LOGRESPONSE']._serialized_start=90
  _globals['_LOGRESPONSE']._serialized_end=116
  _globals['_INDEXREQUEST']._serialized_start=118
  _globals['_INDEXREQUEST']._serialized_end=161
  _globals['_INDEXRESPONSE']._serialized_start=163
  _globals['_INDEXRESPONSE']._serialized_end=207
  _globals['_LOGGER']._serialized_start=209
  _globals['_LOGGER']._serialized_end=318
# @@protoc_insertion_point(module_scope)
