class CartApi {
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

  async createCart() {
    return this.request.post('/carts', { headers: this.headers() });
  }

  async getCart(cartId) {
    return this.request.get(`/carts/${cartId}`, { headers: this.headers() });
  }

  async addItem(cartId, productId, quantity = 1) {
    return this.request.post(`/carts/${cartId}`, {
      headers: this.headers(),
      data: { product_id: productId, quantity }
    });
  }

  async updateQuantity(cartId, productId, quantity) {
    return this.request.put(`/carts/${cartId}/product/quantity`, {
      headers: this.headers(),
      data: { product_id: productId, quantity }
    });
  }
}

module.exports = { CartApi };
