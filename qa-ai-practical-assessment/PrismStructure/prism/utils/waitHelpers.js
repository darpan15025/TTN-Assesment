async function waitForCloudflare(page, timeout = 90000) {
  const challenge = page.getByText(/performing security verification|just a moment|verify you are human/i);
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const blocked = await challenge.isVisible().catch(() => false);
    if (!blocked) {
      return;
    }
    await page.waitForTimeout(1500);
  }
}

async function waitForAppReady(page, readyLocator, timeout = 60000) {
  await waitForCloudflare(page, timeout);
  await readyLocator.waitFor({ state: 'visible', timeout });
}

module.exports = {
  waitForCloudflare,
  waitForAppReady
};
