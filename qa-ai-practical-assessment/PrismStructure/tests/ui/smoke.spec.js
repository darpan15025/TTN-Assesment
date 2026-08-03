const { test, expect } = require('@playwright/test');
const { HomePage } = require('../../prism/pages/HomePage');
const { LoginPage } = require('../../prism/pages/LoginPage');
const { RegisterPage } = require('../../prism/pages/RegisterPage');
const { ProfilePage } = require('../../prism/pages/ProfilePage');
const { buildUserPayload } = require('../../prism/utils/testDataGenerator');
const { registerAndLogin } = require('../../prism/utils/authHelper');

test.describe('UI Smoke Tests @Smoke', () => {
  test('TC-UI-001 @Smoke - Homepage loads with product list', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();

    const count = await homePage.getProductCount();
    expect(count).toBeGreaterThan(0);
  });

  test('TC-UI-002 @Smoke - User can register and login', async ({ page }) => {
    const user = buildUserPayload();
    const registerPage = new RegisterPage(page);
    const loginPage = new LoginPage(page);

    await registerPage.goto();
    await registerPage.register(user);
    await page.waitForURL(/auth\/login|account/, { timeout: 30000 });

    if (page.url().includes('/auth/login') || (await loginPage.emailInput.isVisible().catch(() => false))) {
      await loginPage.login(user.email, user.password);
    }

    await expect(page.getByTestId('nav-menu')).toBeVisible({ timeout: 20000 });
  });

  test('TC-UI-008 @Smoke - User profile displays correct information', async ({ page }) => {
    const user = await registerAndLogin(page);
    const profilePage = new ProfilePage(page);

    await profilePage.goto();
    await expect(profilePage.firstNameInput).toHaveValue(user.first_name);
    await expect(profilePage.lastNameInput).toHaveValue(user.last_name);
    await expect(profilePage.emailInput).toHaveValue(user.email);
  });
});
