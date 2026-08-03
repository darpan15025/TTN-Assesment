Primary AI Tool(s) Used: Cursor AI (Auto / Composer 2.5 for planning, Sonnet for automation)

Application Under Test: Practice Software Testing Toolshop – Checkout & Application Flow

Assessment Start Date: 2026-08-03 / Submission Date: 2026-08-03

## Project Summary

This project validates the Practice Software Testing e-commerce application through manual, UI, and API test coverage. The focus is on user registration/login, product browsing, cart management, cash-on-delivery checkout (with double confirm for invoice generation), and invoice verification — using the Prism page-object framework with Playwright.

## Tools Used

- **Browsers:** Chromium (Playwright)
- **Automation:** Playwright Test with PrismStructure (Page Object Model)
- **API Testing:** Playwright request API
- **AI Tools:** Cursor AI
- **Reporting:** Playwright HTML, JSON, and JUnit reporters

## Setup Summary

### 1. How you provide project and system-under-test context to the tool

Shared the QA assessment document, SUT URLs (UI and API), acceptance criteria (AC1/AC2), and repository structure requirements with Cursor. Referenced Swagger docs at `https://api.practicesoftwaretesting.com/api/documentation` for API contracts.

### 2. How you use AI for requirement analysis

Used Cursor to extract AC1 (Registration & Login) and AC2 (End-to-End Purchase / API Cart-to-Invoice) into testable scenarios. Identified risks: Cloudflare on UI, unique password requirements for API registration, and the double-confirm invoice flow.

### 3. How you use AI for test planning and strategy

Planned 8 manual, 8 UI, and 8 API test cases tagged `@Smoke` and `@regression`. Smoke covers critical paths (homepage, auth, profile); regression covers cart, checkout, invoice, and negative login.

### 4. How you use AI for manual test case design

Generated `FunctionalTestCase.csv` with positive, negative, and edge scenarios mapped to AC1/AC2. Each case includes preconditions, steps, and expected results.

### 5. How you use AI for automation design

Implemented PrismStructure with separated `pages/`, `api/`, `fixtures/`, and `utils/`. Reusable API clients (Auth, Cart, Product, Invoice) and UI page objects follow single-responsibility principles.

### 6. How you validate and refine AI-generated test cases and scripts

Reviewed AI output against live API responses (OpenAPI spec) and UI `data-test` attributes. Adjusted cart endpoint from `/items` to `POST /carts/{id}` per actual API. Verified password policy and invoice double-confirm behavior manually.

### 7. How you use AI for test data generation

`testDataGenerator.js` creates unique emails and breach-safe passwords per run. Invoice payloads use documented billing fields from the assessment example.

### 8. How you use AI for debugging failing tests and interpreting logs

Used Playwright traces, HTML reports, and API status codes. Debugged cart add endpoint, token expiry, and UI selector mismatches iteratively with focused prompts.

### 9. What information you avoid sharing unnecessarily with AI tools

No production credentials, internal tokens, or personal data. Only public SUT URLs and synthetic test user data are used.

### 10. How you would reuse this QA workflow in a real project

Apply the same PrismStructure layout, tag-based test tiers (`@Smoke` / `@regression`), ai-prompts documentation per phase, and iterative git commits. Swap SUT context and page objects while keeping fixtures and reporting patterns.

## Test Coverage Summary

| Layer | Smoke | Regression | Total |
|-------|-------|------------|-------|
| Manual (CSV) | 3 | 5 | 8 |
| UI Automation | 3 | 5 | 8 |
| API Automation | 2 | 6 | 8 |

## Acceptance Criteria Mapping

| AC | Description | Test IDs |
|----|-------------|----------|
| AC1 (UI) | User Registration & Login | TC-MAN-001/002, TC-UI-002/008, TC-API-001/002 |
| AC2 (UI) | End-to-End Purchase Flow | TC-MAN-004–007, TC-UI-003–006 |
| AC1 (API) | User Auth & Cart Creation | TC-API-001–003 |
| AC2 (API) | Product Selection & Invoice | TC-API-004–007 |
