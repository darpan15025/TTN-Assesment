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
    const product = (body.data || []).find((item) => item.in_stock !== false && item.is_rental !== true) || body.data[0];
    return product.id;
  }
}

module.exports = { ProductApi };
