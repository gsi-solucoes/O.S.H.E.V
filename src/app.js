'use strict';
/* ===== Raio X do Relatório · app (etapa 1: shell genérico) ===== */
const $ = s => document.querySelector(s);
const el = (tag, p, ...kids) => {
  const e = document.createElement(tag);
  if (p) for (const [a, v] of Object.entries(p)) { if (a === 'class') e.className = v; else if (a === 'text') e.textContent = v; else if (a.startsWith('on')) e[a] = v; else e.setAttribute(a, v); }
  kids.flat().forEach(x => { if (x != null && x !== false) e.append(x.nodeType ? x : document.createTextNode(String(x))); });
  return e;
};
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const store = { get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { toast('Sem espaço para guardar neste aparelho.'); } } };
const TIPOS = [['ignorar', 'Ignorar'], ['codigo', 'Código'], ['data', 'Data'], ['categoria', 'Categoria'], ['situacao', 'Situação'], ['texto', 'Texto'], ['numero', 'Número']];

const nulo = () => Object.create(null);   // mapa sem herança: 'constructor', '__proto__' etc. são chaves comuns
const copiaNula = o => { const r = nulo(); if (o && typeof o === 'object' && !Array.isArray(o)) Object.keys(o).forEach(k => { r[k] = o[k]; }); return r; };
const LIM = { csv: 50 * 1048576, logo: 2 * 1048576, backup: 200 * 1048576 };
const mb = n => Math.round(n / 1048576) + ' MB';
const TIPOS_OK = new Set(TIPOS.map(x => x[0]));
// todo valor de registro vira texto simples; objeto vira JSON em texto (nunca fórmula/hiperlink)
const paraTexto = x => { if (x == null) return ''; if (typeof x === 'string') return x; if (typeof x === 'number' || typeof x === 'boolean') return String(x); try { return JSON.stringify(x) || ''; } catch (e) { return ''; } };
// segunda barreira para o Excel: só string, número finito, Date ou null
// B-1 (revisão etapa 2): escolhas de indicadores vindas de fora (backup, localStorage): até 200 conjuntos, listas de strings sem repetidos (até 500 ids de até 1000 caracteres); inválido = null
function acompLimpa(o) {
  if (!o || typeof o !== 'object' || Array.isArray(o)) return null;
  const ks = Object.keys(o); if (ks.length > 200) return null;
  const r = Object.create(null);
  for (const k of ks) { const l = o[k]; if (!Array.isArray(l) || l.length > 500 || !l.every(x => typeof x === 'string' && x.length <= 1000)) return null; r[k] = [...new Set(l)]; }
  return r;
}
const primitivo = x => x == null ? null : x instanceof Date ? (isNaN(x) ? null : x) : typeof x === 'number' ? (isFinite(x) ? x : null) : typeof x === 'string' ? x : paraTexto(x);
const cfgLimpa = (o, base) => { const c = Object.assign({}, base); if (!o || typeof o !== 'object') return c; ['cliente', 'area', 'sinonimos'].forEach(k => { if (typeof o[k] === 'string') c[k] = o[k].slice(0, 5000); }); ['meta', 'prazoH'].forEach(k => { if (typeof o[k] === 'number' && isFinite(o[k])) c[k] = o[k]; }); if (typeof o.logo === 'string' && (o.logo === '' || /^data:image\/png;base64,[A-Za-z0-9+\/=]*$/.test(o.logo))) c.logo = o.logo; return c; };
const camposOk = l => Array.isArray(l) && l.every(x => x && typeof x === 'object' && typeof x.n === 'string' && x.n.trim() && TIPOS_OK.has(x.t));
// valida o backup inteiro e devolve cópias limpas; null se inválido (nada é alterado antes disso)
function validarBackup(b) {
  try {
    if (!b || typeof b !== 'object' || b.app !== 'raiox' || !Array.isArray(b.registros)) return null;
    const cj = nulo(), fm = nulo(), rg = [];
    if (b.conjs != null) { if (typeof b.conjs !== 'object' || Array.isArray(b.conjs)) return null; for (const k of Object.keys(b.conjs)) { const x = b.conjs[k]; if (!k.trim() || !x || !camposOk(x.campos)) return null; cj[k] = { campos: x.campos.map(y => ({ n: y.n, t: y.t })) }; } }
    if (b.fmts != null) { if (typeof b.fmts !== 'object' || Array.isArray(b.fmts)) return null; for (const k of Object.keys(b.fmts)) { const x = b.fmts[k]; if (!x || typeof x.conjunto !== 'string' || !x.conjunto.trim() || !camposOk(x.cols)) return null; fm[k] = { conjunto: x.conjunto, cols: x.cols.map(y => ({ n: y.n, t: y.t })) }; } }
    for (const x of b.registros) {
      if (!x || typeof x !== 'object' || typeof x.conjunto !== 'string' || !x.conjunto.trim() || !cj[x.conjunto]) return null;
      if (!(typeof x.codigo === 'string' || typeof x.codigo === 'number') || String(x.codigo).trim() === '') return null;
      if (!x.v || typeof x.v !== 'object' || Array.isArray(x.v)) return null;
      const v = nulo(); for (const k of Object.keys(x.v)) { const t = paraTexto(x.v[k]); if (t !== '') v[k] = t; }
      rg.push({ conjunto: x.conjunto, codigo: String(x.codigo), v });
    }
    if (b.cfg != null && (typeof b.cfg !== 'object' || Array.isArray(b.cfg))) return null;
    const ac = nulo();
    if (b.acomp != null) { if (typeof b.acomp !== 'object' || Array.isArray(b.acomp)) return null; const r = acompLimpa(b.acomp); if (!r) return null; Object.assign(ac, r); }
    return { conjs: cj, fmts: fm, registros: rg, cfg: b.cfg ? cfgLimpa(b.cfg, {}) : null, acomp: ac };
  } catch (e) { return null; }
}
let cfg = cfgLimpa(store.get('gos_cfg', {}), { cliente: '', area: '', logo: '', meta: 90, prazoH: 24, sinonimos: '' });
let fmts = copiaNula(store.get('raiox_fmt', {}));     // formato lembrado: assinatura das colunas -> {conjunto, cols:[{n,t}]}
let conjs = copiaNula(store.get('raiox_conj', {}));   // conjunto -> {campos:[{n,t}]}
let acomp = acompLimpa(store.get('raiox_acomp', {})) || nulo();   // conjunto -> [id dos indicadores escolhidos, na ordem em que foram marcados]
let regs = [];                             // {conjunto, codigo, v:{campo:valor}}
let mapa = new Map();
const F = { conjunto: '', per: 'tudo', mes: '', de: '', ate: '', cd: '', cat: '', val: '', q: '', tA: '', tB: '' };
let mostrar = 50;
const salvaCfg = () => store.set('gos_cfg', cfg);
const salvaConjs = () => store.set('raiox_conj', conjs);
const salvaAcomp = () => store.set('raiox_acomp', acomp);
const chave = (c, k) => c + '\u0001' + k;

function toast(txt) { const t = $('#toast'); t.textContent = txt; t.style.display = 'block'; clearTimeout(toast.h); toast.h = setTimeout(() => { t.style.display = 'none'; }, 5000); }
const hojeISO = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
const fmtData = s => { const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(s || ''); return m ? m[3] + '/' + m[2] + '/' + m[1] + (m[4] + m[5] !== '0000' ? ' ' + m[4] + ':' + m[5] : '') : (s || ''); };
const slug = s => Core.norm(s).replace(/\s+/g, '_') || 'Relatorio';
const ORG = () => [cfg.area, cfg.cliente].filter(Boolean).join(' · ');

/* ---------- IndexedDB (mesmo banco do uso anterior; 'os' fica intacto, 'registros' é o novo) ---------- */
const IDB = {
  db: null,
  open() {
    if (!this.db) this.db = new Promise((ok, no) => {
      const r = indexedDB.open('gos_hist', 2);
      r.onupgradeneeded = () => { const d = r.result; if (!d.objectStoreNames.contains('os')) d.createObjectStore('os', { keyPath: 'os' }); if (!d.objectStoreNames.contains('registros')) d.createObjectStore('registros', { keyPath: ['conjunto', 'codigo'] }); };
      r.onsuccess = () => ok(r.result); r.onerror = () => no(r.error);
    });
    return this.db;
  },
  async run(nome, modo, fn) { const db = await this.open(); return new Promise((ok, no) => { const tx = db.transaction(nome, modo), st = tx.objectStore(nome); let res; const q = fn(st); if (q && 'onsuccess' in q) q.onsuccess = () => { res = q.result; }; tx.oncomplete = () => ok(res); tx.onerror = () => no(tx.error); }); },
  all() { return this.run('registros', 'readonly', s => s.getAll()).then(x => x || []); },
  put(list) { return this.run('registros', 'readwrite', s => { list.forEach(x => s.put(x)); }); },
  clear() { return this.run('registros', 'readwrite', s => s.clear()); },
  oldAll() { return this.run('os', 'readonly', s => s.getAll()).then(x => x || []); },
  oldKey() { return this.open().then(d => d.transaction('os').objectStore('os').keyPath); },
  oldClear() { return this.run('os', 'readwrite', s => s.clear()); }
};

/* ---------- migração do histórico antigo (store 'os'), sem perder nada ---------- */
async function migrar() {
  if (localStorage.getItem('raiox_migrado')) return;
  const velhos = await IDB.oldAll(); if (!velhos.length) return;
  const kp = await IDB.oldKey(), nome = 'Histórico anterior';
  const chaves = []; velhos.forEach(o => Object.keys(o).forEach(k => { if (chaves.indexOf(k) < 0) chaves.push(k); }));
  const tipo = k => {
    if (k === kp) return 'codigo';
    const vs = velhos.slice(0, 500).map(o => o[k]).filter(v => v != null && v !== '');
    if (vs.length && vs.every(v => typeof v === 'number' && v > 1e11 && v < 4e12)) return 'data';
    if (vs.length && vs.every(v => typeof v === 'number')) return 'numero';
    const u = new Set(vs.map(v => Array.isArray(v) ? v.join('; ') : String(v)));
    return u.size <= 20 ? 'categoria' : 'texto';
  };
  const campos = chaves.map(k => ({ n: k, t: tipo(k) }));
  const lista = velhos.map(o => {
    const v = nulo();
    campos.forEach(c => { let x = o[c.n]; if (x == null || x === '') return; v[c.n] = c.t === 'data' ? Core.iso(new Date(x)) : Array.isArray(x) ? x.join('; ') : String(x); });
    return { conjunto: nome, codigo: String(o[kp]), v };
  });
  conjs[nome] = { campos }; salvaConjs();
  await IDB.put(lista); localStorage.setItem('raiox_migrado', String(velhos.length)); // o store antigo 'os' fica intacto
}

/* ---------- leitura do arquivo ---------- */
function perguntar(tit, txt, botoes) {
  return new Promise(ok => {
    const d = $('#dlgPergunta'); $('#pgTit').textContent = tit; $('#pgTxt').textContent = txt;
    const b = $('#pgBtns'); b.textContent = '';
    botoes.forEach(x => b.append(el('button', { class: x.prim ? 'prim' : '', type: 'button', text: x.t, onclick: () => { d.close(); ok(x.v); } })));
    d.oncancel = () => ok(null); d.showModal();
  });
}
function perguntarColunas(arquivo, hdr, corpo) {
  return new Promise(ok => {
    const d = $('#dlgCol'), f = $('#fCol'); f.textContent = '';
    const pal = Core.palpites(hdr, corpo), erro = el('p', { class: 'muted', role: 'alert' });
    const nomeRel = el('input', { type: 'text', id: 'colRel', value: arquivo.replace(/\.[^.]+$/, '') });
    const linhas = hdr.map((h, j) => {
      const ex = corpo.map(r => Core.t(r[j])).find(Boolean) || '';
      const nome = el('input', { type: 'text', value: Core.t(h) || ('Campo ' + (j + 1)), 'aria-label': 'Nome do campo ' + (j + 1) });
      const tp = el('select', { 'aria-label': 'Tipo da coluna ' + (j + 1) }, TIPOS.map(([v, t]) => el('option', { value: v, text: t })));
      tp.value = pal[j];
      return { nome, tp, tr: el('tr', null, el('td', { text: Core.t(h) }), el('td', { text: ex.slice(0, 40) }), el('td', null, nome), el('td', null, tp)) };
    });
    f.append(el('h3', { text: 'Esta coluna é o quê?' }), el('p', { class: 'muted', text: 'Arquivo: ' + arquivo + '. Responda uma vez: o formato fica lembrado. Escolha uma coluna como Código (identifica cada registro).' }),
      el('label', { class: 'f' }, 'Nome do relatório', nomeRel),
      el('div', { class: 'tw', style: 'max-height:50vh;overflow:auto;margin:10px 0' }, el('table', null, el('thead', null, el('tr', null, ['Coluna', 'Exemplo', 'Nome do campo', 'Tipo'].map(x => el('th', { text: x })))), el('tbody', null, linhas.map(l => l.tr)))), erro,
      el('div', { class: 'row' },
        el('button', { class: 'prim', type: 'button', id: 'colOk', text: 'Confirmar', onclick: () => {
          const tipos = linhas.map(l => l.tp.value), nc = tipos.filter(x => x === 'codigo').length;
          if (nc !== 1) { erro.textContent = 'Escolha exatamente uma coluna como Código.'; return; }
          const usados = {}, cols = linhas.map((l, j) => { let n = Core.t(l.nome.value) || ('Campo ' + (j + 1)); const b = n; let i = 2; while (usados[n.toLowerCase()]) n = b + ' ' + i++; usados[n.toLowerCase()] = 1; return { n, t: tipos[j] }; });
          d.close(); ok({ conjunto: Core.t(nomeRel.value) || 'Relatório', cols });
        } }),
        el('button', { type: 'button', text: 'Cancelar', onclick: () => { d.close(); ok(null); } })));
    d.oncancel = () => ok(null); d.showModal();
  });
}
async function lerArquivo(f) {
  if (f.size > LIM.csv) { toast(f.name + ': arquivo grande demais (' + mb(f.size) + '; o limite é ' + mb(LIM.csv) + ').'); return null; }
  const rows = Core.parseCSV(Core.decode(await f.arrayBuffer())), hi = Core.acharCabecalho(rows);
  if (hi < 0) { toast('Não achei o cabeçalho em ' + f.name + '.'); return null; }
  const hdr = rows[hi].map(Core.t), corpo = rows.slice(hi + 1).filter(r => r.some(x => Core.t(x)));
  const sig = Core.assinatura(hdr);
  let fm = fmts[sig];
  if (!fm) { fm = await perguntarColunas(f.name, hdr, corpo); if (!fm) return null; fmts[sig] = fm; store.set('raiox_fmt', fmts); }
  return await importar(fm, corpo);
}
async function importar(fm, corpo) {
  let c = fm.conjunto; const icod = fm.cols.findIndex(x => x.t === 'codigo'), campos = fm.cols.filter(x => x.t !== 'ignorar' && x.t !== 'codigo');
  const cod = fm.cols[icod].n;
  const noArq = new Map();
  corpo.forEach(r => {
    const k = Core.t(r[icod]); if (!k) return;
    const v = nulo(); fm.cols.forEach((x, j) => { if (x.t === 'ignorar' || x.t === 'codigo') return; let s = Core.t(r[j]); if (x.t === 'data') s = Core.dataISO(s); if (s) v[x.n] = s; });
    noArq.set(k, Core.juntar(noArq.get(k), v));
  });
  // Junção: mesmo nome de campo código e ao menos um código já guardado num conjunto -> entra nele, campo a campo.
  const comum = n => { for (const k of noArq.keys()) if (mapa.has(chave(n, k))) return true; return false; };
  const mesmoCod = n => (conjs[n].campos.find(y => y.t === 'codigo') || {}).n === cod;
  if (!(conjs[c] && mesmoCod(c) && comum(c))) { const alvo = Object.keys(conjs).find(n => mesmoCod(n) && comum(n)); if (alvo) c = alvo; }
  const atual = conjs[c] || { campos: [] };
  [{ n: cod, t: 'codigo' }].concat(campos).forEach(x => { if (!atual.campos.some(y => y.n === x.n)) atual.campos.push({ n: x.n, t: x.t }); });
  conjs[c] = atual; salvaConjs();
  const mudou = []; let novos = 0;
  noArq.forEach((v, k) => {
    const ant = mapa.get(chave(c, k));
    if (!ant) { const o = { conjunto: c, codigo: k, v }; regs.push(o); mapa.set(chave(c, k), o); mudou.push(o); novos++; }
    else { const nv = Core.juntar(ant.v, v); if (JSON.stringify(nv) !== JSON.stringify(ant.v)) { ant.v = nv; mudou.push(ant); } }
  });
  await IDB.put(mudou);
  return { c, lidos: noArq.size, novos };
}
async function carregar(files) {
  const msgs = [], tocados = [];
  for (const f of files) {
    try { const r = await lerArquivo(f); if (r) { msgs.push(r.c + ': ' + r.lidos + ' lidos, ' + r.novos + ' novos'); if (tocados.indexOf(r.c) < 0) tocados.push(r.c); } }
    catch (e) { toast('Não consegui ler ' + f.name + '.'); }
  }
  $('#status').textContent = msgs.join(' · ');
  if (!F.conjunto || !conjs[F.conjunto]) F.conjunto = Object.keys(conjs)[0] || '';
  mostrar = 50; render(); renderConfig();
  // D-09: conjunto ainda sem escolha salva abre a janela "O que você quer acompanhar?" sozinha
  for (const c of tocados) { if (!acomp[c] && conjs[c] && doConj(c).length) { F.conjunto = c; render(); await janelaAcomp(c); } }
}

/* ---------- filtros ---------- */
const camposDe = (c, t) => ((conjs[c] || {}).campos || []).filter(x => x.t === t || (t === 'categoria' && x.t === 'situacao'));   // situação também é categoria
const doConj = c => regs.filter(r => r.conjunto === c);
function campoData(c) { const ds = camposDe(c, 'data'); return (ds.find(x => x.n === F.cd) || ds[0] || {}).n; }
function filtrar(c, comCat) {
  let L = doConj(c); const cd = campoData(c);
  if (F.per !== 'tudo' && cd) {
    const de = F.per === 'mes' ? F.mes : F.de, ate = F.per === 'mes' ? F.mes : F.ate;
    L = L.filter(r => { const d = (r.v[cd] || '').slice(0, F.per === 'mes' ? 7 : 10); return d && (!de || d >= de) && (!ate || d <= ate); });
  } else if (F.per !== 'tudo') L = [];
  if (comCat !== false && F.cat && F.val && camposDe(c, 'categoria').some(x => x.n === F.cat)) L = L.filter(r => r.v[F.cat] === F.val);
  if (F.q) { const q = Core.norm(F.q); L = L.filter(r => Core.norm(r.codigo + ' ' + Object.values(r.v).join(' ')).indexOf(q) >= 0); }
  return L;
}
const textoFiltros = () => { const p = []; if (F.per === 'mes' && F.mes) p.push('Mês ' + F.mes); if (F.per === 'de') p.push('De ' + (F.de || '…') + ' até ' + (F.ate || '…')); if (F.cat && F.val) p.push(F.cat + ' = ' + F.val); if (F.q) p.push('Busca “' + F.q + '”'); return p.join(' · '); };

/* ---------- tela ---------- */
function fillSel(s, ops, cur) { s.textContent = ''; ops.forEach(([v, t]) => s.append(el('option', { value: v, text: t }))); if (ops.some(o => o[0] === cur)) s.value = cur; }
function tabela(campos, lista) {
  return el('table', null, el('thead', null, el('tr', null, campos.map(c => el('th', { text: c.n })))),
    el('tbody', null, lista.map(r => el('tr', null, campos.map(c => el('td', { text: c.t === 'codigo' ? r.codigo : c.t === 'data' ? fmtData(r.v[c.n]) : (r.v[c.n] || '') }))))));
}
function barras(itens, abrir) {
  const max = Math.max(1, ...itens.map(i => Math.abs(i[1])));
  return el('div', { class: 'bars' }, itens.map(([nome, n, lista, rot]) => el('button', { class: 'bar', type: 'button', onclick: () => abrir(nome, lista) }, el('span', { text: nome }), el('i', { style: 'width:' + Math.max(2, 100 * Math.abs(n) / max) + '%' }), el('b', { text: rot != null ? rot : n }))));
}
function agrupa(lista, fn) { const m = new Map(); lista.forEach(r => { const k = fn(r); if (k == null || k === '') return; (m.get(k) || m.set(k, []).get(k)).push(r); }); return m; }

function render() {
  const cs = Object.keys(conjs).filter(c => doConj(c).length);
  $('#semDados').hidden = cs.length > 0; $('#comDados').hidden = !cs.length;
  if (!cs.length) return;
  if (!conjs[F.conjunto]) F.conjunto = cs[0];
  const c = F.conjunto, camposC = conjs[c].campos;
  fillSel($('#fConj'), cs.map(x => [x, x]), c); $('#lConj').hidden = cs.length < 2;
  const ds = camposDe(c, 'data'), cats = camposDe(c, 'categoria');
  fillSel($('#fCD'), ds.map(x => [x.n, x.n]), F.cd); F.cd = $('#fCD').value; $('#lCD').hidden = ds.length < 2;
  fillSel($('#fCat'), [['', '(nenhum)']].concat(cats.map(x => [x.n, x.n])), F.cat); F.cat = $('#fCat').value;
  const base = filtrar(c, false);
  const vals = F.cat ? [...new Set(base.map(r => r.v[F.cat]).filter(Boolean))].sort() : [];
  fillSel($('#fVal'), [['', '(todos)']].concat(vals.map(x => [x, x])), F.val); F.val = $('#fVal').value;
  $('#fPer').value = F.per; $('#lMes').hidden = F.per !== 'mes'; $('#lDe').hidden = $('#lAte').hidden = F.per !== 'de';
  const L = filtrar(c), todos = doConj(c);
  const cd = campoData(c), datas = cd ? L.map(r => r.v[cd]).filter(Boolean).sort() : [];
  $('#kTotal b').textContent = L.length; $('#kTotal span').textContent = 'Total de registros' + (L.length !== todos.length ? ' (de ' + todos.length + ' guardados)' : '');
  $('#kAnt b').textContent = datas.length ? fmtData(datas[0]) : '—'; $('#kNov b').textContent = datas.length ? fmtData(datas[datas.length - 1]) : '—';
  $('#kAnt span').textContent = 'Mais antigo' + (cd && ds.length > 1 ? ' (' + cd + ')' : ''); $('#kNov span').textContent = 'Mais novo' + (cd && ds.length > 1 ? ' (' + cd + ')' : '');
  $('#kTotal').onclick = () => abrirJanela('Todos os registros', L, c);

  const escolhidos = blocosEscolhidos(c); $('#kpis').hidden = $('#blocos').hidden = !!escolhidos.length; $('#blocosEsc').hidden = !escolhidos.length;
  $('#btnEntender').hidden = !escolhidos.length; $('#blocosEsc').textContent = '';
  if (escolhidos.length) escolhidos.forEach(b => $('#blocosEsc').append(b.desenha(L, c)));
  const bl = $('#blocos'); bl.textContent = '';
  if (!escolhidos.length) cats.slice(0, 3).forEach(cat => {
    const g = [...agrupa(L, r => r.v[cat.n])].sort((a, b) => b[1].length - a[1].length).slice(0, 8).map(([k, l]) => [k, l.length, l]);
    if (g.length) bl.append(el('div', { class: 'card' }, el('h3', { text: 'Por ' + cat.n }), barras(g, (k, l) => abrirJanela(cat.n + ': ' + k, l, c))));
  });
  if (cd && !escolhidos.length) {
    const g = [...agrupa(L, r => (r.v[cd] || '').slice(0, 7))].sort((a, b) => a[0] < b[0] ? -1 : 1).slice(-12).map(([k, l]) => [k.slice(5) + '/' + k.slice(0, 4), l.length, l]);
    if (g.length) bl.append(el('div', { class: 'card' }, el('h3', { text: 'Por mês (' + cd + ')' }), barras(g, (k, l) => abrirJanela('Mês ' + k, l, c))));
  }
  if (ds.length >= 2 && !escolhidos.length) bl.append(cartaoTempo(L, c, ds));
  const txs = camposDe(c, 'texto');
  if (txs.length && !escolhidos.length) bl.append(el('div', { class: 'card' }, el('h3', { text: 'Possíveis repetidos' }), el('p', { class: 'muted', text: 'Registros com texto parecido em “' + txs[0].n + '”, para você decidir.' }),
    el('button', { type: 'button', id: 'btnRep', text: 'Procurar repetidos', onclick: () => procurarRepetidos(L, c, txs[0].n) })));

  const campos = camposC, vis = L.slice().sort((a, b) => cd ? (b.v[cd] || '').localeCompare(a.v[cd] || '') : a.codigo.localeCompare(b.codigo, 'pt', { numeric: true }));
  $('#tabReg').textContent = ''; $('#tabReg').append(tabela(campos, vis.slice(0, mostrar)));
  $('#maisReg').hidden = vis.length <= mostrar; $('#infoReg').textContent = 'Mostrando ' + Math.min(mostrar, vis.length) + ' de ' + vis.length;
  $('#maisReg').onclick = () => { mostrar += 100; render(); };
}
function parTempo(ds) { if (!ds.some(x => x.n === F.tA)) F.tA = ds[0].n; if (!ds.some(x => x.n === F.tB) || F.tB === F.tA) F.tB = (ds.find(x => x.n !== F.tA) || ds[1]).n; return [F.tA, F.tB]; }
const paresTempo = (L, A, B) => { const itens = []; L.forEach(r => { const a = Core.msISO(r.v[A]), b = Core.msISO(r.v[B]); if (a != null && b != null && b >= a) itens.push([r, b - a]); }); return itens; };
function cartaoTempo(L, c, ds, titulo) {
  parTempo(ds); const itens = paresTempo(L, F.tA, F.tB);
  const durs = itens.map(x => x[1]), pct = Core.pctDentro(durs, cfg.prazoH * 3600000), m = Core.meta(pct, cfg.meta);
  const sa = el('select', { 'aria-label': 'De' }, ds.map(x => el('option', { value: x.n, text: x.n }))), sb = el('select', { 'aria-label': 'Até' }, ds.map(x => el('option', { value: x.n, text: x.n })));
  sa.value = F.tA; sb.value = F.tB; sa.onchange = () => { F.tA = sa.value; render(); }; sb.onchange = () => { F.tB = sb.value; render(); };
  const fx = Core.FAIXAS.map((n, i) => [n, 0, []]); itens.forEach(([r, d]) => { const f = fx[Core.faixa(d)]; f[1]++; f[2].push(r); });
  return el('div', { class: 'card', id: 'cartaoTempo' }, el('h3', { text: titulo || 'Tempo entre datas' }), el('div', { class: 'row' }, sa, ' → ', sb),
    el('p', null, 'Mediana: ', el('b', { text: Core.hm(Core.mediana(durs)) })), el('p', { class: pct != null && m.ok ? 'good' : '' }, 'Dentro de ' + cfg.prazoH + ' h: ', el('b', { text: pct == null ? '—' : pct.toFixed(1).replace('.', ',') + '%' }), m.txt ? ' · ' + m.txt : ''),
    barras(fx, (k, l) => abrirJanela(k + ' (' + F.tA + ' → ' + F.tB + ')', l, c)));
}
function procurarRepetidos(L, c, campo) {
  const base = L.slice(0, 5000), pares = Core.repetidos(base, r => r.v[campo] || '', Core.lerSinonimos(cfg.sinonimos)).slice(0, 100);
  const cod = camposDe(c, 'codigo')[0].n;
  if (!pares.length) { toast('Nenhum possível repetido encontrado.'); return; }
  const lista = []; const vistos = new Set();
  pares.forEach(p => [base[p[0]], base[p[1]]].forEach(r => { if (!vistos.has(r.codigo)) { vistos.add(r.codigo); lista.push(r); } }));
  abrirJanela('Possíveis repetidos (' + pares.length + ' pares)', lista, c);
}

/* ---------- etapa 2: "O que você quer acompanhar?" (catálogo de indicadores, blocos e resumo "Seu painel") ---------- */
const fmtN = n => n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtI = n => n.toLocaleString('pt-BR');
const fmtP = n => n.toFixed(1).replace('.', ',') + '%';
const fmtD = s => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s || ''); return m ? m[3] + '/' + m[2] + '/' + m[1] : (s || ''); };
const fmtM = k => k.slice(5) + '/' + k.slice(0, 4);
const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
const NAO_ABERTO = ['conclu', 'finaliz', 'encerr', 'fechad', 'entreg', 'cancel', 'resolvid', 'pag'];
const emAberto = (r, sit) => { const s = Core.norm(r.v[sit] || '').toLowerCase(); return !NAO_ABERTO.some(p => s.startsWith(p)); };
const numeros = (L, f) => L.map(r => Core.numero(r.v[f])).filter(n => n != null);
const ordenaGrupos = m => [...m].sort((a, b) => b[1].length - a[1].length || String(a[0]).localeCompare(String(b[0]), 'pt'));
// top 10 + "Outros" (itens: [nome, lista])
function top10(gr, valor) {
  const t = gr.slice(0, 10).map(([k, l]) => [k, l]); const resto = gr.slice(10).flatMap(x => x[1]);
  if (resto.length) t.push(['Outros', resto]); return t.map(([k, l]) => [k, valor ? valor(l) : l.length, l]);
}
const kpiBtn = (pre, val, suf, abrir) => el('button', { class: 'kpi', type: 'button', onclick: abrir }, pre, el('b', { text: val }), suf);
const cartao = (b, ...kids) => el('div', { class: 'card bloco' }, el('h3', { text: b.nome }), ...kids);

// catálogo de indicadores possíveis do conjunto: só entram os que dá para calcular (ex() devolve null quando não dá)
function catalogo(c, soIds) {
  const todos = doConj(c), campos = (conjs[c] || {}).campos || [], cs = camposDe(c, 'categoria'), ns = camposDe(c, 'numero'), ds = camposDe(c, 'data'), ss = camposDe(c, 'situacao');
  const abrir = (t, l) => abrirJanela(t, l, c), SEP = '\u0001', out = [];
  out.push({ id: 'total', grupo: 'num', nome: 'Total de registros', oque: 'quantos registros há', conta: 'contagem de todos os registros', campos: 'nenhum campo específico, conta os registros',
    ex: L => L.length ? fmtI(L.length) + (L.length === 1 ? ' registro' : ' registros') : null,
    desenha: L => cartao({ nome: 'Total de registros' }, kpiBtn('', fmtI(L.length), L.length === 1 ? ' registro' : ' registros', () => abrir('Todos os registros', L))) });
  cs.forEach(k => out.push({ id: 'cat' + SEP + k.n, grupo: 'graf', nome: 'Por ' + k.n, oque: 'quantos registros há em cada ' + k.n + ' (os 10 maiores; o resto em Outros)', conta: 'contagem de registros por ' + k.n, campos: k.n,
    ex: L => { const g = ordenaGrupos(agrupa(L, r => r.v[k.n])); return g.length ? k.n + ': ' + g[0][0] + ' lidera com ' + fmtI(g[0][1].length) : null; },
    desenha: L => cartao({ nome: 'Por ' + k.n }, barras(top10(ordenaGrupos(agrupa(L, r => r.v[k.n]))), (n, l) => abrir(k.n + ': ' + n, l))) }));
  ns.forEach(k => out.push({ id: 'num' + SEP + k.n, grupo: 'num', nome: k.n + ' (soma, média e mediana)', oque: 'a soma, a média e a mediana de ' + k.n, conta: 'soma, média e mediana do campo ' + k.n, campos: k.n,
    ex: L => { const v = numeros(L, k.n); return v.length ? 'Soma: ' + fmtN(v.reduce((a, b) => a + b, 0)) + ' · Média: ' + fmtN(v.reduce((a, b) => a + b, 0) / v.length) + ' · Mediana: ' + fmtN(Core.mediana(v)) : null; },
    desenha: L => { const v = numeros(L, k.n), com = L.filter(r => Core.numero(r.v[k.n]) != null), soma = v.reduce((a, b) => a + b, 0), ab = () => abrir(k.n, com);
      return cartao({ nome: k.n + ' (soma, média e mediana)' }, kpiBtn('Soma: ', v.length ? fmtN(soma) : '—', '', ab), kpiBtn('Média: ', v.length ? fmtN(soma / v.length) : '—', '', ab), kpiBtn('Mediana: ', v.length ? fmtN(Core.mediana(v)) : '—', '', ab)); } }));
  ns.forEach(k => cs.forEach(g => out.push({ id: 'numcat' + SEP + k.n + SEP + g.n, grupo: 'graf', nome: k.n + ' por ' + g.n, oque: 'quanto ' + k.n + ' soma em cada ' + g.n + ' (os 10 maiores; o resto em Outros)', conta: 'soma do campo ' + k.n + ', separada por ' + g.n, campos: k.n + ', ' + g.n,
    ex: L => { const m = ordenaGrupos(agrupa(L.filter(r => Core.numero(r.v[k.n]) != null), r => r.v[g.n])).map(([n, l]) => [n, l, numeros(l, k.n).reduce((a, b) => a + b, 0)]).sort((a, b) => b[2] - a[2]); return m.length ? 'Maior soma: ' + m[0][0] + ' (' + fmtN(m[0][2]) + ')' : null; },
    desenha: L => { const m = ordenaGrupos(agrupa(L.filter(r => Core.numero(r.v[k.n]) != null), r => r.v[g.n])).map(([n, l]) => [n, l, numeros(l, k.n).reduce((a, b) => a + b, 0)]).sort((a, b) => b[2] - a[2]);
      return cartao({ nome: k.n + ' por ' + g.n }, barras(top10(m.map(x => [x[0], x[1]]), l => numeros(l, k.n).reduce((a, b) => a + b, 0)).map(x => [x[0], x[1], x[2], fmtN(x[1])]), (n, l) => abrir(k.n + ' por ' + g.n + ': ' + n, l))); } })));
  ds.forEach(k => out.push({ id: 'mes' + SEP + k.n, grupo: 'graf', nome: 'Evolução por mês (' + k.n + ')', oque: 'quantos registros há em cada mês', conta: 'registros por mês do campo ' + k.n, campos: k.n, dataCampo: k.n,
    ex: L => { const g = [...agrupa(L, r => (r.v[k.n] || '').slice(0, 7))].sort((a, b) => b[1].length - a[1].length || (a[0] < b[0] ? -1 : 1)); return g.length ? 'Mês com mais registros: ' + fmtM(g[0][0]) + ' (' + fmtI(g[0][1].length) + ')' : null; },
    desenha: L => { const g = [...agrupa(L, r => (r.v[k.n] || '').slice(0, 7))].sort((a, b) => a[0] < b[0] ? -1 : 1).map(([m, l]) => [fmtM(m), l.length, l]);
      return cartao({ nome: 'Evolução por mês (' + k.n + ')' }, barras(g, (m, l) => abrir('Mês ' + m, l))); } }));
  if (ds.length >= 2) out.push({ id: 'tempo', grupo: 'num', nome: 'Tempo entre duas datas', get oque() { const p = parTempo(ds); return 'o tempo que passa entre ' + p[0] + ' e ' + p[1] + ', em faixas e dentro do prazo'; }, get conta() { const p = parTempo(ds); return 'mediana do tempo entre ' + p[0] + ' e ' + p[1]; }, get campos() { return parTempo(ds).join(', '); }, get dataCampo() { return parTempo(ds)[0]; },
    ex: L => { const p = parTempo(ds), it = paresTempo(L, p[0], p[1]); return it.length ? 'Mediana: ' + Core.hm(Core.mediana(it.map(x => x[1]))) : null; },
    desenha: L => cartaoTempo(L, c, ds, 'Tempo entre duas datas') });
  ss.forEach(k => out.push({ id: 'sit' + SEP + k.n, grupo: 'num', nome: '% por ' + k.n, oque: 'a parte de cada ' + k.n + ' no total', conta: 'percentual de registros por ' + k.n, campos: k.n,
    ex: L => { const g = ordenaGrupos(agrupa(L, r => r.v[k.n])), n = g.reduce((a, x) => a + x[1].length, 0); return g.length ? g[0][0] + ': ' + fmtP(100 * g[0][1].length / n) : null; },
    desenha: L => { const g = ordenaGrupos(agrupa(L, r => r.v[k.n])), n = g.reduce((a, x) => a + x[1].length, 0);
      return cartao({ nome: '% por ' + k.n }, barras(g.map(([v, l]) => [v, l.length, l, fmtP(100 * l.length / n)]), (v, l) => abrir(k.n + ': ' + v, l))); } }));
  campos.filter(k => k.t !== 'codigo' && k.t !== 'ignorar').forEach(k => out.push({ id: 'vazio' + SEP + k.n, grupo: 'num', nome: 'Sem valor em ' + k.n, oque: 'quantos registros estão sem ' + k.n, conta: 'registros com o campo ' + k.n + ' vazio', campos: k.n,
    ex: L => { const n = L.filter(r => !r.v[k.n]).length; return n ? fmtI(n) + ' sem valor em ' + k.n : null; },
    desenha: L => { const l = L.filter(r => !r.v[k.n]); return cartao({ nome: 'Sem valor em ' + k.n }, kpiBtn('', fmtI(l.length), ' sem valor em ' + k.n, () => abrir('Sem valor em ' + k.n, l))); } }));
  if (ds.length && ss.length) {
    const sit = ss[0].n, dat = () => campoData(c);
    const lista = L => L.filter(r => r.v[dat()] && emAberto(r, sit)).sort((a, b) => a.v[dat()] < b.v[dat()] ? -1 : 1);
    out.push({ id: 'aberto', grupo: 'num', nome: 'Mais antigos em aberto', oque: 'o registro em aberto mais antigo e quantos estão em aberto', get conta() { return 'registros em aberto mais antigos pela data ' + dat(); }, get campos() { return dat() + ', ' + sit; }, get dataCampo() { return dat(); },
      ex: L => { const l = lista(L); return l.length ? 'Mais antigo: ' + fmtData(l[0].v[dat()]) : null; },
      desenha: L => { const l = lista(L); return cartao({ nome: 'Mais antigos em aberto' }, kpiBtn('Mais antigo: ', l.length ? fmtData(l[0].v[dat()]) : '—', '', () => abrir('Mais antigos em aberto', l)), el('p', { class: 'muted', text: fmtI(l.length) + ' em aberto' })); } });
  }
  return (soIds ? out.filter(x => soIds.indexOf(x.id) >= 0) : out).filter(x => x.ex(todos) != null);
}
// blocos escolhidos do conjunto, na ordem da especificação: números, gráficos (cada grupo na ordem em que foram marcados); [] = painel da etapa 1
function blocosEscolhidos(c) {
  const ids = Array.isArray(acomp[c]) ? acomp[c] : []; if (!ids.length || !conjs[c]) return [];
  const cat = catalogo(c, ids), lista = ids.map(i => cat.find(x => x.id === i)).filter(Boolean);
  return lista.filter(b => b.grupo === 'num').concat(lista.filter(b => b.grupo !== 'num'));
}

/* resumo em texto ("Seu painel"): gerado a partir de uma lista de blocos; as etapas 3 e 6 só passam a lista nova */
function filtrosResumo() {
  const p = [];
  if (F.cat && F.val) p.push('só ' + F.cat.toLowerCase() + ' ' + F.val);
  if (F.per === 'mes' && F.mes) p.push(MESES[+F.mes.slice(5, 7) - 1] + '/' + F.mes.slice(0, 4));
  if (F.per === 'de' && (F.de || F.ate)) p.push(F.de && F.ate ? 'de ' + fmtD(F.de) + ' a ' + fmtD(F.ate) : F.de ? 'a partir de ' + fmtD(F.de) : 'até ' + fmtD(F.ate));
  if (F.q) p.push('busca “' + F.q + '”');
  return p.length ? p.join('; ') : 'sem filtros';
}
function resumoBlocos(c, blocos, L) {
  const fl = filtrosResumo();
  return blocos.map(b => {
    const cd = b.dataCampo || campoData(c), datas = cd ? L.map(r => r.v[cd]).filter(Boolean).sort() : [];
    const per = datas.length ? 'de ' + fmtD(datas[0]) + ' a ' + fmtD(datas[datas.length - 1]) : 'sem datas';
    return { nome: b.nome, texto: b.nome + ' — ' + b.oque + '. Conta: ' + b.conta + '. Campos: ' + b.campos + '. Período: ' + per + '. Filtros: ' + fl + '.' };
  });
}
function abrirPainel(c) {
  const bl = blocosEscolhidos(c); if (!bl.length) return;
  const d = $('#dlgPainel'), ol = $('#painelLista'); ol.textContent = '';
  resumoBlocos(c, bl, filtrar(c)).forEach(x => ol.append(el('li', null, x.texto)));
  d.showModal();
}
// janela "O que você quer acompanhar?"; resolve ao fechar (Confirmar salva; Cancelar não salva nada)
function janelaAcomp(c) {
  return new Promise(ok => {
    const d = $('#dlgAcomp'), ul = $('#acompLista'), erro = $('#acompErro'); ul.textContent = ''; erro.textContent = '';
    const cat = catalogo(c), todos = doConj(c), ja = (Array.isArray(acomp[c]) ? acomp[c] : []).filter(i => cat.some(x => x.id === i)), sel = ja.slice();
    cat.forEach(b => {
      const cx = el('input', { type: 'checkbox', 'aria-label': b.nome }); cx.checked = sel.indexOf(b.id) >= 0;
      cx.onchange = () => { const i = sel.indexOf(b.id); if (cx.checked && i < 0) sel.push(b.id); if (!cx.checked && i >= 0) sel.splice(i, 1); erro.textContent = ''; };
      ul.append(el('li', null, el('label', null, cx, el('span', { class: 'acNome', text: b.nome }), el('span', { class: 'acEx muted', text: b.ex(todos) }))));
    });
    $('#acompOk').onclick = () => { if (!sel.length) { erro.textContent = 'Marque pelo menos um indicador.'; return; } acomp[c] = sel.slice(); salvaAcomp(); d.close('ok'); };
    $('#acompCancela').onclick = () => d.close('cancela');
    d.onclose = () => { const salvou = d.returnValue === 'ok'; d.returnValue = ''; if (salvou) { render(); abrirPainel(c); } ok(salvou); };
    d.showModal();
  });
}

/* ---------- janelas flutuantes ---------- */
let nJan = 0;
function abrirJanela(titulo, lista, c) {
  const campos = conjs[c].campos, cats = campos.filter(x => x.t === 'categoria' || x.t === 'situacao').slice(0, 2), sel = {};
  const filtrada = () => lista.filter(r => cats.every(k => !sel[k.n] || !sel[k.n].size || sel[k.n].has(r.v[k.n])));
  const j = el('div', { class: 'jan', role: 'dialog', 'aria-label': titulo }), corpo = el('div', { class: 'corpo' }), info = el('p', { class: 'muted' });
  const w = Math.min(720, window.innerWidth * 0.96); j.style.left = Math.max(4, Math.min(20 + (nJan % 8) * 28, window.innerWidth - w - 4)) + 'px'; j.style.top = (70 + (nJan % 8) * 28) + 'px'; nJan++;
  const tit = el('b', { text: titulo + ' (' + lista.length + ')' });
  const dock = el('button', { type: 'button', text: titulo, onclick: () => { j.style.display = ''; dock.remove(); } });
  const hd = el('header', null, tit,
    el('button', { type: 'button', 'aria-label': 'Minimizar', text: '_', onclick: () => { j.style.display = 'none'; $('#dock').append(dock); } }),
    el('button', { type: 'button', 'aria-label': 'Fechar', text: '×', onclick: () => { j.remove(); dock.remove(); } }));
  const desenha = () => {
    const f = filtrada(); corpo.textContent = '';
    cats.forEach(k => { const g = [...agrupa(lista, r => r.v[k.n])].sort((a, b) => b[1].length - a[1].length).slice(0, 8); if (g.length) corpo.append(el('div', { class: 'chips' }, el('span', { class: 'muted', text: k.n + ':' }), g.map(([v, l]) => el('button', { type: 'button', class: 'chip' + (sel[k.n] && sel[k.n].has(v) ? ' on' : ''), text: v + ' (' + l.length + ')', onclick: () => { const s = sel[k.n] || (sel[k.n] = new Set()); s.has(v) ? s.delete(v) : s.add(v); desenha(); } })))); });
    const txt = cats.map(k => sel[k.n] && sel[k.n].size ? k.n + ': ' + [...sel[k.n]].join(', ') : '').filter(Boolean).join(' · ');
    info.textContent = (txt ? 'Seleção: ' + txt + ' · ' : '') + f.length + ' registros' + (f.length > 200 ? ' (mostrando 200)' : ''); corpo.append(info, el('div', { class: 'tw' }, tabela(campos, f.slice(0, 200))));
    corpo._f = f; corpo._txt = txt;
  };
  const barra = el('div', { class: 'barra' },
    el('button', { type: 'button', text: 'Limpar seleção', onclick: () => { Object.keys(sel).forEach(k => delete sel[k]); desenha(); } }),
    el('button', { type: 'button', text: 'Imprimir', onclick: () => imprimir(titulo, corpo._f, campos, corpo._txt) }),
    el('button', { type: 'button', text: 'Copiar', onclick: () => copiar(corpo._f, campos) }));
  j.append(hd, corpo, barra); document.body.append(j); desenha();
  j.addEventListener('pointerdown', () => { j.style.zIndex = 20 + (++abrirJanela.z || (abrirJanela.z = 1)); });
  hd.addEventListener('pointerdown', e => {
    if (e.target.closest('button')) return; const r = j.getBoundingClientRect(), dx = e.clientX - r.left, dy = e.clientY - r.top; hd.setPointerCapture(e.pointerId);
    hd.onpointermove = ev => { j.style.left = Math.max(0, Math.min(window.innerWidth - 60, ev.clientX - dx)) + 'px'; j.style.top = Math.max(0, Math.min(window.innerHeight - 40, ev.clientY - dy)) + 'px'; };
    hd.onpointerup = () => { hd.onpointermove = hd.onpointerup = null; };
  });
  return j;
}
function copiar(lista, campos) {
  const tsv = [campos.map(c => c.n).join('\t')].concat(lista.map(r => campos.map(c => (c.t === 'codigo' ? r.codigo : c.t === 'data' ? fmtData(r.v[c.n]) : (r.v[c.n] || '')).replace(/[\t\r\n]/g, ' ').replace(/^[=+\-@]/, "'$&")).join('\t'))).join('\n');
  (navigator.clipboard ? navigator.clipboard.writeText(tsv) : Promise.reject()).then(() => toast('Copiado.'), () => toast('Não consegui copiar neste navegador.'));
}
function imprimir(titulo, lista, campos, sel) {
  const w = window.open('', '_blank'); if (!w) { toast('O navegador bloqueou a janela de impressão.'); return; }
  const lin = lista.slice(0, 2000).map(r => '<tr>' + campos.map(c => '<td>' + esc(c.t === 'codigo' ? r.codigo : c.t === 'data' ? fmtData(r.v[c.n]) : (r.v[c.n] || '')) + '</td>').join('') + '</tr>').join('');
  w.document.write('<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>' + esc(titulo) + '</title><style>@page{size:A4 landscape;margin:12mm}body{font:12px system-ui,sans-serif}h1{font-size:18px;margin:0}p{margin:2px 0 8px;color:#444}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:3px 5px;text-align:left;font-size:11px}thead{display:table-header-group}tr{page-break-inside:avoid}</style></head><body><h1>Raio X do Relatório · ' + esc(titulo) + '</h1><p>' + esc(ORG()) + '</p>' + (sel ? '<p><b>Seleção:</b> ' + esc(sel) + '</p>' : '') + '<p>' + lista.length + ' registros · ' + esc(new Date().toLocaleDateString('pt-BR')) + '</p><table><thead><tr>' + campos.map(c => '<th>' + esc(c.n) + '</th>').join('') + '</tr></thead><tbody>' + lin + '</tbody></table></body></html>');
  w.document.close(); w.focus(); setTimeout(() => w.print(), 200);
}

/* ---------- Excel ---------- */
function baixar(blob, nome) { const a = el('a', { href: URL.createObjectURL(blob), download: nome }); document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); }
function nomeAba(wb, n) { let b = n.replace(/[\[\]:*?\/\\]/g, ' ').slice(0, 28) || 'Aba', x = b, i = 2; while (wb.getWorksheet(x)) x = b.slice(0, 26) + ' ' + i++; return x; }
function capa(wb, nomeRel, grupos) {
  const ws = wb.addWorksheet('Capa', { views: [{ showGridLines: false }] }); ws.columns = [{ width: 26 }, { width: 44 }, { width: 22 }];
  const tot = grupos.reduce((s, g) => s + g.lista.length, 0), datas = [];
  grupos.forEach(g => { const cd = campoData(g.c); if (cd) g.lista.forEach(r => { if (r.v[cd]) datas.push(r.v[cd]); }); }); datas.sort();
  ws.getCell('B2').value = 'Raio X do Relatório'; ws.getCell('B2').font = { size: 22, bold: true, color: { argb: 'FF0F2A4A' } };
  ws.getCell('B3').value = ORG(); ws.getCell('B3').font = { size: 13, color: { argb: 'FF555555' } };
  if (cfg.logo) try { const id = wb.addImage({ base64: cfg.logo, extension: 'png' }); ws.addImage(id, { tl: { col: 0.2, row: 1 }, ext: { width: 90, height: 60 } }); } catch (e) { /* logo ilegível: segue sem */ }
  ws.getRow(5).values = ['Total de registros', 'Mais antigo', 'Mais novo']; ws.getRow(6).values = [tot, datas.length ? fmtData(datas[0]) : '—', datas.length ? fmtData(datas[datas.length - 1]) : '—'];
  ws.getRow(5).font = { bold: true, color: { argb: 'FFFFFFFF' } }; ws.getRow(5).eachCell(c => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0F2A4A' } }; }); ws.getRow(6).font = { size: 14, bold: true }; ws.getRow(6).alignment = { horizontal: 'left' };
  const info = [['Relatório', nomeRel], ['Período', datas.length ? fmtData(datas[0]) + ' a ' + fmtData(datas[datas.length - 1]) : 'sem datas'], ['Filtros', textoFiltros() || 'nenhum'], ['Gerado em', new Date().toLocaleString('pt-BR')]];
  info.forEach((p, i) => { ws.getCell(8 + i, 1).value = p[0]; ws.getCell(8 + i, 1).font = { bold: true }; ws.getCell(8 + i, 2).value = p[1]; });
  ws.pageSetup = { paperSize: 9, orientation: 'portrait', fitToPage: true, fitToWidth: 1, fitToHeight: 1 }; ws.headerFooter.oddFooter = '&LRaio X do Relatório&RPágina &P de &N';
}
const cortaCelula = v => typeof v === 'string' && v.length > 32000 ? v.slice(0, 32000) : v;   // B-3: limite do Excel é 32.767 caracteres por célula
function comoLer(wb, grupos) {
  const itens = []; grupos.forEach(g => { const bl = blocosEscolhidos(g.c); if (bl.length) resumoBlocos(g.c, bl, g.lista).forEach(x => itens.push(grupos.length > 1 && grupos.filter(h => blocosEscolhidos(h.c).length).length > 1 ? '[' + g.c + '] ' + x.texto : x.texto)); });
  if (!itens.length) return;   // sem escolha confirmada a planilha não é criada
  const ws = wb.addWorksheet('Como ler este relatório'); ws.columns = [{ width: 120 }];
  ws.getCell('A1').value = 'Seu painel'; ws.getCell('A1').font = { size: 16, bold: true, color: { argb: 'FF0F2A4A' } };
  itens.forEach((t, i) => { const c = ws.getCell(2 + i, 1); c.value = cortaCelula(primitivo(t)); c.alignment = { wrapText: true, vertical: 'top' }; });
  ws.pageSetup = { paperSize: 9, orientation: 'portrait', fitToPage: true, fitToWidth: 1, fitToHeight: 0 };
}
const primitivoXL = x => cortaCelula(primitivo(x));
function aba(wb, nome, campos, linhas, comRel) {
  const ws = wb.addWorksheet(nomeAba(wb, nome)), cols = (comRel ? [{ n: 'Relatório', t: 'texto' }] : []).concat(campos);
  ws.addRow(cols.map(c => c.n)); const h = ws.getRow(1); h.font = { bold: true, color: { argb: 'FFFFFFFF' } }; h.eachCell(c => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0F2A4A' } }; });
  linhas.forEach(({ r, c }) => ws.addRow(cols.map((k, i) => {
    if (comRel && i === 0) return primitivoXL(c); if (k.t === 'codigo') return primitivoXL(r.codigo); const v = r.v[k.n]; if (!v) return null;
    if (k.t === 'data') { const m = Core.msISO(v); return m == null ? primitivoXL(v) : new Date(Date.UTC(+v.slice(0, 4), +v.slice(5, 7) - 1, +v.slice(8, 10), +v.slice(11, 13), +v.slice(14, 16))); }
    if (k.t === 'numero') { const n = Core.numero(v); return n == null ? primitivoXL(v) : primitivoXL(n); } return primitivoXL(v); })));
  cols.forEach((k, i) => { const col = ws.getColumn(i + 1); let w = k.n.length; ws.eachRow({ includeEmpty: false }, (row, n) => { if (n < 400) { const x = row.getCell(i + 1).value; w = Math.max(w, x instanceof Date ? 16 : String(x == null ? '' : x).length); } }); col.width = Math.min(60, w + 3); if (k.t === 'data') col.numFmt = 'dd/mm/yyyy hh:mm'; });
  ws.views = [{ state: 'frozen', ySplit: 1 }]; if (cols.length) ws.autoFilter = { from: { row: 1, column: 1 }, to: { row: 1, column: cols.length } };
  ws.pageSetup = { paperSize: 9, orientation: 'landscape', fitToPage: true, fitToWidth: 1, fitToHeight: 0, printTitlesRow: '1:1' }; ws.headerFooter.oddFooter = '&L' + (ORG() || 'Raio X do Relatório').replace(/&/g, '&&') + '&CPágina &P de &N&R&D';
}
async function gerarExcel() {
  const msg = $('#xMsg');
  if (!window.ExcelJS) { msg.textContent = 'O gerador de Excel não carregou. Recarregue a página.'; return; }
  const cs = Object.keys(conjs).filter(c => doConj(c).length), fm = $('#xFmt').value, data = hojeISO();
  const grupos = cs.map(c => ({ c, campos: conjs[c].campos, lista: filtrar(c) }));
  msg.textContent = 'Gerando…';
  try {
    const novo = () => { const wb = new ExcelJS.Workbook(); wb.creator = 'Raio X do Relatório'; wb.title = 'Raio X do Relatório' + (ORG() ? ' · ' + ORG() : ''); wb.created = new Date(); return wb; };
    const grava = async (wb, nome) => baixar(new Blob([await wb.xlsx.writeBuffer()], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), 'RaioX_' + slug(nome) + '_' + data + '.xlsx');
    if (fm === 'sep') { for (const g of grupos) { const wb = novo(); capa(wb, g.c, [g]); comoLer(wb, [g]); aba(wb, g.c, g.campos, g.lista.map(r => ({ r, c: g.c }))); await grava(wb, g.c); await new Promise(r => setTimeout(r, 300)); } }
    else {
      const nome = grupos.length === 1 ? grupos[0].c : 'Tudo', wb = novo(); capa(wb, nome, grupos); comoLer(wb, grupos);
      if (fm === 'tudo') { const u = []; grupos.forEach(g => g.campos.forEach(k => { if (!u.some(x => x.n === k.n)) u.push({ n: k.n, t: k.t === 'codigo' ? 'texto' : k.t }); })); aba(wb, 'Tudo', u, grupos.flatMap(g => g.lista.map(r => ({ r: { codigo: r.codigo, v: Object.assign({ [camposDe(g.c, 'codigo')[0].n]: r.codigo }, r.v) }, c: g.c }))), true); }
      else grupos.forEach(g => aba(wb, g.c, g.campos, g.lista.map(r => ({ r, c: g.c }))));
      await grava(wb, nome);
    }
    msg.textContent = 'Excel gerado.';
  } catch (e) { msg.textContent = 'Não consegui gerar o Excel: ' + e.message; }
}

/* ---------- Config ---------- */
const PASSOS = ['Baixe o arquivo RaioX_Relatorio.bas (botão “Baixar versão Excel para o PC”).', 'Abra o Excel (2016 ou mais novo), crie uma pasta de trabalho nova e salve como “Pasta de Trabalho Habilitada para Macro (.xlsm)”.', 'Aperte Alt+F11, vá em Arquivo → Importar arquivo e escolha o RaioX_Relatorio.bas.', 'Volte ao Excel, aperte Alt+F8, escolha a macro Instalar e clique em Executar (se o Excel avisar sobre macros, escolha “Habilitar conteúdo”).'];
function topo() {
  $('#clienteTopo').textContent = ORG() ? '· ' + ORG() : '';
  const lt = $('#logoTopo'); lt.textContent = ''; if (cfg.logo) lt.append(el('img', { src: cfg.logo, alt: 'Logo' }));
  const lp = $('#cfgLogoPrev'); lp.textContent = ''; if (cfg.logo) lp.append(el('img', { src: cfg.logo, alt: 'Logo', style: 'height:34px' }));
  $('#cfgLogoX').hidden = !cfg.logo;
}
function renderConfig() {
  const l = $('#listaFmt'); l.textContent = '';
  const ks = Object.keys(fmts); if (!ks.length) l.append(el('p', { class: 'muted', text: 'Nenhum formato lembrado ainda.' }));
  ks.forEach(k => l.append(el('div', { class: 'row', style: 'margin-bottom:6px' }, el('span', { text: fmts[k].conjunto + ' (' + fmts[k].cols.length + ' colunas)' }), el('button', { type: 'button', text: 'Esquecer', onclick: () => { delete fmts[k]; store.set('raiox_fmt', fmts); renderConfig(); } }))));
  $('#infoDados').textContent = regs.length + ' registros guardados neste aparelho.';
}
function iniciaConfig() {
  const lig = (id, k, num) => { const i = $(id); i.value = cfg[k]; i.oninput = () => { cfg[k] = num ? (parseFloat(i.value) || (k === 'meta' ? 90 : 24)) : i.value; salvaCfg(); topo(); render(); }; };
  lig('#cfgCliente', 'cliente'); lig('#cfgArea', 'area'); lig('#cfgMeta', 'meta', true); lig('#cfgPrazo', 'prazoH', true); lig('#cfgSin', 'sinonimos');
  $('#cfgLogo').onchange = e => { const f = e.target.files[0]; if (!f) return; if (f.size > LIM.logo) { toast('Logo grande demais (' + mb(f.size) + '; o limite é ' + mb(LIM.logo) + ').'); e.target.value = ''; return; } const img = new Image(); img.onload = () => { const k = Math.min(1, 240 / Math.max(img.width, img.height)), cv = document.createElement('canvas'); cv.width = Math.round(img.width * k); cv.height = Math.round(img.height * k); cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height); cfg.logo = cv.toDataURL('image/png'); salvaCfg(); topo(); URL.revokeObjectURL(img.src); }; img.onerror = () => toast('Não consegui ler essa imagem.'); img.src = URL.createObjectURL(f); e.target.value = ''; };
  $('#cfgLogoX').onclick = () => { cfg.logo = ''; salvaCfg(); topo(); };
  document.querySelectorAll('.passosBas').forEach(p => { const d = el('details', null, el('summary', { text: 'Como instalar a versão Excel (4 passos)' }), el('ol', { class: 'passos' }, PASSOS.map(x => el('li', { text: x })))); p.append(d); });
  document.querySelectorAll('[data-baixar-bas]').forEach(a => a.addEventListener('click', () => document.querySelectorAll('.passosBas details').forEach(d => { d.open = true; })));
  $('#bkBaixar').onclick = () => baixar(new Blob([JSON.stringify({ app: 'raiox', formato: 1, criado: new Date().toISOString(), cfg, fmts, conjs, acomp, registros: regs })], { type: 'application/json' }), 'historico_RaioX_' + hojeISO() + '.json');
  $('#bkArq').onchange = async e => {
    const f = e.target.files[0]; e.target.value = ''; if (!f) return;
    if (f.size > LIM.backup) { toast('Backup grande demais (' + mb(f.size) + '; o limite é ' + mb(LIM.backup) + '). Nada foi alterado.'); return; }
    let b; try { b = validarBackup(JSON.parse(await f.text())); } catch (x) { b = null; }
    if (!b) { toast('Esse arquivo não é um backup do Raio X (ou está com a estrutura errada). Nada foi alterado.'); return; }
    const r = await perguntar('Restaurar backup', 'O backup tem ' + b.registros.length + ' registros. Somar aos dados atuais ou substituir tudo?', [{ t: 'Somar', v: 'somar', prim: true }, { t: 'Substituir', v: 'subst' }, { t: 'Cancelar', v: null }]);
    if (!r) return;
    if (r === 'subst') { await IDB.clear(); regs = []; mapa = new Map(); conjs = nulo(); fmts = nulo(); acomp = nulo(); if (b.cfg) { cfg = cfgLimpa(b.cfg, cfg); salvaCfg(); } }
    Object.keys(b.conjs).forEach(k => { conjs[k] = b.conjs[k]; }); Object.keys(b.fmts).forEach(k => { fmts[k] = b.fmts[k]; }); Object.keys(b.acomp).forEach(k => { acomp[k] = b.acomp[k]; }); salvaAcomp();
    const mud = []; b.registros.forEach(x => { const a = mapa.get(chave(x.conjunto, x.codigo)); if (!a) { regs.push(x); mapa.set(chave(x.conjunto, x.codigo), x); mud.push(x); } else { a.v = Core.juntar(a.v, x.v); mud.push(a); } });
    await IDB.put(mud); salvaConjs(); store.set('raiox_fmt', fmts); F.conjunto = Object.keys(conjs)[0] || ''; iniciaCfgCampos(); topo(); render(); renderConfig(); toast('Backup restaurado.');
  };
  $('#apagarTudo').onclick = async () => {
    const r = await perguntar('Apagar todos os dados', 'Isso apaga os ' + regs.length + ' registros deste aparelho. Baixe um backup antes se quiser guardar. Apagar mesmo?', [{ t: 'Apagar', v: true, prim: true }, { t: 'Cancelar', v: null }]);
    if (!r) return; await IDB.clear(); await IDB.oldClear(); regs = []; mapa = new Map(); conjs = nulo(); salvaConjs(); acomp = nulo(); salvaAcomp(); F.conjunto = ''; render(); renderConfig(); toast('Dados apagados.');
  };
}
function iniciaCfgCampos() { $('#cfgCliente').value = cfg.cliente; $('#cfgArea').value = cfg.area; $('#cfgMeta').value = cfg.meta; $('#cfgPrazo').value = cfg.prazoH; $('#cfgSin').value = cfg.sinonimos; }

/* ---------- partida ---------- */
function abas(qual) { $('#painel').hidden = qual !== 'painel'; $('#config').hidden = qual !== 'config'; $('#tPainel').classList.toggle('on', qual === 'painel'); $('#tConfig').classList.toggle('on', qual === 'config'); window.scrollTo(0, 0); }
$('#tPainel').onclick = () => abas('painel'); $('#tConfig').onclick = () => abas('config');
$('#arquivo').onchange = e => { const fs = [...e.target.files]; e.target.value = ''; if (fs.length) carregar(fs); };
$('#fConj').onchange = e => { F.conjunto = e.target.value; F.cat = F.val = F.cd = ''; mostrar = 50; render(); };
$('#fPer').onchange = e => { F.per = e.target.value; render(); };
$('#fMes').oninput = e => { F.mes = e.target.value; render(); }; $('#fDe').oninput = e => { F.de = e.target.value; render(); }; $('#fAte').oninput = e => { F.ate = e.target.value; render(); };
$('#fCD').onchange = e => { F.cd = e.target.value; render(); }; $('#fCat').onchange = e => { F.cat = e.target.value; F.val = ''; render(); }; $('#fVal').onchange = e => { F.val = e.target.value; render(); };
$('#fQ').oninput = e => { F.q = e.target.value; mostrar = 50; render(); };
$('#gerarXlsx').onclick = gerarExcel;
$('#btnAcomp').onclick = () => { if (F.conjunto) janelaAcomp(F.conjunto); };
$('#btnEntender').onclick = () => abrirPainel(F.conjunto);
$('#painelFechar').onclick = () => $('#dlgPainel').close();
$('#versao').textContent = 'Versão ' + VERSAO;

(async function iniciar() {
  iniciaConfig(); topo();
  const vAnt = localStorage.getItem('raiox_ver'); if (vAnt && vAnt !== VERSAO) toast('Versão nova instalada'); try { localStorage.setItem('raiox_ver', VERSAO); } catch (e) { /* sem espaço: segue */ }
  if ('serviceWorker' in navigator) { const tinha = !!navigator.serviceWorker.controller; navigator.serviceWorker.register('sw.js').catch(() => {}); navigator.serviceWorker.addEventListener('controllerchange', () => { if (tinha) toast('Versão nova instalada'); }); }
  try { await migrar(); regs = (await IDB.all()).map(r => Object.assign(r, { v: copiaNula(r.v) })); } catch (e) { toast('Não consegui abrir os dados guardados neste aparelho.'); }
  regs.forEach(r => mapa.set(chave(r.conjunto, r.codigo), r));
  F.conjunto = Object.keys(conjs).find(c => doConj(c).length) || '';
  render(); renderConfig();
})();
