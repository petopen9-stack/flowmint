# NearAction

> Durable, resumable, checkpointed agent workflows on NEAR  
> with human-approval gates, verifiable receipts, and policy-controlled payments.

**Built for [NEAR HACKATHON 2026](https://nearhackathon.com)**  
Tracks: **Agent Economy** · **AI Security & Defense** · **Autonomous Business**

---

## Why NearAction exists

Most AI agents are ephemeral.  
A multi-step research pipeline, a payment sequence, or any work that needs a human checkpoint disappears the moment the process dies.

**NearAction** turns agent work into durable execution:

- Actions survive restarts
- Explicit human gates (`waiting_approval`)
- Checkpoint + resume at any step
- Hash-chained receipts (local + optional on-chain anchor on NEAR)
- Native support for **policy-controlled payment steps** (agentic wallet foundation)
- Works with any agent that can call tools (NEAR AI, IronClaw, custom, Claude, etc.)

This is the foundation for reliable agents that can safely hold and move money.

---

## Quick start

```bash
pip install -e .

# Create a durable action
nearaction create --file examples/research-digest.yaml

# List actions
nearaction list

# Resume / get current step
nearaction resume <action_id>

# Record result & advance (or approve human gate)
nearaction approve <action_id> --note "looks good"

# Full audit trail
nearaction history <action_id>
```

The same capabilities are exposed as tools an agent can call:

- `nearaction_create`
- `nearaction_list`
- `nearaction_status`
- `nearaction_resume`
- `nearaction_approve`
- `nearaction_cancel`
- `nearaction_history`
- `nearaction_anchor` (push receipt root to NEAR)

---

## Example workflow (with payment step)

```yaml
title: Weekly research digest + tip
description: Research → summarize → human review → publish → tip the source
steps:
  - name: gather
    instruction: Search and collect the top relevant items from the last 7 days
  - name: summarize
    instruction: Write a concise bullet-point summary for each item
  - name: human-review
    instruction: Wait for human approval of the draft digest
    needs_approval: true
  - name: publish
    instruction: Post the approved digest to the configured channel
  - name: tip-source
    type: payment
    instruction: Send a small tip to the original source via NEAR Intents
    payment:
      amount: "0.5"
      token: "NEAR"
      # recipient will be filled at runtime or from allowlist
```

---

## Architecture (v0.1)

- **Local-first storage** under `~/.nearaction/` (survives restarts)
- JSON action documents + individual receipt files
- SHA-256 hash chain for a simple verifiable audit trail
- Optional **on-chain anchor**: compute receipt root and submit to NEAR (or store in a named account)
- Payment steps are first-class (`type: payment`) and designed to plug into a policy wallet later
- Zero telemetry, minimal dependencies

### Design principles

1. **Durability first** — state must survive process death
2. **Human gates are first-class** — not an afterthought
3. **Auditability** — every important transition produces a receipt
4. **Money is dangerous** — payment steps are explicit and policy-ready
5. **Minimal surface** — easy to understand, easy to extend

---

## Agentic Wallet foundation

NearAction already models payment steps.  
The next natural layer (already stubbed) is a **policy wallet**:

- Human sets spending limits, allowlists, velocity rules
- Agent only receives a tightly scoped function-call key
- Every payment goes through the same durable + receipt machinery

This keeps the agent powerful but unable to drain funds.

---

## Installation

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
pip install -e .
```

Optional (for real NEAR anchoring later):

```bash
pip install near-api-py   # or your preferred NEAR Python client
```

---

## For NEAR Hackathon judges

1. Clone the repo
2. `pip install -e .`
3. Run the demo flow in `DEMO.md`
4. Inspect `~/.nearaction/actions/` and the receipt chain
5. See how a `type: payment` step is modeled (ready for Intents / policy wallet)

README + DEMO + clear “do X, see Y” steps are provided.

---

## Roadmap (post-hackathon)

- [ ] Full policy wallet contract (function-call key + on-chain limits)
- [ ] Native NEAR Intents execution inside payment steps
- [ ] On-chain action state (for multi-agent / public audit)
- [ ] DAG / parallel steps
- [ ] Time-based triggers
- [ ] Signed receipts with NEAR keys

---

## License

MIT

---

Built for NEAR HACKATHON 2026.  
Durable agents. Safe money. Verifiable work.
