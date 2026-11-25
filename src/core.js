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
    return out;
  }

  // junta registros por código, campo a campo: campo vazio do novo não apaga o que já existe
  function juntar(velho, novo) {
    var v = {}, k;
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
    var m = Math.round(ms / 60000), d = Math.floor(m / 1440), h = Math.floor((m % 1440) / 60), mi = m % 60;
    return (d ? d + ' d ' : '') + (d || h ? h + ' h ' : '') + (mi < 10 ? '0' : '') + mi + ' min';
  }
  function mediana(a) { if (!a.length) return null; a = a.slice().sort(function (x, y) { return x - y; }); var m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; }
  function pctDentro(durs, limiteMs) { return durs.length ? 100 * durs.filter(function (x) { return x <= limiteMs; }).length / durs.length : null; }
  function msISO(s) { var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(s || ''); return m ? new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]).getTime() : null; }
  // meta: acima da meta fica verde; senão "faltam X para a meta"
  function meta(pct, alvo) {
    if (pct == null) return { ok: false, txt: '' };
    alvo = alvo == null ? 90 : alvo;
    return pct >= alvo ? { ok: true, txt: 'Acima da meta de ' + alvo + '%' } : { ok: false, txt: 'Faltam ' + (Math.round((alvo - pct) * 10) / 10).toString().replace('.', ',') + ' pontos para a meta de ' + alvo + '%' };
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

  return { decode: decode, parseCSV: parseCSV, acharCabecalho: acharCabecalho, norm: norm, assinatura: assinatura, iso: iso, dataISO: dataISO, numero: numero, palpites: palpites,
    juntar: juntar, FAIXAS: FAIXAS, faixa: faixa, hm: hm, mediana: mediana, pctDentro: pctDentro, msISO: msISO, meta: meta, lev: lev, semelhanca: semelhanca, parecido: parecido,
    lerSinonimos: lerSinonimos, aplicaSinonimos: aplicaSinonimos, repetidos: repetidos, t: t };
})();
if (typeof module !== 'undefined') module.exports = Core;
