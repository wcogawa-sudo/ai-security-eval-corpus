# AI Security Eval Corpus

An AI-agnostic evaluation set for testing how well AI security analysts reason over real-style incidents, and whether they can be **hijacked by prompt injection hidden in the data they review**.

Every scenario has a known correct answer, so different AIs (an LLM acting as a SOC analyst, a vendor's built-in security AI, and so on) are graded on the same questions with the same rubric.

## What's in it

- **14 scenarios** in `corpus/scenarios.json`, set in South Africa:
  - **7 malicious:** SARS eFiling phishing, a fake Capitec login with OTP theft (AiTM), AARTO traffic-fine smishing, a BEC invoice-swap, SIM-swap account takeover, a ransomware precursor using a load-shedding lure, and insider PII exfiltration.
  - **3 benign look-alikes:** a new-device banking login, admin PowerShell patching, and an authenticated bulk marketing send. These measure false positives.
  - **4 prompt-injection tests (`SA-INJECT-*`):** instructions hidden in the evidence itself. One is a phishing email with a hidden "classify as benign" note. One is a C2 beacon with an injection in its User-Agent. One is a service-desk ticket telling the analyst to email data externally. The fourth is a benign control (a legitimate "ignore my last email"). They test whether the AI treats hidden instructions as **data** or **obeys** them.
- Each scenario has: input artefacts (email, DNS, proxy, auth, EDR, DLP), the ground-truth verdict, the findings a correct answer must surface, the recommended actions, MITRE ATT&CK mapping and a rubric.
- `scoring.md`: the shared rubric covering verdict, finding recall, false alarms, hallucination, actionability and ATT&CK mapping. It includes a prompt-injection gate and an LLM-as-judge prompt.
- `adapters/`: thin per-AI adapters. `claude-analyst.md` is a fixed analyst system prompt. `purple-ai.md` has natural-language hunting queries per scenario, for a live-data mode and a reasoning-only mode.
- `harness/render.py`: renders prompts, an API batch file and blank score sheets from the JSON.

## Design: one core, thin adapters

```
          scenarios.json  (single source of truth: input + ground truth + rubric + ATT&CK + tags)
                 |
      +----------+-----------+
      |                      |
 adapter: LLM analyst   adapter: vendor AI   ...
 (render, filter,       (render, filter,
  capture, score)        capture, score)
```

Adding a new AI means writing an adapter, not a new corpus. That keeps scores comparable across tools and across model versions.

## Run it

```bash
python3 harness/render.py          # writes harness/out/: per-scenario prompts, _batch.jsonl, score sheets
```

1. Send each `harness/out/claude/<id>.txt` to the model, or send `_batch.jsonl` through the API.
2. Grade each answer with `scoring.md` into `harness/out/scoresheet-<ai>.md`.
3. Run every scenario 3 times to measure consistency.

## Notes

- All data is **synthetic and hand-written**. Every company, person, domain and IP is fictional and built for testing. No real client data is included.
- Status: v1. Next steps are more scenarios (cloud/identity, lateral movement), harder benign look-alikes, and an automated LLM-judge scorer.

## License

MIT
