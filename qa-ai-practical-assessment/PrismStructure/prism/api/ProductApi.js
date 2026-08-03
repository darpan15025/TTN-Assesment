class ProductApi {
  constructor(request, accessToken = null) {
    this.request = request;
    this.accessToken = accessToken;
  }

  headers() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`;
    }
    return headers;
  }

  async getProducts() {
    return this.request.get('/products', { headers: this.headers() });
  }

  async getFirstProductId() {
    const response = await this.getProducts();
    const body = await response.json();
    return body.data[0].id;
  }
}

module.exports = { ProductApi };
