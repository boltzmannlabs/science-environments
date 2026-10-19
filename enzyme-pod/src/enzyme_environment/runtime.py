"""Explicit, operator-owned native runtime paths; no installation or auto-update."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from enzyme_environment.policy import strict_json


def regular_file(path, *, limit=2097152):
    path = Path(path)
    if (not path.is_absolute() or path.resolve() != path or not path.is_file()
            or not 0 < path.stat().st_size <= limit):
        raise ValueError("Expected a bounded, absolute, non-symlink regular file")
    return path.read_bytes()


def directory(value, name):
    if not isinstance(value, str) or not value:
        raise ValueError(name + " must be an absolute directory path")
    path = Path(value)
    if not path.is_absolute() or path.resolve() != path or not path.is_dir():
        raise ValueError(name + " must be an existing absolute directory without symlink aliases")
    return path


@dataclass(frozen=True)
class NativeRuntime:
    agent_source: Path
    python_root: Path
    site_packages: Path
    agent_revision: str
    profile: Path | None = None
    bubblewrap: Path = Path("/usr/bin/bwrap")
    limit_python: Path = Path("/usr/bin/python3")

    @classmethod
    def from_file(cls, path):
        value = strict_json(regular_file(path, limit=65536))
        required = {"schema_version", "agent_source", "python_root", "site_packages", "agent_revision"}
        if not isinstance(value, dict) or not required <= set(value) or set(value)-required-{"profile","bubblewrap","limit_python"}:
            raise ValueError("Unexpected or missing native runtime configuration fields")
        if value["schema_version"] != "enzyme-native-runtime/1": raise ValueError("Unsupported native runtime schema")
        revision = value["agent_revision"]
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError("An exact 40-character Agent-Scientist revision is required")
        profile = value.get("profile")
        result = cls(directory(value["agent_source"],"agent_source"), directory(value["python_root"],"python_root"),
            directory(value["site_packages"],"site_packages"), revision,
            directory(profile,"profile") if profile is not None else None,
            Path(value.get("bubblewrap","/usr/bin/bwrap")), Path(value.get("limit_python","/usr/bin/python3")))
        for executable in (result.bubblewrap,result.limit_python):
            if not executable.is_absolute() or not executable.is_file() or not os.access(executable,os.X_OK):
                raise ValueError("Required Linux executable is unavailable")
        native = result.python_root/"bin/python3"
        if not native.is_file() or not native.resolve().is_relative_to(result.python_root):
            raise ValueError("Native interpreter must stay inside its standalone runtime directory")
        if not (result.agent_source/"run_agent.py").is_file(): raise ValueError("Agent source entry point missing")
        # Full original source/profile must not leak through the system mounts.
        for private in (result.agent_source,result.profile):
            if private is not None and any(private.is_relative_to(Path(p)) for p in ("/usr","/lib","/lib64")):
                raise ValueError("Private source/profile cannot be inside a whole-system read-only mount")
        return result

    def check(self):
        if sys.platform != "linux": raise ValueError("Native namespace execution currently requires Linux")
        head = subprocess.check_output(["git","-C",str(self.agent_source),"rev-parse","HEAD"],text=True).strip()
        status = subprocess.check_output(["git","-C",str(self.agent_source),"status","--porcelain"],text=True)
        if head != self.agent_revision or status:
            raise ValueError("Agent checkout must match the pinned clean revision; no checkout/reset was attempted")
        data = subprocess.check_output([str(self.python_root/"bin/python3"),"-I","-B","-c",
            'import json,sys; print(json.dumps({"version":list(sys.version_info[:3])}))'],text=True,
            env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8"},timeout=10)
        version = strict_json(data)["version"]
        if version[:2] != [3,14]: raise ValueError("Inspected native Agent-Scientist requires Python 3.14")
        wanted={"openai","httpx","httpcore","anyio","pydantic","pydantic-core","ruamel-yaml"}
        dependencies={}
        for dist in importlib.metadata.distributions(path=[str(self.site_packages)]):
            name=re.sub(r"[-_.]+","-",(dist.metadata.get("Name") or "").lower())
            if name in wanted:
                dependencies[name]={"version":dist.version,"metadata_sha256":hashlib.sha256((dist.read_text("METADATA") or "").encode()).hexdigest()}
        if not {"openai","httpx","pydantic"}<=set(dependencies):raise ValueError("Existing native SDK dependencies are incomplete; no install was attempted")
        return {"agent_revision":head,"agent_worktree_clean":True,"python_version":".".join(map(str,version)),
                "critical_dependency_metadata":dependencies,"installation_changed":False,"source_modified":False}

    def source_snapshot(self):
        names = subprocess.check_output(["git","-C",str(self.agent_source),"ls-files","-z"]).decode().split("\0")
        hashes = {}
        for name in names:
            if not name: continue
            path = self.agent_source/name
            if path.is_file() and not path.is_symlink() and path.stat().st_size < 5*1024**2:
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return {"head":subprocess.check_output(["git","-C",str(self.agent_source),"rev-parse","HEAD"],text=True).strip(),
                "status":subprocess.check_output(["git","-C",str(self.agent_source),"status","--porcelain"],text=True),"hashes":hashes}

    def export_source(self, destination, snapshot):
        directories = {"agent","tools","sci_cli","pm","gateway","providers","environments","plugins","sci_platform",
            "locales","sci_traces","sci_datasets","sci_hooks","hooks","cron","acp_adapter","assets"}
        suffixes = {".py",".json",".yaml",".yml",".toml",".txt",".md",".j2"}
        exported = {}
        for name, expected in snapshot["hashes"].items():
            relative = Path(name)
            if relative.suffix not in suffixes or (len(relative.parts)>1 and relative.parts[0] not in directories): continue
            if any(part.startswith(".") or part in {"tests","test_data","fixtures","contract_sources"} for part in relative.parts): continue
            if any(word in relative.name.lower() for word in ("credential","auth.json","secret",".env")) and relative.suffix != ".py": continue
            path = self.agent_source/relative
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError("Agent source changed during read-only export")
            target = destination/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
            exported[name]=expected
        (destination.parent/"source_export_manifest.json").write_text(json.dumps(exported,indent=2)+"\n")
        return exported

    def command(self, run, socket):
        import enzyme_benchmark
        import enzyme_environment
        package = Path(enzyme_environment.__file__).resolve().parent
        benchmark = Path(enzyme_benchmark.__file__).resolve().parent
        args=[str(self.bubblewrap),"--unshare-all","--die-with-parent","--new-session","--cap-drop","ALL","--clearenv"]
        for path in ("/usr","/lib","/lib64"):
            if Path(path).is_dir(): args.extend(["--ro-bind",path,path])
        args += ["--proc","/proc","--dev","/dev","--tmpfs","/tmp","--dir","/run","--dir","/etc",
            "--ro-bind",str(self.python_root),"/runtime/python","--ro-bind",str(self.site_packages),"/runtime/site-packages",
            "--ro-bind",str(run/"source"),"/agent","--ro-bind",str(package),"/runner/enzyme_environment",
            "--ro-bind",str(benchmark),"/runner/enzyme_benchmark","--ro-bind",str(run/"inputs"),"/inputs",
            "--bind",str(run/"guest_work"),"/work","--ro-bind",str(socket),"/run/benchmark.sock","--chdir","/work"]
        probes=[str(self.agent_source),str(run),"/var/run/docker.sock"]
        if self.profile is not None: probes.append(str(self.profile))
        env={"HOME":"/work/home","SCI_HOME":"/work/profile","PATH":"/runtime/python/bin:/usr/bin","LANG":"C.UTF-8",
            "PYTHONDONTWRITEBYTECODE":"1","PYTHONNOUSERSITE":"1","SCI_DISABLE_LAZY_INSTALLS":"1","CUDA_VISIBLE_DEVICES":"",
            "OMP_NUM_THREADS":"2","OPENBLAS_NUM_THREADS":"2","MKL_NUM_THREADS":"2","BENCHMARK_HOST_PID":str(os.getpid()),
            "ENZYME_HOST_PROBES":json.dumps(probes)}
        for key,value in env.items(): args.extend(["--setenv",key,value])
        args += ["/runtime/python/bin/python3","-I","-B","/runner/enzyme_environment/native_worker.py"]
        return [str(self.limit_python),"-I","-B",str(package/"limits.py"),*args]
