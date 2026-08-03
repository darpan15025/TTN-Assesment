const { config } = require('./config');

function uniqueEmail(prefix = 'qauser') {
  return `${prefix}${Date.now()}@example.com`;
}

function uniquePassword() {
  return `Qa${Date.now()}!Zx`;
}

function buildUserPayload(overrides = {}) {
  const email = overrides.email || uniqueEmail();
  const password = overrides.password || uniquePassword();

  return {
    first_name: 'QA',
    last_name: 'Tester',
    email,
    password,
    dob: '1990-01-01',
    phone: '1234567890',
    address: {
      street: 'Test Street',
      city: 'Test City',
      state: 'Florida',
      country: 'US',
      postal_code: '12345'
    },
    ...overrides
  };
}

function buildInvoicePayload(cartId, overrides = {}) {
  return {
    ...config.invoiceBilling,
    cart_id: cartId,
    ...overrides
  };
}

module.exports = {
  uniqueEmail,
  uniquePassword,
  buildUserPayload,
  buildInvoicePayload
};
