from typing import Dict, Any

import simplejson
from google.protobuf import json_format
from google.protobuf.message import Message


def DictToMessage(
    data: Dict[Any, Any],
    message: Message,
    ignore_unknown_fields: bool = True,
) -> Message:
    if not isinstance(message, Message):
        raise ValueError("Invalid message! Must be an instance of Message")
    return json_format.Parse(
        text=simplejson.dumps(data),
        message=message,
        ignore_unknown_fields=ignore_unknown_fields,
    )


def MessageToDict(
    message: Message,
    including_default_value_fields: bool = True,
    preserving_proto_field_name: bool = True,
    use_integers_for_enums: bool = True,
) -> Dict[Any, Any]:
    return simplejson.loads(
        json_format.MessageToJson(
            message=message,
            including_default_value_fields=including_default_value_fields,
            preserving_proto_field_name=preserving_proto_field_name,
            use_integers_for_enums=use_integers_for_enums,
        )
    )
