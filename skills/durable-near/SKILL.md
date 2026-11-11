---
name: durable-near
description: How to create and manage durable, resumable, checkpointed actions on NEAR with human gates, verifiable receipts, and policy-ready payment steps using FlowMint.
---

# FlowMint — Durable Workflows for Agents

Use **FlowMint** whenever a task should:

- Survive process restarts or machine reboots
- Contain explicit human approval gates
- Produce an audit trail / verifiable receipt chain
- Optionally move money under policy controls
- Be pauseable and resumable days later

## When to use

Good candidates:
- Multi-day research or content pipelines
- Any workflow that needs a human to approve a risky step
- Sequences that end with a payment / tip / settlement
- Long-running local automation that must not be lost
- Tasks you may want to audit later (“what exactly did the agent do?”)

Bad candidates:
- One-shot questions
- Purely conversational replies

## Typical flow

1. **Create** the action with clear steps (including optional `type: payment` steps):

```
flowmint_create(
  title="Prepare weekly research digest",
  steps=[
    {"name": "gather", "instruction": "Search and collect the top 10 items on X this week"},
    {"name": "summarize", "instruction": "Write a concise summary of each item"},
    {"name": "review", "instruction": "Human reviews the digest", "needs_approval": true},
    {"name": "publish", "instruction": "Post the approved digest"},
    {
      "name": "tip",
      "type": "payment",
      "instruction": "Send 0.5 NEAR tip to the best source",
      "payment": {"amount": "0.5", "token": "NEAR"}
    }
  ],
  require_approval=true
)
```

2. **Resume** when ready to work:

```
flowmint_resume(action_id="...")
```

Returns the current step instruction (and payment details if it is a payment step).

3. Execute the instruction (using other tools, browsing, etc.).

4. **Approve / record result** and advance:

```
flowmint_approve(action_id="...", result={...}, note="optional note")
```

5. If the next step has `needs_approval` or is a payment under policy, status becomes `waiting_approval`.

6. Inspect anytime:

```
flowmint_status(action_id="...")
flowmint_history(action_id="...")   # full receipt chain
flowmint_list(status="waiting_approval")
flowmint_anchor(action_id="...")    # prepare on-chain root
```

## CLI equivalents

```bash
flowmint list
flowmint status <id>
flowmint resume <id>
flowmint approve <id> --note "looks good"
flowmint history <id>
flowmint anchor <id> --account youraccount.near
flowmint create --file examples/research-digest.yaml
```

## Design notes

- Each significant event produces a receipt whose hash chains to the previous one.
- State lives in `~/.flowmint/` and survives restarts.
- Payment steps are first-class and ready to be connected to a policy wallet + NEAR Intents.
- `flowmint_anchor` prepares a root hash that can be submitted to NEAR for public verifiability.

Prefer durable actions for anything that matters beyond the current session — especially when money is involved.
