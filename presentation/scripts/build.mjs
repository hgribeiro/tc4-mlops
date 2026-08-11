import { createHash } from 'node:crypto';
import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const presentationDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repositoryDir = path.resolve(presentationDir, '..');
const sourceDir = path.join(presentationDir, 'src');
const distDir = path.join(presentationDir, 'dist');
const reportPath = path.join(repositoryDir, 'artifacts/official-experiment/report.json');
const officialArtifactsDir = path.dirname(reportPath);
const provenancePath = path.join(officialArtifactsDir, 'provenance.json');
const policyPath = path.join(officialArtifactsDir, 'policy.json');

const [reportContents, provenanceContents, policyContents] = await Promise.all([
  readFile(reportPath, 'utf8'),
  readFile(provenancePath, 'utf8'),
  readFile(policyPath, 'utf8'),
]);
const report = JSON.parse(reportContents);
const provenance = JSON.parse(provenanceContents);
const policy = JSON.parse(policyContents);
const sha256 = (contents) => createHash('sha256').update(contents).digest('hex');

if (
  report.experiment_schema_version !== 'offline_bandit_experiment_v0.1'
  || !Array.isArray(report.runs)
  || report.runs.length < 5
  || report.dataset?.row_count !== report.horizon_per_seed
  || report.reward_contract?.not_causal_evidence !== true
  || provenance.evidence_classification?.synthetic !== true
  || provenance.evidence_classification?.offline !== true
  || provenance.evidence_classification?.causal !== false
  || provenance.artifacts?.['report.json']?.sha256 !== sha256(reportContents)
  || provenance.artifacts?.['policy.json']?.sha256 !== sha256(policyContents)
  || policy.experiment_ref !== report.experiment_ref
  || policy.policy_version !== provenance.experiment?.adaptive_policy_version
) {
  throw new Error('Os artefatos oficiais não satisfazem o contrato de proveniência do deck.');
}

await rm(distDir, { recursive: true, force: true });
await cp(sourceDir, distDir, { recursive: true });
await mkdir(path.join(distDir, 'assets'), { recursive: true });
await mkdir(path.join(distDir, 'vendor/reveal'), { recursive: true });
await mkdir(path.join(distDir, 'vendor/plotly'), { recursive: true });
await mkdir(path.join(distDir, 'vendor/mermaid'), { recursive: true });
await mkdir(path.join(distDir, 'data'), { recursive: true });

const apiUrl = process.env.DEMO_API_URL ?? 'http://127.0.0.1:8000';
const timeoutMs = Number(process.env.DEMO_API_TIMEOUT_MS ?? 5000);
if (!Number.isInteger(timeoutMs) || timeoutMs < 100) {
  throw new Error('DEMO_API_TIMEOUT_MS deve ser um inteiro >= 100.');
}

await Promise.all([
  cp(path.join(presentationDir, 'node_modules/reveal.js/dist/reveal.js'), path.join(distDir, 'vendor/reveal/reveal.js')),
  cp(path.join(presentationDir, 'node_modules/reveal.js/dist/reveal.css'), path.join(distDir, 'vendor/reveal/reveal.css')),
  cp(path.join(presentationDir, 'node_modules/reveal.js/plugin/notes/notes.js'), path.join(distDir, 'vendor/reveal/notes.js')),
  cp(path.join(presentationDir, 'node_modules/plotly.js-dist-min/plotly.min.js'), path.join(distDir, 'vendor/plotly/plotly.min.js')),
  cp(path.join(presentationDir, 'node_modules/mermaid/dist/mermaid.min.js'), path.join(distDir, 'vendor/mermaid/mermaid.min.js')),
  cp(reportPath, path.join(distDir, 'data/report.json')),
  cp(path.join(officialArtifactsDir, 'provenance.json'), path.join(distDir, 'data/provenance.json')),
  cp(path.join(officialArtifactsDir, 'policy.json'), path.join(distDir, 'data/policy.json')),
  cp(path.join(sourceDir, 'data/contingency-responses.json'), path.join(distDir, 'data/contingency-responses.json')),
]);

await writeFile(
  path.join(distDir, 'assets/report-data.js'),
  `window.OFFICIAL_REPORT = ${JSON.stringify(report)};\n`,
  'utf8',
);

const contingency = JSON.parse(
  await readFile(path.join(sourceDir, 'data/contingency-responses.json'), 'utf8'),
);
if (contingency.version !== 'contingency_responses_v1' || typeof contingency.responses !== 'object') {
  throw new Error('Respostas de contingência versionadas inválidas.');
}
await Promise.all([
  writeFile(
    path.join(distDir, 'assets/runtime-config.js'),
    `window.DEMO_CONFIG = ${JSON.stringify({ apiUrl, timeoutMs })};\n`,
    'utf8',
  ),
  writeFile(
    path.join(distDir, 'assets/contingency-data.js'),
    `window.CONTINGENCY_RESPONSES = ${JSON.stringify(contingency)};\n`,
    'utf8',
  ),
]);

console.log(`Deck offline gerado em ${path.relative(repositoryDir, distDir)} (${report.runs.length} seeds, ${report.dataset.row_count} registros por seed; API configurada no build).`);
