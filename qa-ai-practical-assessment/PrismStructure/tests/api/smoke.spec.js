const { expect } = require('@playwright/test');
const { test } = require('../../prism/fixtures/testFixtures');
const { buildUserPayload } = require('../../prism/utils/testDataGenerator');

test.describe('API Smoke Tests @Smoke', () => {
  test('TC-API-001 @Smoke - Register new user via API', async ({ authApi }) => {
    const user = buildUserPayload();
    const response = await authApi.register(user);

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.email).toBe(user.email);
    expect(body.id).toBeTruthy();
  });

  test('TC-API-002 @Smoke - Login and obtain bearer token', async ({ authApi }) => {
    const user = buildUserPayload();
    await authApi.register(user);

    const response = await authApi.login(user.email, user.password);
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.access_token).toBeTruthy();
    expect(body.token_type).toBe('bearer');
  });
});
