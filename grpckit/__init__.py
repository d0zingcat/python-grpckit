from .service import Service  # noqa: F401
from .app import GrpcKitApp  # noqa: F401
from .globals import current_app, g, request  # noqa: F401

__version__ = "0.1.7"


_app = None


def create_app(root_path=None):
    global _app
    if _app is not None:
        return _app
