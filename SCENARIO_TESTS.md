# Sendible Connector — Scenario Tests (PST)

**Standard:** SCENARIO_TESTING_STANDARD.md  
**Status:** Initial Verification Matrix Prepared  
**Last Run:** 2026-09-07  

## Step 1: Personas
- **SMM Manager (Elena):** Manages 12 social profiles, schedules 35 weekly posts, monitors Priority Inbox.
- **Content Director (Sergey):** Approves cross-network campaigns, reviews delivery errors and account health.
- **Security & Workspace Admin (Alexander):** Owns BYOC tokens, reviews API scopes, verifies zero secret leakage.

## Step 2: Test Data Matrix (Equivalence Partitioning)
| Class | Parameters | Purpose |
|---|---|---|
| **Typical (Happy)** | 3 profiles, standard UTF-8 text (200 chars), valid schedule ISO string | Basic message scheduling |
| **Boundary Minimum** | Empty profile list / 0 scheduled messages | Verify empty state & validation errors |
| **Boundary Maximum** | 50 profiles in one call, 2000-char text | Check vendor limits & pagination |
| **Invalid** | Malformed date string, missing access_token | Verify 400 Bad Request & error mapping |
| **Exotic / Escape** | Emojis, quotes, newlines, multilingual text | Escaping & JSON payload safety |

## Step 3: Scenarios (Given-When-Then)
1. **Happy Path:** Connect account -> `list_profiles` -> `create_message` -> `list_messages(status='scheduled')` -> `delete_message`.
2. **Missing/Error Path:** `create_message` with invalid profile_id -> graceful upstream error with clear code.
3. **Blocked State:** `delete_message` on already deleted message -> idempotency check & not found handling.
4. **Recovery Path:** Network timeout during `list_activities` -> exponential backoff without crash.
5. **Adversarial / Soap-Opera:** Fast double-click on `create_message` -> prevent duplicate posts if supported.

## Step 4: Part D Validation Log
- **D1 (Deploy Verification):** Pending live credentials for end-to-end publish test.
- **D2 (Idempotency):** Verify message deduplication and safe deletes.
- **D3 (Security & Secret Leaks):** Authorization headers masked in all logs and ActionResult returns.
- **D4 (Regression Grep):** No C30 email residuals (`subscriber`, `campaign`, `audience_health`).
