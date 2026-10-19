"""Portable entry point. Existing native runtime is explicit and never installed."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

if __package__ is None or __package__=="":
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.dont_write_bytecode=True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    check=commands.add_parser("check-runtime")
    check.add_argument("--runtime",type=Path,required=True)
    demo_parser=commands.add_parser("demo")
    demo_parser.add_argument("--output",type=Path,required=True)
    run=commands.add_parser("run")
    run.add_argument("--config",type=Path,required=True)
    run.add_argument("--allow-live-model",action="store_true")
    args=parser.parse_args()
    from enzyme_environment.runtime import NativeRuntime
    try:
        if args.command=="demo":
            from enzyme_environment.demo import demo
            print(json.dumps(demo(args.output),indent=2));return 0
        if args.command=="check-runtime":
            result=NativeRuntime.from_file(args.runtime.absolute()).check()
            print(json.dumps(result,indent=2));return 0
        from enzyme_environment.inputs import Episode
        episode=Episode.from_file(args.config.absolute())
        if episode.backend=="live" and not args.allow_live_model:raise ValueError("Live execution needs --allow-live-model")
        native=episode.runtime.python_root/"bin/python3"
        if Path(sys.executable).resolve()!=native.resolve():
            os.execv(str(native),[str(native),"-I","-B",str(Path(__file__).resolve()),*sys.argv[1:]])
        sys.path[:0]=[str(episode.runtime.site_packages),str(episode.runtime.agent_source)]
        if episode.runtime.profile is not None:os.environ["SCI_HOME"]=str(episode.runtime.profile)
        import logging
        logging.disable(logging.CRITICAL)
        from enzyme_environment.runner import run_episode
        report=run_episode(episode,allow_live=args.allow_live_model)
        print(json.dumps(report,indent=2))
        return 0 if report["success"] else 1
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({"success":False,"stage":"episode_setup","error_type":type(exc).__name__,"message":str(exc)}))
        return 1


if __name__=="__main__":raise SystemExit(main())
