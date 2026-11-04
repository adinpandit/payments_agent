# CollectFlow AI — Technical Requirements Document (TRD)

**Version:** 1.0  
**Status:** MVP technical specification  
**Architecture:** Modular monolith  
**Proposed stack:** Next.js, TypeScript, FastAPI, PostgreSQL, SQLAlchemy, Alembic, LangGraph, Docker

## 1. Technical Overview

CollectFlow AI will use a modular monolith architecture for the MVP. This keeps the application simple enough for a solo developer while separating business logic into components that can evolve independently.

### Technology decisions

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js App Router | Dashboard, tables, forms and review queues |
| Language | TypeScript | Frontend type safety |
| Styling | Tailwind CSS | Responsive interface |
| Backend | Python and FastAPI | REST API and business logic |
| Validation | Pydantic | Request, response and configuration validation |
| Database | PostgreSQL | Invoices, customers, commitments and events |
| ORM and migrations | SQLAlchemy 2.x and Alembic | Database access and schema evolution |
| AI orchestration | LangGraph | Controlled, stateful agent workflows |
| LLM | Provider-independent adapter | Structured reply classification and reminder drafting |
| Background jobs | Celery with Redis | Scheduled follow-ups and asynchronous processing |
| File parsing | pandas and openpyxl | CSV and XLSX import |
| Testing | pytest and Vitest | Backend and frontend tests |
| Deployment | Docker and Docker Compose | Reproducible local development and deployment |

**MVP simplification:** Redis and Celery can be introduced when background scheduling is needed. For a very small prototype, a database-backed job runner can reduce operational complexity. Do not run business-critical scheduled jobs solely in an unreliable in-process timer.

## 2. System Architecture

```text
                 Next.js Web Application
                          |
                          | HTTPS / JSON
                          v
                    FastAPI Backend
                          |
          +---------------+----------------+
          |               |                |
          v               v                v
    Invoice Service  Agent Service   Authentication
          |               |                |
          +---------------+----------------+
                          |
                          v
                     PostgreSQL
                          |
              +-----------+-----------+
              |                       |
              v                       v
        Background Jobs          Audit Events
              |
              v
       Follow-up Scheduler

    Agent Service
          |
          +---- Rule-based prioritization
          |
          +---- LLM adapter
          |
          +---- Approval and policy checks
          |
          +---- Messaging adapter (later)
```

The AI agent does not receive unrestricted database or messaging access. It invokes narrowly defined application tools that enforce authorization, validate inputs, and record important actions.

## 3. Backend Module Responsibilities

### API layer

Responsible for HTTP routes, authentication dependencies, request validation, response serialization, status codes, pagination and filtering.

The API layer should not contain large business workflows or raw LLM prompts.

### Service layer

Responsible for invoice import, invoice aging, outstanding balance calculations, customer summaries, reminder creation, commitment tracking, dispute handling, approval and sending policies.

### Repository and database layer

Responsible for persistence and queries. Use SQLAlchemy models for database entities and explicit service methods for operations. Avoid allowing LLM outputs to directly construct arbitrary database updates.

### Agent layer

Responsible for building structured context, calling the LLM, validating structured outputs, classifying customer replies, selecting approved next actions, maintaining workflow state, and requesting human intervention.

The agent orchestrates application services; it does not replace them.

## 4. Database Design

Use PostgreSQL as the source of truth.

### Core tables

**organizations**
- `id`: UUID primary key
- `name`
- `timezone`
- `created_at`
- `updated_at`

**users**
- `id`: UUID primary key
- `email`: unique login identifier
- `password_hash` or external identity reference
- `created_at`

**organization_memberships**
- `organization_id`
- `user_id`
- `role`: owner or accountant
- `created_at`

**customers**
- `id`
- `organization_id`
- `name`
- `email`, nullable
- `phone`, nullable
- `external_reference`, nullable
- `created_at`
- `updated_at`

**invoices**
- `id`
- `organization_id`
- `customer_id`
- `invoice_number`
- `invoice_date`
- `due_date`
- `currency`
- `total_amount`
- `status`
- `created_at`
- `updated_at`

**payments**
- `id`
- `organization_id`
- `customer_id`
- `amount`
- `currency`
- `payment_date`
- `external_reference`, nullable
- `source`
- `created_at`

**payment_allocations**
- `id`
- `organization_id`
- `payment_id`
- `invoice_id`
- `allocated_amount`
- `created_at`

**collection_cases**
- `id`
- `organization_id`
- `invoice_id`
- `priority`
- `status`
- `next_action_at`, nullable
- `created_at`
- `updated_at`

**messages**
- `id`
- `organization_id`
- `customer_id`
- `invoice_id`, nullable
- `direction`
- `channel`
- `body`
- `status`
- `provider_message_id`, nullable
- `created_at`

**payment_commitments**
- `id`
- `organization_id`
- `invoice_id`
- `source_message_id`, nullable
- `promised_date`
- `promised_amount`, nullable
- `status`
- `confidence`, nullable
- `created_at`
- `updated_at`

**disputes**
- `id`
- `organization_id`
- `invoice_id`
- `source_message_id`, nullable
- `category`
- `description`
- `status`
- `assigned_to`, nullable
- `created_at`
- `updated_at`

**approval_requests**
- `id`
- `organization_id`
- `message_id`
- `requested_by`
- `reviewed_by`, nullable
- `status`
- `reviewed_at`, nullable
- `created_at`

**agent_runs**
- `id`
- `organization_id`
- `workflow_type`
- `status`
- `input_reference`
- `output_summary`, nullable
- `error_code`, nullable
- `started_at`
- `completed_at`, nullable

**audit_events**
- `id`
- `organization_id`
- `actor_type`
- `actor_id`, nullable
- `event_type`
- `entity_type`
- `entity_id`
- `metadata`
- `created_at`

### Data integrity rules

1. Use UUIDs for externally referenced records.
2. Store currency as an explicit ISO currency code.
3. Store monetary amounts using `NUMERIC`, never floating-point types.
4. Store timestamps as timezone-aware values and configure each organization's timezone.
5. Use foreign keys and appropriate unique constraints.
6. Scope queries to the authenticated organization.
7. Keep invoice amounts and payment allocations separate.
8. Derive outstanding balances from invoice amounts, credits where supported, and payment allocations rather than relying on AI-generated values.
9. Wrap payment allocation and balance-sensitive updates in database transactions.
10. Add indexes on organization ID, invoice due date, customer ID, status, and scheduled action time.

**Accounting distinction:** An invoice's original amount is not the same as its outstanding balance. Model payments and allocations explicitly so that partial payments are supported.

## 5. Invoice Aging and Priority Logic

### Aging calculation

For a given business-local date:

`days_overdue = max(0, business_date - due_date)`

Compute this using date values and the configured timezone. An invoice is overdue only when its due date is before the business-local date and its outstanding balance is greater than zero.

### Initial priority algorithm

Use an explainable rules engine. For example:

- Base score from days overdue
- Additional weight for large outstanding balances
- Additional weight for a missed payment commitment
- Additional weight for repeated delays, if reliable history exists
- Separate exception status for open disputes

Do not allow an open dispute to trigger an aggressive automated reminder. Route it for review instead.

The score is a queue-ordering aid, not a creditworthiness or default probability score.

## 6. Agent Workflow

Use a bounded LangGraph workflow.

### Workflow A — Generate a reminder

1. Receive an invoice or collection-case ID.
2. Authenticate the user and verify organization access.
3. Retrieve invoice, customer, outstanding balance and previous interactions.
4. Apply deterministic eligibility rules.
5. Build a minimal, structured LLM context.
6. Generate a reminder draft.
7. Validate output against a Pydantic schema.
8. Check for prohibited or unsupported claims.
9. Store the draft and create an approval request.
10. Wait for a human to approve, edit or reject the draft.

The workflow must not bypass approval.

### Workflow B — Process a customer reply

1. Receive a manually entered reply or verified provider webhook.
2. Validate the source and resolve the relevant customer or invoice.
3. Store the incoming message.
4. Classify the message using structured LLM output.
5. Validate extracted dates and amounts.
6. Save the classification and supporting message reference.
7. If a promise is identified, create a proposed commitment.
8. If a dispute or negotiation is identified, create a review task.
9. If confidence is low or the invoice is ambiguous, request human review.
10. Record the workflow result in the audit log.

### Example structured output schema

```python
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

class ReplyClassification(BaseModel):
    category: Literal[
        "payment_promised",
        "payment_completed",
        "invoice_dispute",
        "payment_delayed",
        "invoice_copy_requested",
        "clarification_requested",
        "negotiation_requested",
        "other",
    ]
    promised_date: date | None = None
    promised_amount: Decimal | None = None
    confidence: float = Field(ge=0, le=1)
    explanation: str
    requires_human_review: bool
```

Validate the classification against invoice context. A claimed payment date must not automatically mark an invoice as paid.

## 7. REST API Design

Prefix all endpoints with `/api/v1`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate a user |
| GET | `/dashboard/summary` | Retrieve dashboard metrics |
| POST | `/imports` | Create an import job |
| GET | `/imports/{id}` | Retrieve import status |
| GET | `/customers` | List customers |
| GET | `/invoices` | Filter and paginate invoices |
| GET | `/invoices/{id}` | Retrieve invoice details |
| GET | `/collection-cases` | Retrieve prioritized collection queue |
| POST | `/invoices/{id}/reminders/draft` | Generate a reminder draft |
| GET | `/approvals` | List pending approvals |
| POST | `/approvals/{id}/approve` | Approve a draft |
| POST | `/approvals/{id}/reject` | Reject a draft |
| POST | `/messages/manual-log` | Record manually sent communication |
| POST | `/messages/inbound` | Record a manually entered reply |
| GET | `/commitments` | List payment commitments |
| POST | `/commitments` | Create or confirm a commitment |
| PATCH | `/commitments/{id}` | Update commitment status |
| GET | `/disputes` | List unresolved disputes |
| PATCH | `/disputes/{id}` | Update dispute status |
| GET | `/audit-events` | Retrieve audit history |
| GET | `/health` | Application health check |

Use consistent error responses and pagination.

Example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The due date is required.",
    "details": {
      "field": "due_date"
    }
  }
}
```

The approval endpoint must verify the user's role and that the draft is still eligible for approval. Later messaging endpoints must use idempotency controls and provider delivery tracking.

## 8. Security and Privacy Requirements

- Use a well-maintained authentication library or identity provider.
- Never store plaintext passwords.
- Enforce authorization on the server, not just in the frontend.
- Scope all business data by organization.
- Validate uploaded file types, size, row counts and contents.
- Reject spreadsheet formulas as executable content; treat imported values as untrusted data.
- Keep API keys in environment-based secrets or a secrets manager.
- Do not expose LLM provider keys to the browser.
- Redact sensitive fields from logs.
- Minimize customer information sent to external LLM providers.
- Define retention and deletion procedures.
- Verify webhook signatures before processing inbound messages.
- Protect against prompt injection in customer replies.
- Require explicit approval before sending customer-facing messages.
- Maintain backups and periodically test restoration.

For an Indian business deployment, review applicable Indian privacy and data-protection requirements, contractual obligations, and messaging-provider policies before onboarding live customer data.

## 9. Testing Strategy

### Unit tests

Test invoice aging, outstanding balance calculations, partial payment allocation, priority scoring, CSV/XLSX validation, reminder eligibility, reply schema validation, commitment status transitions, and approval authorization.

### Integration tests

Test API routes with a test database, import persistence and duplicate detection, organization isolation, agent output validation, approval/rejection flows, database transaction behavior, and background job retries.

### End-to-end tests

1. Upload a ledger.
2. View overdue invoices.
3. Generate a reminder.
4. Approve the reminder.
5. Record a customer reply.
6. Create a payment commitment.
7. Trigger a missed-commitment alert.
8. Verify the audit history.

### AI evaluation tests

Maintain representative customer replies covering clear promises, ambiguous dates, partial-payment offers, disputes, discount requests, multiple invoices, irrelevant messages, and prompt-injection attempts.

Measure classification accuracy, date extraction accuracy, unsupported claims, and correct human-review routing.

## 10. Deployment and Operations

Local development should use Docker Compose for the frontend, backend, PostgreSQL, and any required job infrastructure.

Production should include:

- HTTPS and secure environment configuration
- Managed PostgreSQL or properly backed-up PostgreSQL
- Database migrations during controlled deployments
- Health and readiness checks
- Centralized error reporting
- Scheduled-job monitoring
- Backup and restoration procedures
- AI token and cost monitoring
- Import and webhook failure monitoring

Use separate development, staging, and production environments. Never test autonomous messaging against real customers without explicit authorization and suitable safeguards.
