const { test: base } = require('@playwright/test');
const { AuthApi } = require('../api/AuthApi');
const { ProductApi } = require('../api/ProductApi');
const { CartApi } = require('../api/CartApi');
const { InvoiceApi } = require('../api/InvoiceApi');

const test = base.extend({
  authApi: async ({ request }, use) => {
    await use(new AuthApi(request));
  },
  productApi: async ({ request }, use) => {
    await use(new ProductApi(request));
  },
  authenticatedApis: async ({ request, authApi }, use) => {
    const { buildUserPayload } = require('../utils/testDataGenerator');
    const user = buildUserPayload();
    const { accessToken } = await authApi.registerAndLogin(user);

    await use({
      user,
      accessToken,
      productApi: new ProductApi(request, accessToken),
      cartApi: new CartApi(request, accessToken),
      invoiceApi: new InvoiceApi(request, accessToken)
    });
  }
});

module.exports = { test };
