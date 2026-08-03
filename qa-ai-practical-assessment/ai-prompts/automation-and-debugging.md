# AI Prompts – Automation and Debugging

## Entry 1

- **Prompt:** Create AuthApi, CartApi, ProductApi, and InvoiceApi classes following Prism pattern for Playwright request API.

- **AI Response Summary:** Built API client classes with bearer token headers, methods for register, login, createCart, addItem, getProducts, and createInvoice.

- **Validation Notes:** All API regression tests pass. Fixed cart add from incorrect /items path to POST /carts/{id} after 404 debugging.

## Entry 2

- **Prompt:** Create Playwright page objects for LoginPage, RegisterPage, HomePage, CartPage, CheckoutPage with data-test selectors. Handle double confirm on invoice.

- **AI Response Summary:** Implemented page objects with getByTestId selectors. CheckoutPage.completeOrder() clicks confirm button twice.

- **Validation Notes:** UI tests may need selector tuning against live site. Added fallback locators and visibility checks for resilient interactions.

## Entry 3

- **Prompt:** Debug API test failure — cart items endpoint returns 404 when using POST /carts/{id}/items.

- **AI Response Summary:** Checked OpenAPI spec and found correct endpoint is POST /carts/{id} with product_id and quantity in body.

- **Debugging Outcome:** Updated CartApi.addItem() to use correct endpoint. TC-API-005 and TC-API-006 now pass.

## Entry 4

- **Prompt:** Configure Playwright reporters for HTML, JSON, and JUnit output in reports/ folder per assessment requirements.

- **AI Response Summary:** Added list, html, json, and junit reporters to playwright.config.js with output paths under reports/.

- **Debugging Outcome:** Reports generated successfully after test run. All test statuses recorded as passed in execution-results.json.
