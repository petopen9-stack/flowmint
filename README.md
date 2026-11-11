# FlowMint

> Durable, resumable agent workflows on NEAR  
> with human gates, verifiable receipts, **x402 micropayments**, and policy-ready spending.

**NEAR HACKATHON 2026** · Tracks: **Agent Economy** · **AI Security & Defense** · **Autonomous Business**

---

## 60-second demo (no network)

```bash
git clone https://github.com/petopen9-stack/flowmint.git
cd flowmint
pip install -e .
flowmint demo
```

You will see: create → human gates → **x402 challenge (mock 402)** → payment confirm → receipt chain → NEAR anchor prep.

Full script: [DEMO.md](./DEMO.md)

### Security demo

```bash
flowmint security-demo
```

This simulates a prompt-injected agent trying to send `9,000,000` atomic units
to `attacker.near`. The deterministic policy engine blocks the payment before
any payment intent can be signed, records `security_blocked` in the hash-chained
audit trail, and reports **funds sent: 0**.

---

## Why this exists

Agents that move money need three things:

1. **Durability** — multi-step work must survive restarts  
2. **Policy control** — the agent must not be able to drain funds  
3. **Standard rails** — [x402](https://x402.org) for HTTP micropayments, NEAR Intents for cross-chain settlement  

FlowMint delivers (1) + (2) today and is structured for (3).

---

## Features

| Feature | Status |
|---------|--------|
| Durable actions + checkpoints | ✅ |
| Human approval gates | ✅ |
| Hash-chained receipts | ✅ |
| On-chain anchor preparation | ✅ |
| `type: payment` steps | ✅ |
| **Native x402** (`challenge` / `confirm`) | ✅ |
| Offline one-command demo | ✅ |
| Deterministic allow / warn / block policy engine | ✅ |
| Prompt-injection payment block demo | ✅ |
| Policy wallet stubs | ✅ foundation |

---

## CLI

```bash
flowmint create --file examples/x402-api-call.yaml
flowmint list
flowmint resume <id>
flowmint approve <id> --note "ok"
flowmint x402-challenge <id> --mock      # offline 402
flowmint x402-confirm <id> --note "paid"
flowmint history <id>
flowmint anchor <id> --account you.near
flowmint demo                            # full walkthrough
flowmint security-demo                   # block a malicious payment
flowmint facilitator-supported            # live PingPay capability check
```

---

## x402 flow (agent micropayments)

1. Step with `type: x402` + target URL  
2. Agent requests URL → receives **HTTP 402**  
3. `flowmint x402-challenge` stores payment intent + receipt  
4. Status → `waiting_approval` (human or policy)  
5. Sign with limited key (`@x402/near`, policy wallet, …) and retry  
6. `flowmint x402-confirm` → step done, chain continues  

Example: `examples/x402-api-call.yaml`

NEAR is first-class in the x402 ecosystem. FlowMint keeps the **workflow + audit trail** durable while signing stays with your runtime / policy wallet.

Resources from [nearbuilders.org/build](https://nearbuilders.org/build):
- NEAR Intents / Agent Connect  
- NEAR AI Cloud  
- Docs: [docs.near.org](https://docs.near.org) · [docs.near-intents.org](https://docs.near-intents.org)

---

## Install

```bash
git clone https://github.com/petopen9-stack/flowmint.git
cd flowmint
pip install -e .

# optional tests
pip install pytest && python -m pytest tests/ -q
```

---

## For judges

**Do X, see Y:**

| Step | Command | Expected |
|------|---------|----------|
| Install | `pip install -e .` | package available |
| Demo | `flowmint demo` | full flow prints events including `x402_challenged` |
| History | `flowmint history <id>` | hash chain of receipts |
| Anchor | `flowmint anchor <id>` | `root_hash` prepared for NEAR |

State lives in `~/.flowmint/` and survives restarts.

### Payment policy

Actions can carry a policy with `max_per_payment_atomic`, `max_total_atomic`,
`allowed_recipients`, `allowed_networks`, and approval thresholds. Every x402
payment is checked before signing. A rejected payment pauses the action and
adds a `security_blocked` receipt with the reasons; a payment requiring human
review is recorded as `warn` and remains gated.

### Live x402 / NEAR settlement adapter

FlowMint includes an optional PingPay facilitator adapter for the official
x402 v2 `quote` → origin-chain payment → `settle` flow. It never stores a
private key or submits an origin-chain transaction. Configure credentials only
through environment variables:

```bash
export FLOWMINT_PING_API_KEY="..."              # never commit this
export FLOWMINT_PING_FACILITATOR_URL="https://pay.pingpay.io/agentpay/x402"
flowmint facilitator-supported
flowmint x402-quote --body response-402.json --refund-to 0xYourRefundAddress
# send the quoted amount with your wallet, then:
flowmint x402-settle --body response-402.json \
  --operation-token "..." --deposit-address "0x..." --tx-hash "0x..."
```

The policy check must pass before `x402-quote`; the wallet or managed Agent API
performs the actual origin-chain payment. Settlement returns the NEAR Intents
transaction reference and can be attached to the FlowMint receipt.

---

## Architecture

- Local-first JSON storage + SHA-256 receipt chain  
- Optional NEAR anchor of the root hash  
- `type: payment` and `type: x402` are first-class  
- Zero telemetry, minimal deps (`pyyaml`)

---

## Roadmap

- [x] Durable core + human gates + receipts  
- [x] x402 challenge/confirm + offline demo  
- [x] Deterministic payment policy + prompt-injection block demo
- [x] PingPay x402 v2 quote/settle adapter (keyless transaction submission)
- [ ] Live `@x402/near` / official `x402` Python signing helper  
- [ ] Policy wallet contract (function-call key + limits)  
- [ ] NEAR Intents inside payment steps  
- [ ] On-chain action state for multi-agent handoff  

---

## License

MIT · Built for NEAR HACKATHON 2026
