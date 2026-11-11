# NearAction — Demo (offline, ~60–90 detik)

Tidak butuh network, testnet, atau API key. Cocok untuk rekaman & judge review.

## Satu perintah

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
pip install -e .
nearaction demo
```

Atau:

```bash
bash scripts/run_demo.sh
```

Output yang diharapkan:
1. Action dibuat (dengan step `type: x402`)
2. Step non-payment dijalankan + human gate di-approve
3. **x402 challenge** (mock 402) → payment intent muncul
4. Payment di-confirm (simulasi sign + retry)
5. Receipt chain menampilkan `x402_challenged` → `step_completed` → `completed`
6. Anchor root hash disiapkan untuk NEAR

## Manual step-by-step (untuk video)

```bash
pip install -e .

# 1. Create
nearaction create --file examples/x402-api-call.yaml
# catat action_id, mis. a1b2c3d4

# 2. Maju sampai step x402
nearaction resume <id>
nearaction approve <id> --note "free sources ok"
nearaction resume <id>
nearaction approve <id> --note "yes, pay for premium"

# 3. Simulasi 402 dari API
nearaction resume <id>
nearaction x402-challenge <id> --mock

# 4. Policy / human approve + confirm payment
nearaction x402-confirm <id> --note "signed with limited key" --proof '{"tx":"demo-tx"}'

# 5. Selesai + audit
nearaction status <id>
nearaction history <id>
nearaction anchor <id> --account youraccount.near
```

## Caption X (copy-paste)

```
NearAction — durable agent workflows + x402 on NEAR.

Agents that can pay need more than a wallet:
• checkpoints that survive restarts
• human / policy gates before money moves
• hash-chained receipts
• native x402 (HTTP 402 → sign → retry)

Offline demo in one command:
nearaction demo

Repo: https://github.com/petopen9-stack/nearaction
#NEARHackathon @NEARProtocol
```

## Tips rekaman
- Font terminal besar, tema gelap
- Jalankan `nearaction demo` sekali full, lalu potong highlight
- Tunjukkan baris `x402_challenged` di `history`
- Sebut: “real signing plugs into @x402/near or a policy wallet; NearAction keeps the workflow durable and auditable”
