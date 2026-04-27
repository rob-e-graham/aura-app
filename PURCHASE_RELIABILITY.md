# AURA — Purchase Reliability

How the app handles consumable top-ups (token packs and memory expansions)
without losing user money to network/server failures.

---

## The problem

Apple charges the user the moment a consumable purchase succeeds in
StoreKit. If the app then calls our server to credit the user's account
and the server is unreachable (network drop, server hiccup, server
deploy), the user has paid but received nothing. Without recovery this
results in:

- The user thinks they paid for nothing → 1-star reviews / chargebacks
- Apple's review team rejecting the app under guideline 3.1.1
- Lost trust

## The architecture

```
┌─────────────┐      Apple charges user       ┌─────────────┐
│  iOS app    │ ────────────────────────────> │   Apple     │
│             │                                │  StoreKit   │
│             │ <──────────────────────────── │             │
│             │   transactionIdentifier       └─────────────┘
│             │
│             │      POST /api/tokens/topup
│             │      { amount, transactionId, productId }
│             │ ────────────────────────────> ┌─────────────┐
│             │                                │  AURA       │
│             │ ←─── { ok: true,               │  server     │
│             │       bonus_tokens: N }        │             │
│             │                                │ - validates │
│             │                                │   receipt   │
│             │                                │   via RC    │
│             │                                │ - dedupes   │
│             │                                │   on tx ID  │
│             │                                │ - credits   │
│             │                                │   account   │
│             │                                └─────────────┘
└─────────────┘
       │
       │   If server call FAILS at any stage
       │
       v
┌─────────────────────────────────────────────────┐
│  localStorage["aura.pending_topups_v1"]         │
│  [                                               │
│    {                                             │
│      id, kind, amount,                           │
│      transactionId,    ← Apple's tx ID           │
│      productId,                                  │
│      attemptCount, lastAttempt, createdAt        │
│    }                                             │
│  ]                                               │
└─────────────────────────────────────────────────┘
       │
       │   Retried automatically:
       │   - On every app launch (4s after boot)
       │   - On every successful syncEntitlementsFromServer()
       │   - On user tap of "Retry now" in Settings
       v
   Server credits account, returns confirmed bonus_tokens.
   Local UI updates from server response. Entry removed from queue.
```

## What the iOS app guarantees

After a successful StoreKit purchase, the app **never silently credits
locally**. Either the server confirms the credit (and the local balance
updates from the server's authoritative response), or the entry sits in
the pending queue with the Apple `transactionIdentifier` until the
server can confirm.

The user sees a clear UI state in Settings: an amber "Purchase pending"
card with a "Retry now" button. The retry runs automatically every app
launch and every server sync; the manual button is just for impatient
users.

If the queue grows to 50 failed attempts on the same entry, it's dropped
to prevent infinite loops. At that point the user should contact support —
the entry is logged in localStorage and recoverable from device storage.

## What the SERVER must do

The two endpoints are `POST /api/tokens/topup` and `POST /api/memory/topup`.
Both receive:

```json
{
    "amount": 25000,                        // how many tokens / memory slots
    "transactionId": "2000000123456789",    // Apple's transaction identifier
    "productId": "tokens_25k_pack"          // the product identifier
}
```

Plus the `Authorization: Bearer <jwt>` header for the user's account.

### Required server behaviours

**1. Idempotency on `transactionId`**

The same `transactionId` MUST never credit the user twice. Implementation:

```sql
CREATE TABLE topup_transactions (
    transaction_id TEXT PRIMARY KEY,        -- Apple's tx ID
    user_id UUID NOT NULL REFERENCES users(id),
    kind TEXT NOT NULL CHECK (kind IN ('tokens', 'memory')),
    amount INTEGER NOT NULL,
    product_id TEXT,
    credited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Endpoint logic:

```
INSERT INTO topup_transactions (transaction_id, user_id, kind, amount, product_id)
VALUES (...)
ON CONFLICT (transaction_id) DO NOTHING
RETURNING credited_at;
```

If the INSERT happened: credit the user.
If the INSERT was skipped (already credited): return the current balance
WITHOUT crediting again. Both cases return `{ ok: true, bonus_tokens: N }`.

This makes the endpoint safely retriable — the client can call it 100
times for the same transaction and the user only gets credited once.

**2. Receipt validation (recommended)**

In production, you should verify that `transactionId` corresponds to a
real Apple purchase before crediting. Two options:

- **RevenueCat REST API**: Call `GET /v1/subscribers/{user_id}/transactions/{transaction_id}` and confirm the transaction exists and belongs to the user.
- **RevenueCat webhook**: Subscribe to `INITIAL_PURCHASE` and `NON_RENEWING_PURCHASE` events. Maintain a pending-credits table; the client topup call only credits if the webhook has already fired for that transactionId.

Either works. The webhook approach is more robust against client tampering — a malicious client can't fabricate a `transactionId` and get free tokens, because the server only credits transactions it has received via webhook.

For TestFlight beta this can wait, but **before App Store launch**
receipt validation should be in place. Otherwise a determined attacker
can pull tokens for free by replaying the topup endpoint with random
transaction IDs (since you only check that your `topup_transactions`
table doesn't have one yet — and any new-to-you ID would pass that).

**3. Response shape**

```json
{
    "ok": true,
    "bonus_tokens": 25000,        // for /api/tokens/topup
    // OR
    "storage_bonus": 100          // for /api/memory/topup
}
```

The client uses these as the new authoritative balance — don't omit them
on the response (otherwise the client falls back to whatever it had).

**4. Auth check**

Reject the call with 401 if the JWT is missing or invalid. The client
won't retry indefinitely against a bad auth state.

### Required server behaviour for `/api/account/state`

Already implemented correctly per `syncEntitlementsFromServer()`:

```json
{
    "ok": true,
    "tier": "premium" | "pro" | "free",
    "usage": {
        "monthly_allowance": 1000000,
        "monthly_used": 12345,
        "bonus_tokens": 25000,        // ← top-up survivors live here
        "period_start": "2026-04-01T00:00:00Z",
        "storage_limit": 200,
        "storage_used": 18,
        "storage_bonus": 100          // ← top-up survivors live here
    }
}
```

When a user reinstalls / switches devices, the client calls this on
sign-in and the server returns the truth. As long as the server has
correctly recorded purchases (via the topup endpoints + idempotency
table), the user's bonus tokens and memory follow them everywhere.

## Edge cases handled

| Scenario | What happens |
|---|---|
| User buys, server returns 200 | Tokens added, queue not used |
| User buys, network drops | Entry queued, retries on launch + sync |
| User buys, server returns 500 | Entry queued, retries on launch + sync |
| User force-quits during purchase | RC plugin completes the transaction in the background; on next launch RC has the entitlement, but the topup endpoint hasn't been called yet → caught by `restorePurchases` flow + by RC webhook to server (if configured) |
| User reinstalls app | Pending queue is in localStorage on the *device*. If they reinstall, the queue is gone, but the server has the truth via syncEntitlementsFromServer (assuming the original credit landed). If it never landed and the device is wiped, the only recovery is RC webhook + server-side reconciliation. **This is why receipt validation matters before launch.** |
| User switches devices | Same as reinstall. Server is authoritative; sync pulls correct balance. |
| User retries a successful purchase via "Retry now" | Idempotency on transactionId means server returns the same balance, no double-credit. |
| Same transactionId queued twice | Client `queuePendingTopUp` deduplicates by transactionId before saving |

## Testing checklist

Before TestFlight beta:

- [ ] In Xcode, configure the StoreKit configuration file with sandbox products matching your RC product IDs
- [ ] Buy a token pack with airplane mode ON → verify "Purchase pending" appears in Settings
- [ ] Turn airplane mode OFF → wait or tap "Retry now" → verify tokens credited
- [ ] Force-quit during purchase → verify the transaction completes on next launch
- [ ] Verify `topup_transactions` table on server is recording transactionIds
- [ ] Verify hitting `/api/tokens/topup` twice with same transactionId only credits once

Before App Store launch:

- [ ] Implement RC webhook → topup_transactions table reconciliation
- [ ] Add server-side receipt validation that rejects unknown transactionIds
- [ ] Add a small admin endpoint to manually credit a user from a transactionId (for support tickets)
- [ ] Set up alerting for any topup endpoint 5xx response

---

*This doc is the contract between the iOS app and the AURA server. Update
it whenever the topup flow changes.*
