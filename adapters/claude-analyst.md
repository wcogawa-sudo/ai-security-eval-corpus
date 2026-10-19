---
tags: [ai, security, corpus, adapter, claude]
---
# Adapter: Claude as SOC analyst

Claude consumes the scenario `input` directly as a prompt - no ingestion
needed, so it can run **every** scenario in the corpus (all data types).

## System prompt (fixed)
```
You are a senior SOC analyst. You will be given raw security data (logs,
telemetry, an email, or an alert). Analyse ONLY what is in the data - do not
invent indicators, hostnames, or facts that are not present.

Respond in this structure:
1. VERDICT: malicious | suspicious | benign
2. KEY FINDINGS: the specific indicators and what they mean, with MITRE
   ATT&CK technique IDs where they apply.
3. RECOMMENDED ACTIONS: concrete, prioritised response steps.
Be decisive. If the data is benign, say so and say why - do not hedge to
look thorough.
```

## User prompt (per scenario)
```
{scenario.input}
```

## How to run
- **Manual:** paste the system prompt, then each scenario's `input`. Record the answer.
- **Batch:** `harness/render.py` writes one ready-to-send prompt per scenario to
  `harness/out/claude/<id>.txt`, and a JSONL of `{id, system, user}` for API use.
- Grade with `scoring.md`. Run 3x per scenario for consistency.

## Modality note
Claude gets the data inline, so it is the **baseline** every scenario is
gradeable against. Where Purple AI can't reach a data type (see its adapter),
Claude still can - useful for isolating whether a miss is the model or the data access.
