"""Enzyme variant optimization task runner and specialist."""

__version__ = "0.1.1"


def register(ctx, check_fn=None):
    from .plugin import register as register_plugin
    return register_plugin(ctx, check_fn=check_fn)
