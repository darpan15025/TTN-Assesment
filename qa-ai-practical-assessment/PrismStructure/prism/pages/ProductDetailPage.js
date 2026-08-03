const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class ProductDetailPage extends BasePage {
  constructor(page) {
    super(page);
    this.addToCartButton = page.getByTestId('add-to-cart');
    this.productName = page.getByTestId('product-name').first();
    this.quantityInput = page.getByTestId('quantity');
    this.successToast = page.getByText('Product added to shopping cart');
  }

  async waitForLoaded() {
    await waitForAppReady(this.page, this.addToCartButton);
  }

  async addToCart(quantity = 1) {
    await this.waitForLoaded();
    if (quantity !== 1 && (await this.quantityInput.isVisible().catch(() => false))) {
      await this.quantityInput.fill(String(quantity));
    }
    await this.addToCartButton.click();
    await this.successToast.waitFor({ state: 'visible', timeout: 15000 });
  }
}

module.exports = { ProductDetailPage };
