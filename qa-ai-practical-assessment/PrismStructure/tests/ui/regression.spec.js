const { test, expect } = require('@playwright/test');
const { HomePage } = require('../../prism/pages/HomePage');
const { LoginPage } = require('../../prism/pages/LoginPage');
const { ProductDetailPage } = require('../../prism/pages/ProductDetailPage');
const { CartPage } = require('../../prism/pages/CartPage');
const { CheckoutPage } = require('../../prism/pages/CheckoutPage');
const { InvoicesPage } = require('../../prism/pages/InvoicesPage');
const { registerAndLogin } = require('../../prism/utils/authHelper');

test.describe('UI Regression Tests @regression', () => {
  test('TC-UI-003 @regression - Add product to cart', async ({ page }) => {
    await registerAndLogin(page);

    const homePage = new HomePage(page);
    const productDetailPage = new ProductDetailPage(page);
    const cartPage = new CartPage(page);

    await homePage.goto();
    await homePage.openProductByName('Combination Pliers');
    await productDetailPage.addToCart(1);

    await cartPage.goto();
    await expect(page.getByText('Combination Pliers').first()).toBeVisible();
    await expect(cartPage.proceedCheckoutButton).toBeVisible();
  });

  test('TC-UI-004 @regression - Update cart item quantity', async ({ page }) => {
    await registerAndLogin(page);

    const homePage = new HomePage(page);
    const productDetailPage = new ProductDetailPage(page);
    const cartPage = new CartPage(page);

    await homePage.goto();
    await homePage.openProductByName('Combination Pliers');
    await productDetailPage.addToCart(1);

    await cartPage.goto();
    await cartPage.updateQuantity(0, 3);
    await expect(cartPage.quantityInputs.first()).toHaveValue('3');
  });

  test('TC-UI-005 @regression - Complete purchase flow with cash on delivery', async ({ page }) => {
    await registerAndLogin(page);

    const homePage = new HomePage(page);
    const productDetailPage = new ProductDetailPage(page);
    const cartPage = new CartPage(page);
    const checkoutPage = new CheckoutPage(page);

    await homePage.goto();
    await homePage.openProductByName('Combination Pliers');
    await productDetailPage.addToCart(1);

    await cartPage.goto();
    await cartPage.proceedToCheckout();
    await checkoutPage.continueSignedIn();
    await checkoutPage.fillBillingDetails();
    await checkoutPage.selectCashOnDelivery();
    await checkoutPage.completeOrder();

    await expect(page.getByText(/thanks for your order|invoice number/i)).toBeVisible();
  });

  test('TC-UI-006 @regression - Verify invoice in My Invoices after double confirm', async ({ page }) => {
    await registerAndLogin(page);

    const homePage = new HomePage(page);
    const productDetailPage = new ProductDetailPage(page);
    const cartPage = new CartPage(page);
    const checkoutPage = new CheckoutPage(page);
    const invoicesPage = new InvoicesPage(page);

    await homePage.goto();
    await homePage.openProductByName('Combination Pliers');
    await productDetailPage.addToCart(1);

    await cartPage.goto();
    await cartPage.proceedToCheckout();
    await checkoutPage.continueSignedIn();
    await checkoutPage.fillBillingDetails();
    await checkoutPage.selectCashOnDelivery();
    await checkoutPage.completeOrder();

    await invoicesPage.goto();
    const count = await invoicesPage.getInvoiceCount();
    expect(count).toBeGreaterThan(0);
  });

  test('TC-UI-007 @regression - Login with invalid credentials shows error', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login('invalid@example.com', 'WrongPass1!');

    await expect(loginPage.errorAlert.first()).toBeVisible({ timeout: 15000 });
  });
});
