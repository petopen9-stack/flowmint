# NearAction

> Durable, resumable agent workflows on NEAR  
> with human gates, verifiable receipts, **x402 micropayments**, and policy-ready spending.

**NEAR HACKATHON 2026** · Tracks: **Agent Economy** · **AI Security & Defense** · **Autonomous Business**

---

## 60-second demo (no network)

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
pip install -e .
nearaction demo
```

You will see: create → human gates → **x402 challenge (mock 402)** → payment confirm → receipt chain → NEAR anchor prep.

Full script: [DEMO.md](./DEMO.md)

---

## Why this exists

Agents that move money need three things:

1. **Durability** — multi-step work must survive restarts  
2. **Policy control** — the agent must not be able to drain funds  
3. **Standard rails** — [x402](https://x402.org) for HTTP micropayments, NEAR Intents for cross-chain settlement  

NearAction delivers (1) + (3) today and is structured for (2).

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
| Policy wallet stubs | ✅ foundation |

---

## CLI

```bash
nearaction create --file examples/x402-api-call.yaml
nearaction list
nearaction resume <id>
nearaction approve <id> --note "ok"
nearaction x402-challenge <id> --mock      # offline 402
nearaction x402-confirm <id> --note "paid"
nearaction history <id>
nearaction anchor <id> --account you.near
nearaction demo                            # full walkthrough
```

---

## x402 flow (agent micropayments)

1. Step with `type: x402` + target URL  
2. Agent requests URL → receives **HTTP 402**  
3. `nearaction x402-challenge` stores payment intent + receipt  
4. Status → `waiting_approval` (human or policy)  
5. Sign with limited key (`@x402/near`, policy wallet, …) and retry  
6. `nearaction x402-confirm` → step done, chain continues  

Example: `examples/x402-api-call.yaml`

NEAR is first-class in the x402 ecosystem. NearAction keeps the **workflow + audit trail** durable while signing stays with your runtime / policy wallet.

Resources from [nearbuilders.org/build](https://nearbuilders.org/build):
- NEAR Intents / Agent Connect  
- NEAR AI Cloud  
- Docs: [docs.near.org](https://docs.near.org) · [docs.near-intents.org](https://docs.near-intents.org)

---

## Install

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
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
| Demo | `nearaction demo` | full flow prints events including `x402_challenged` |
| History | `nearaction history <id>` | hash chain of receipts |
| Anchor | `nearaction anchor <id>` | `root_hash` prepared for NEAR |

State lives in `~/.nearaction/` and survives restarts.

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
- [ ] Live `@x402/near` / official `x402` Python signing helper  
- [ ] Policy wallet contract (function-call key + limits)  
- [ ] NEAR Intents inside payment steps  
- [ ] On-chain action state for multi-agent handoff  

---

## License

MIT · Built for NEAR HACKATHON 2026
