# CollectFlow AI — Product Requirements Document (PRD)

**Version:** 1.0  
**Status:** MVP specification  
**Product category:** AI-powered accounts receivable and collections automation  
**Initial market:** Small Indian B2B distributors and suppliers  
**Target build time:** 30 days

## 1. Executive Summary

CollectFlow AI is an AI-powered receivables operations agent that helps small and medium-sized Indian B2B businesses collect outstanding payments more systematically.

The product imports invoice data from Excel or CSV, identifies overdue payments, prioritizes collection work, drafts personalized payment reminders, interprets customer replies, tracks payment commitments, and escalates disputes to a human employee.

Unlike a conventional invoice dashboard, CollectFlow AI manages the workflow associated with each outstanding invoice.

**Product vision:** Become the receivables operations layer for small B2B businesses that currently depend on spreadsheets, accounting exports, phone calls, and WhatsApp conversations to collect payments.

**Core value proposition:** Know who owes you money, what to do next, and which customers need your attention—without manually tracking every invoice.

## 2. Problem Statement

Small B2B distributors often sell goods on credit. Their accounts employees must track outstanding invoices, send reminders, record customer responses, remember promised payment dates, and resolve invoice disputes.

These processes are frequently fragmented across spreadsheets, accounting software, messaging applications, and manual notes. This creates several problems:

- Overdue invoices are overlooked.
- Collection priorities are unclear.
- Employees repeatedly send generic reminders.
- Customer payment promises are forgotten.
- Invoice disputes are not escalated promptly.
- Owners lack visibility into collection activity.

CollectFlow AI aims to centralize these workflows without requiring businesses to replace their existing accounting software.

## 3. Target Customers

### Initial ideal customer profile

Small Indian B2B distributors and suppliers that:

- Maintain approximately 50–1,000 active customer invoices.
- Offer credit terms to business customers.
- Track receivables using Excel, accounting exports, or a combination of tools.
- Use WhatsApp, email, or telephone calls for collections.
- Have an owner, accountant, or small accounts team responsible for follow-ups.

Potential initial verticals include electrical goods wholesalers, industrial suppliers, packaging distributors, and other businesses selling goods on credit. These are target hypotheses to validate through customer interviews, not assumptions about proven demand.

### Primary user personas

- **Business owner:** Wants to know how much money is overdue, which customers are delaying payments, and where intervention is necessary.
- **Accounts employee:** Needs a daily collection queue, accurate invoice details, ready-to-send reminders, and a way to track customer commitments.
- **Accounts manager:** Needs oversight of collection performance, disputed invoices, missed promises, and employee activity.

## 4. Product Goals and Non-Goals

### MVP goals

1. Import invoice ledgers reliably.
2. Calculate outstanding balances and invoice aging.
3. Prioritize invoices requiring follow-up.
4. Generate personalized payment reminder drafts.
5. Classify customer responses into actionable categories.
6. Track promised payment dates and missed commitments.
7. Require human approval for outbound communications.
8. Maintain an auditable history of agent decisions and actions.

### Non-goals

The initial release will not:

- Replace accounting or ERP software.
- Initiate bank transfers or collect money on behalf of customers.
- Automatically grant discounts or alter invoice terms.
- Make legally binding decisions or issue legal notices.
- Provide autonomous, unrestricted messaging.
- Attempt to predict payment defaults using a large custom ML model.
- Depend on vector databases or a complex RAG architecture.

## 5. User Stories

| ID | User story | Priority |
|---|---|---|
| US-01 | As an owner, I want to upload an invoice ledger so that my outstanding receivables are visible. | P0 |
| US-02 | As an accountant, I want to see overdue invoices sorted by urgency. | P0 |
| US-03 | As an accountant, I want personalized reminder drafts for each customer. | P0 |
| US-04 | As an accountant, I want to approve or reject messages before sending. | P0 |
| US-05 | As an accountant, I want to record customer payment promises. | P0 |
| US-06 | As an owner, I want disputes and missed promises flagged for intervention. | P0 |
| US-07 | As an accountant, I want to classify incoming customer replies. | P0 |
| US-08 | As an owner, I want to see collection activity and outstanding balances. | P0 |
| US-09 | As an accountant, I want to send messages through an approved messaging integration. | P1 |
| US-10 | As an accountant, I want payments reconciled against invoices automatically. | P2 |

P0 means essential for the MVP, P1 means the next increment, and P2 means a later release.

## 6. Functional Requirements

### FR-01: Authentication and organization management

- Users can register and sign in.
- Each business operates within its own organization.
- Users can access only their organization's data.
- Initial roles: Owner and Accountant.
- The system records the actor responsible for important actions.

**Acceptance criteria:** A user from Organization A cannot access invoices belonging to Organization B, including through direct API requests.

### FR-02: Invoice ledger import

Support CSV and XLSX imports.

**Required fields:**

- Invoice number
- Customer name
- Invoice date
- Due date
- Invoice amount
- Outstanding amount or sufficient information to calculate it
- Currency

**Optional fields:**

- Customer contact name
- Customer email
- Customer phone number
- Payment terms
- Invoice status
- Customer identifier

**Import workflow:**

1. Upload a file.
2. Parse its headers and rows.
3. Map spreadsheet columns to application fields.
4. Validate required fields and data types.
5. Display errors and a preview.
6. Confirm the import.
7. Store valid records and report skipped rows.

Duplicate invoices should be detected using a business-defined identity, such as organization, invoice number, and customer. Re-imports must not silently duplicate records.

**Acceptance criteria:** Invalid rows are reported with row numbers and actionable error messages. Existing invoices are not overwritten without a defined update policy.

### FR-03: Invoice aging and dashboard

Display:

- Total outstanding balance
- Total overdue balance
- Number of overdue invoices
- Invoices due soon
- Outstanding amounts by customer
- Unresolved disputes
- Upcoming and missed payment commitments

Use aging buckets such as:

- Not yet due
- 1–30 days overdue
- 31–60 days overdue
- 61–90 days overdue
- More than 90 days overdue

Aging is calculated using the due date and the business's configured timezone.

Outstanding balances must come from invoice and payment records, not from an LLM-generated calculation.

### FR-04: Collection prioritization

The system creates a daily collection queue based on:

- Days overdue
- Outstanding amount
- Previous missed commitments
- Open disputes
- Existing follow-up status
- Upcoming payment commitments

The first release uses deterministic, explainable rules. An LLM may summarize the reason for a recommendation, but it does not determine the underlying invoice balance or override financial rules.

Example: “High priority: ₹85,000 is 42 days overdue, and the customer missed a recorded payment commitment.”

The user must be able to inspect why an invoice received its priority.

### FR-05: AI reminder generation

Generate customer-specific drafts containing:

- Customer name
- Invoice number
- Outstanding amount
- Due date
- Days overdue, where relevant
- A polite request for a payment update
- An appropriate business tone

Supported tones: Polite, Professional, Firm.

Rules:

- The agent may use only verified invoice data.
- Missing information must not be invented.
- Discounts, penalties, legal threats, and changed payment terms must not be fabricated.
- Every outbound message requires explicit human approval in the MVP.

### FR-06: Customer reply classification

Classify incoming messages into:

1. Payment promised
2. Payment completed
3. Invoice dispute
4. Payment delayed
5. Request for invoice copy
6. Request for clarification
7. Discount or negotiation request
8. Other or uncertain

The structured response should include classification, confidence score, extracted payment date and amount if present, a short explanation, and recommended next action.

If a message is ambiguous, the system must request human review rather than assume a payment date or amount.

### FR-07: Payment commitment tracking

Each commitment contains invoice, customer, promised payment date, promised amount if stated, source message, status, creation timestamp, and review history.

Statuses: `pending`, `fulfilled`, `missed`, `cancelled`, `superseded`.

When a promised date passes without a corresponding payment record, flag the commitment for review. A promise to pay is not proof of payment. Mark a commitment fulfilled only when supported by a recorded or reconciled payment.

### FR-08: Dispute management

Disputes include incorrect invoice amounts, goods not received, missing credit notes, duplicate invoices, incorrect due dates, and discount requests.

The system must not change an invoice amount, issue a credit note, or approve a discount autonomously.

### FR-09: Messaging integration

**MVP:**

- Generate and approve drafts.
- Copy messages for manual sending.
- Record the intended recipient and action in the activity log.

**Next stage:**

- Integrate the official WhatsApp Business Platform or an approved provider.
- Record provider message identifiers and delivery status.
- Receive replies through verified webhooks.
- Prevent duplicate sends and process repeated webhook deliveries safely.

Use appropriate customer consent, messaging policies, and applicable privacy requirements.

### FR-10: Activity log and audit trail

Record significant events including ledger import, invoice update, reminder generation, message approval/rejection/sending, customer reply, commitment recording, dispute creation, and agent failure.

Audit events should include organization, actor or system identity, timestamp, action, relevant record identifier, and safe metadata. Sensitive information should not be copied indiscriminately into logs.

## 7. Core User Journey

1. Owner creates an organization and signs in.
2. Accountant uploads a CSV or Excel ledger.
3. CollectFlow validates and imports invoices.
4. Dashboard shows outstanding balances and overdue invoices.
5. Agent generates a prioritized collection queue.
6. Accountant opens an invoice and reviews a reminder draft.
7. Accountant approves the message and sends it manually.
8. Customer replies with a payment promise or dispute.
9. Accountant records or confirms the structured outcome.
10. System schedules the next follow-up or escalates the exception.

This journey must work end to end before adding autonomous messaging.

## 8. Non-Functional Requirements

| Requirement | MVP target |
|---|---|
| Availability | Best-effort pilot availability with health checks |
| Import performance | Typical 5,000-row ledger targeted under 30 seconds |
| API responsiveness | Target p95 under 500 ms for ordinary database-backed endpoints, excluding file processing and AI calls |
| Data isolation | Organization-level authorization on every relevant operation |
| Reliability | Imports, background jobs, and webhooks safe to retry |
| Security | HTTPS in deployment, managed secrets, restricted database access |
| Observability | Structured logs, error tracking, request IDs and job status |
| Accessibility | Keyboard-accessible core workflows and clear validation errors |
| Maintainability | Typed API contracts, modular services and automated tests |

These are initial engineering targets, not measured performance claims. Validate them with representative test data.

## 9. Success Metrics

Measure during a supervised pilot:

- Percentage of uploaded rows imported correctly
- Time required to prepare the daily collection queue
- Percentage of generated reminders approved without edits
- Percentage of customer replies classified correctly
- Number of missed commitments identified
- Number of duplicate or incorrectly addressed messages
- Hours saved per week for the accounts team
- Reduction in days sales outstanding (DSO), where the pilot duration and data allow meaningful comparison

Do not claim that the software reduces DSO until the pilot produces credible evidence.

## 10. MVP Release Criteria

The MVP is ready for a supervised pilot when:

- A business can create an account and import its ledger.
- Outstanding balances and aging are calculated correctly.
- Users can generate and approve reminder drafts.
- Customer replies can be classified and reviewed.
- Promises and disputes are tracked.
- Important actions appear in the audit log.
- Organization isolation and authentication tests pass.
- Financial calculations have deterministic tests.
- No outbound message can be sent without required authorization.
- Deployment has backups, error monitoring, and a documented recovery procedure.
