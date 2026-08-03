const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class ProfilePage extends BasePage {
  constructor(page) {
    super(page);
    this.firstNameInput = page.getByTestId('first-name');
    this.lastNameInput = page.getByTestId('last-name');
    this.emailInput = page.getByTestId('email');
  }

  async goto() {
    await super.goto('/account/profile');
    await waitForAppReady(this.page, this.firstNameInput);
  }
}

module.exports = { ProfilePage };
