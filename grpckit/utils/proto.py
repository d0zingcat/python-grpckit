import importlib
import os
import re

r_add_funcs = re.compile(r"add_\S+Servicer_to_server")
r_desc_name = re.compile(r"DESCRIPTOR.services_by_name\['(.*)'\]")


def _walk_path_files(path=None):
    for root, _, files in os.walk(path or "."):
        # invalid path
        if root.startswith("./venv") or root.startswith(".git"):
            continue

        for file in files:
            yield root, file


def scan_pb_grpc(path=None):
    server_register_funcs = dict()

    for root, file in _walk_path_files(path=path):
        if not file.endswith("pb2_grpc.py"):
            continue

        path = os.path.join(root, file)
        with open(path, "r", encoding="utf-8") as f:
            funcs = r_add_funcs.findall(f.read())
            print(funcs)
            if not funcs:
                continue

            module = path.replace("./", "").replace("/", ".").replace(".py", "")
            print(module)
            obj = importlib.import_module(module)
            for func in funcs:
                server_register_funcs[func] = getattr(obj, func)

    return server_register_funcs
