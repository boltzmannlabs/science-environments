"""Independent add-on using native hooks; original Boltzmann code is untouched."""

from pathlib import Path


def register(ctx, check_fn=None):
    from .hooks import CallObserver
    from .schemas import SCHEMAS
    from .tools import dispatch
    if check_fn is None:
        def check_fn():
            from tools.registry import registry
            entry = registry.get_entry("boltzmann_submit")
            return bool(entry and entry.check_fn and entry.check_fn())
    for schema in SCHEMAS:
        name = schema["name"]
        ctx.register_tool(name=name, toolset="boltzmann", schema=schema,
            handler=lambda args, _name=name, **kw: dispatch(_name, args,
                config=lambda: {"bindings": ctx.get_config("bindings", {}),
                                "contracts": ctx.get_config("contracts", {})}, authorized=check_fn),
                          check_fn=check_fn, description=schema["description"])
    observer = CallObserver()
    ctx.register_hook("pre_tool_call", observer.pre)
    ctx.register_hook("post_tool_call", observer.post)
    if check_fn():
        register_skills(ctx)


def register_skills(ctx):
    root = Path(__file__).parent / "skills"
    for name, folder in (("enzyme-workflow", "enzyme-design-workflow"),
                         ("reaction-template-builder", "reaction-template-builder"),
                         ("mol-probity-reviewer", "mol-probity-reviewer")):
        ctx.register_skill(name, root / folder / "SKILL.md",
                           description={"enzyme-workflow": "Run resumable enzyme design workflows.",
                                        "reaction-template-builder": "Build reaction-specific geometry templates.",
                                        "mol-probity-reviewer": "Interpret protein structure quality reports."}[name])
