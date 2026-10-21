#!/usr/bin/env python3
"""OpenMontage preflight: concise capability report from the repo registry.
Requires OPENMONTAGE_PATH (or --path). Source of truth = the repo's own registry."""
import json
import os
import sys
from pathlib import Path

root = Path(os.environ.get("OPENMONTAGE_PATH", "") or "").expanduser()
# allow --path override
if "--path" in sys.argv:
    root = Path(sys.argv[sys.argv.index("--path") + 1]).expanduser()

if not root.is_dir():
    print(json.dumps({
        "status": "blocked",
        "error": f"OpenMontage directory not found: {root}",
    }, indent=2))
    sys.exit(2)

sys.path.insert(0, str(root))

from tools.tool_registry import registry  # noqa: E402

registry.discover()

print(json.dumps({
    "root": str(root),
    "provider_menu": registry.provider_menu_summary(),
    "capabilities": registry.capability_catalog(),
}, indent=2))
