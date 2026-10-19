#!/usr/bin/env python3
"""Render per-AI prompts from the shared corpus (corpus/scenarios.json).

Keeps the adapters in sync with the single source of truth: run this after
editing scenarios and the Claude prompts / Purple AI query list regenerate.

Usage:
    python3 harness/render.py            # render everything
    python3 harness/render.py --list     # just list scenario ids + verdicts
"""
import json, os, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus" / "scenarios.json"
OUT = ROOT / "harness" / "out"

CLAUDE_SYSTEM = (
    "You are a senior SOC analyst. You will be given raw security data (logs, "
    "telemetry, an email, or an alert). Analyse ONLY what is in the data - do "
    "not invent indicators, hostnames, or facts that are not present.\n\n"
    "Respond in this structure:\n"
    "1. VERDICT: malicious | suspicious | benign\n"
    "2. KEY FINDINGS: the specific indicators and what they mean, with MITRE "
    "ATT&CK technique IDs where they apply.\n"
    "3. RECOMMENDED ACTIONS: concrete, prioritised response steps.\n"
    "Be decisive. If the data is benign, say so and say why - do not hedge to "
    "look thorough."
)

def main():
    data = json.loads(CORPUS.read_text())
    scen = data["scenarios"]
    if "--list" in sys.argv:
        for s in scen:
            print(f"{s['id']:16} {s['ground_truth']['verdict']:10} {s['title']}")
        return

    (OUT / "claude").mkdir(parents=True, exist_ok=True)
    jsonl = []
    for s in scen:
        # one pasteable prompt file per scenario
        (OUT / "claude" / f"{s['id']}.txt").write_text(
            f"# SYSTEM\n{CLAUDE_SYSTEM}\n\n# USER\n{s['input']}\n"
        )
        jsonl.append(json.dumps({
            "id": s["id"], "system": CLAUDE_SYSTEM, "user": s["input"],
            "expected_verdict": s["ground_truth"]["verdict"], "rubric": s["rubric"],
        }))
    (OUT / "claude" / "_batch.jsonl").write_text("\n".join(jsonl) + "\n")

    # a blank per-AI scoring sheet
    hdr = "| id | verdict | finding_recall | false_alarm | halluc | action | attck | notes |\n"
    sep = "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
    rows = "".join(f"| {s['id']} |  |  |  |  |  |  |  |\n" for s in scen)
    for ai in ("claude", "purple-ai"):
        (OUT / f"scoresheet-{ai}.md").write_text(
            f"# Score sheet - {ai}\nmodel/version: ____   date: ____\n\n{hdr}{sep}{rows}"
        )
    print(f"rendered {len(scen)} scenarios -> {OUT}")
    print(f"  claude prompts: harness/out/claude/<id>.txt (+ _batch.jsonl)")
    print(f"  score sheets:   harness/out/scoresheet-claude.md, scoresheet-purple-ai.md")

if __name__ == "__main__":
    main()
