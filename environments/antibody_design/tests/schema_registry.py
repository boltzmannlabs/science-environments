"""Resolve the versioned schema catalog locally; unknown references never use the network."""
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
import yaml

from contract_io import read_json, require

ROOT = Path(__file__).resolve().parents[1]


def environment_config():
    return yaml.safe_load((ROOT / 'config/environment.yaml').read_text())


def config_path(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT / 'config'), 'Configuration path escapes config/')
    require(path.is_file(), f'Missing configuration file: {relative}')
    return path


@lru_cache(maxsize=1)
def schema_registry():
    resources = []
    identifiers = set()
    for path in sorted((ROOT / 'config').rglob('*.schema.json')):
        schema = read_json(path)
        Draft202012Validator.check_schema(schema)
        identifier = schema['$id']
        require(identifier not in identifiers, 'Duplicate schema identifier')
        identifiers.add(identifier)
        resources.append((identifier, Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def schema_path(name):
    return config_path(environment_config()['contracts'][name])


def validator_for_path(path):
    schema = read_json(path)
    return Draft202012Validator(schema, registry=schema_registry(), format_checker=FormatChecker())


def schema_validator(name):
    return validator_for_path(schema_path(name))
