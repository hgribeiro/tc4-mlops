import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, stat } from 'node:fs/promises';
import test from 'node:test';

const dist = new URL('../dist/', import.meta.url);

async function text(path) {
  return readFile(new URL(path, dist), 'utf8');
}

test('build empacota dependências e evidência oficial sem recursos remotos', async () => {
  const html = await text('index.html');
  const css = await text('assets/deck.css');
  const runtimeReferences = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map((match) => match[1]);

  assert.equal(runtimeReferences.some((value) => /^https?:|^\/\//.test(value)), false);
  assert.doesNotMatch(css, /@import\s+url\(['"]?https?:|url\(['"]?https?:/i);
  for (const reference of runtimeReferences.filter((value) => !value.startsWith('#'))) {
    assert.ok((await stat(new URL(reference, dist))).size > 0, `${reference} deve existir no build`);
  }

  for (const asset of [
    'vendor/reveal/reveal.js',
    'vendor/reveal/reveal.css',
    'vendor/reveal/notes.js',
    'vendor/plotly/plotly.min.js',
    'vendor/mermaid/mermaid.min.js',
    'assets/report-data.js',
    'assets/runtime-config.js',
    'assets/contingency-data.js',
    'data/contingency-responses.json',
    'data/report.json',
    'data/provenance.json',
    'data/policy.json',
  ]) {
    assert.ok((await stat(new URL(asset, dist))).size > 0, `${asset} deve existir`);
  }
});

test('build incorpora exatamente o relatório oficial versionado', async () => {
  const official = JSON.parse(
    await readFile(new URL('../../artifacts/official-experiment/report.json', import.meta.url), 'utf8'),
  );
  const generated = await text('assets/report-data.js');
  const payload = JSON.parse(generated.trim().match(/^window\.OFFICIAL_REPORT = (.*);$/s)?.[1] ?? 'null');

  assert.deepEqual(payload, official);
  assert.equal(payload.runs.length, 5);
  assert.equal(payload.dataset.row_count, 45211);
  assert.equal(payload.reward_contract.not_causal_evidence, true);
});

test('build preserva a proveniência e os hashes oficiais', async () => {
  const officialDir = new URL('../../artifacts/official-experiment/', import.meta.url);
  const [report, policy, provenance] = await Promise.all([
    readFile(new URL('report.json', officialDir), 'utf8'),
    readFile(new URL('policy.json', officialDir), 'utf8'),
    readFile(new URL('provenance.json', officialDir), 'utf8'),
  ]);
  const copiedProvenance = await text('data/provenance.json');
  const copiedPolicy = await text('data/policy.json');
  const manifest = JSON.parse(provenance);
  const hash = (contents) => createHash('sha256').update(contents).digest('hex');

  assert.equal(copiedProvenance, provenance);
  assert.equal(copiedPolicy, policy);
  assert.equal(manifest.artifacts['report.json'].sha256, hash(report));
  assert.equal(manifest.artifacts['policy.json'].sha256, hash(policy));
  assert.equal(manifest.evidence_classification.causal, false);
});
