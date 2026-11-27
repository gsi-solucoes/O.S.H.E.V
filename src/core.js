/* ===== Raio X do Relatório · núcleo genérico: leitura de CSV, tipos, tempo entre datas, semelhança de texto ===== */
var Core = (function () {
  function decode(buf) {
    try { return new TextDecoder('utf-8', { fatal: true }).decode(buf).replace(/^﻿/, ''); }
    catch (e) { return new TextDecoder('windows-1252').decode(buf); }
  }
  function t(s) { return (s == null ? '' : String(s)).replace(/\s+/g, ' ').trim(); }

  // CSV: separador ; , ou tab (o mais frequente nas primeiras linhas), aspas, quebras dentro de aspas
  function parseCSV(text) {
    var amostra = text.slice(0, 4000).split('\n').slice(0, 15).join('\n'), sep = ',', best = -1;
    [';', ',', '\t'].forEach(function (s) { var n = amostra.split(s).length - 1; if (n > best) { best = n; sep = s; } });
    var rows = [], row = [], cell = '', q = false, i = 0, c, n = text.length;
    for (; i < n; i++) {
      c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
      else if (c === '"') q = true;
      else if (c === sep) { row.push(cell); cell = ''; }
      else if (c === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
      else if (c !== '\r') cell += c;
    }
    if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }
  // acha sozinho a linha do cabeçalho: a primeira com 2+ células, quase todas texto, seguida de linha preenchida
  function acharCabecalho(rows) {
    var cheio = function (r) { return (r || []).filter(function (x) { return t(x); }).length; };
    for (var i = 0; i < Math.min(40, rows.length - 1); i++) {
      var r = rows[i], n = cheio(r);
      if (n < 2) continue;
      var texto = r.filter(function (x) { x = t(x); return x && !/^[\d\s\/:.,-]+$/.test(x); }).length;
      if (texto >= Math.max(2, n * 0.7) && cheio(rows[i + 1]) >= 2) return i;
    }
    return -1;
  }
  function norm(x) { return (x || '').toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^A-Z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim(); }
  function assinatura(hdr) { return hdr.map(norm).filter(Boolean).join('|'); }

  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function iso(d) { return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()) + 'T' + p2(d.getHours()) + ':' + p2(d.getMinutes()); }
  // data em vários jeitos -> texto padrão AAAA-MM-DDTHH:MM (ou '')
  function dataISO(v) {
    v = t(v); var m, d;
    if ((m = /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{1,2}):(\d{2}))?/.exec(v))) d = new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0));
    else if ((m = /^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{2,4})(?:[ T,]+(\d{1,2}):(\d{2}))?/.exec(v))) { var y = +m[3]; if (y < 100) y += 2000; d = new Date(y, +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0)); if (+m[2] > 12 || +m[1] > 31) return ''; }
    else return '';
    return isNaN(d) ? '' : iso(d);
  }
  function numero(v) {
    v = t(v); if (!v) return null;
    if (/^-?\d{1,3}(\.\d{3})+(,\d+)?$/.test(v)) return parseFloat(v.replace(/\./g, '').replace(',', '.'));
    if (/^-?\d+,\d+$/.test(v)) return parseFloat(v.replace(',', '.'));
    if (/^-?\d+(\.\d+)?$/.test(v)) return parseFloat(v);
    return null;
  }
  // palpite do tipo de cada coluna: codigo | data | numero | categoria | texto | ignorar
  function palpites(hdr, rows) {
    var out = hdr.map(function (h, j) {
      var vals = rows.slice(0, 200).map(function (r) { return t(r[j]); }).filter(Boolean);
      if (!vals.length) return 'ignorar';
      var k = vals.length, nd = vals.filter(function (v) { return dataISO(v); }).length, nn = vals.filter(function (v) { return numero(v) !== null; }).length;
      var dist = {}; vals.forEach(function (v) { dist[v] = 1; }); var nu = Object.keys(dist).length;
      if (nd >= k * 0.8) return 'data';
      if (nn >= k * 0.9 && nu > 20) return 'numero';
      if (nu <= Math.max(12, k * 0.15)) return 'categoria';
      return 'texto';
    });
    var ci = -1;
    hdr.forEach(function (h, j) { if (ci < 0 && /^(COD|CODIGO|ID|NUMERO|NUM|NR|N|PROTOCOLO|PEDIDO|CHAMADO|REGISTRO)\b/.test(norm(h)) && out[j] !== 'data') ci = j; });
    if (ci < 0) hdr.forEach(function (h, j) {
      if (ci >= 0 || out[j] === 'data' || out[j] === 'ignorar') return;
      var vs = rows.slice(0, 200).map(function (r) { return t(r[j]); }).filter(Boolean);
      var u = {}; vs.forEach(function (v) { u[v] = 1; }); if (vs.length > 5 && Object.keys(u).length === vs.length && out[j] !== 'texto') ci = j;
    });
    if (ci < 0) ci = 0;
    out[ci] = 'codigo';
    // situação: sugestão (não palpite): campo categoria cujo nome tem situa, status ou estado; a pessoa troca na tela de colunas
    hdr.forEach(function (h, j) { if (out[j] === 'categoria' && /(SITUA|STATUS|ESTADO)/.test(norm(h))) out[j] = 'situacao'; });
    return out;
  }

  // junta registros por código, campo a campo: campo vazio do novo não apaga o que já existe
  function juntar(velho, novo) {
    var v = Object.create(null), k;
    for (k in (velho || {})) v[k] = velho[k];
    for (k in novo) if (t(novo[k]) !== '') v[k] = novo[k];
    return v;
  }

  // ---- tempo entre duas datas ----
  var H = 3600000;
  var FAIXAS = ['Até 1 h', 'De 1 a 4 h', 'De 4 a 24 h', 'De 1 a 3 dias', 'De 3 a 7 dias', 'Mais de 7 dias'];
  function faixa(ms) { var h = ms / H; return h <= 1 ? 0 : h <= 4 ? 1 : h <= 24 ? 2 : h <= 72 ? 3 : h <= 168 ? 4 : 5; }
  function hm(ms) {
    if (ms == null || isNaN(ms)) return '—';
    var m = Math.round(ms / 60000), h = Math.floor(m / 60), mi = m % 60;
    return h ? h + ' h ' + (mi < 10 ? '0' : '') + mi + ' min' : mi + ' min';
  }
  function mediana(a) { if (!a.length) return null; a = a.slice().sort(function (x, y) { return x - y; }); var m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; }
  function pctDentro(durs, limiteMs) { return durs.length ? 100 * durs.filter(function (x) { return x <= limiteMs; }).length / durs.length : null; }
  function msISO(s) { var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(s || ''); return m ? new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]).getTime() : null; }
  // meta: acima da meta fica verde; senão "faltam X para a meta"
  function meta(pct, alvo) {
    if (pct == null) return { ok: false, txt: '' };
    if (alvo === null) return { ok: false, txt: '' };
    alvo = alvo === undefined ? 90 : alvo;
    return pct >= alvo ? { ok: true, txt: 'Acima da meta de ' + alvo + '%' } : { ok: false, txt: 'faltam ' + (Math.round((alvo - pct) * 10) / 10).toString().replace('.', ',') + ' pontos para a meta de ' + alvo + '%' };
  }

  // ---- semelhança de texto ----
  function lev(a, b) {
    var m = a.length, n = b.length, d = [], i, j;
    if (!m) return n; if (!n) return m;
    for (j = 0; j <= n; j++) d[j] = j;
    for (i = 1; i <= m; i++) { var prev = d[0]; d[0] = i; for (j = 1; j <= n; j++) { var tmp = d[j]; d[j] = Math.min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1)); prev = tmp; } }
    return d[n];
  }
  // 0 a 1; vale como "parecido" a partir de 0,8 (erro de digitação)
  function semelhanca(a, b) { a = norm(a); b = norm(b); var L = Math.max(a.length, b.length); return L ? 1 - lev(a, b) / L : 1; }
  function parecido(a, b, lim) { return semelhanca(a, b) >= (lim || 0.8); }
  function aplicaSinonimos(txt, sin) { var s = ' ' + norm(txt) + ' '; (sin || []).forEach(function (p) { if (p[0]) s = s.split(' ' + p[0] + ' ').join(' ' + p[1] + ' '); }); return s.trim(); }
  function lerSinonimos(texto) { return (texto || '').split('\n').map(function (l) { var p = l.split('='); return p.length === 2 ? [norm(p[0]), norm(p[1])] : null; }).filter(function (p) { return p && p[0] && p[1]; }); }

  // possíveis repetidos: registros com texto parecido; palavra rara pesa mais (log da raridade)
  function repetidos(lista, getTxt, sin, lim) {
    lim = lim || 0.6;
    var P = lista.map(function (o) { return aplicaSinonimos(getTxt(o), sin).split(' ').filter(function (w) { return w.length >= 3; }); });
    var df = {}; P.forEach(function (ws) { var u = {}; ws.forEach(function (w) { u[w.slice(0, 5)] = 1; }); Object.keys(u).forEach(function (k) { df[k] = (df[k] || 0) + 1; }); });
    var peso = function (w) { return Math.log((lista.length + 1) / (df[w.slice(0, 5)] || 1)) + 0.1; };
    var idx = {}; P.forEach(function (ws, i) { var u = {}; ws.forEach(function (w) { u[w.slice(0, 5)] = 1; }); Object.keys(u).forEach(function (k) { if (df[k] <= 40) (idx[k] = idx[k] || []).push(i); }); });
    var vistos = {}, pares = [];
    Object.keys(idx).forEach(function (k) {
      var l = idx[k];
      for (var x = 0; x < l.length; x++) for (var y = x + 1; y < l.length; y++) {
        var a = l[x], b = l[y], key = a + '_' + b; if (vistos[key]) continue; vistos[key] = 1;
        var sa = 0, sb = 0, ok = 0;
        P[a].forEach(function (w) { var p = peso(w); sa += p; if (P[b].some(function (z) { return z === w || (w.length > 3 && z.length > 3 && semelhanca(w, z) >= 0.8); })) ok += p; });
        P[b].forEach(function (w) { sb += peso(w); });
        var sc = Math.max(sa, sb) ? ok / Math.max(sa, sb) : 0;
        if (sc >= lim) pares.push([a, b, sc]);
      }
    });
    pares.sort(function (x, y) { return y[2] - x[2]; });
    return pares;
  }

  // ---- pedido escrito ("Peça um indicador"): separa a frase em medida, campo, agrupar, filtros e período; sem rede e sem IA ----
  var P_STOP = ' de do da dos das o a os as um uma uns umas e em no na nos nas ao aos para pra pelo pela pelos pelas com sem que foi foram ser sao esta estao tem teve houve me mostre mostra mostrar ver veja quero queria gostaria so soh somente apenas agrupado agrupada separado separada dividido dividida segundo conforme ate entre desde por cada este esse neste nesse qual quais ';
  var P_MED = [['quantidade', 'quantidade'], ['quanto', 'quantidade'], ['quanta', 'quantidade'], ['qtd', 'quantidade'], ['qtde', 'quantidade'], ['qte', 'quantidade'], ['contagem', 'quantidade'],
    ['soma', 'soma'], ['somar', 'soma'], ['some', 'soma'], ['somatorio', 'soma'], ['total', 'total'], ['totalizar', 'total'], ['media', 'media'], ['medio', 'media'], ['mediana', 'mediana'],
    ['minimo', 'minimo'], ['minima', 'minimo'], ['menor', 'minimo'], ['maximo', 'maximo'], ['maxima', 'maximo'], ['maior', 'maximo'],
    ['percentual', 'percentual'], ['porcentagem', 'percentual'], ['percentagem', 'percentual'], ['pct', 'percentual'], ['proporcao', 'percentual'], ['porcento', 'percentual'], ['%', 'percentual']];
  var P_SUBST = ' registro linha item ocorrencia caso resultado dado ';
  var P_MESES = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
  function sing1(w) {
    if (w.length <= 3) return w;
    if (/oes$/.test(w) || /aes$/.test(w)) return w.slice(0, -3) + 'ao';
    if (/ais$/.test(w)) return w.slice(0, -3) + 'al';
    if (/eis$/.test(w)) return w.slice(0, -3) + 'el';
    if (/ns$/.test(w)) return w.slice(0, -2) + 'm';
    if (/(res|zes|ses)$/.test(w) && w.length > 4 || w === 'meses') return w.slice(0, -2);
    if (/s$/.test(w)) return w.slice(0, -1);
    return w;
  }
  function nz(s) { return norm(s).toLowerCase(); }
  function S(s) { return nz(s).split(' ').filter(Boolean).map(sing1).join(' '); }
  // razão de caracteres iguais (2·casados/total, como o SequenceMatcher); abaixo de 4 letras só vale igual
  function casados(a, b) {
    if (!a.length || !b.length) return 0;
    var bi = 0, bj = 0, bl = 0, i, j, k;
    for (i = 0; i < a.length; i++) for (j = 0; j < b.length; j++) { k = 0; while (i + k < a.length && j + k < b.length && a[i + k] === b[j + k]) k++; if (k > bl) { bl = k; bi = i; bj = j; } }
    return bl ? bl + casados(a.slice(0, bi), b.slice(0, bj)) + casados(a.slice(bi + bl), b.slice(bj + bl)) : 0;
  }
  function sim(a, b) { if (a === b) return 1; if (a.length < 4 || b.length < 4) return 0; if (2 * Math.min(a.length, b.length) / (a.length + b.length) < 0.8) return 0; return 2 * casados(a, b) / (a.length + b.length); }
  function p2n(n) { return (n < 10 ? '0' : '') + n; }
  function entender(frase, ctx) {
    frase = String(frase == null ? '' : frase).slice(0, 300); ctx = ctx || {};
    var campos = (ctx.campos || []).filter(function (k) { return k.t !== 'codigo' && k.t !== 'ignorar'; }), vals = Object.assign(Object.create(null), ctx.valores), sin = ctx.sin || {};
    var out = { medida: null, campo: null, agrupar: null, filtros: [], periodo: null, naoEntendi: [] };
    var H = ctx.hoje && /^\d{4}-\d{2}-\d{2}/.test(ctx.hoje) ? { a: +ctx.hoje.slice(0, 4), m: +ctx.hoje.slice(5, 7), d: +ctx.hoje.slice(8, 10) } : null;
    var tk = [], re = /\S+/g, mm;
    while ((mm = re.exec(frase))) { var raw = mm[0].replace(/^[("'“‘¿¡]+|[)"'”’,.;:!?]+$/g, ''); if (!raw) continue; tk.push({ raw: raw, ini: mm.index, fim: mm.index + mm[0].length, n: raw === '%' ? '%' : sing1(nz(raw)), ok: false, forca: null }); }
    var fld = campos.map(function (k) { return { ref: k, chave: S(k.n) }; });
    var vls = []; Object.keys(vals).forEach(function (c) { (Array.isArray(vals[c]) ? vals[c] : []).forEach(function (v) { var ch = S(v).slice(0, 60); if (ch) vls.push({ campo: c, valor: v, chave: ch }); }); });
    function conhecida(n) { return P_STOP.indexOf(' ' + n + ' ') >= 0 || P_MED.some(function (x) { return x[0] === n; }) || fld.some(function (f) { return f.chave === n; }) || vls.some(function (v) { return v.chave === n; }); }
    // sinônimos (raiox_sin): apelido -> medida ou campo (ou valor)
    var sinL = Object.keys(sin).map(function (a) { return [S(a).split(' '), String(sin[a])]; }).filter(function (p) { return p[0][0]; }).sort(function (a, b) { return b[0].length - a[0].length; });
    sinL.forEach(function (p) {
      for (var i = 0; i + p[0].length <= tk.length; i++) {
        if (tk[i].ok || tk[i].forca || !p[0].every(function (w, j) { return !tk[i + j].ok && !tk[i + j].forca && tk[i + j].n === w; })) continue;
        var al = S(p[1]), f = null, md = P_MED.filter(function (x) { return x[0] === al; })[0];
        if (md) f = { t: 'med', m: md[1] }; else { var fc = fld.filter(function (x) { return x.chave === al; })[0]; if (fc) f = { t: 'campo', ref: fc.ref }; else { var vv = vls.filter(function (x) { return x.chave === al; })[0]; if (vv) f = { t: 'val', campo: vv.campo, valor: vv.valor }; } }
        if (!f) continue;
        tk[i].forca = f; for (var j = 1; j < p[0].length; j++) tk[i + j].ok = true;
      }
    });
    // ---- período (antes do resto: "este mês", "mês passado", datas...) ----
    function validD(a, m, d) { var x = new Date(a, m - 1, d); return x.getFullYear() === a && x.getMonth() === m - 1 && x.getDate() === d; }
    function isoD(a, m, d) { return a + '-' + p2n(m) + '-' + p2n(d); }
    function addDias(iso, n) { var x = new Date(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10) + n); return x.getFullYear() + '-' + p2n(x.getMonth() + 1) + '-' + p2n(x.getDate()); }
    function dataDe(raw) {
      var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(raw); if (m) return validD(+m[1], +m[2], +m[3]) ? isoD(+m[1], +m[2], +m[3]) : null;
      m = /^(\d{1,2})\/(\d{1,2})(?:\/(\d{4}|\d{2}))?$/.exec(raw); if (!m) return null;
      var a = m[3] ? (m[3].length === 2 ? 2000 + +m[3] : +m[3]) : (H ? H.a : null); if (a == null) return null;
      return validD(a, +m[2], +m[1]) ? isoD(a, +m[2], +m[1]) : null;
    }
    var hojeISO = H ? isoD(H.a, H.m, H.d) : null;
    function anoDoMes(mes) { var a = null; (ctx.meses || []).forEach(function (k) { if (+k.slice(5, 7) === mes && (a == null || +k.slice(0, 4) > a)) a = +k.slice(0, 4); }); return a != null ? a : (H ? H.a : null); }
    function setP(p, ids) { if (out.periodo || !p) return false; out.periodo = p; ids.forEach(function (j) { tk[j].ok = true; }); return true; }
    function livre(i) { return i < tk.length && !tk[i].ok && !tk[i].forca; }
    for (var i = 0; i < tk.length; i++) {
      if (!livre(i)) continue;
      var r = tk[i].raw, n = tk[i].n, m2, d1 = dataDe(r), prev = i > 0 && !tk[i - 1].ok ? tk[i - 1].n : '', nx = livre(i + 1) ? tk[i + 1].n : '';
      if ((m2 = /^(\d{1,2})\/(\d{4})$/.exec(r))) { if (+m2[1] >= 1 && +m2[1] <= 12) setP({ tipo: 'mes', mes: +m2[1], ano: +m2[2] }, [i]); continue; }
      if (d1) {
        if (livre(i + 2) && /^(a|ate|e|ao|-)$/.test(nx) && dataDe(tk[i + 2].raw)) { var d2 = dataDe(tk[i + 2].raw), de = d1, ate = d2; if (de > ate) { de = d2; ate = d1; } setP({ tipo: 'intervalo', de: de, ate: ate }, [i, i + 1, i + 2]); }
        else setP({ tipo: 'intervalo', de: d1, ate: d1 }, [i]);
        continue;
      }
      if (n === 'hoje' && hojeISO) { setP({ tipo: 'intervalo', de: hojeISO, ate: hojeISO }, [i]); continue; }
      if (n === 'ontem' && hojeISO) { var o = addDias(hojeISO, -1); setP({ tipo: 'intervalo', de: o, ate: o }, [i]); continue; }
      if (/^(19|20)\d\d$/.test(r) && !(i > 0 && P_MESES.indexOf(prev) >= 0)) { setP({ tipo: 'ano', ano: +r }, [i]); continue; }
      if ((n === 'mes' || n === 'ano') && prev !== 'por' && prev !== 'cada') {
        var rel = /^(este|esse|neste|nesse)$/.test(prev) || /^(atual|corrente)$/.test(nx) ? 0 : /^(passado|anterior)$/.test(nx) || prev === 'ultimo' ? -1 : null;
        if (rel != null && H) {
          var ids = [i]; if (/^(este|esse|neste|nesse|ultimo)$/.test(prev)) ids.push(i - 1); if (/^(atual|corrente|passado|anterior)$/.test(nx)) ids.push(i + 1);
          if (ids.every(function (j) { return !tk[j].ok; })) {
            if (n === 'ano') setP({ tipo: 'ano', ano: H.a + rel }, ids);
            else { var mes = H.m + rel, ano = H.a; if (mes < 1) { mes = 12; ano--; } setP({ tipo: 'mes', mes: mes, ano: ano }, ids); }
          }
        }
        continue;
      }
      if (n === 'ultimo' && livre(i + 1) && /^\d+$/.test(tk[i + 1].raw) && livre(i + 2) && tk[i + 2].n === 'dia' && hojeISO) { setP({ tipo: 'intervalo', de: addDias(hojeISO, -(+tk[i + 1].raw)), ate: hojeISO }, [i, i + 1, i + 2]); continue; }
      var im = P_MESES.indexOf(n), simM = 1;
      if (im < 0 && n.length >= 5 && !conhecida(n) && !/\d/.test(n)) {
        var best = 0.8, cnt = 0; P_MESES.forEach(function (x, j) { var s = sim(n, x); if (s > best + 1e-9) { best = s; im = j; cnt = 1; } else if (s >= best - 1e-9 && s >= 0.8 && j !== im) cnt++; }); if (cnt !== 1) im = -1;
      }
      if (im >= 0) {
        var ids2 = [i], ano2 = null;
        if (livre(i + 1) && tk[i + 1].n === 'de' && livre(i + 2) && /^(19|20)\d\d$/.test(tk[i + 2].raw)) { ano2 = +tk[i + 2].raw; ids2.push(i + 1, i + 2); }
        else if (livre(i + 1) && /^(19|20)\d\d$/.test(tk[i + 1].raw)) { ano2 = +tk[i + 1].raw; ids2.push(i + 1); }
        if (ano2 == null) ano2 = anoDoMes(im + 1);
        if (ano2 != null) setP({ tipo: 'mes', mes: im + 1, ano: ano2 }, ids2);
      }
    }
    // ---- medida, campo, agrupar e filtros ----
    function achar(i, lista, getCh, maxw) {
      var best = { s: 0, n: 0, ref: null };
      for (var w = Math.min(maxw, tk.length - i); w >= 1; w--) {
        var ok = true, gs = []; for (var j = 0; j < w; j++) { if (!livre(i + j)) { ok = false; break; } gs.push(tk[i + j].n); } if (!ok) continue;
        var g = gs.join(' ');
        lista.forEach(function (x) { var s = sim(g, getCh(x)); if (s >= 0.8 && s > best.s) best = { s: s, n: w, ref: x }; });
      }
      return best;
    }
    var porProx = false, aposQuant = false, total = false, unk = [];
    function marca(i, w) { for (var j = 0; j < w; j++) tk[i + j].ok = true; }
    function filtra(campo, valor) { if (!out.filtros.some(function (f) { return f.campo === campo && f.valor === valor; })) out.filtros.push({ campo: campo, valor: valor }); }
    function setMed(m) { if (m === 'total') { total = true; return; } if (!out.medida) out.medida = m; }
    for (i = 0; i < tk.length; i++) {
      var t = tk[i]; if (t.ok) continue;
      var cls = null;
      if (t.forca) { cls = t.forca; t.ok = true; }
      else if (t.n === 'por' || t.n === 'cada') { t.ok = true; porProx = true; continue; }
      else if (P_STOP.indexOf(' ' + t.n + ' ') >= 0 && !fld.some(function (f) { return f.chave === t.n; }) && !vls.some(function (v) { return v.chave === t.n; }) && achar(i, vls, function (x) { return x.chave; }, 4).n < 2 && achar(i, fld, function (x) { return x.chave; }, 4).n < 2) { t.ok = true; continue; }
      if (!cls) {
        if (t.n === 'numero' && i + 1 < tk.length && tk[i + 1].n === 'de' && !fld.some(function (f) { return f.chave === 'numero'; })) { marca(i, 2); setMed('quantidade'); aposQuant = true; porProx = false; continue; }
        if ((t.n === 'mes' || /^mensal/.test(t.n)) && (porProx || /^mensal/.test(t.n))) { t.ok = true; if (!out.agrupar) out.agrupar = 'mês'; porProx = false; aposQuant = false; continue; }
        var med = { s: 0, m: null }; P_MED.forEach(function (x) { var s = sim(t.n, x[0]); if (s > med.s && s >= 0.8) med = { s: s, m: x[1] }; });
        var fc = achar(i, fld, function (x) { return x.chave; }, 4);
        if (!fc.n) { // palavra distintiva de um único campo de nome composto
          var hit = fld.filter(function (f) { return f.chave.indexOf(' ') > 0 && f.chave.split(' ').some(function (w) { return w.length >= 4 && w === t.n; }); }); if (hit.length === 1) fc = { s: 0.9, n: 1, ref: hit[0] };
        }
        var vc = achar(i, vls, function (x) { return x.chave; }, 4);
        if (med.m && med.s >= fc.s && med.s >= vc.s) cls = { t: 'med', m: med.m, w: 1 };
        else if (fc.n && fc.s >= vc.s) cls = { t: 'campo', ref: fc.ref.ref, w: fc.n };
        else if (vc.n) cls = { t: 'val', campo: vc.ref.campo, valor: vc.ref.valor, w: vc.n };
        if (cls) marca(i, cls.w); else if (P_SUBST.indexOf(' ' + t.n + ' ') >= 0 || aposQuant) { t.ok = true; aposQuant = false; continue; } else { unk.push(i); porProx = false; continue; }
      }
      var por = porProx; porProx = false; aposQuant = false;
      if (cls.t === 'med') { setMed(cls.m); if (cls.m === 'quantidade') aposQuant = true; }
      else if (cls.t === 'val') filtra(cls.campo, cls.valor);
      else {
        var k = cls.ref, w2 = cls.w || 1;
        var falha = function () { for (var q0 = i; q0 < i + w2; q0++) unk.push(q0); };
        if (por) { if (k.t === 'data') { if (!out.agrupar) out.agrupar = 'mês'; } else if (k.t !== 'numero' && !out.agrupar) out.agrupar = k.n; else falha(); }
        else if (k.t === 'numero') { if (!out.campo) out.campo = k.n; }
        else if (k.t === 'data') { /* menção ao campo de data: nada a fazer */ }
        else {
          var j2 = i + w2; while (j2 < tk.length && !tk[j2].ok && /^(de|do|da|igual|e|=)$/.test(tk[j2].n) && j2 - (i + w2) < 2) j2++;
          var lv = (Array.isArray(vals[k.n]) ? vals[k.n] : []).map(function (v) { return { campo: k.n, valor: v, chave: S(v) }; }), vm = j2 < tk.length ? achar(j2, lv, function (x) { return x.chave; }, 4) : { n: 0 };
          if (vm.n) { for (var q = i + w2; q < j2 + vm.n; q++) tk[q].ok = true; filtra(k.n, vm.ref.valor); }
          else falha();
        }
      }
    }
    if (!out.medida && total) out.medida = out.campo ? 'soma' : 'quantidade';
    if (!out.medida && out.campo) out.medida = 'soma';
    // trechos não entendidos: palavras soltas (e as palavrinhas entre elas) viram um trecho só, com o texto original da frase
    var unkSet = {}; unk.forEach(function (j) { unkSet[j] = 1; });
    var j3 = 0; while (j3 < tk.length) {
      if (!unkSet[j3]) { j3++; continue; }
      var fim = j3, k3 = j3 + 1; while (k3 < tk.length) { if (unkSet[k3]) fim = k3; else if (P_STOP.indexOf(' ' + tk[k3].n + ' ') < 0) break; k3++; }
      out.naoEntendi.push(frase.slice(tk[j3].ini, tk[fim].fim).replace(/[,.;:!?]+$/, '')); j3 = fim + 1;
    }
    if (!out.medida && !out.campo && !out.agrupar && !out.filtros.length && !out.periodo && out.naoEntendi.length) out.naoEntendi = [frase.trim().replace(/[,.;:!?]+$/, '')];   // nada entendido: a frase inteira é o trecho
    return out;
  }

  // ---- etapa 5: contas personalizadas (interpretador próprio; nunca eval/Function) ----
  var FUNC = { quantidade: [0, 0, 1], soma: [1, 1, 1], media: [1, 1, 1], mediana: [1, 1, 1], distintos: [1, 1, 1], dias: [2, 2, 1] };   // nome: [mín campos, máx campos, aceita filtro]
  function compilaFormula(txt, campos) {
    txt = String(txt == null ? '' : txt);
    if (!txt.trim()) return { ok: false, erro: 'escreva a fórmula' };
    if (txt.length > 300) return { ok: false, erro: 'a fórmula passa de 300 caracteres' };
    var mapa = Object.create(null), nomes = [];
    (campos || []).forEach(function (k) { if (k.t === 'ignorar') return; mapa[norm(k.n)] = k.n; nomes.push(k.n); });
    var tk = [], i = 0, m, s = txt;
    while (i < s.length) {
      var c = s[i];
      if (/\s/.test(c)) { i++; continue; }
      if ((m = /^\d+(\.\d+)?/.exec(s.slice(i)))) { tk.push({ k: 'n', v: parseFloat(m[0]), raw: m[0] }); i += m[0].length; continue; }
      if ((m = /^[\p{L}_][\p{L}\p{N}_]*/u.exec(s.slice(i)))) { tk.push({ k: 'id', v: m[0], raw: m[0] }); i += m[0].length; continue; }
      if (c === '"' || c === '“' || c === '”') { var j = s.slice(i + 1).search(/["“”]/); if (j < 0) return { ok: false, erro: 'falta fechar as aspas' }; tk.push({ k: 'str', v: s.slice(i + 1, i + 1 + j), raw: s.slice(i, i + j + 2) }); i += j + 2; continue; }
      if ('+-*/(),='.indexOf(c) >= 0) { tk.push({ k: c, raw: c }); i++; continue; }
      return { ok: false, erro: "não entendi '" + c + "' na fórmula" };
    }
    var p = 0, prof = 0;
    function campo(t) {
      if (!t || (t.k !== 'id' && t.k !== 'str')) throw new Error('esperava o nome de um campo');
      var n = mapa[norm(t.v)]; if (n) return n;
      var best = null, bs = 0.6; nomes.forEach(function (x) { var sm = semelhanca(t.v, x); if (sm >= bs) { bs = sm; best = x; } });
      throw new Error("campo '" + t.v + "' não existe" + (best ? "; você quis dizer '" + best.toLowerCase() + "'?" : ''));
    }
    function filtro(g) {
      if (g.length !== 3 || g[1].k !== '=' || (g[2].k !== 'id' && g[2].k !== 'str' && g[2].k !== 'n')) throw new Error('o filtro deve ser no formato campo = valor');
      return { campo: campo(g[0]), valor: g[2].k === 'n' ? g[2].raw : g[2].v };
    }
    function chamada(nome) {
      var f = FUNC[nome]; p++; var grupos = [[]], dep = 0, fechou = false;
      while (p < tk.length) {
        var t = tk[p];
        if (t.k === '(') dep++;
        if (t.k === ')') { if (!dep) { fechou = true; break; } dep--; }
        if (t.k === ',' && !dep) grupos.push([]); else grupos[grupos.length - 1].push(t);
        p++;
      }
      if (!fechou) throw new Error('falta fechar o parêntese'); p++;
      if (grupos.length === 1 && !grupos[0].length) grupos = [];
      var nf = grupos.length - f[1];
      if (grupos.length < f[0] || grupos.length > f[1] + f[2]) throw new Error("a função '" + nome + "' pede " + (f[1] ? f[1] + ' campo' + (f[1] > 1 ? 's' : '') : 'nenhum campo') + (f[2] ? ' e, se quiser, um filtro' : ''));
      var no = { t: 'f', nome: nome, campos: grupos.slice(0, f[1]).map(function (g) { if (g.length !== 1) throw new Error('esperava o nome de um campo'); return campo(g[0]); }), filtro: null };
      if (nf > 0) no.filtro = filtro(grupos[f[1]]);
      return no;
    }
    function prim() {
      var t = tk[p]; if (!t) throw new Error('a fórmula termina antes da hora');
      if (t.k === 'n') { p++; return { t: 'n', v: t.v }; }
      if (t.k === '(') { if (++prof > 40) throw new Error('fórmula complicada demais'); p++; var e = soma(); if (!tk[p] || tk[p].k !== ')') throw new Error('falta fechar o parêntese'); p++; prof--; return e; }
      if (t.k === 'id' && tk[p + 1] && tk[p + 1].k === '(') {
        var nome = norm(t.v).toLowerCase();
        if (!Object.prototype.hasOwnProperty.call(FUNC, nome)) throw new Error("função '" + t.v + "' não existe");
        p++; return chamada(nome);
      }
      if (t.k === ')') throw new Error('parêntese fechado sem abrir');
      throw new Error("não entendi '" + t.raw + "' na fórmula");
    }
    function un() { var t = tk[p]; if (t && t.k === '-') { if (++prof > 40) throw new Error('fórmula complicada demais'); p++; var a = un(); prof--; return { t: 'neg', a: a }; } return prim(); }
    function prod() { var a = un(); while (tk[p] && (tk[p].k === '*' || tk[p].k === '/')) { var o = tk[p++].k; a = { t: 'op', o: o, a: a, b: un() }; } return a; }
    function soma() { var a = prod(); while (tk[p] && (tk[p].k === '+' || tk[p].k === '-')) { var o = tk[p++].k; a = { t: 'op', o: o, a: a, b: prod() }; } return a; }
    try {
      var ast = soma();
      if (p < tk.length) throw new Error(tk[p].k === ')' ? 'parêntese fechado sem abrir' : "não entendi '" + tk[p].raw + "' na fórmula");
      return { ok: true, ast: ast };
    } catch (e) { return { ok: false, erro: (e instanceof RangeError || /recursion|call stack/i.test(String(e.message))) ? 'fórmula complicada demais' : e.message }; }
  }
  // lista = registros; get(registro, campo) -> texto. Devolve número ou null ("sem dados").
  function avaliaFormula(ast, lista, get) {
    function sel(no) { if (!no.filtro) return lista; var v = norm(no.filtro.valor); return lista.filter(function (r) { return norm(get(r, no.filtro.campo)) === v; }); }
    function ms(v) { var x = msISO(v); if (x != null) return x; var d = /^(\d{4})-(\d{2})-(\d{2})/.exec(v || ''); return d ? new Date(+d[1], +d[2] - 1, +d[3]).getTime() : null; }
    function nums(L, f) { return L.map(function (r) { return numero(get(r, f)); }).filter(function (x) { return x != null && isFinite(x); }); }
    function ev(n) {
      if (n.t === 'n') return n.v;
      if (n.t === 'neg') { var a0 = ev(n.a); return a0 == null ? null : -a0; }
      if (n.t === 'op') {
        var a = ev(n.a), b = ev(n.b); if (a == null || b == null) return null;
        var r = n.o === '+' ? a + b : n.o === '-' ? a - b : n.o === '*' ? a * b : (b === 0 ? null : a / b);
        return r != null && isFinite(r) ? r : null;
      }
      var L = sel(n), v;
      if (n.nome === 'quantidade') return L.length;
      if (n.nome === 'distintos') { var u = Object.create(null), q = 0; L.forEach(function (r) { var x = String(get(r, n.campos[0]) || '').trim(); if (x && !u[norm(x)]) { u[norm(x)] = 1; q++; } }); return q; }
      if (n.nome === 'dias') { var ds = []; L.forEach(function (r) { var d1 = ms(get(r, n.campos[0])), d2 = ms(get(r, n.campos[1])); if (d1 != null && d2 != null) ds.push((d2 - d1) / 86400000); }); return ds.length ? ds.reduce(function (x, y) { return x + y; }, 0) / ds.length : null; }
      v = nums(L, n.campos[0]); if (!v.length) return null;
      if (n.nome === 'mediana') return mediana(v);
      var sm = v.reduce(function (x, y) { return x + y; }, 0); return n.nome === 'soma' ? sm : sm / v.length;
    }
    var out = ev(ast); return out != null && isFinite(out) ? out : null;
  }

  // PDF com texto (etapa 7b): paginas = [[{x, y, w, h, t}]] (pedaços de texto com posição) -> {rows, baixas:[[linha, coluna]]} ou null (R-124).
  // rows[0] é o cabeçalho; baixas indexa rows (0 = cabeçalho). Linha = mesmo y (± metade do corpo); coluna = x de início (± 6 pt).
  function tabelaPdf(paginas, maxLin) {
    maxLin = maxLin || 20000;
    var cortado = false, linhas = [], totItens = 0; // por página: [[{x, t}]] (células já coladas)
    paginas.forEach(function (itens) {
      if (totItens > 400000) return; totItens += itens.length; itens = itens.length > 100000 ? itens.slice(0, 100000) : itens;   // teto de pedaços de texto
      var its = itens.filter(function (i) { return t(i.t); }).sort(function (a, b) { return b.y - a.y; }), ls = [];
      its.forEach(function (i) { var l = ls[ls.length - 1]; if (l && Math.abs(l.y - i.y) <= (l.h || 10) / 2) l.its.push(i); else ls.push({ y: i.y, h: i.h, its: [i] }); });
      linhas.push(ls.map(function (l) {
        var it = l.its.sort(function (a, b) { return a.x - b.x; }), nc = 0, nw = 0;
        it.forEach(function (i) { nc += t(i.t).length; nw += i.w; });
        var cw = nc ? nw / nc : 5, cel = [];
        it.forEach(function (i) {
          var c = cel[cel.length - 1], gap = c ? i.x - c.fim : 0;
          if (c && gap < 1.5 * cw) { c.t += (gap > 0.15 * cw && !/\s$/.test(c.t) && !/^\s/.test(i.t) ? ' ' : '') + i.t; c.fim = i.x + i.w; }
          else cel.push({ x: i.x, t: i.t, fim: i.x + i.w });
        });
        return cel.map(function (c) { return { x: c.x, t: t(c.t) }; });
      }));
    });
    var tab = [], xs = [];
    linhas.forEach(function (ls) { ls.forEach(function (l) { if (l.length >= 2) { tab.push(l); l.forEach(function (c) { xs.push(c.x); }); } }); });
    if (tab.length < 2) return null;
    xs.sort(function (a, b) { return a - b; });
    var gr = [];
    xs.forEach(function (x) { var g = gr[gr.length - 1]; if (g && x - g.ult <= 6) { g.n++; g.ult = x; g.soma += x; } else gr.push({ n: 1, ult: x, soma: x, ini: x }); });
    var cols = gr.filter(function (g) { return g.n >= Math.max(2, tab.length * 0.25); }).map(function (g) { return g.ini; }).slice(0, 200);   // teto de colunas
    if (cols.length < 2) return null;
    var colDe = function (x) { var lo = 0, hi = cols.length - 1, j = 0; while (lo <= hi) { var md = (lo + hi) >> 1; if (cols[md] <= x + 6) { j = md; lo = md + 1; } else hi = md - 1; } return j; };   // busca binária (cols está em ordem)
    var cabP = linhas[0] || [], hdr = null, hdrT = '', rows = [], baixas = [], lm = [];
    // monta cada linha de tabela: texto por coluna + marcas (colisão de duas células na mesma coluna)
    var monta = function (l) { var r = cols.map(function () { return ''; }), col = {}; l.forEach(function (c) { var j = colDe(c.x); if (r[j]) { r[j] += ' ' + c.t; col[j] = 1; } else r[j] = c.t; }); return { r: r, col: col, n: l.length }; };
    for (var k = 0; k < cabP.length && !hdr; k++) { if (cabP[k].length < 2) continue; var m = monta(cabP[k]); if (m.r.every(function (x) { return x; })) { hdr = m; hdrT = m.r.join('\u0001'); cabP = { desde: k }; } }
    if (!hdr) return null;
    rows.push(hdr.r);
    linhas.forEach(function (ls, p) {
      ls.forEach(function (l, k) {
        if (l.length < 2 || (p === 0 && k <= cabP.desde)) return;
        var m = monta(l); if (m.r.join('\u0001') === hdrT) return;
        if (rows.length > maxLin || rows.length * cols.length > 1000000) { cortado = true; return; }   // teto de linhas e de células
        rows.push(m.r); lm.push(m);
      });
    });
    if (rows.length < 2) return null;
    // baixa confiança: vazia em linha com as demais preenchidas; nº de pedaços diferente do cabeçalho (colisão); foge do padrão número/data da coluna
    var padrao = cols.map(function (c, j) {
      var v = rows.slice(1).map(function (r) { return r[j]; }).filter(Boolean);
      return v.length > 0 && v.filter(function (x) { return numero(x) !== null || dataISO(x) !== ''; }).length >= 0.9 * v.length;
    });
    lm.forEach(function (m, i) {
      m.r.forEach(function (x, j) {
        if ((!x && m.r.some(Boolean)) || m.col[j] || (x && padrao[j] && numero(x) === null && dataISO(x) === '')) baixas.push([i + 1, j]);
      });
    });
    return { rows: rows, baixas: baixas, cortado: cortado };
  }

  // OCR (etapa 7c). words = [{t, x0, y0, x1, y1, c}] de uma página/foto (coordenadas da imagem, y para baixo; c = confiança 0-100).
  // Vira itens {x, y, w, h, t} na escala do PDF (corpo do texto ~10) com y invertido (topo = maior y). Palavra de confiança < 75 leva a marca .
  var MARCA = '';
  function itensOcr(words) {
    var ws = words.filter(function (w) { return t(w.t) && w.x1 > w.x0 && w.y1 > w.y0; });
    if (!ws.length) return [];
    var hs = ws.map(function (w) { return w.y1 - w.y0; }).sort(function (a, b) { return a - b; }), mh = Math.max(1, hs[hs.length >> 1]), k = 10 / mh;
    ws = ws.filter(function (w) { return /[0-9A-Za-zÀ-ÿ]/.test(w.t) || (w.y1 - w.y0) <= 1.25 * mh; });   // traço fantasma (borda, sujeira) bem mais alto que o texto: descarta
    return ws.map(function (w) { return { x: w.x0 * k, y: -(w.y0 + w.y1) / 2 * k, w: (w.x1 - w.x0) * k, h: (w.y1 - w.y0) * k, t: (w.c < 75 ? MARCA : '') + t(w.t) }; });
  }
  // Regra 3: coluna de códigos (letra + dígitos) ou de números/datas (>= 60% das células) tem as confusões O/I/S/B/Z trocadas; só nessas colunas.
  function corrigeOcr(rows, baixas) {
    var ba = {}; baixas.forEach(function (b) { ba[b[0] + ',' + b[1]] = 1; });
    var COD = /^[A-Za-z]\d+$/, NUM = /^[\d,.\/: ]+$/, DEC = /^[\d.]*\d,\d{2}$/;
    var troca = function (s) { return s.replace(/[OoQD]/g, '0').replace(/[Il|]/g, '1').replace(/S/g, '5').replace(/B/g, '8').replace(/Z/g, '2'); };
    var cod = function (x) { return /^[A-Za-z]/.test(x) ? x.charAt(0) + troca(x.slice(1)) : ''; };   // no código a letra do começo fica
    for (var j = 0; j < rows[0].length; j++) {
      var cel = rows.slice(1).map(function (r) { return r[j]; }).filter(Boolean); if (!cel.length) continue;
      // o formato vale também depois da troca (um código lido "VOOOO1" ainda é código), desde que a célula tenha ao menos um dígito
      var nc = cel.filter(function (x) { return COD.test(x) || (/\d/.test(x) && COD.test(cod(x))); }).length, nn = cel.filter(function (x) { return NUM.test(x) || (/\d/.test(x) && NUM.test(troca(x))); }).length;
      var modo = nc >= 0.6 * cel.length ? 'cod' : nn >= 0.6 * cel.length ? 'num' : '';
      if (!modo) {   // coluna de texto: nada é alterado; só marca a célula que começa em minúscula quando as demais começam em maiúscula (ex.: "I" lido como "l")
        if (cel.filter(function (x) { return /^[A-ZÀ-Ý]/.test(x); }).length >= 0.8 * cel.length) rows.forEach(function (r, i) { if (i && /^[a-zà-ÿ]/.test(r[j])) ba[i + ',' + j] = 1; });
        continue;
      }
      var dec = modo === 'num' && cel.filter(function (x) { return DEC.test(troca(x)); }).length >= 0.8 * cel.length;   // coluna de valores com 2 casas
      var ln = {}, ml = 0; if (modo === 'cod') { cel.forEach(function (x) { ln[x.length] = (ln[x.length] || 0) + 1; }); Object.keys(ln).forEach(function (k) { if (!ml || ln[k] > ln[ml]) ml = +k; }); }   // tamanho mais comum dos códigos
      for (var i = 1; i < rows.length; i++) {
        var x = rows[i][j]; if (!x || !/\d/.test(x)) continue;   // célula sem nenhum dígito ("Isento", "N/D") nunca é trocada
        var y = modo === 'cod' ? cod(x.replace(/\s+/g, '')) || x : troca(x);   // código não tem espaço
        if (modo === 'cod' && ml && y.length === ml + 1 && y.indexOf('00') > 0) y = y.replace('00', '0');   // um zero a mais (letra O lida em dobro)
        if (dec && !DEC.test(y)) { if (/^\d+ \d{2}$/.test(y)) y = y.replace(' ', ','); else if (/^\d{3,}$/.test(y)) y = y.slice(0, -2) + ',' + y.slice(-2); }   // vírgula lida como espaço ou perdida
        if (y !== x) { rows[i][j] = y; ba[i + ',' + j] = 1; }
      }
    }
    return Object.keys(ba).map(function (k) { var p = k.split(','); return [+p[0], +p[1]]; });
  }
  // paginas = [words]; devolve {rows, baixas} (como tabelaPdf, já com a regra 3) ou null
  function tabelaOcr(paginas) {
    var r = tabelaPdf(paginas.map(itensOcr), 20000); if (!r) return null;
    var baixas = [];
    r.rows = r.rows.map(function (lin, i) { return lin.map(function (x, j) { if (x.indexOf(MARCA) >= 0) { baixas.push([i, j]); return t(x.split(MARCA).join('')); } return x; }); });
    r.baixas.forEach(function (b) { baixas.push(b); });
    return { rows: r.rows, baixas: corrigeOcr(r.rows, baixas) };
  }

  // ---- tela Relatório (9c): contas puras, sem tela ----
  var FAIXAS_IDADE = ['0 a 7 dias', '8 a 15 dias', '16 a 30 dias', 'Mais de 30 dias'];
  // idade em dias inteiros (para baixo) = hoje - data do registro; hojeMs = hoje às 00:00 local (R-164)
  function idadeDias(iso, hojeMs) {
    var ms = msISO(iso), m;
    if (ms == null) { m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || ''); if (!m) return null; ms = new Date(+m[1], +m[2] - 1, +m[3]).getTime(); }
    return Math.floor((hojeMs - ms) / 86400000);
  }

  // ---- "O que o Raio X encontrou" (9c.7, E2): regras fixas, sem IA. Devolve TODOS os achados na ordem de prioridade; o corte (2 por regra, 5 no total) é da tela.
  // o = { regs:[{codigo,v}], campos:[{n,t}], cd, sit, aberto(r), hoje:'aaaa-mm-dd', hojeMs, par:[1ª data, 2ª data]|null, pares:n, fmtN, fmtP }
  function achadosDe(o) {
    var L = o.regs, campos = o.campos, cd = o.cd, sit = o.sit, hoje = o.hoje, out = [], ok = function (s) { return /^\d{4}-\d{2}-\d{2}/.test(s || ''); };
    var d10 = function (s) { return (s || '').slice(0, 10); }, br = function (s) { return s.slice(8, 10) + '/' + s.slice(5, 7) + '/' + s.slice(0, 4); }, mmaa = function (m) { return m.slice(5) + '/' + m.slice(0, 4); };
    var dh = function (s) { return s.length >= 16 ? s.slice(0, 16) : d10(s) + 'T00:00'; }, fI = function (n) { return n.toLocaleString('pt-BR'); };
    var fN = o.fmtN || String, fP = o.fmtP || function (n) { return n.toFixed(1).replace('.', ',') + '%'; };
    var datas = campos.filter(function (k) { return k.t === 'data'; }), nums = campos.filter(function (k) { return k.t === 'numero'; });
    var cats = campos.filter(function (k) { return k.t === 'categoria' || k.t === 'situacao'; }), grupos = cats.filter(function (k) { return k.n !== sit; });
    var aberto = sit ? function (r) { return o.aberto(r); } : function () { return false; };
    var dia = function (s) { var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s); return Date.UTC(+m[1], +m[2] - 1, +m[3]) / 86400000; };
    var por = function (regra, lista) { lista.sort(function (a, b) { return b.ix.length - a.ix.length; }); lista.forEach(function (a) { a.regra = regra; out.push(a); }); };
    var idx = function (f) { var r = []; L.forEach(function (x, i) { if (f(x, i)) r.push(i); }); return r; };
    var A = [];
    // A1 data no futuro
    datas.forEach(function (k) {
      var ix = idx(function (r) { return ok(r.v[k.n]) && d10(r.v[k.n]) > hoje; }); if (!ix.length) return;
      var mx = ix.map(function (i) { return d10(L[i].v[k.n]); }).sort().pop();
      A.push({ titulo: 'Datas no futuro', frase: fI(ix.length) + ' registros com ' + k.n + ' depois de hoje; a mais distante é ' + br(mx) + '.', porque: 'data maior que a data de hoje', ix: ix });
    }); por('A1', A); A = [];
    // A2 data final antes da inicial
    if (o.par && o.par[0] && o.par[1] && o.par[0] !== o.par[1]) {
      var a = o.par[0], b = o.par[1], ix2 = idx(function (r) { return ok(r.v[a]) && ok(r.v[b]) && dh(r.v[b]) < dh(r.v[a]); });
      if (ix2.length) A.push({ titulo: 'Datas fora de ordem', frase: fI(ix2.length) + ' registros com ' + b + ' antes de ' + a + '.', porque: b + ' anterior a ' + a, ix: ix2 });
    } por('A2', A); A = [];
    // A3 parados há muito tempo
    if (cd && sit) {
      var id3 = {}, ix3 = idx(function (r, i) { if (!aberto(r) || !ok(r.v[cd])) return false; var d = idadeDias(r.v[cd], o.hojeMs); id3[i] = d; return d != null && d > 30; });
      if (ix3.length) A.push({ titulo: 'Parados há muito tempo', frase: fI(ix3.length) + ' registros em aberto há mais de 30 dias; o mais antigo há ' + maxDe(ix3.map(function (i) { return id3[i]; })) + ' dias.', porque: 'em aberto há mais de 30 dias', ix: ix3 });
    } por('A3', A); A = [];
    // A4 fora da curva
    nums.forEach(function (k) {
      var v = []; L.forEach(function (r) { var x = numero(r.v[k.n]); if (x != null) v.push(x); });
      var med = mediana(v); if (med == null || !(med > 0)) return;
      var ix = idx(function (r) { var x = numero(r.v[k.n]); return x != null && x > 3 * med; }); if (!ix.length) return;
      var mi = ix[0]; ix.forEach(function (i) { var x = numero(L[i].v[k.n]), y = numero(L[mi].v[k.n]); if (x > y || (x === y && L[i].codigo < L[mi].codigo)) mi = i; });
      A.push({ titulo: 'Valores fora da curva em ' + k.n, frase: fI(ix.length) + ' registros com ' + k.n + ' acima de 3 vezes a mediana (' + fN(3 * med) + '); o maior é ' + fN(numero(L[mi].v[k.n])) + ' (' + L[mi].codigo + ').', porque: 'mais de 3 vezes a mediana', ix: ix });
    }); por('A4', A); A = [];
    // meses com registros (sem data no futuro), usados por A5 e A6
    var meses = []; if (cd) { var ms = {}; L.forEach(function (r) { if (ok(r.v[cd]) && d10(r.v[cd]) <= hoje) ms[r.v[cd].slice(0, 7)] = 1; }); meses = Object.keys(ms).sort(); }
    // A5 pendências crescendo
    if (cd && sit && meses.length >= 3) {
      var u3 = meses.slice(-3), ln = u3.map(function (m) { return idx(function (r) { return aberto(r) && ok(r.v[cd]) && r.v[cd].slice(0, 7) === m; }); });
      if (ln[0].length < ln[1].length && ln[1].length < ln[2].length)
        A.push({ titulo: 'Pendências crescendo', frase: 'Os registros em aberto que entram a cada mês cresceram 3 meses seguidos: ' + u3.map(function (m, j) { return mmaa(m) + ' ' + ln[j].length; }).join(', ') + '.', porque: '3 meses seguidos de alta', ix: ln[0].concat(ln[1], ln[2]) });
    } por('A5', A); A = [];
    // A6 mudança brusca
    if (cd && meses.length >= 2) {
      var m1 = meses[meses.length - 2], m2 = meses[meses.length - 1];
      var r1 = idx(function (r) { return ok(r.v[cd]) && r.v[cd].slice(0, 7) === m1; }), r2 = idx(function (r) { return ok(r.v[cd]) && r.v[cd].slice(0, 7) === m2; });
      if (r1.length >= 20 && r2.length >= 20) {
        cats.sort(function (x, y) { return (y.n === sit) - (x.n === sit); }).forEach(function (k) {
          var c1 = new Map(), c2 = new Map();
          r1.forEach(function (i) { var x = L[i].v[k.n]; if (x) { if (!c1.has(x)) c1.set(x, []); c1.get(x).push(i); } });
          r2.forEach(function (i) { var x = L[i].v[k.n]; if (x) { if (!c2.has(x)) c2.set(x, []); c2.get(x).push(i); } });
          var vals = Array.from(new Set(Array.from(c1.keys()).concat(Array.from(c2.keys())))).sort();
          vals.forEach(function (val) {
            var i1 = c1.get(val) || [], i2 = c2.get(val) || [];
            var p1 = 100 * i1.length / r1.length, p2 = 100 * i2.length / r2.length;
            if (Math.abs(p2 - p1) >= 15) A.push({ titulo: 'Mudança brusca em ' + k.n, frase: val + ' foi de ' + fP(p1) + ' em ' + mmaa(m1) + ' para ' + fP(p2) + ' em ' + mmaa(m2) + '.', porque: 'mudou 15 pontos ou mais de um mês para o outro', ix: i1.concat(i2) });
          });
        });
      }
    } por('A6', A); A = [];
    // A7 concentração escondida
    if (sit) {
      var porSit = new Map(); L.forEach(function (r, i) { var x = r.v[sit]; if (x) { if (!porSit.has(x)) porSit.set(x, []); porSit.get(x).push(i); } });
      var tot = grupos.map(function (g) { var m = new Map(); L.forEach(function (r) { var x = r.v[g.n]; if (x) m.set(x, (m.get(x) || 0) + 1); }); return m; });
      Array.from(porSit.keys()).sort().forEach(function (val) {
        var base = porSit.get(val); if (base.length < 10) return;
        grupos.forEach(function (g, gi) {
          var m = new Map(); base.forEach(function (i) { var x = L[i].v[g.n]; if (x) { if (!m.has(x)) m.set(x, []); m.get(x).push(i); } });
          Array.from(m.keys()).sort().forEach(function (gval) {
            var ix = m.get(gval), pa = 100 * ix.length / base.length, pt = 100 * tot[gi].get(gval) / L.length;
            if (pa >= 50 && pa >= 2 * pt) A.push({ titulo: 'Concentração em ' + val, frase: g.n + ' ' + gval + ' responde por ' + fP(pa) + ' dos registros ' + val + ', mas só por ' + fP(pt) + ' do total.', porque: 'metade ou mais de uma situação num só grupo', ix: ix });
          });
        });
      });
    } por('A7', A); A = [];
    // A8 buracos: (a) campo vazio, (b) dias sem registro
    var saida = o.par && o.par[1] && sit ? o.par[1] : null;
    campos.forEach(function (k) {
      if (k.t === 'codigo' || !L.length) return;
      var ix = idx(function (r) { if (String(r.v[k.n] == null ? '' : r.v[k.n]).trim() !== '') return false; return !(k.n === saida && aberto(r)); });
      var p = 100 * ix.length / L.length;
      if (ix.length && p >= 20) A.push({ titulo: 'Campo vazio: ' + k.n, frase: k.n + ' está vazio em ' + fP(p) + ' dos registros (' + fI(ix.length) + ').', porque: 'vazio em 20% ou mais', ix: ix });
    });
    datas.forEach(function (k) {
      var com = idx(function (r) { return ok(r.v[k.n]) && d10(r.v[k.n]) <= hoje; }); if (com.length < 30) return;
      var ds = {}; com.forEach(function (i) { ds[d10(L[i].v[k.n])] = 1; }); ds = Object.keys(ds).sort();
      var best = null; for (var j = 1; j < ds.length; j++) { var d = dia(ds[j]) - dia(ds[j - 1]) - 1; if (d >= 14 && (!best || d > best.d)) best = { d: d, a: ds[j - 1], b: ds[j] }; }
      if (!best) return;
      var ix = com.filter(function (i) { var x = d10(L[i].v[k.n]); return x === best.a || x === best.b; }), pr = new Date(dia(best.a) * 86400000 + 86400000), nx = new Date(dia(best.b) * 86400000 - 86400000);
      var iso = function (t) { return t.toISOString().slice(0, 10); };
      A.push({ titulo: 'Dias sem registro', frase: 'Nenhum registro de ' + br(iso(pr)) + ' a ' + br(iso(nx)) + ' (' + best.d + ' dias).', porque: '14 dias ou mais sem registro', ix: ix });
    }); por('A8', A); A = [];
    // A9 possíveis repetidos
    if (o.pares > 0) A.push({ titulo: 'Possíveis repetidos', frase: fI(o.pares) + ' pares de registros parecidos; confira se são o mesmo.', porque: 'texto muito parecido entre registros', ix: o.parIx || [] });
    por('A9', A);
    return out;
  }
  function faixaIdade(d) { return d == null || d < 0 ? -1 : d <= 7 ? 0 : d <= 15 ? 1 : d <= 30 ? 2 : 3; }
  // R-165 / D-66: múltiplo de 24 e >= 48 vira dias
  function fmtPrazo(h) { return h >= 48 && h % 24 === 0 ? (h / 24) + ' dias' : h + ' h'; }
  function maxDe(v) { var m = -Infinity; for (var i = 0; i < v.length; i++) if (v[i] > m) m = v[i]; return m; }
  function minDe(v) { var m = Infinity; for (var i = 0; i < v.length; i++) if (v[i] < m) m = v[i]; return m; }
  function estat(v) {
    if (!v.length) return null;
    var s = v.reduce(function (a, b) { return a + b; }, 0);
    return { n: v.length, soma: s, media: s / v.length, mediana: mediana(v), min: minDe(v), max: maxDe(v) };
  }
  // R-167: frases da distribuição (D-70: nada com mediana <= 0)
  function fraseDist(e, fmt) {
    var f = ['Metade dos registros ficou abaixo de ' + fmt(e.mediana) + '.'];
    if (e.mediana > 0 && e.media > 1.2 * e.mediana) f.push('A média está acima da mediana porque alguns valores são bem altos.');
    else if (e.mediana > 0 && e.media < 0.8 * e.mediana) f.push('A média está abaixo da mediana porque alguns valores são bem baixos.');
    return f;
  }
  // itens = [{codigo, valor, grupo}]; maiores/menores com empate pelo código (R-167)
  function extremos(itens, n, maiores) {
    return itens.slice().sort(function (a, b) { return (maiores ? b.valor - a.valor : a.valor - b.valor) || (a.codigo < b.codigo ? -1 : a.codigo > b.codigo ? 1 : 0); }).slice(0, n);
  }
  // R-168: grupos = [[nome, valor]]; devolve linhas (até 10 + Outros), frases e k para 80%
  function concentracao(grupos) {
    var g = grupos.filter(function (x) { return x[1] > 0; }).sort(function (a, b) { return b[1] - a[1] || (String(a[0]) < String(b[0]) ? -1 : String(a[0]) > String(b[0]) ? 1 : 0); });
    var tot = g.reduce(function (a, x) { return a + x[1]; }, 0); if (!tot) return null;
    var ac = 0, k80 = 0, acs = g.map(function (x, i) { ac += x[1]; if (!k80 && 100 * ac / tot >= 80 - 1e-9) k80 = i + 1; return ac; });
    var linhas = g.slice(0, 10).map(function (x, i) { return { nome: x[0], valor: x[1], pct: 100 * x[1] / tot, acum: 100 * acs[i] / tot }; });
    if (g.length > 10) { var r = g.slice(10).reduce(function (a, x) { return a + x[1]; }, 0); linhas.push({ nome: 'Outros', valor: r, pct: 100 * r / tot, acum: 100 }); }
    linhas[linhas.length - 1].acum = 100;
    var nTop = Math.min(3, g.length), topo = acs[nTop - 1];
    return { linhas: linhas, total: tot, n: g.length, nTop: nTop, pctTop: 100 * topo / tot, k80: k80 };
  }
  // R-157 / R-169: sentido e percentual (sem sinal, 1 casa) ou sem base
  function compara(atual, anterior) {
    if (anterior == null || anterior === 0 || atual == null) return { tipo: 'sem' };
    if (atual === anterior) return { tipo: 'eq' };
    return { tipo: atual > anterior ? 'up' : 'down', p: Math.round(Math.abs((atual - anterior) / anterior * 1000)) / 10 };
  }
  function p2s(n) { return (n < 10 ? '0' : '') + n; }
  function mesMenos1(k) { var a = +k.slice(0, 4), m = +k.slice(5, 7) - 1; if (m < 1) { m = 12; a--; } return a + '-' + p2s(m); }
  function fimMes(k) { return k + '-' + p2s(new Date(Date.UTC(+k.slice(0, 4), +k.slice(5, 7), 0)).getUTCDate()); }
  function somaDias(iso, n) { var d = new Date(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10)) + n * 86400000); return d.getUTCFullYear() + '-' + p2s(d.getUTCMonth() + 1) + '-' + p2s(d.getUTCDate()); }
  function brData(iso) { return iso.slice(8, 10) + '/' + iso.slice(5, 7) + '/' + iso.slice(0, 4); }
  // R-169: períodos atual e anterior ({ini, fim, rot}); null = sem base. ultimoMes = 'aaaa-mm' do último mês com registros (usado com Tudo)
  function periodoAnterior(per, mes, de, ate, ultimoMes) {
    var rm = function (k) { return k.slice(5) + '/' + k.slice(0, 4); }, mm = function (k) { return { ini: k + '-01', fim: fimMes(k), rot: rm(k) }; };
    if (per === 'mes') return /^\d{4}-\d{2}$/.test(mes || '') ? { atual: mm(mes), ant: mm(mesMenos1(mes)) } : null;
    if (per === 'de') {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(de || '') || !/^\d{4}-\d{2}-\d{2}$/.test(ate || '') || ate < de) return null;
      var n = Math.round((Date.UTC(+ate.slice(0, 4), +ate.slice(5, 7) - 1, +ate.slice(8, 10)) - Date.UTC(+de.slice(0, 4), +de.slice(5, 7) - 1, +de.slice(8, 10))) / 86400000) + 1, ai = somaDias(de, -n), af = somaDias(de, -1);
      return { atual: { ini: de, fim: ate, rot: brData(de) + ' a ' + brData(ate) }, ant: { ini: ai, fim: af, rot: brData(ai) + ' a ' + brData(af) } };
    }
    return /^\d{4}-\d{2}$/.test(ultimoMes || '') ? { atual: mm(ultimoMes), ant: mm(mesMenos1(ultimoMes)) } : null;
  }

  /* formas de gráfico novas (9c.10): só contas de geometria, sem DOM */
  var GTAU = Math.PI * 2, gR2 = function (x) { return Math.round(x * 100) / 100; };
  function gMax(a, ini) { var m = ini; for (var i = 0; i < a.length; i++) if (a[i] > m) m = a[i]; return m; }
  function gMin(a, ini) { var m = ini; for (var i = 0; i < a.length; i++) if (a[i] < m) m = a[i]; return m; }
  // fatia de rosca (anel entre r0 e r1, de a0 a a1 em radianos); volta inteira vira quase inteira para o arco não sumir
  function arcoPath(cx, cy, r0, r1, a0, a1) {
    if (a1 - a0 >= GTAU - 0.0002) a1 = a0 + GTAU - 0.0002;
    var g = a1 - a0 > Math.PI ? 1 : 0, P = function (r, a) { return gR2(cx + r * Math.cos(a)) + ' ' + gR2(cy + r * Math.sin(a)); };
    return 'M' + P(r1, a0) + ' A' + r1 + ' ' + r1 + ' 0 ' + g + ' 1 ' + P(r1, a1) + ' L' + P(r0, a1) + ' A' + r0 + ' ' + r0 + ' 0 ' + g + ' 0 ' + P(r0, a0) + ' Z';
  }
  // regra do radar: 3 a 10 grupos e nenhum "Outros"
  function radarOk(nomes) { if (nomes.length < 3 || nomes.length > 10) return false; for (var i = 0; i < nomes.length; i++) if (nomes[i] === 'Outros') return false; return true; }
  // radar: eixos (pontas), pontos do polígono e anéis da grade; raio proporcional ao maior valor
  function radarGeom(valores, cx, cy, R) {
    var n = valores.length, mx = gMax(valores, 0), eixos = [], pontos = [], aneis = [], i, k;
    for (i = 0; i < n; i++) {
      var a = -Math.PI / 2 + i * GTAU / n, f = mx > 0 ? Math.max(0, valores[i]) / mx : 0;
      eixos.push({ x: gR2(cx + R * Math.cos(a)), y: gR2(cy + R * Math.sin(a)), ang: a });
      pontos.push({ x: gR2(cx + R * f * Math.cos(a)), y: gR2(cy + R * f * Math.sin(a)) });
    }
    [0.5, 1].forEach(function (q) { var p = []; for (k = 0; k < n; k++) p.push(gR2(cx + R * q * Math.cos(eixos[k].ang)) + ',' + gR2(cy + R * q * Math.sin(eixos[k].ang))); aneis.push(p.join(' ')); });
    return { eixos: eixos, pontos: pontos, aneis: aneis, max: mx };
  }
  // velocímetro: meio círculo de 0 a 100% (esquerda a direita); devolve o ponto de uma porcentagem na circunferência de raio r
  function velocPonto(pct, cx, cy, r) { var p = Math.max(0, Math.min(100, pct)), a = Math.PI + Math.PI * p / 100; return { x: gR2(cx + r * Math.cos(a)), y: gR2(cy + r * Math.sin(a)), ang: a }; }
  function velocArco(p0, p1, cx, cy, r) { var a = velocPonto(p0, cx, cy, r), b = velocPonto(p1, cx, cy, r); return 'M' + a.x + ' ' + a.y + ' A' + r + ' ' + r + ' 0 0 1 ' + b.x + ' ' + b.y; }
  // bolhas: x = nº de registros, y = média, área proporcional à soma; g = [{ n, media, soma }]
  function bolhasGeom(g, W, H, P, rMax) {
    var ns = g.map(function (x) { return x.n; }), ms = g.map(function (x) { return x.media; }), ss = g.map(function (x) { return Math.max(0, x.soma); });
    var n0 = gMin(ns, Infinity), n1 = gMax(ns, -Infinity), m0 = gMin(ms, Infinity), m1 = gMax(ms, -Infinity), s1 = gMax(ss, 0), pad = P + rMax;
    return g.map(function (x, i) {
      var r = s1 > 0 ? rMax * Math.sqrt(ss[i] / s1) : rMax / 2; if (r < 2) r = 2;
      return { x: gR2(n1 > n0 ? pad + (x.n - n0) / (n1 - n0) * (W - 2 * pad) : W / 2), y: gR2(m1 > m0 ? H - pad - (x.media - m0) / (m1 - m0) * (H - 2 * pad) : H / 2), r: gR2(r) };
    });
  }
  // área: caminho fechado da linha até o eixo (yBase)
  function areaPath(pts, yBase) { if (!pts.length) return ''; return 'M' + pts[0].x + ' ' + yBase + ' ' + pts.map(function (p) { return 'L' + p.x + ' ' + p.y; }).join(' ') + ' L' + pts[pts.length - 1].x + ' ' + yBase + ' Z'; }

  return { arcoPath: arcoPath, radarOk: radarOk, radarGeom: radarGeom, velocPonto: velocPonto, velocArco: velocArco, bolhasGeom: bolhasGeom, areaPath: areaPath, entender: entender, decode: decode, parseCSV: parseCSV, acharCabecalho: acharCabecalho, norm: norm, assinatura: assinatura, iso: iso, dataISO: dataISO, numero: numero, palpites: palpites,
    juntar: juntar, FAIXAS: FAIXAS, faixa: faixa, hm: hm, mediana: mediana, pctDentro: pctDentro, msISO: msISO, meta: meta, lev: lev, semelhanca: semelhanca, parecido: parecido,
    compilaFormula: compilaFormula, avaliaFormula: avaliaFormula, lerSinonimos: lerSinonimos, aplicaSinonimos: aplicaSinonimos, repetidos: repetidos, FAIXAS_IDADE: FAIXAS_IDADE, idadeDias: idadeDias, achadosDe: achadosDe, faixaIdade: faixaIdade, fmtPrazo: fmtPrazo, estat: estat, fraseDist: fraseDist, extremos: extremos, concentracao: concentracao, compara: compara, periodoAnterior: periodoAnterior, somaDias: somaDias, tabelaPdf: tabelaPdf, tabelaOcr: tabelaOcr, corrigeOcr: corrigeOcr, itensOcr: itensOcr, t: t };
})();
if (typeof module !== 'undefined') module.exports = Core;
