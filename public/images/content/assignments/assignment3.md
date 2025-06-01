---
title: "Assignment 3 — Deployment & Integration of LLMs"
date: 2025-05-31
draft: false
---


## 1  Objective

Deploy **one cloud‑hosted** and **one local** LLM, integrate both inside Visual Studio Code, and document the process end‑to‑end.

---

## 2  Environment Snapshot

| Component | Details                           |
| --------- | --------------------------------- |
| Host OS   | Windows 11 + WSL 2 (Ubuntu 22.04) |
| CPU / RAM | Intel i7‑12700H · 7.6 GiB RAM     |
| Editors   | VS Code 1.89 + Continue ext.      |
| Python    | 3.12 (venv `llm‐lab`)             |

---

## 3  Online Model API — Together AI

### 3.1 Key & Endpoint

```bash
pip install requests
export TOGETHER_AI_KEY="together‑xxxxxxxxxxxxxxxx"
```

* **Endpoint:** `https://api.together.xyz/v1/chat/completions`
* **Model:** `mistralai/Mixtral‑8x7B‑Instruct‑v0.1`

### 3.2 Minimal Test Script

```python
import os, json, requests
url = "https://api.together.xyz/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('TOGETHER_AI_KEY')}",
    "Content-Type": "application/json"
}
payload = {
  "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user",   "content": "Hello from Together AI!"}
  ]
}
print(requests.post(url, headers=headers, json=payload).json()
      ["choices"][0]["message"]["content"])
```

![Together AI terminal test](images/together_ping.png)

> *Checkpoint:* Cloud LLM replies, confirming key + endpoint work.

---

## 4  Local Model — Ollama `llama3:8b`

```bash
ollama pull llama3:8b   # one‑time download (~4 GB)
ollama run  llama3:8b   # interactive chat
```

![Local Ollama chat](images/ollama_chat.png)

> *Checkpoint:* Model answers fully offline.

---

## 5  IDE Integration — VS Code + Continue

| Provider            | Base URL                      | Auth    |
| ------------------- | ----------------------------- | ------- |
| **Together AI**     | `https://api.together.xyz/v1` | API key |
| **Ollama (LL3‑8B)** | `http://127.0.0.1:11434`      | none    |

> *Note:* Continue v1.0.10 currently sends OpenAI‑style calls to its global `openai.*` endpoint. Local model works; cloud calls show a 401 in this build. The standalone API (Section 3) verifies cloud access and will be re‑enabled once the extension supports custom endpoints.

![VS Code Continue panel](images/vscode_continue.png)

\------------------- | ----------------------------- | ------- |
\| **Together AI**     | `https://api.together.xyz/v1` | API key |
\| **Ollama (LL3‑8B)** | `http://127.0.0.1:11434`      | none    |

> *Note:* Continue v1.0.10 currently sends OpenAI‑style calls to its global `openai.*` endpoint. Local model works; cloud calls show a 401 in this build. The standalone API (Section 3) verifies cloud access and will be re‑enabled once the extension supports custom base URLs.

---

## 6  Evaluation & Comparison

| Metric           | Together AI | Ollama llama3‑8B |
| ---------------- | ----------- | ---------------- |
| Latency (≈)      | 1.8 s       | 0.08 s           |
| Cost / 1k tokens | free tier   | \$0              |
| Max context      | 32 k        | 8 k              |

**Observation:** Cloud model excels at large‑context reasoning; local model is instant, private, and cost‑free.

---

## 7  Conclusion

Both cloud and local LLMs coexist in a single tool‑chain: cloud for heavy reasoning, local for fast, private coding help. VS Code integration (even local‑only) reduced refactor time and docstring generation overhead.

---

## 8  Appendix

* `requirements.txt` — `requests`, `ollama‑py` (optional)
* Shell helpers: `run_llama.sh`, `together_ping.py`



