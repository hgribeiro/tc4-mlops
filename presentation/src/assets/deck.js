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

  const configureInteractiveDemo = () => {
    const scenario = document.querySelector('#demo-scenario');
    const policy = document.querySelector('#demo-policy');
    const execute = document.querySelector('#execute-demo');
    const status = document.querySelector('#demo-status');
    const output = document.querySelector('#decision-output');
    const badge = document.querySelector('#demo-badge');
    const apiUrlElement = document.querySelector('#demo-api-url');
    const contingencySwitch = document.querySelector('#contingency-switch');
    const confirmation = document.querySelector('#confirm-contingency');
    const useContingency = document.querySelector('#use-contingency');
    const sourceButtons = [...document.querySelectorAll('[data-demo-source]')];
    const config = window.DEMO_CONFIG ?? {};
    const contingencies = window.CONTINGENCY_RESPONSES?.responses ?? {};
    let source = 'live';

    if (apiUrlElement) {
      apiUrlElement.textContent = config.apiUrl ? `API: ${config.apiUrl}` : 'API não configurada no build';
    }

    const setStatus = (message, state = 'idle') => {
      status.textContent = message;
      status.dataset.state = state;
    };
    const setBadge = (mode) => {
      badge.textContent = mode === 'live' ? 'AO VIVO' : 'CONTINGÊNCIA';
      badge.className = `demo-badge ${mode === 'live' ? 'live' : 'contingency'}`;
    };
    const setSource = (mode) => {
      source = mode;
      setBadge(mode);
      sourceButtons.forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.demoSource === mode));
      });
      if (mode === 'contingency') {
        confirmation.checked = false;
        useContingency.disabled = true;
        contingencySwitch.hidden = false;
        execute.disabled = true;
        setStatus('Contingência selecionada. Confirme antes de exibir a resposta estática.', 'idle');
      } else {
        contingencySwitch.hidden = true;
        execute.disabled = false;
        setStatus('Pronto para executar um cenário oficial.', 'idle');
      }
    };
    const fillList = (selector, values, emptyLabel) => {
      const list = document.querySelector(selector);
      list.replaceChildren();
      const items = values.length ? values : [emptyLabel];
      items.forEach((value) => {
        const item = document.createElement('li');
        item.textContent = value;
        list.append(item);
      });
    };
    const renderDecision = (decision, mode) => {
      document.querySelector('#selected-action').textContent = decision.selected_action;
      fillList('#eligible-actions', decision.eligible_actions ?? [], 'Nenhuma ação elegível');
      document.querySelector('#policy-version').textContent = decision.policy_version;
      document.querySelector('#audit-log-ref').textContent = decision.audit_log_ref;
      fillList('#reason-codes', decision.reason_codes ?? [], 'Nenhum Reason Code');
      fillList('#guardrails', decision.guardrails_triggered ?? [], 'Nenhum Guardrail acionado');
      document.querySelector('#human-review').textContent = decision.requires_human_review ? 'Sim' : 'Não';
      const authority = [
        ['not_credit_approval', 'não é aprovação'],
        ['not_credit_contracting', 'não é contratação'],
        ['does_not_define_real_rate', 'não define taxa real'],
        ['does_not_define_real_limit', 'não define limite real'],
        ['not_simulated_qualified_proposal', 'não é Proposta Qualificada Simulada'],
      ].filter(([key]) => decision[key]).map(([, label]) => label);
      document.querySelector('#authority-flags').textContent = `Limites de autoridade: ${authority.join(' · ') || 'não informados'}`;
      output.hidden = false;
      setBadge(mode);
      setStatus(mode === 'live' ? 'Resposta recebida e auditada pela API.' : 'Resposta estática versionada exibida em contingência.', 'success');
    };
    const showContingencyOffer = (state, message) => {
      output.hidden = true;
      source = 'live';
      setBadge('live');
      sourceButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.demoSource === 'live')));
      contingencySwitch.hidden = false;
      confirmation.checked = false;
      useContingency.disabled = true;
      execute.disabled = false;
      setStatus(message, state);
    };
    const contingencyForSelection = () => contingencies[scenario.value]?.[policy.value];

    sourceButtons.forEach((button) => button.addEventListener('click', () => setSource(button.dataset.demoSource)));
    confirmation.addEventListener('change', () => { useContingency.disabled = !confirmation.checked; });
    useContingency.addEventListener('click', () => {
      if (!confirmation.checked) return;
      const decision = contingencyForSelection();
      if (!decision) {
        setStatus('Resposta de contingência indisponível para a seleção.', 'error');
        return;
      }
      renderDecision(decision, 'contingency');
      contingencySwitch.hidden = true;
      execute.disabled = false;
    });
    execute.addEventListener('click', async () => {
      if (source !== 'live') return;
      output.hidden = true;
      contingencySwitch.hidden = true;
      execute.disabled = true;
      setStatus('Consultando a API de Demonstração…', 'loading');
      const controller = new AbortController();
      const timeout = window.setTimeout(() => controller.abort(), Number(config.timeoutMs) || 5000);
      try {
        if (!config.apiUrl) throw new Error('API_URL_NOT_CONFIGURED');
        const endpoint = `${String(config.apiUrl).replace(/\/$/, '')}/v1/decisions`;
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ scenario_id: scenario.value, policy_mode: policy.value }),
          signal: controller.signal,
        });
        if (!response.ok) throw new Error(`HTTP_${response.status}`);
        const decision = await response.json();
        renderDecision(decision, 'live');
        contingencySwitch.hidden = true;
      } catch (error) {
        const timedOut = error?.name === 'AbortError';
        showContingencyOffer(timedOut ? 'timeout' : 'error', timedOut
          ? 'Tempo esgotado na API. Nenhum fallback ocorreu; confirme a contingência abaixo.'
          : 'Não foi possível obter uma resposta ao vivo. Nenhum fallback ocorreu; confirme a contingência abaixo.');
      } finally {
        window.clearTimeout(timeout);
      }
    });
  };

  Promise.all([rewardPlot, upliftPlot, exposurePlot, mermaidReady, revealReady]).then(() => {
    configureInteractiveDemo();
    window.__DECK_READY__ = true;
    document.documentElement.dataset.deckReady = 'true';
  });
})();
