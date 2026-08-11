import { expect, test } from '@playwright/test';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const deckUrl = pathToFileURL(path.resolve('dist/index.html')).href;

test.beforeEach(async ({ page }) => {
  await page.goto(deckUrl);
  await page.waitForFunction(() => window.__DECK_READY__ === true);
});

test('deck 16:9 oferece narrativa principal, notas e apêndice', async ({ page }) => {
  await expect(page.locator('.slides > section[data-main-slide]')).toHaveCount(11);
  await expect(page.locator('.slides > section[data-appendix-slide]')).toHaveCount(5);
  await expect(page.locator('.slides > section[data-main-slide] aside.notes')).toHaveCount(11);

  const config = await page.evaluate(() => ({
    width: window.Reveal.getConfig().width,
    height: window.Reveal.getConfig().height,
  }));
  expect(config).toEqual({ width: 1600, height: 900 });

  await page.keyboard.press('ArrowRight');
  await expect(page.locator('.slides > section.present')).toHaveAttribute('id', 'problem');
  await expect(page.locator('#responsible-next-step')).toHaveCount(1);
  await expect(page.locator('#journey-boundaries')).toHaveCount(1);
});

test('Plotly deriva gráficos e ressalvas do relatório oficial', async ({ page }) => {
  await expect(page.locator('.js-plotly-plot')).toHaveCount(3);
  await expect(page.locator('[data-metric="sample"]').first()).toHaveText('45.211');
  await expect(page.locator('[data-metric="seeds"]')).toHaveText('5 seeds');
  await expect(page.locator('[data-metric="uplift"]').first()).toHaveText('+5.434,2');
  await expect(page.locator('[data-metric="arm-count"]')).toHaveText('7 Braços');
  await expect(page.locator('[data-metric="low-home-exposure"]').first()).toHaveText('3,8/seed');
  await expect(page.locator('[data-metric="low-investment-exposure"]').first()).toHaveText('0,8/seed');
  await page.evaluate(() => window.Reveal.slide(5));
  await expect(page.getByText('sintética, offline e não causal', { exact: false }).first()).toBeVisible();

  const seedValues = await page.evaluate(() => window.__DECK_CHARTS__.upliftBySeed.y);
  expect(seedValues).toEqual([5419, 5416, 5468, 5388, 5480]);
});

test('Mermaid renderiza localmente e o deck não requisita rede', async ({ browser }) => {
  const context = await browser.newContext();
  await context.route(/^https?:\/\//, (route) => route.abort());
  const page = await context.newPage();
  const remoteRequests = [];
  page.on('request', (request) => {
    if (/^https?:/.test(request.url())) remoteRequests.push(request.url());
  });

  await page.goto(deckUrl);
  await page.waitForFunction(() => window.__DECK_READY__ === true);
  await expect(page.locator('.mermaid svg')).toHaveCount(2);
  expect(remoteRequests).toEqual([]);

  await context.setOffline(true);
  await page.keyboard.press('End');
  await expect(page.locator('#reproduction')).toHaveClass(/present/);
  await context.close();
});
