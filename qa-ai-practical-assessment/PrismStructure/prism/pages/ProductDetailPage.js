const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class ProductDetailPage extends BasePage {
  constructor(page) {
    super(page);
    this.addToCartButton = page.getByTestId('add-to-cart');
    this.productName = page.getByTestId('product-name').first();
    this.quantityInput = page.getByTestId('quantity');
    this.successToast = page.getByText('Product added to shopping cart');
    this.outOfStock = page.getByText(/out of stock/i);
  }

  async waitForLoaded() {
    await waitForAppReady(this.page, this.addToCartButton.or(this.outOfStock));
  }

  async addToCart(quantity = 1) {
    await this.waitForLoaded();
    if (await this.outOfStock.isVisible().catch(() => false)) {
      throw new Error('Selected product is out of stock');
    }
    await this.addToCartButton.waitFor({ state: 'visible', timeout: 15000 });
    await expectEnabled(this.addToCartButton);
    if (quantity !== 1 && (await this.quantityInput.isVisible().catch(() => false))) {
      await this.quantityInput.fill(String(quantity));
    }
    await this.addToCartButton.click();
    await this.successToast.waitFor({ state: 'visible', timeout: 15000 });
  }
}

async function expectEnabled(locator, timeout = 20000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (await locator.isEnabled().catch(() => false)) {
      return;
    }
    await locator.page().waitForTimeout(500);
  }
  throw new Error('Add to cart button did not become enabled');
}

module.exports = { ProductDetailPage };
