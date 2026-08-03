const { request } = require('@playwright/test');
const { AuthApi } = require('../api/AuthApi');
const { buildUserPayload } = require('./testDataGenerator');
const { LoginPage } = require('../pages/LoginPage');

async function registerUserViaApi(overrides = {}) {
  const apiContext = await request.newContext({
    baseURL: 'https://api.practicesoftwaretesting.com'
  });
  const authApi = new AuthApi(apiContext);
  const user = buildUserPayload(overrides);
  const response = await authApi.register(user);
  if (response.status() !== 201) {
    const body = await response.text();
    await apiContext.dispose();
    throw new Error(`API registration failed (${response.status()}): ${body}`);
  }
  await apiContext.dispose();
  return user;
}

async function loginViaUi(page, user) {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login(user.email, user.password);
  await page.waitForURL(/account|\/$/, { timeout: 30000 });
  await page.getByTestId('nav-menu').waitFor({ state: 'visible', timeout: 20000 });
}

async function registerAndLogin(page, overrides = {}) {
  const user = await registerUserViaApi(overrides);
  await loginViaUi(page, user);
  return user;
}

module.exports = {
  registerUserViaApi,
  loginViaUi,
  registerAndLogin
};
