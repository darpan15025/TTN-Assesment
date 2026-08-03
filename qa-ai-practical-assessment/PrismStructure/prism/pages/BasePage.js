const { waitForCloudflare } = require('../utils/waitHelpers');

class BasePage {
  constructor(page) {
    this.page = page;
  }

  async goto(path = '/') {
    await this.page.goto(path, { waitUntil: 'domcontentloaded' });
    await waitForCloudflare(this.page);
  }
}

module.exports = { BasePage };
