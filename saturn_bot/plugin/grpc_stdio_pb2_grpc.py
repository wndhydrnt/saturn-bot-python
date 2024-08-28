# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from saturn_bot.plugin import grpc_stdio_pb2 as saturn__bot_dot_plugin_dot_grpc__stdio__pb2


class GRPCStdioStub(object):
    """GRPCStdio is a service that is automatically run by the plugin process
    to stream any stdout/err data so that it can be mirrored on the plugin
    host side.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StreamStdio = channel.unary_stream(
                '/plugin.GRPCStdio/StreamStdio',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=saturn__bot_dot_plugin_dot_grpc__stdio__pb2.StdioData.FromString,
                )


class GRPCStdioServicer(object):
    """GRPCStdio is a service that is automatically run by the plugin process
    to stream any stdout/err data so that it can be mirrored on the plugin
    host side.
    """

    def StreamStdio(self, request, context):
        """StreamStdio returns a stream that contains all the stdout/stderr.
        This RPC endpoint must only be called ONCE. Once stdio data is consumed
        it is not sent again.

        Callers should connect early to prevent blocking on the plugin process.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GRPCStdioServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'StreamStdio': grpc.unary_stream_rpc_method_handler(
                    servicer.StreamStdio,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=saturn__bot_dot_plugin_dot_grpc__stdio__pb2.StdioData.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'plugin.GRPCStdio', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class GRPCStdio(object):
    """GRPCStdio is a service that is automatically run by the plugin process
    to stream any stdout/err data so that it can be mirrored on the plugin
    host side.
    """

    @staticmethod
    def StreamStdio(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/plugin.GRPCStdio/StreamStdio',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            saturn__bot_dot_plugin_dot_grpc__stdio__pb2.StdioData.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
