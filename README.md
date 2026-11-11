# NearAction

> Durable, resumable, checkpointed agent workflows on NEAR  
> with human-approval gates, verifiable receipts, **x402 micropayments**, and policy-controlled spending.

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
- **Native x402 support** — agents can pay for APIs/data over HTTP 402 with stablecoins / NEAR
- First-class payment steps ready for a policy wallet
- Works with any agent that can call tools (NEAR AI, IronClaw, custom, Claude, …)

This is the foundation for reliable agents that can safely hold and move money.

---

## Quick start

```bash
pip install -e .

nearaction create --file examples/research-digest.yaml
nearaction list
nearaction resume <action_id>
nearaction approve <action_id> --note "looks good"
nearaction history <action_id>
```

### Agent tools

- `nearaction_create` / `list` / `status` / `resume` / `approve` / `cancel` / `history`
- `nearaction_anchor` — prepare receipt root for NEAR
- `nearaction_x402_challenge` — record an HTTP 402 and build a payment intent
- `nearaction_x402_confirm` — mark payment fulfilled and advance
- `nearaction_add_x402_step` — append a paid API step to a live action

---

## x402 payments (agent micropayments)

[x402](https://x402.org) revives HTTP **402 Payment Required** so an agent can pay for a resource inside the request itself — no accounts, no API keys, no human checkout form.

NearAction makes that durable:

1. Step with `type: x402` and a target URL
2. Agent hits the URL → receives 402
3. Call `nearaction_x402_challenge(...)` → payment intent is stored + receipt emitted
4. Human / policy approves (status becomes `waiting_approval`)
5. Agent signs (via policy-limited NEAR key, `@x402/near`, etc.) and retries
6. Call `nearaction_x402_confirm(...)` → step completes, chain continues

Example workflow: `examples/x402-api-call.yaml`

```yaml
- name: fetch-premium
  type: x402
  instruction: Request the premium endpoint and handle 402 via NearAction
  x402:
    url: "https://api.example.com/v1/premium-research"
    method: GET
    max_amount: "1.00"
    preferred_network: "near:mainnet"
```

NEAR is a first-class network in the x402 ecosystem (`@x402/near`, market.near.ai, etc.). NearAction keeps the **workflow + audit trail** durable while the actual signature stays with your policy wallet / agent runtime.

---

## Architecture (v0.1)

- Local-first storage under `~/.nearaction/`
- JSON actions + individual receipt files
- SHA-256 hash chain for a simple verifiable audit trail
- Optional on-chain anchor of the receipt root
- `type: payment` and `type: x402` steps are first-class
- Zero telemetry, minimal dependencies

### Design principles

1. **Durability first**
2. **Human gates are first-class**
3. **Auditability** — every important transition produces a receipt
4. **Money is dangerous** — payment & x402 steps default to approval / policy
5. **Minimal surface** — easy to understand, easy to extend

---

## Agentic Wallet foundation

NearAction already models payment and x402 steps.  
The next layer is a **policy wallet**:

- Human sets spending limits, allowlists, velocity rules
- Agent only receives a tightly scoped function-call key
- Every payment (Intents or x402) goes through the same durable + receipt machinery

This keeps the agent powerful but unable to drain funds.

---

## Installation

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
pip install -e .
```

Optional later:

```bash
# real x402 client libraries
pip install "x402[httpx]"          # official Python SDK
# or use @x402/near / uvd-x402-sdk from your agent runtime
```

---

## For NEAR Hackathon judges

1. Clone the repo
2. `pip install -e .`
3. Run the demo flow in `DEMO.md`
4. Inspect `~/.nearaction/actions/` and the receipt chain
5. Open `examples/x402-api-call.yaml` to see how agentic micropayments are modeled

---

## Roadmap

- [x] Durable actions + human gates + receipts
- [x] On-chain anchor preparation
- [x] x402 challenge / confirm tools
- [ ] Full policy wallet contract (function-call key + limits)
- [ ] Live `@x402/near` / official `x402` Python signing helpers
- [ ] Direct NEAR Intents execution inside payment steps
- [ ] On-chain action state for multi-agent coordination

---

## License

MIT

---

Built for NEAR HACKATHON 2026.  
Durable agents. Safe money. Verifiable work. x402-ready.
