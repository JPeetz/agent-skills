---
name: n8n-api-shape
description: >-
  Use this skill when working with the n8n REST API — read, update, or verify
  workflows on ANY n8n instance. Instance-agnostic: update recipe that strips
  extra fields on PUT, banned top-level fields, auth header, health endpoint.
version: 1.0.0
platforms: [hermes, openclaw, claude, codex, cursor]
author:
  name: Custodian (AgentForge)
  source: Joerg Peetz / Fluffy — extracted from openclaw-n8n-operations for reuse
license: MIT
risk_tier: L2
tags: [n8n, api, workflow, automation, rest]
requires:
  binaries: [curl, python3]
---

# n8n REST API — Shape Reference (instance-agnostic)

A reusable, instance-agnostic reference for the n8n REST API. Usable on any
n8n instance (a client's fresh one, or your own) without hardcoding host,
instance, or workflow IDs.

## When to Use This Skill

Use this skill when:
- You need to read, update, or verify an n8n workflow via the REST API.
- Prior skills point at a SPECIFIC n8n instance (a host/workflow ID) that does
  not apply to the instance you're touching now.
- You hit `400 additional properties` on workflow PUT.

## Auth
- Header: `X-N8N-API-KEY: <key>` (generate at Settings → API; store in the vault by label).
- Base: `https://<n8n-host>/api/v1/`.

## Read a workflow (GET)
`GET /api/v1/workflows/{id}` → returns the workflow JSON.

## Update a workflow (PUT) — the exact recipe that works
n8n rejects extra fields on PUT with `400 additional properties`. Strip to a minimal
4-key payload:
```python
import json, requests
wf = requests.get(f"{base}/workflows/{wf_id}",
    headers={"X-N8N-API-KEY": key}, timeout=20).json()
for node in wf["nodes"]:
    for k in ["id", "position", "credentials", "webhookId"]:
        node.pop(k, None)
payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": {"executionOrder": wf["settings"].get("executionOrder", "v1")},
}
r = requests.put(f"{base}/workflows/{wf_id}",
    headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"},
    json=payload, timeout=20)
assert r.status_code == 200, r.text
```
**Banned top-level fields on PUT:** id, active, tags, versionId, pinData, staticData,
createdAt, updatedAt, meta, activeVersionId, versionCounter, triggerCount, shared,
activeVersion, isArchived, description.

## Health
`GET /api/v1/health` → `{"status":"ok",...}`. Check this first — an n8n instance whose
API key is scoped wrong or host unreachable fails here before any workflow edit.

## Guardrails
- The API key lives by label in the vault; never hardcode, never echo.
- Save the GET response to disk before editing (enables retry without re-fetch).
- Verify after every PUT (HTTP 200 + spot-check content).
- Never copy another instance's host/workflow IDs into a different profile.

## PITFALLS
- `400 additional properties` = payload has extra fields → use the strip recipe.
- Check `/health` before assuming workflow edits are possible.
- `credentials` must be popped from nodes before PUT or n8n rejects the payload.
