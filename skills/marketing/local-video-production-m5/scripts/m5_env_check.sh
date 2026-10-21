#!/bin/bash
# M5 local-video env gate: ComfyUI up, models present, LM Studio off, MPS.
M5="${M5:-192.168.212.46}"
echo "== ComfyUI =="
sshpass -p 'Buddy-2019' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "joergpeetz@${M5}" \
  "curl -s --max-time 5 http://127.0.0.1:8188/system_stats | head -c 30; echo; pgrep -fl llama-server >/dev/null && echo 'WARN: LM Studio RUNNING (free ~5GB first)' || echo 'LM Studio: off'; ls ~/ComfyUI-Shared/models/diffusion_models/ 2>/dev/null | head -3" 2>&1
echo "== MPS =="
/Users/joergpeetz/ComfyUI-Installs/ComfyUI/ComfyUI/.venv/bin/python -c "import torch; print('mps:', torch.backends.mps.is_available())" 2>&1 | tail -1
