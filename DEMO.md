# Demo Script (≤ 90 seconds)

## Suggested flow

1. **0–10s** — Hook  
   “Most agents forget everything when they restart. NearAction keeps multi-step work (and money moves) alive.”

2. **10–25s** — Create  
   ```bash
   nearaction create --file examples/research-digest.yaml
   ```
   Show the new action ID.

3. **25–40s** — Resume + current step  
   ```bash
   nearaction resume <id>
   nearaction status <id>
   ```
   Highlight the current instruction.

4. **40–55s** — Human gate  
   Advance until `waiting_approval`, then:  
   ```bash
   nearaction approve <id> --note "approved"
   ```

5. **55–70s** — Receipt + anchor  
   ```bash
   nearaction history <id>
   nearaction anchor <id>
   ```
   Point at the hash chain and the prepared on-chain root.

6. **70–80s** — Close  
   “Durable workflows. Human gates. Verifiable receipts. Payment steps ready for policy wallets.  
   That’s NearAction for the agent economy on NEAR.”

---

## Caption for X

```
NearAction — durable agent workflows on NEAR.

Most agents die when the process restarts.
NearAction keeps multi-step work alive with:
• checkpoints & resume
• human approval gates
• hash-chained receipts
• first-class payment steps (policy wallet ready)

Built for #NEARHackathon

Repo: https://github.com/petopen9-stack/nearaction
```
