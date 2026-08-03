const { BasePage } = require('./BasePage');

class CheckoutPage extends BasePage {
  constructor(page) {
    super(page);
    this.proceedSignIn = page.getByTestId('proceed-2');
    this.proceedBilling = page.getByTestId('proceed-3');
    this.streetInput = page.getByTestId('street');
    this.cityInput = page.getByTestId('city');
    this.stateInput = page.getByTestId('state');
    this.countrySelect = page.getByTestId('country');
    this.postalCodeInput = page.getByTestId('postal_code');
    this.houseNumberInput = page.getByTestId('house_number');
    this.paymentMethod = page.getByTestId('payment-method');
    this.confirmButton = page.getByTestId('finish');
    this.successMessage = page.getByText(/thanks for your order|payment was successful|invoice number/i);
  }

  async continueSignedIn() {
    await this.proceedSignIn.waitFor({ state: 'visible', timeout: 15000 });
    await this.proceedSignIn.click();
  }

  async fillBillingDetails(billing = {}) {
    const defaults = {
      street: 'Zoey Shore',
      city: 'Hesselbury',
      state: 'Florida',
      country: 'US',
      postalCode: '12345',
      houseNumber: '42'
    };
    const data = { ...defaults, ...billing };

    await this.countrySelect.waitFor({ state: 'visible', timeout: 15000 });
    await this.countrySelect.selectOption(data.country);
    await this.postalCodeInput.fill(data.postalCode);
    if (await this.houseNumberInput.isVisible().catch(() => false)) {
      await this.houseNumberInput.fill(data.houseNumber);
    }
    await this.streetInput.fill(data.street);
    await this.cityInput.fill(data.city);
    await this.stateInput.fill(data.state);
    await this.proceedBilling.click();
  }

  async selectCashOnDelivery() {
    await this.paymentMethod.waitFor({ state: 'visible', timeout: 15000 });
    await this.paymentMethod.selectOption('cash-on-delivery');
  }

  async completeOrder() {
    await this.confirmButton.waitFor({ state: 'visible', timeout: 15000 });
    await this.confirmButton.click();
    await this.page.getByText(/payment was successful/i).waitFor({ timeout: 15000 });
    await this.confirmButton.click();
    await this.page.getByText(/thanks for your order|invoice number/i).waitFor({ timeout: 20000 });
  }
}

module.exports = { CheckoutPage };
