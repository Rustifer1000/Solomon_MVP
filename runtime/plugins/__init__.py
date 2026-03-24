from __future__ import annotations

"""Domain plugin adapters for the Solomon runtime scaffold."""

from runtime.plugins.base import PluginRuntime
from runtime.plugins.divorce import DIVORCE_PLUGIN_RUNTIME


_PLUGIN_REGISTRY: dict[str, PluginRuntime] = {
    DIVORCE_PLUGIN_RUNTIME.plugin_type: DIVORCE_PLUGIN_RUNTIME,
}


def _resolve_plugin_type(case_or_state: dict) -> str:
    if "case_metadata" in case_or_state:
        return case_or_state["case_metadata"]["plugin_type"]
    if "meta" in case_or_state:
        return case_or_state["meta"]["plugin_type"]
    raise KeyError("Could not resolve plugin_type from the provided object.")


def get_plugin_runtime(case_or_state: dict) -> PluginRuntime:
    plugin_type = _resolve_plugin_type(case_or_state)
    try:
        return _PLUGIN_REGISTRY[plugin_type]
    except KeyError as exc:
        raise NotImplementedError(f"No plugin runtime is registered for plugin type {plugin_type}.") from exc
