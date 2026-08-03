const { request } = require('@playwright/test');

async function getInStockProduct() {
  const apiContext = await request.newContext({
    baseURL: 'https://api.practicesoftwaretesting.com'
  });
  const response = await apiContext.get('/products?page=1');
  const body = await response.json();
  await apiContext.dispose();

  const product = (body.data || []).find((item) => item.in_stock !== false && item.is_rental !== true);
  if (!product) {
    throw new Error('No in-stock products available from Toolshop API');
  }
  return product;
}

module.exports = { getInStockProduct };
