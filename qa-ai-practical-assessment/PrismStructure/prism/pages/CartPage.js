const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class CartPage extends BasePage {
  constructor(page) {
    super(page);
    this.cartItems = page.locator('table tbody tr');
    this.proceedCheckoutButton = page.getByTestId('proceed-1');
    this.quantityInputs = page.locator('input[type="number"], [data-test="product-quantity"]');
    this.navCart = page.getByTestId('nav-cart');
  }

  async goto() {
    if (await this.navCart.isVisible().catch(() => false)) {
      await this.navCart.click();
    } else {
      await super.goto('/checkout');
    }
    await this.page.waitForURL(/checkout/, { timeout: 30000 }).catch(async () => {
      await super.goto('/checkout');
    });
    await waitForAppReady(
      this.page,
      this.proceedCheckoutButton.or(this.page.getByText(/cart is empty/i))
    );
  }

  async updateQuantity(index, quantity) {
    const input = this.quantityInputs.nth(index);
    await input.waitFor({ state: 'visible', timeout: 15000 });
    await input.fill(String(quantity));
    await input.blur();
    await this.page.waitForTimeout(1000);
  }

  async proceedToCheckout() {
    await this.proceedCheckoutButton.click();
  }
}

module.exports = { CartPage };
