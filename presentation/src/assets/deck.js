(() => {
  const report = window.OFFICIAL_REPORT;
  if (!report) throw new Error('Relatório oficial não foi incorporado ao build.');

  const metrics = report.metrics;
  const pt = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1, minimumFractionDigits: 1 });
  const integer = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
  const percentage = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 2 });

  const display = {
    sample: integer.format(report.dataset.row_count),
    'seed-count': integer.format(report.seeds.length),
    seeds: `${integer.format(report.seeds.length)} seeds`,
    'arm-count': `${integer.format(report.actions.length)} Braços`,
    'baseline-structural-zero-count': integer.format(
      report.actions.filter((action) => metrics.baseline_exposure[action] === 0).length,
    ),
    'low-home-exposure': `${pt.format(metrics.adaptive_exposure.simulate_home_equity)}/seed`,
    'low-investment-exposure': `${pt.format(metrics.adaptive_exposure.simulate_investment_secured_loan)}/seed`,
    horizon: `${integer.format(report.horizon_per_seed)} decisões por seed`,
    'baseline-reward': pt.format(metrics.baseline_cumulative_reward_mean),
    'adaptive-reward': pt.format(metrics.adaptive_cumulative_reward_mean),
    uplift: `+${pt.format(metrics.uplift_mean)}`,
    'uplift-stddev': pt.format(metrics.uplift_stddev),
    regret: pt.format(metrics.adaptive_cumulative_regret_mean),
    exploration: percentage.format(metrics.exploration_rate_mean),
  };

  Object.entries(display).forEach(([name, value]) => {
    document.querySelectorAll(`[data-metric="${name}"]`).forEach((element) => {
      element.textContent = value;
    });
  });

  const colors = {
    baseline: '#75829a',
    adaptive: '#39d4b4',
    accent: '#f4b860',
    text: '#eef3fa',
    grid: '#314159',
    transparent: 'rgba(0,0,0,0)',
  };
  const font = { family: 'Inter, Aptos, Segoe UI, sans-serif', color: colors.text, size: 19 };
  const commonLayout = {
    paper_bgcolor: colors.transparent,
    plot_bgcolor: colors.transparent,
    font,
    margin: { l: 90, r: 40, t: 35, b: 75 },
    showlegend: false,
    autosize: true,
  };
  const plotConfig = { displayModeBar: false, responsive: true, staticPlot: true };

  const rewardComparison = {
    x: ['Baseline Determinístico', 'Política Adaptativa'],
    y: [metrics.baseline_cumulative_reward_mean, metrics.adaptive_cumulative_reward_mean],
  };
  const upliftBySeed = {
    x: report.runs.map((run) => `seed ${run.seed}`),
    y: report.runs.map((run) => run.uplift),
  };
  const actionLabels = {
    educational_content_secured_credit: 'Conteúdo educativo',
    no_offer_now: 'no_offer_now',
    request_documents: 'Solicitar documentos',
    route_to_specialist: 'Encaminhar especialista',
    simulate_home_equity: 'Simular imóvel',
    simulate_investment_secured_loan: 'Simular investimentos',
    simulate_vehicle_secured_loan: 'Simular veículo',
  };
  const exposureActions = report.actions;
  const exposure = {
    actions: exposureActions.map((action) => actionLabels[action] ?? action),
    baseline: exposureActions.map((action) => metrics.baseline_exposure[action]),
    adaptive: exposureActions.map((action) => metrics.adaptive_exposure[action]),
  };
  window.__DECK_CHARTS__ = { rewardComparison, upliftBySeed, exposure };

  const rewardPlot = window.Plotly.newPlot('reward-chart', [{
    type: 'bar',
    x: rewardComparison.x,
    y: rewardComparison.y,
    marker: { color: [colors.baseline, colors.adaptive], line: { width: 0 } },
    text: rewardComparison.y.map((value) => pt.format(value)),
    textposition: 'outside',
    cliponaxis: false,
    hoverinfo: 'skip',
  }], {
    ...commonLayout,
    yaxis: { title: 'Recompensa acumulada média', gridcolor: colors.grid, rangemode: 'tozero' },
    xaxis: { tickfont: { size: 21 } },
  }, plotConfig);

  const upliftPadding = Math.max(1, (Math.max(...upliftBySeed.y) - Math.min(...upliftBySeed.y)) * 0.3);
  const upliftPlot = window.Plotly.newPlot('uplift-chart', [{
    type: 'scatter',
    mode: 'lines+markers+text',
    x: upliftBySeed.x,
    y: upliftBySeed.y,
    line: { color: colors.adaptive, width: 5 },
    marker: { color: colors.accent, size: 14 },
    text: upliftBySeed.y.map((value) => integer.format(value)),
    textposition: 'top center',
    hoverinfo: 'skip',
  }], {
    ...commonLayout,
    yaxis: {
      title: 'Uplift absoluto',
      gridcolor: colors.grid,
      range: [Math.min(...upliftBySeed.y) - upliftPadding, Math.max(...upliftBySeed.y) + upliftPadding],
    },
    xaxis: { tickfont: { size: 20 } },
  }, plotConfig);

  const exposurePlot = window.Plotly.newPlot('exposure-chart', [
    {
      type: 'bar', orientation: 'h', name: 'Baseline', y: exposure.actions,
      x: exposure.baseline.map((value) => value === 0 ? null : value),
      marker: { color: colors.baseline }, hoverinfo: 'skip',
    },
    {
      type: 'bar', orientation: 'h', name: 'Adaptativa', y: exposure.actions,
      x: exposure.adaptive, marker: { color: colors.adaptive }, hoverinfo: 'skip',
    },
  ], {
    ...commonLayout,
    showlegend: true,
    legend: { orientation: 'h', x: 0.58, y: 1.12 },
    barmode: 'group',
    margin: { l: 265, r: 35, t: 45, b: 60 },
    xaxis: { title: 'Exposição média por seed · escala log', type: 'log', gridcolor: colors.grid },
    yaxis: { automargin: true, autorange: 'reversed' },
  }, plotConfig);

  window.mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'base',
    themeVariables: {
      background: '#101827',
      primaryColor: '#1b2a3e',
      primaryTextColor: colors.text,
      primaryBorderColor: colors.adaptive,
      lineColor: '#8fa2bb',
      secondaryColor: '#243550',
      tertiaryColor: '#152238',
      fontFamily: font.family,
      fontSize: '20px',
    },
    flowchart: { curve: 'basis', htmlLabels: true },
  });

  const mermaidReady = window.mermaid.run({ querySelector: '.mermaid' });
  const revealReady = window.Reveal.initialize({
    width: 1600,
    height: 900,
    margin: 0.045,
    minScale: 0.2,
    maxScale: 1.5,
    hash: true,
    controls: true,
    progress: true,
    center: false,
    transition: 'fade',
    backgroundTransition: 'fade',
    plugins: [window.RevealNotes],
  });

  Promise.all([rewardPlot, upliftPlot, exposurePlot, mermaidReady, revealReady]).then(() => {
    window.__DECK_READY__ = true;
    document.documentElement.dataset.deckReady = 'true';
  });
})();
