const { expect } = require('@playwright/test');
const { test } = require('../../prism/fixtures/testFixtures');
const { buildUserPayload } = require('../../prism/utils/testDataGenerator');

test.describe('API Regression Tests @regression', () => {
  test('TC-API-003 @regression - Create cart with bearer token', async ({ authenticatedApis }) => {
    const { cartApi } = authenticatedApis;
    const response = await cartApi.createCart();

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.id).toBeTruthy();
  });

  test('TC-API-004 @regression - Retrieve products list', async ({ productApi }) => {
    const response = await productApi.getProducts();

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.data.length).toBeGreaterThan(0);
    expect(body.data[0]).toHaveProperty('name');
    expect(body.data[0]).toHaveProperty('price');
  });

  test('TC-API-005 @regression - Add product to cart', async ({ authenticatedApis, productApi }) => {
    const { cartApi } = authenticatedApis;
    const productId = await productApi.getFirstProductId();
    const cartResponse = await cartApi.createCart();
    const cart = await cartResponse.json();

    const response = await cartApi.addItem(cart.id, productId, 1);
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.result).toContain('added');
  });

  test('TC-API-006 @regression - Verify cart contents', async ({ authenticatedApis, productApi }) => {
    const { cartApi } = authenticatedApis;
    const productId = await productApi.getFirstProductId();
    const cartResponse = await cartApi.createCart();
    const cart = await cartResponse.json();

    await cartApi.addItem(cart.id, productId, 2);
    const response = await cartApi.getCart(cart.id);

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.cart_items.length).toBeGreaterThan(0);
    expect(body.cart_items[0].quantity).toBe(2);
  });

  test('TC-API-007 @regression - Generate invoice with cash on delivery', async ({ authenticatedApis, productApi }) => {
    const { cartApi, invoiceApi } = authenticatedApis;
    const productId = await productApi.getFirstProductId();
    const cartResponse = await cartApi.createCart();
    const cart = await cartResponse.json();

    await cartApi.addItem(cart.id, productId, 1);
    const response = await invoiceApi.createInvoice(cart.id);

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.id).toBeTruthy();
    expect(body.invoice_number).toMatch(/^INV-/);
    expect(body.total).toBeGreaterThan(0);
  });

  test('TC-API-008 @regression - Login with invalid credentials returns 401', async ({ authApi }) => {
    const response = await authApi.login('invalid@example.com', 'WrongPass1!');

    expect(response.status()).toBe(401);
    const body = await response.json();
    expect(body.error).toBeTruthy();
  });
});
