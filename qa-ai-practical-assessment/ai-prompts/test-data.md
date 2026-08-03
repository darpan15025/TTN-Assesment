# AI Prompts – Test Data

## Entry 1

- **Prompt:** Create a test data generator for API registration that produces unique emails and passwords passing Toolshop validation (uppercase, lowercase, symbol, not in breach database).

- **AI Response Summary:** Implemented uniqueEmail() and uniquePassword() in testDataGenerator.js using timestamp-based values like Qa{timestamp}!Zx.

- **Validation Notes:** Tested live registration — confirmed passwords rejected when appearing in breach DB. Timestamp-based passwords pass validation.

## Entry 2

- **Prompt:** Provide invoice POST request body for cash-on-delivery checkout matching the assessment example with billing fields and cart_id.

- **AI Response Summary:** Created config.invoiceBilling with billing_street, billing_city, billing_state, billing_country, billing_postal_code, payment_method, and payment_details fields.

- **Validation Notes:** Matched assessment example payload. Verified invoice creation returns INV- prefixed invoice_number via API test TC-API-007.

## Entry 3

- **Prompt:** How should UI checkout billing data align with API invoice payload for consistent end-to-end testing?

- **AI Response Summary:** Recommended shared billing defaults (Zoey Shore, Hesselbury, Florida, TG, 1234AA) in config.js used by both CheckoutPage and InvoiceApi.

- **Validation Notes:** Applied same values in UI CheckoutPage.fillBillingDetails() and API buildInvoicePayload() for traceability.
