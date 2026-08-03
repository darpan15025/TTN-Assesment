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

    const start = Date.now();
    while (Date.now() - start < 25000) {
      if (await this.houseNumberInput.isVisible().catch(() => false)) {
        await this.houseNumberInput.fill(data.houseNumber);
      }

      const streetValue = await this.streetInput.inputValue().catch(() => '');
      if (!streetValue) {
        await this.streetInput.fill(data.street);
      }
      const cityValue = await this.cityInput.inputValue().catch(() => '');
      if (!cityValue) {
        await this.cityInput.fill(data.city);
      }
      const stateValue = await this.stateInput.inputValue().catch(() => '');
      if (!stateValue) {
        await this.stateInput.fill(data.state);
      }

      // Require two consecutive enabled reads to avoid postcode-lookup races.
      const enabledOnce = await this.proceedBilling.isEnabled().catch(() => false);
      await this.page.waitForTimeout(300);
      if (await this.houseNumberInput.isVisible().catch(() => false)) {
        const houseValue = await this.houseNumberInput.inputValue().catch(() => '');
        if (houseValue !== data.houseNumber) {
          await this.houseNumberInput.fill(data.houseNumber);
          await this.page.waitForTimeout(200);
        }
      }
      const enabledTwice = await this.proceedBilling.isEnabled().catch(() => false);
      if (enabledOnce && enabledTwice) {
        await this.proceedBilling.click({ force: true });
        return;
      }
      await this.page.waitForTimeout(400);
    }

    throw new Error('Billing proceed button remained disabled after filling required fields');
  }

  async selectCashOnDelivery() {
    await this.paymentMethod.waitFor({ state: 'visible', timeout: 15000 });
    await this.paymentMethod.selectOption('cash-on-delivery');
  }

  async completeOrder() {
    await this.confirmButton.waitFor({ state: 'visible', timeout: 15000 });
    await this.waitForEnabled(this.confirmButton);

    const paymentResponse = this.page.waitForResponse(
      (response) => response.url().includes('/payment/check') && response.status() === 200,
      { timeout: 20000 }
    );
    await this.confirmButton.click();
    await paymentResponse;
    await this.page.getByText(/payment was successful/i).waitFor({ timeout: 15000 });
    await this.page.waitForTimeout(1000);

    const invoiceResponse = this.page.waitForResponse(
      (response) => response.url().includes('/invoices') && response.request().method() === 'POST',
      { timeout: 20000 }
    );
    await this.waitForEnabled(this.confirmButton);
    await this.confirmButton.click();
    const response = await invoiceResponse;
    if (response.status() !== 201) {
      throw new Error(`Invoice creation failed with status ${response.status()}: ${await response.text()}`);
    }
    await this.page.getByText(/thanks for your order|invoice number/i).waitFor({ timeout: 20000 });
  }

  async waitForEnabled(locator, timeout = 20000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      if (await locator.isEnabled().catch(() => false)) {
        return;
      }
      await this.page.waitForTimeout(400);
    }
    throw new Error(`Locator remained disabled: ${locator}`);
  }
}

module.exports = { CheckoutPage };
