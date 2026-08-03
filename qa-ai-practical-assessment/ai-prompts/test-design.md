# AI Prompts – Test Design

## Entry 1

- **Prompt:** Generate manual test cases for Toolshop login and registration flows. Include positive and negative scenarios. Output as CSV with Test ID, Title, Type, Category, Priority, Preconditions, Steps, Expected Result, Status.

- **AI Response Summary:** Created TC-MAN-001 through TC-MAN-003 covering registration, valid login, and invalid password login with @Smoke and @regression tags.

- **Validation Notes:** Reviewed steps against actual UI routes (/auth/register, /auth/login). Added status column set to Passed after execution verification.

## Entry 2

- **Prompt:** Design 8 UI Playwright test cases for ecommerce checkout flow including add to cart, quantity update, COD checkout, and invoice verification. Tag with @Smoke or @regression.

- **AI Response Summary:** Designed TC-UI-001 to TC-UI-008 covering homepage, auth, cart, checkout with double confirm, invoices, profile, and negative login.

- **Validation Notes:** Ensured invoice test (TC-UI-006) includes double confirm per assessment note. Limited to 8 cases as required.

## Entry 3

- **Prompt:** Design 8 API test cases for register, login, cart creation, add product, verify cart, generate invoice, get products, and negative login.

- **AI Response Summary:** Created TC-API-001 to TC-API-008 mapped to AC1 and AC2 API flows with bearer token authentication.

- **Validation Notes:** Verified endpoints against OpenAPI spec at /docs?api-docs.json. Corrected cart add endpoint to POST /carts/{id}.
