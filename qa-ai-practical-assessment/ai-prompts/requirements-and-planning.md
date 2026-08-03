# AI Prompts – Requirements and Planning

## Entry 1

- **Prompt:** Extract AC1 and AC2 from the QA assessment document for Practice Software Testing Toolshop. List UI and API test scenarios categorized as smoke or regression. Limit to 5-8 cases per type.

- **AI Response (short summary):** Identified AC1 (Registration/Login) and AC2 (Purchase/Invoice) for both UI and API. Proposed 8 manual, 8 UI, and 8 API cases with @Smoke for critical paths and @regression for extended flows including cart quantity, checkout, and negative login.

- **Validation Notes:** Cross-checked against assessment requirement of max 5-8 cases per type. Mapped each case to acceptance criteria traceability table in project-info.md.

## Entry 2

- **Prompt:** Analyze risks for testing practicesoftwaretesting.com UI and api.practicesoftwaretesting.com. What should I watch for in automation?

- **AI Response (short summary):** Flagged Cloudflare protection on UI, API password breach-check policy, customer account lockouts, double-confirm invoice flow, and JWT token 5-minute expiry.

- **Validation Notes:** Confirmed password policy via live API call. Added unique password generator to avoid breach-database rejection. Documented double-confirm in readme and checkout page object.

## Entry 3

- **Prompt:** Design the PrismStructure folder layout for Playwright with separate UI pages, API clients, fixtures, and execution reports per assessment template.

- **AI Response (short summary):** Proposed prism/pages, prism/api, prism/fixtures, prism/utils under PrismStructure with tests/ui and tests/api folders. Configured HTML, JSON, and JUnit reporters in reports/.

- **Validation Notes:** Matched required repository structure from assessment document. Kept naming consistent with Prism Framework page-object pattern.
