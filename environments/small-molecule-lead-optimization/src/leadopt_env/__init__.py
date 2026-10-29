"""Small-molecule lead-optimization campaign environment."""
__version__ = "0.1.0"


def register(ctx):
    from .plugin import register as register_plugin
    return register_plugin(ctx)
