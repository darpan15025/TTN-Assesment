const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class HomePage extends BasePage {
  constructor(page) {
    super(page);
    this.productNames = page.getByTestId('product-name');
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
}

module.exports = { HomePage };
