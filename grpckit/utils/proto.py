from typing import Tuple, Dict
import importlib
import os
import re

r_add_funcs = re.compile(r"add_\S+Servicer_to_server")
r_request_model = re.compile(r"request_serializer=(.+?)\.(.+?)\.SerializeToString")
r_response_model = re.compile(r"response_deserializer=(.+?)\.(.+?)\.FromString,")
r_desc_name = re.compile(r"DESCRIPTOR.services_by_name\['(.*)'\]")


def _walk_path_files(path=None):
    for root, _, files in os.walk(path or "."):
        # invalid path
        if root.startswith("./venv") or root.startswith(".git"):
            continue

        for file in files:
            yield root, file


def scan_pb_grpc(path=None, import_request_model=False) -> Tuple[Dict, Dict]:
    """Return two dict
    the formel is pb register funcs,
    the latter is pb models
    """
    server_register_funcs = dict()
    server_request_models = dict()

    for root, file in _walk_path_files(path=path):
        if not file.endswith("pb2_grpc.py"):
            continue

        path = os.path.join(root, file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            funcs = r_add_funcs.findall(content)
            if not funcs:
                continue

            module = path.replace("./", "").replace("/", ".").replace(".py", "")
            obj = importlib.import_module(module)
            for func in funcs:
                server_register_funcs[func] = getattr(obj, func)
            if import_request_model:
                for model, request in r_request_model.findall(content):
                    _m = getattr(obj, model)
                    server_request_models[f"{model}.{request}"] = getattr(_m, request)
                for model, response in r_response_model.findall(content):
                    _m = getattr(obj, model)
                    server_request_models[f"{model}.{response}"] = getattr(_m, response)

    return server_register_funcs, server_request_models
