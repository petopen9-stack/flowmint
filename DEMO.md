# FlowMint — Demo (offline, ~90 detik)

Tidak butuh network, testnet, atau API key. Cocok untuk rekaman & judge review.

## Satu perintah

```bash
git clone https://github.com/petopen9-stack/flowmint.git
cd flowmint
pip install -e .
flowmint demo
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

## Security segment

Jalankan setelah demo utama:

```bash
flowmint security-demo
```

Output yang harus terlihat:

```text
Decision: BLOCK
Funds sent: 0
Audit receipt: security_blocked
```

Segmen ini adalah simulasi prompt injection. Jelaskan di video bahwa demo
offline memakai mock payment proof; adapter PingPay live tersedia untuk quote
dan settlement report, tetapi private key dan transaksi origin-chain tetap
berada di wallet atau Agent API pengguna.

## Manual step-by-step (untuk video)

```bash
pip install -e .

# 1. Create
flowmint create --file examples/x402-api-call.yaml
# catat action_id, mis. a1b2c3d4

# 2. Maju sampai step x402
flowmint resume <id>
flowmint approve <id> --note "free sources ok"
flowmint resume <id>
flowmint approve <id> --note "yes, pay for premium"

# 3. Simulasi 402 dari API
flowmint resume <id>
flowmint x402-challenge <id> --mock

# 4. Policy / human approve + confirm payment
flowmint x402-confirm <id> --note "signed with limited key" --proof '{"tx":"demo-tx"}'

# 5. Selesai + audit
flowmint status <id>
flowmint history <id>
flowmint anchor <id> --account youraccount.near
```

## Caption X (copy-paste)

```
FlowMint — durable agent workflows + x402 on NEAR.

Agents that can pay need more than a wallet:
• checkpoints that survive restarts
• human / policy gates before money moves
• hash-chained receipts
• native x402 (HTTP 402 → sign → retry)
• prompt-injection defense (malicious payment → BLOCKED)

Offline demo in one command:
flowmint demo

Repo: https://github.com/petopen9-stack/flowmint
#NEARHackathon @NEARProtocol

Demo note: the recorded flow is offline/mock; FlowMint also includes an
optional PingPay x402 quote/settle adapter that never stores private keys.
```

## Tips rekaman
- Font terminal besar, tema gelap
- Jalankan `flowmint demo` sekali full, lalu potong highlight
- Jalankan `flowmint security-demo` dan sisipkan setelah payment flow
- Tunjukkan baris `x402_challenged` di `history`
- Tunjukkan `security_blocked` dan `Funds sent: 0`
- Sebut: “This recording uses a mock payment proof. Real signing stays in a wallet or policy-bound Agent API; FlowMint keeps the workflow durable and auditable.”
