import { expect, test } from '@playwright/test';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const deckUrl = pathToFileURL(path.resolve('dist/index.html')).href;

test.beforeEach(async ({ page }) => {
  await page.goto(deckUrl);
  await page.waitForFunction(() => window.__DECK_READY__ === true);
});

test('deck 16:9 oferece narrativa principal, notas e apêndice', async ({ page }) => {
  await expect(page.locator('.slides > section[data-main-slide]')).toHaveCount(12);
  await expect(page.locator('.slides > section[data-appendix-slide]')).toHaveCount(5);
  await expect(page.locator('.slides > section[data-main-slide] aside.notes')).toHaveCount(12);
  await expect(page.locator('.slides > section[data-main-slide] aside.notes .note-goal')).toHaveCount(12);
  await expect(page.locator('.slides > section[data-main-slide] aside.notes .note-script')).toHaveCount(12);
  await expect(page.locator('.slides > section[data-main-slide] aside.notes .note-interpretation')).toHaveCount(12);
  await expect(page.locator('.slides > section[data-main-slide] aside.notes .note-caution')).toHaveCount(12);

  const config = await page.evaluate(() => ({
    width: window.Reveal.getConfig().width,
    height: window.Reveal.getConfig().height,
  }));
  expect(config).toEqual({ width: 1600, height: 900 });

  await page.keyboard.press('ArrowRight');
  await expect(page.locator('.slides > section.present')).toHaveAttribute('id', 'problem');
  await expect(page.locator('#responsible-next-step')).toHaveCount(1);
  await expect(page.locator('#journey-boundaries')).toHaveCount(1);
  await expect(page.getByText('MLflow local', { exact: false })).toHaveCount(1);
  await expect(page.getByText('AWS está ativa nesta demo', { exact: false })).toHaveCount(1);
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

test('demo executa API configurável e renderiza contrato responsável', async ({ page }) => {
  await page.evaluate(() => window.Reveal.slide(11));
  await page.route('http://127.0.0.1:8000/v1/decisions', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        selected_action: 'route_to_specialist',
        eligible_actions: ['route_to_specialist', 'no_offer_now'],
        policy_version: 'baseline_deterministic_v0.1',
        reason_codes: ['human_in_the_loop'],
        guardrails_triggered: [],
        requires_human_review: true,
        audit_log_ref: 'memory://audit/demo.json',
        not_credit_approval: true,
        not_credit_contracting: true,
        does_not_define_real_rate: true,
        does_not_define_real_limit: true,
        not_simulated_qualified_proposal: true,
      }),
    });
  });

  await page.locator('#demo-scenario').selectOption('home_complex');
  await page.locator('#demo-policy').selectOption('baseline');
  await page.locator('#execute-demo').click();
  await expect(page.locator('#demo-status')).toHaveAttribute('data-state', 'success');
  await expect(page.locator('#demo-badge')).toHaveText('AO VIVO');
  await expect(page.locator('#selected-action')).toHaveText('route_to_specialist');
  await expect(page.locator('#eligible-actions')).toContainText('route_to_specialist');
  await expect(page.locator('#policy-version')).toHaveText('baseline_deterministic_v0.1');
  await expect(page.locator('#reason-codes')).toContainText('human_in_the_loop');
  await expect(page.locator('#authority-flags')).toContainText('não é aprovação');
});

test('falha ao vivo mantém badge, exige confirmação e usa contingência offline', async ({ page, context }) => {
  await page.evaluate(() => window.Reveal.slide(11));
  await page.route('http://127.0.0.1:8000/v1/decisions', (route) => route.abort());
  await page.locator('#demo-scenario').selectOption('guardrail_sensitive');
  await page.locator('#demo-policy').selectOption('adaptive');
  await page.locator('#execute-demo').click();
  await expect(page.locator('#demo-status')).toHaveAttribute('data-state', 'error');
  await expect(page.locator('#demo-badge')).toHaveText('AO VIVO');
  await expect(page.locator('#contingency-switch')).toBeVisible();
  await expect(page.locator('#use-contingency')).toBeDisabled();
  await page.locator('#confirm-contingency').check();
  await page.locator('#use-contingency').click();
  await expect(page.locator('#demo-badge')).toHaveText('CONTINGÊNCIA');
  await expect(page.locator('#demo-status')).toHaveAttribute('data-state', 'success');
  await expect(page.locator('#selected-action')).toHaveText('no_offer_now');
  await expect(page.locator('#guardrails')).toContainText('adversarial_or_unsafe_context');
  await context.setOffline(true);
  await page.reload();
  await page.waitForFunction(() => window.__DECK_READY__ === true);
  await page.evaluate(() => window.Reveal.slide(11));
  await page.locator('[data-demo-source="contingency"]').click();
  await page.locator('#confirm-contingency').check();
  await page.locator('#use-contingency').click();
  await expect(page.locator('#demo-badge')).toHaveText('CONTINGÊNCIA');
});

test('timeout ao vivo oferece a mesma contingência sem trocar o badge automaticamente', async ({ page }) => {
  await page.evaluate(() => {
    window.Reveal.slide(11);
    window.DEMO_CONFIG.timeoutMs = 100;
  });
  await page.route('http://127.0.0.1:8000/v1/decisions', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    await route.fulfill({ status: 200, body: '{}' });
  });
  await page.locator('#execute-demo').click();
  await expect(page.locator('#demo-status')).toHaveAttribute('data-state', 'timeout');
  await expect(page.locator('#demo-badge')).toHaveText('AO VIVO');
  await expect(page.locator('#contingency-switch')).toBeVisible();
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
