# CollectFlow AI — Recommended File Structure

This document defines the proposed monorepo layout and the order in which to implement it. Do not create every file on day one; build a working vertical slice and expand incrementally.

## 1. Repository layout

```text
collectflow-ai/
│
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── docs/
│   ├── PRD.md
│   ├── TRD.md
│   ├── FILE_STRUCTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── SECURITY.md
│   ├── AGENT_WORKFLOWS.md
│   └── MVP_ROADMAP.md
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs
│   │
│   ├── public/
│   │   └── images/
│   │
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   └── (dashboard)/
│   │   │       ├── layout.tsx
│   │   │       ├── dashboard/page.tsx
│   │   │       ├── invoices/page.tsx
│   │   │       ├── invoices/[id]/page.tsx
│   │   │       ├── customers/page.tsx
│   │   │       ├── collection-queue/page.tsx
│   │   │       ├── approvals/page.tsx
│   │   │       ├── commitments/page.tsx
│   │   │       ├── disputes/page.tsx
│   │   │       ├── imports/page.tsx
│   │   │       └── settings/page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   ├── dashboard/
│   │   │   ├── invoices/
│   │   │   ├── collections/
│   │   │   ├── approvals/
│   │   │   └── imports/
│   │   ├── features/
│   │   │   ├── invoices/
│   │   │   │   ├── api.ts
│   │   │   │   ├── schemas.ts
│   │   │   │   └── types.ts
│   │   │   ├── customers/
│   │   │   ├── collections/
│   │   │   ├── approvals/
│   │   │   ├── commitments/
│   │   │   └── disputes/
│   │   ├── lib/
│   │   │   ├── api-client.ts
│   │   │   ├── auth.ts
│   │   │   ├── format-currency.ts
│   │   │   ├── format-date.ts
│   │   │   └── utils.ts
│   │   └── hooks/
│   │
│   └── tests/
│       └── e2e/
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── dashboard.py
│   │   │           ├── imports.py
│   │   │           ├── customers.py
│   │   │           ├── invoices.py
│   │   │           ├── collections.py
│   │   │           ├── approvals.py
│   │   │           ├── messages.py
│   │   │           ├── commitments.py
│   │   │           ├── disputes.py
│   │   │           └── audit.py
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   ├── permissions.py
│   │   │   ├── exceptions.py
│   │   │   ├── logging.py
│   │   │   └── middleware.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── models/
│   │   │       ├── organization.py
│   │   │       ├── user.py
│   │   │       ├── customer.py
│   │   │       ├── invoice.py
│   │   │       ├── payment.py
│   │   │       ├── collection_case.py
│   │   │       ├── message.py
│   │   │       ├── commitment.py
│   │   │       ├── dispute.py
│   │   │       ├── approval.py
│   │   │       ├── agent_run.py
│   │   │       └── audit_event.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── customer.py
│   │   │   ├── invoice.py
│   │   │   ├── payment.py
│   │   │   ├── collection.py
│   │   │   ├── message.py
│   │   │   ├── commitment.py
│   │   │   ├── dispute.py
│   │   │   └── common.py
│   │   ├── repositories/
│   │   │   ├── customer_repository.py
│   │   │   ├── invoice_repository.py
│   │   │   ├── payment_repository.py
│   │   │   ├── message_repository.py
│   │   │   └── commitment_repository.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── import_service.py
│   │   │   ├── invoice_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── aging_service.py
│   │   │   ├── prioritization_service.py
│   │   │   ├── collection_service.py
│   │   │   ├── reminder_service.py
│   │   │   ├── approval_service.py
│   │   │   ├── commitment_service.py
│   │   │   ├── dispute_service.py
│   │   │   └── audit_service.py
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   ├── nodes.py
│   │   │   ├── routing.py
│   │   │   ├── policies.py
│   │   │   ├── tools.py
│   │   │   ├── prompts/
│   │   │   │   ├── reminder.py
│   │   │   │   └── classify_reply.py
│   │   │   ├── schemas/
│   │   │   │   ├── reminder.py
│   │   │   │   └── reply.py
│   │   │   └── evaluation/
│   │   │       ├── datasets/
│   │   │       └── evaluate.py
│   │   ├── integrations/
│   │   │   ├── llm/
│   │   │   │   ├── base.py
│   │   │   │   └── provider.py
│   │   │   ├── messaging/
│   │   │   │   ├── base.py
│   │   │   │   └── whatsapp.py
│   │   │   └── accounting/
│   │   │       └── base.py
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   ├── import_tasks.py
│   │   │   ├── followup_tasks.py
│   │   │   └── reconciliation_tasks.py
│   │   └── utils/
│   │       ├── dates.py
│   │       ├── money.py
│   │       └── idempotency.py
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       │   ├── test_aging.py
│       │   ├── test_prioritization.py
│       │   ├── test_payments.py
│       │   ├── test_imports.py
│       │   ├── test_commitments.py
│       │   └── test_agent_schemas.py
│       ├── integration/
│       │   ├── test_auth.py
│       │   ├── test_invoice_api.py
│       │   ├── test_approvals.py
│       │   └── test_tenant_isolation.py
│       └── fixtures/
│           ├── sample_ledger.csv
│           └── customer_replies.json
│
└── scripts/
    ├── seed_demo_data.py
    └── create_demo_user.py
```

## 2. What the main directories do

- `frontend/src/app/`: Route pages and layouts using the Next.js App Router.
- `frontend/src/components/`: Reusable UI components grouped by product area.
- `frontend/src/features/`: Frontend API calls, types and validation schemas for each feature.
- `backend/app/api/`: HTTP endpoints only; keep business logic out of route handlers.
- `backend/app/core/`: Authentication, permissions, middleware, errors and logging.
- `backend/app/db/`: SQLAlchemy models, sessions and database base configuration.
- `backend/app/schemas/`: Pydantic request and response schemas.
- `backend/app/repositories/`: Database query and persistence functions.
- `backend/app/services/`: Deterministic business logic, financial calculations and workflow policies.
- `backend/app/agent/`: LangGraph orchestration, prompts, tools, state and evaluations.
- `backend/app/integrations/`: External LLM, messaging and accounting provider adapters.
- `backend/app/workers/`: Asynchronous imports, scheduled follow-ups and later reconciliation tasks.
- `backend/tests/`: Unit, integration and fixture data.
- `docs/`: Product, technical, API, security and roadmap documentation.

## 3. Implement files in this order

Do not create every file at the beginning. Start with the smallest end-to-end path.

| Order | Files | Purpose |
|---|---|---|
| 1 | `backend/app/main.py`, `config.py` | Start FastAPI and load configuration |
| 2 | `backend/app/db/session.py`, `db/base.py` | Configure database access |
| 3 | `db/models/organization.py`, `customer.py`, `invoice.py` | Establish core schema |
| 4 | `schemas/invoice.py`, `services/import_service.py` | Import and validate ledgers |
| 5 | `services/aging_service.py`, `invoice_service.py` | Calculate balances and aging |
| 6 | `api/v1/endpoints/imports.py`, `invoices.py` | Expose core API routes |
| 7 | `services/prioritization_service.py` | Create collection queue |
| 8 | `agent/schemas/reminder.py`, `agent/prompts/reminder.py` | Define safe reminder generation |
| 9 | `services/reminder_service.py`, `services/approval_service.py` | Draft and approve reminders |
| 10 | `services/commitment_service.py`, `agent/schemas/reply.py` | Track commitments and classify replies |
| 11 | `frontend/src/app/(dashboard)/...` | Build usable dashboard |
| 12 | `tests/` | Validate calculations, authorization and workflows |

## 4. Environment configuration

Create `.env.example` at the repository root:

```dotenv
APP_ENV=development
APP_NAME=CollectFlow AI

DATABASE_URL=postgresql+psycopg://collectflow:change-me@localhost:5432/collectflow

AUTH_SECRET=replace-with-a-long-random-secret

LLM_PROVIDER=openai
LLM_API_KEY=
LLM_MODEL=

REDIS_URL=redis://localhost:6379/0

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

WHATSAPP_ENABLED=false
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=
WHATSAPP_APP_SECRET=
```

The exact provider configuration depends on the selected LLM and messaging integrations. Keep real credentials in local environment files or a secrets manager; never commit them to Git.

## 5. Local development commands

Suggested Makefile interface:

```makefile
.PHONY: dev test backend frontend migrate

dev:
	docker compose up --build

test:
	cd backend && pytest

frontend:
	cd frontend && npm run dev

backend:
	cd backend && uvicorn app.main:app --reload

migrate:
	cd backend && alembic upgrade head
```

Add the matching package scripts and Docker services before relying on these commands.

## 6. Implementation notes

- Keep monetary calculations in deterministic Python services, using `Decimal` and database `NUMERIC`.
- Treat the LLM as an untrusted language-processing component.
- Enforce organization-level authorization on every relevant operation.
- Do not implement live WhatsApp sending until approval, audit logging, idempotency, and webhook verification are tested.
- Start with CSV/XLSX import, invoice aging, prioritization, and draft approval. Add background workers only when the workflow requires them.
