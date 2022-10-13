from .utils import (
    cached_property,
    deserialize_request,
)


class Request:
    def __init__(self, request, context):
        """Init request"""
        self.request = request
        self.context = context

    @cached_property
    def headers(self):
        """Get header"""
        if self.rpc_event is not None:
            metadata = getattr(self.rpc_event, "invocation_metadata")
            return dict(metadata)
        return None

    @cached_property
    def values(self):
        """Get request params"""
        if self.request is not None:
            return deserialize_request(self.request)
        return None

    @cached_property
    def method(self):
        """Get request method"""
        if self.call_details is not None:
            method = getattr(self.call_details, "method")
            return method.decode("utf8") if method else method
        return None

    @cached_property
    def service(self):
        """Get request method"""
        if self.method is not None:
            return self.method.split("/")[-2]
        return None

    @cached_property
    def rpc_event(self):
        """Get rpc event"""
        if self.context is not None:
            return getattr(self.context, "_rpc_event")
        return None

    @cached_property
    def call_details(self):
        """Get call details"""
        if self.rpc_event is not None:
            return getattr(self.rpc_event, "call_details")
        return None
