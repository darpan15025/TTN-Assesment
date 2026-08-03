const { config } = require('../utils/config');

class InvoiceApi {
  constructor(request, accessToken) {
    this.request = request;
    this.accessToken = accessToken;
  }

  headers() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.accessToken}`
    };
  }

  async createInvoice(cartId, overrides = {}) {
    return this.request.post('/invoices', {
      headers: this.headers(),
      data: {
        ...config.invoiceBilling,
        cart_id: cartId,
        ...overrides
      }
    });
  }

  async getInvoices() {
    return this.request.get('/invoices', { headers: this.headers() });
  }
}

module.exports = { InvoiceApi };
