"""Smoke tests for the dependency-free Vercel entrypoint."""

import importlib.util
from pathlib import Path


def _load_handler_module():
    path = Path(__file__).parents[1] / "api" / "index.py"
    spec = importlib.util.spec_from_file_location("flowmint_vercel_entrypoint", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vercel_entrypoint_exports_handler():
    module = _load_handler_module()
    assert hasattr(module, "handler")
    assert module.handler.__name__ == "handler"
