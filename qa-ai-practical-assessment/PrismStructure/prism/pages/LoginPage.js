const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class LoginPage extends BasePage {
  constructor(page) {
    super(page);
    this.emailInput = page.getByTestId('email');
    this.passwordInput = page.getByTestId('password');
    this.loginButton = page.getByTestId('login-submit');
    this.errorAlert = page.locator('.alert-danger, [role="alert"], .help-block');
  }

  async goto() {
    await super.goto('/auth/login');
    await waitForAppReady(this.page, this.emailInput);
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

module.exports = { LoginPage };
