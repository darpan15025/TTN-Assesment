const { BasePage } = require('./BasePage');
const { waitForAppReady } = require('../utils/waitHelpers');

class RegisterPage extends BasePage {
  constructor(page) {
    super(page);
    this.firstNameInput = page.getByTestId('first-name');
    this.lastNameInput = page.getByTestId('last-name');
    this.dobInput = page.getByTestId('dob');
    this.streetInput = page.getByTestId('street');
    this.postalCodeInput = page.getByTestId('postal_code');
    this.houseNumberInput = page.getByTestId('house_number');
    this.cityInput = page.getByTestId('city');
    this.stateInput = page.getByTestId('state');
    this.countrySelect = page.getByTestId('country');
    this.phoneInput = page.getByTestId('phone');
    this.emailInput = page.getByTestId('email');
    this.passwordInput = page.getByTestId('password');
    this.registerButton = page.getByTestId('register-submit');
  }

  async goto() {
    await super.goto('/auth/register');
    await waitForAppReady(this.page, this.firstNameInput);
  }

  async register(user) {
    await this.firstNameInput.fill(user.first_name);
    await this.lastNameInput.fill(user.last_name);
    await this.dobInput.fill(user.dob);
    await this.countrySelect.selectOption(user.address.country);
    await this.postalCodeInput.fill(user.address.postal_code);
    await this.houseNumberInput.fill('42');
    await this.streetInput.fill(user.address.street);
    await this.cityInput.fill(user.address.city);
    await this.stateInput.fill(user.address.state);
    await this.phoneInput.fill(user.phone);
    await this.emailInput.fill(user.email);
    await this.passwordInput.fill(user.password);
    await this.registerButton.click();
  }
}

module.exports = { RegisterPage };
