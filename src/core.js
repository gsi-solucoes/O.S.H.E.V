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
    alvo = alvo == null ? 90 : alvo;
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
    } catch (e) { return { ok: false, erro: e.message === 'Maximum call stack size exceeded' ? 'fórmula complicada demais' : e.message }; }
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

  return { entender: entender, decode: decode, parseCSV: parseCSV, acharCabecalho: acharCabecalho, norm: norm, assinatura: assinatura, iso: iso, dataISO: dataISO, numero: numero, palpites: palpites,
    juntar: juntar, FAIXAS: FAIXAS, faixa: faixa, hm: hm, mediana: mediana, pctDentro: pctDentro, msISO: msISO, meta: meta, lev: lev, semelhanca: semelhanca, parecido: parecido,
    compilaFormula: compilaFormula, avaliaFormula: avaliaFormula, lerSinonimos: lerSinonimos, aplicaSinonimos: aplicaSinonimos, repetidos: repetidos, t: t };
})();
if (typeof module !== 'undefined') module.exports = Core;
