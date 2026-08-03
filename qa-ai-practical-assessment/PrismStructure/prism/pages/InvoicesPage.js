const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class InvoicesPage extends BasePage {
  constructor(page) {
    super(page);
    this.pageTitle = page.getByTestId('page-title');
    this.invoiceRows = page.locator('table tbody tr');
  }

  async goto() {
    await super.goto('/account/invoices');
    await waitForAppReady(this.page, this.pageTitle);
  }

  async getInvoiceCount() {
    await this.page.waitForTimeout(1000);
    return this.invoiceRows.count();
  }
}

module.exports = { InvoicesPage };
