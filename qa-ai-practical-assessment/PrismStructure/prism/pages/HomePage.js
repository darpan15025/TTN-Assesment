const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class HomePage extends BasePage {
  constructor(page) {
    super(page);
    this.productNames = page.getByTestId('product-name');
    this.productCards = page.locator('a.card[data-test^="product-"]');
    this.navSignIn = page.getByTestId('nav-sign-in');
    this.navCart = page.getByTestId('nav-cart');
  }

  async goto() {
    await super.goto('/');
    await this.waitForProducts();
  }

  async waitForProducts() {
    await waitForAppReady(this.page, this.productNames.first());
  }

  async getProductCount() {
    return this.productNames.count();
  }

  async openProductByName(productName) {
    await this.productNames.filter({ hasText: productName }).first().click();
  }

  async openFirstInStockProduct() {
    const cards = this.productCards;
    const count = await cards.count();
    for (let i = 0; i < count; i += 1) {
      const card = cards.nth(i);
      const outOfStock = await card.getByText(/out of stock/i).isVisible().catch(() => false);
      if (!outOfStock) {
        await card.click();
        return card;
      }
    }
    throw new Error('No in-stock product cards found on homepage');
  }
}

module.exports = { HomePage };
