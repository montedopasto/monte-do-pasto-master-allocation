// Resumo da App de Alocação para a verificação diária.
// Abre a própria app (mesma lógica) num browser sem janela e devolve um JSON com:
// zona verde (vendido / por vender, fecho de quarentena), alerta de animais acima do peso e próximas cargas.
// Uso: node resumo_app.js <pasta com App_Alocacao_Animais.html e _controlo/*.js> [dias_cargas=21]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2] || '.');
  const horizon = Number(process.argv[3] || 21);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 1100 } });
  const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('file://' + path.join(dir, 'App_Alocacao_Animais.html'));
  await p.waitForTimeout(2000);
  const out = await p.evaluate((H) => {
    const r = { fonte: DB.source, animais: DB.rows.length, analises: (typeof anaInfoText === 'function' ? anaInfoText() : '') };
    // zona verde
    const secOf = {}; (DB.qsec || []).forEach(([n, s]) => { secOf[n] = s; });
    const g = {};
    DB.rows.forEach((a) => {
      const n = String(a.alloc).trim(); if (secOf[n] !== 'Exportação') return;
      const x = g[n] || (g[n] = { alocacao: n, vendido_a: saleOf(n) || '', animais: 0, M: 0, F: 0, quarentenas: {}, sem_quarentena: 0 });
      x.animais++; if (a.m) x.M++; else x.F++;
      if (a.q >= 0) { const k = fmt(a.q); x.quarentenas[k] = (x.quarentenas[k] || 0) + 1; } else x.sem_quarentena++;
    });
    r.zona_verde = Object.values(g).map((x) => Object.assign(x, { aptos_35d: Object.keys(x.quarentenas).map((d) => { const [dd, mm, yy] = d.split('-').map(Number); return fmt(Math.floor(Date.UTC(yy, mm - 1, dd) / DAY) + 35); }) }));
    r.zona_verde_totais = { vendido: r.zona_verde.filter((x) => x.vendido_a).reduce((s, x) => s + x.animais, 0), por_vender: r.zona_verde.filter((x) => !x.vendido_a).reduce((s, x) => s + x.animais, 0) };
    // cargas
    r.cargas = {};
    ['angus', 'esp'].forEach((grp) => {
      GA.grp = grp; const P = planAngus();
      r.cargas[grp] = {
        grupo: G_GRPS[grp].label,
        acima_do_peso: P.heavy.length,
        acima_do_peso_lista: P.heavy.slice(0, 15).map((a) => ({ sia: 'PT' + a.id, sexo: a.m ? 'M' : 'F', alocacao: a.alloc, parque: a.g, peso_hoje: kgAt(a, TODAY), excesso: kgAt(a, TODAY) - P.rng(a)[1], ultima_pesagem: a.wd > 0 ? fmt(a.wd) : '' })),
        camioes: P.trucks.length,
        proximos: P.trucks.filter((t) => t.date <= TODAY + H).map((t) => ({ data: fmt(t.date), destino: gDest(t.list[0].a.alloc), alocacao: t.list[0].a.alloc, animais: t.n, machos: t.nM, femeas: t.n - t.nM, carga_kg: Math.round(t.kg), pesagem_mais_50_dias: t.oldW, sem_angus_certificado: grp === 'angus' ? t.noCert : undefined })),
        a_aguardar_completar: P.rest.reduce((s, x) => s + x.list.length, 0)
      };
    });
    return r;
  }, horizon);
  out.erros = errs;
  console.log(JSON.stringify(out, null, 1));
  await b.close();
})();
