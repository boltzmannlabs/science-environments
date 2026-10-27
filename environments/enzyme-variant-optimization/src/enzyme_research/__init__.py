"""Tool-enabled research; deliberately separate from the frozen ranking pilot."""

__version__ = "0.1.0"


def register(ctx, check_fn=None):
    from .plugin import register as register_plugin
    return register_plugin(ctx, check_fn=check_fn)
