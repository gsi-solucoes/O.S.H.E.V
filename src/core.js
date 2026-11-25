/* ===== Raio X do Relatório · núcleo: leitura dos relatórios (MV R_ORDEM_SERVICO, detalhado, planilhas) e cálculos ===== */
var Core = (function () {
  function decode(buf) {
    try { return new TextDecoder('utf-8', { fatal: true }).decode(buf); }
    catch (e) { return new TextDecoder('windows-1252').decode(buf); }
  }

  function parseCSV(text) {
    var rows = [], row = [], cell = '', q = false, i = 0, c, n = text.length;
    var sep = ',';
    var firstLine = text.slice(0, 2000).split('\n')[0];
    if ((firstLine.match(/;/g) || []).length > (firstLine.match(/,/g) || []).length) sep = ';';
    for (; i < n; i++) {
      c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; }
        else cell += c;
      } else if (c === '"') q = true;
      else if (c === sep) { row.push(cell); cell = ''; }
      else if (c === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
      else if (c !== '\r') cell += c;
    }
    if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }

  var LABELS = {
    'situação': 'situacao', 'situacao': 'situacao', 'tipo': 'tipo', 'especialidade': 'especialidade',
    'solicitante': 'solicitante', 'data pedido': 'pedido', 'data término': 'termino', 'data termino': 'termino',
    'setor': 'setor', 'localidade': 'localidade', 'bem': 'bem', 'nr. do patrimônio': 'patrimonio',
    'marca': 'marca', 'modelo': 'modelo', 'série': 'serie', 'serie': 'serie', 'observações': 'obs',
    'observacoes': 'obs', 'prioridade': 'criticidade', 'criticidade': 'criticidade'
  };
  var RX_DATE = /^(\d{2})\/(\d{2})\/(\d{2,4})\s+(\d{1,2}):(\d{2})/;

  function toDate(s) {
    var m = RX_DATE.exec((s || '').trim());
    if (!m) return null;
    var y = +m[3]; if (y < 100) y += 2000;
    return new Date(y, +m[2] - 1, +m[1], +m[4], +m[5]);
  }
  function t(s) { return (s || '').replace(/\s+/g, ' ').trim(); }

  var FILAS = [
    ['aberta', /abert/], ['agendar', /agend/], ['aguardando material', /aguard|material/],
    ['conserto externo', /extern/], ['não atendida', /n[aã]o.?atend|nao_atend/],
    ['cancelada', /cancel/], ['concluída', /conclu/]
  ];
  function filaFrom(s) {
    s = (s || '').toLowerCase();
    if (/n[aã]o.?atend/.test(s)) return 'não atendida';
    for (var i = 0; i < FILAS.length; i++) if (FILAS[i][1].test(s)) return FILAS[i][0];
    return '';
  }

  function parseMV(rows, fileName) {
    var out = [], cur = null, mode = '', pendingFim = null;
    function close() { if (cur) out.push(cur); cur = null; }
    for (var r = 0; r < rows.length; r++) {
      var row = rows[r], first = t(row[0]);
      if (/^Ordem de Servi[çc]o Relacionadas/i.test(first)) { mode = 'rel'; continue; }
      if (/^Ordem de Servi[çc]o$/i.test(first)) { close(); cur = { os: '', desc: '', exec: [], file: fileName }; mode = 'head'; pendingFim = null; continue; }
      if (!cur) continue;
      if (mode === 'head' && !cur.os) {
        for (var k = 0; k < row.length; k++) {
          var v = t(row[k]);
          if (!cur.os && /^\d{4,7}$/.test(v)) { cur.os = v; continue; }
          if (cur.os && v) { cur.desc = v; break; }
        }
        if (cur.os) mode = 'fields';
        continue;
      }
      if (/^Servi[çc]o$/i.test(first)) { mode = 'exec'; continue; }
      if (mode === 'fields') {
        var lab = null;
        for (var j = 0; j < row.length; j++) {
          var cv = t(row[j]); if (!cv) continue;
          var key = LABELS[cv.toLowerCase()];
          if (key) { lab = key; continue; }
          if (lab && cur[lab] === undefined) { cur[lab] = cv; lab = null; }
        }
        continue;
      }
      if (mode === 'exec') {
        var vals = row.map(t).filter(function (x) { return x && x !== ':'; });
        if (!vals.length) continue;
        var dates = vals.filter(function (x) { return RX_DATE.test(x); });
        if (!first) { if (dates.length) pendingFim = dates[0]; continue; }
        var func = '';
        for (var z = 1; z < vals.length; z++) if (!RX_DATE.test(vals[z]) && !/^\d+:\d+$/.test(vals[z])) { func = vals[z]; break; }
        var ini = dates[0] || null, fim = dates[1] || pendingFim;
        cur.exec.push({ servico: first, func: func, ini: toDate(ini), fim: toDate(fim) });
        pendingFim = null;
      }
    }
    close();
    var filaArq = filaFrom(fileName);
    return out.filter(function (o) { return o.os; }).map(function (o) {
      o.fila = filaFrom(o.situacao) || filaArq || 'sem fila';
      o.pedido = toDate(o.pedido); o.termino = toDate(o.termino);
      o.especialidade = o.especialidade || 'Sem especialidade';
      o.tipo = o.tipo || 'Sem tipo';
      o.setor = o.setor || 'Sem setor';
      o.criticidade = o.criticidade || 'Não informada';
      return o;
    });
  }

  var RANK = { 'concluída': 3, 'cancelada': 3 };
  // ---- relatório DETALHADO do MV (histórico): Oficina > Setor > OS (sem horas, sem observação)
  function isDet(text) { var h = text.slice(0, 6000); return /Nr\.OS/.test(h) && /Funcion.rio da Oficina/.test(h); }
  function toDateD(s) { var d = toDate(s); if (d) return d; var m = /^(\d{2})\/(\d{2})\/(\d{2,4})$/.exec(t(s)); if (!m) return null; var y = +m[3]; if (y < 100) y += 2000; return new Date(y, +m[2] - 1, +m[1]); }
  function parseDet(rows) {
    var by = {}, setor = '', hdr = null, cur = null, modo = '';
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i]; if (!r || !r.length) continue;
      var c0 = t(r[0]), c1 = t(r[1]);
      if (c1 === 'Setor:') { setor = t(r[3]); cur = null; continue; }
      if (c0 === 'Nr.OS') { hdr = r.map(t); continue; }
      if (hdr && !c0 && /^\d+$/.test(c1)) {
        cur = { os: c1, setor: setor, tecnicos: [] };
        for (var j = 2; j < r.length; j++) {
          var v = t(r[j]); if (!v) continue;
          var k = Math.min(j, hdr.length - 1); while (k > 0 && !hdr[k]) k--;
          var lab = hdr[k] || '';
          if (/Pedido/.test(lab)) cur.pedido = v; else if (/Tipo/.test(lab)) cur.tipo = v; else if (/^Bem/.test(lab)) cur.bem = v;
          else if (/Plaqueta/.test(lab)) cur.plaqueta = v; else if (/Prev/.test(lab)) cur.prev = v; else if (/Execu/.test(lab)) cur.termino = v;
          else if (/Situa/.test(lab)) cur.situacao = v; else if (/Solicit/.test(lab)) cur.solicitante = v;
        }
        by[cur.os] = cur; modo = ''; continue;
      }
      if (!cur) continue;
      if (t(r[2]) === 'Servico:') { cur.desc = t(r.slice(3).join(' ')); modo = ''; continue; }
      if (c1.indexOf('Funcion') === 0) { modo = 'func'; var n = t(r.slice(2).join(' ')); if (n) cur.tecnicos.push(n); continue; }
      if (modo === 'func' && !c0 && !c1) { var n2 = t(r.join(' ')); if (n2 && !/^\d+$/.test(n2) && !/Total/.test(n2)) { cur.tecnicos.push(n2); continue; } }
      modo = '';
    }
    return Object.keys(by).map(function (k) {
      var o = by[k], p = toDateD(o.pedido), te = toDateD(o.termino), pv = toDateD(o.prev);
      return { os: o.os, p: p ? p.getTime() : null, te: te ? te.getTime() : null, pv: pv ? pv.getTime() : null, f: filaFrom(o.situacao) || 'sem fila',
        ti: o.tipo || 'Sem tipo', se: o.setor || 'Sem setor', so: o.solicitante || '', d: o.desc || '', b: o.bem || '', pl: o.plaqueta || '', tc: o.tecnicos };
    });
  }
  // ---- qualquer CSV em forma de tabela: acha o cabeçalho, chuta o que é cada coluna e lê com o mapa confirmado
  var CAMPOS = [['os', 'Nº da OS'], ['pedido', 'Data do pedido / abertura'], ['termino', 'Data de término / fechamento'], ['situacao', 'Situação / fila / status'],
    ['tipo', 'Tipo de OS'], ['especialidade', 'Especialidade'], ['setor', 'Setor'], ['localidade', 'Localidade / local'], ['solicitante', 'Solicitante'],
    ['desc', 'Descrição / serviço'], ['obs', 'Observações / tratativa'], ['tecnico', 'Técnico / funcionário'], ['criticidade', 'Criticidade / prioridade'],
    ['bem', 'Equipamento / bem'], ['plaqueta', 'Plaqueta / patrimônio'], ['prev', 'Data prevista / programada']];
  var PISTAS = { os: ['NR OS', 'NR.OS', 'N OS', 'NO OS', 'NUMERO OS', 'NUMERO DA OS', 'ORDEM SERVICO', 'ORDEM DE SERVICO', 'ORD SERVICO', 'OS', 'O.S', 'O.S.'],
    pedido: ['DT PEDIDO', 'DT. PEDIDO', 'DATA PEDIDO', 'DATA DO PEDIDO', 'ABERTURA', 'DATA ABERTURA', 'DT ABERTURA', 'SOLICITADO EM', 'CRIADO EM', 'DATA SOLICITACAO'],
    termino: ['TERMINO', 'DATA TERMINO', 'FECHAMENTO', 'CONCLUSAO', 'DT EXECUCAO', 'DT. EXECUCAO', 'ENCERRAMENTO', 'FINALIZACAO', 'DATA FIM'],
    situacao: ['SITUACAO', 'STATUS', 'FILA', 'ESTADO'], tipo: ['TIPO', 'TIPO DE OS', 'TIPO OS'], especialidade: ['ESPECIALIDADE', 'OFICINA', 'AREA', 'DISCIPLINA'],
    setor: ['SETOR', 'DEPARTAMENTO', 'CENTRO DE CUSTO', 'UNIDADE'], localidade: ['LOCALIDADE', 'LOCAL', 'AMBIENTE', 'QUARTO', 'SALA'],
    solicitante: ['SOLICITANTE', 'REQUISITANTE', 'USUARIO', 'SOLICITADO POR'], desc: ['DESCRICAO', 'SERVICO', 'PROBLEMA', 'DEFEITO', 'SOLICITACAO', 'DESCRICAO DO SERVICO'],
    obs: ['OBSERVACAO', 'OBSERVACOES', 'OBS', 'OBS.', 'COMENTARIO', 'COMENTARIOS', 'TRATATIVA'], tecnico: ['TECNICO', 'FUNCIONARIO', 'FUNCIONARIO DA OFICINA', 'RESPONSAVEL', 'EXECUTANTE', 'COLABORADOR'],
    criticidade: ['CRITICIDADE', 'PRIORIDADE', 'URGENCIA', 'CLASSIFICACAO', 'RISCO', 'GRAU'], bem: ['BEM', 'EQUIPAMENTO', 'ATIVO'], plaqueta: ['PLAQUETA', 'NR. DA PLAQUETA', 'PATRIMONIO', 'TAG'],
    prev: ['DT PREV', 'DT. PREV. EXEC.', 'PREVISTA', 'PREVISAO', 'PROGRAMADA', 'DT PROGRAMADA', 'PRAZO'] };
  function chuteCampo(h) {
    var n = norm(h).replace(/\./g, ' ').replace(/\s+/g, ' ').trim(), melhor = '', nota = 0;
    if (!n) return '';
    Object.keys(PISTAS).forEach(function (c) {
      PISTAS[c].forEach(function (p) {
        var q = norm(p).replace(/\./g, ' ').replace(/\s+/g, ' ').trim(), sc = 0;
        if (n === q) sc = 3 + q.length / 100;
        else if (q.length >= 4 && (' ' + n + ' ').indexOf(' ' + q + ' ') >= 0) sc = 2 + q.length / 100;
        else if (q.length >= 5 && n.indexOf(q) >= 0) sc = 1 + q.length / 100;
        if (sc > nota) { nota = sc; melhor = c; }
      });
    });
    return melhor;
  }
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
  function assinatura(hdr) { return hdr.map(function (h) { return norm(h); }).filter(Boolean).join('|'); }
  function dataQualquer(v) {
    var d = toDateD(v); if (d) return d;
    var m = /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?/.exec(t(v)); if (m) return new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0));
    m = /^(\d{1,2})\/(\d{1,2})\/(\d{2,4})(?:\s+(\d{1,2}):(\d{2}))?/.exec(t(v)); if (m) { var y = +m[3]; if (y < 100) y += 2000; return new Date(y, +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0)); }
    return null;
  }
  function lerGenerico(rows, hi, mapa) {
    var by = {};
    for (var i = hi + 1; i < rows.length; i++) {
      var r = rows[i], x = {};
      Object.keys(mapa).forEach(function (col) { var c = mapa[col], v = t(r[+col]); if (c && v) x[c] = x[c] ? x[c] + ' ' + v : v; });
      var os = (x.os || '').replace(/\D/g, ''); if (!os) continue;
      var o = by[os] || { os: os }, d;
      if (x.pedido && (d = dataQualquer(x.pedido))) o.p = d.getTime();
      if (x.termino && (d = dataQualquer(x.termino))) o.te = d.getTime();
      if (x.prev && (d = dataQualquer(x.prev))) o.pv = d.getTime();
      if (x.situacao) o.f = filaFrom(x.situacao) || x.situacao.toLowerCase();
      if (x.tipo) o.ti = x.tipo; if (x.setor) o.se = x.setor; if (x.solicitante) o.so = x.solicitante; if (x.desc) o.d = x.desc;
      if (x.bem) o.b = x.bem; if (x.plaqueta) o.pl = x.plaqueta; if (x.especialidade) o.e = x.especialidade; if (x.localidade) o.lo = x.localidade;
      if (x.obs) o.ob = x.obs; if (x.criticidade) o.cr = x.criticidade;
      if (x.tecnico) { o.tc = o.tc || []; x.tecnico.split(/\s*[;|]\s*/).forEach(function (n) { if (n && o.tc.indexOf(n) < 0) o.tc.push(n); }); }
      by[os] = o;
    }
    return Object.keys(by).map(function (k) { return by[k]; });
  }

  // registro guardado do histórico -> formato que as telas usam
  function histView(h) {
    h.f = h.f || 'sem fila'; h.ti = h.ti || 'Sem tipo'; h.se = h.se || 'Sem setor';
    var pend = h.f === 'aberta' || h.f === 'não atendida' || h.f === 'agendar', terc = h.f === 'aguardando material' || h.f === 'conserto externo';
    var p = h.p ? new Date(h.p) : null, te = h.te ? new Date(h.te) : null, tc = h.tc || [];
    return { os: h.os, pedido: p, termino: te, prevExec: h.pv ? new Date(h.pv) : null, fila: h.f, tipo: h.ti, setor: h.se, solicitante: h.so, desc: h.d, bem: h.b, plaqueta: h.pl,
      tecnicos: tc, tecnico: tc[0] || '', exec: tc.map(function (n) { return { servico: '', func: n, ini: null, fim: null }; }),
      especialidade: h.e || '—', localidade: h.lo || '', obs: h.ob || '', pendente: '', criticidade: h.cr || '', arrumar: [], ok: true, provisorio: false,
      backlog: pend, terceiros: terc, horas: 0, espera: null, total: p && te && te >= p ? (te - p) / 36e5 : null, carregado: h.t || 0, hist: true };
  }

  function merge(list) {
    var map = {};
    list.forEach(function (o) {
      var a = map[o.os];
      if (!a || (RANK[o.fila] || 0) >= (RANK[a.fila] || 0)) map[o.os] = o;
    });
    return Object.keys(map).map(function (k) { return map[k]; });
  }

  var PEND = ['aberta', 'agendar', 'não atendida'];
  var TERC = ['aguardando material', 'conserto externo'];
  var H = 3600000;

  function enrich(list, cfg) {
    var gen = (cfg.genericos || []).map(function (s) { return s.toUpperCase(); });
    var depara = cfg.depara || {};
    list.forEach(function (o) {
      o.issues = [];
      var e = o.exec[0];
      o.tecnicos = o.exec.map(function (x) {
        var n = (x.func || '').toUpperCase();
        if (depara[n]) n = depara[n];
        if (gen.some(function (g) { return g && n.indexOf(g) === 0; })) n = cfg.genericoNome || 'LANÇAMENTOS GENÉRICOS';
        return n || 'SEM FUNCIONÁRIO';
      });
      o.tecnico = o.tecnicos[0] || 'SEM FUNCIONÁRIO';
      o.servico = e ? e.servico : '';
      o.inicio = e && e.ini; o.fim = e && e.fim;
      o.espera = (o.inicio && o.pedido) ? (o.inicio - o.pedido) / H : null;
      o.horas = 0; o.avisos = [];
      var maxH0 = cfg.maxExec || 12;
      o.exec.forEach(function (x) { if (x.ini && x.fim && x.fim >= x.ini) o.horas += Math.min((x.fim - x.ini) / H, (x.fim - x.ini) / H > maxH0 ? 1 : Infinity); });
      o.total = (o.termino && o.pedido) ? (o.termino - o.pedido) / H : null;
      if (!o.pedido) o.issues.push('Sem data do pedido');
      // o MV valida pelo DIA: hora anterior no mesmo dia não é erro (espera fica 0)
      var dia = function (d) { return d ? new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() : null; };
      if (o.espera !== null && o.espera < 0) { if (dia(o.inicio) < dia(o.pedido)) { o.issues.push('Atendimento antes da abertura'); o.espera = null; } else o.espera = 0; }
      if (o.total !== null && o.total < 0) { if (dia(o.termino) < dia(o.pedido)) { o.issues.push('Término antes da abertura'); o.total = null; } else o.total = 0; }
      var maxH = cfg.maxExec || 12, agora = cfg.agora || new Date();
      o.exec.forEach(function (x) {
        if (x.ini && x.fim && x.fim < x.ini) o.issues.push('Fim da execução antes do início');
        if (x.ini && x.fim && (x.fim - x.ini) / H > maxH) o.avisos.push('Execução de ' + Math.round((x.fim - x.ini) / H) + ' h (acima de ' + maxH + ' h): usado 1 h provisória no cálculo');
        if (x.ini && !x.fim && o.fila === 'concluída') { o.avisos.push('Execução sem hora de fim: usado 1 h provisória no cálculo'); o.horas += 1; }
        if ((x.ini && x.ini > agora) || (x.fim && x.fim > agora)) o.issues.push('Execução com data futura');
      });
      if ((o.pedido && o.pedido > agora) || (o.termino && o.termino > agora)) o.issues.push('Data futura no pedido ou término');
      if (o.termino && o.inicio && dia(o.termino) < dia(o.inicio)) o.issues.push('Término antes do início do atendimento');
      if (o.fila === 'concluída' && !o.exec.length) o.issues.push('Concluída sem execução lançada');
      if (o.especialidade === 'Sem especialidade' && o.fila !== 'aberta') o.issues.push('Sem especialidade');
      // provável erro de dia: execução fora do período da OS, mas cabe trocando 1 dia
      if (e && e.ini && o.pedido && o.issues.some(function (x) { return /antes da abertura|antes do início do atendimento/.test(x); })) {
        var lim = o.termino || agora;
        [-1, 1].forEach(function (sh) {
          var ni = new Date(e.ini.getTime() + sh * 864e5), nf = e.fim ? new Date(e.fim.getTime() + sh * 864e5) : null;
          if (!o.sugestao && ni >= o.pedido && ni <= lim && (!nf || nf <= lim)) o.sugestao = ni;
        });
        if (o.sugestao) o.issues.unshift('Provável erro de dia na execução: data sugerida ' + o.sugestao.toLocaleDateString('pt-BR') + ' ' + o.sugestao.toTimeString().slice(0, 5));
      }
      var rg = cfg.regrasObs ? cfg.regrasObs.concat(REGRAS_PADRAO.filter(function (d) { return !cfg.regrasObs.some(function (r) { return r[0] === d[0]; }); })) : null; // regras novas entram mesmo com regras salvas
      var c = classificar(o.obs, rg);
      // fechada/cancelada: sem pendência. Em aguardando material / conserto externo a tratativa já foi feita:
      // a OS está com terceiros, então a pendência é a fila (o que está escrito é histórico)
      o.pendente = (o.fila === 'concluída' || o.fila === 'cancelada') ? '' : o.fila === 'aguardando material' ? 'Material' : o.fila === 'conserto externo' ? 'Externo' : c.resp;
      o.encaminhado = o.pendente ? c.em : null;
      o.parado = o.encaminhado ? Math.max(0, Math.floor((agora - o.encaminhado) / 864e5)) : null;
      o.ok = o.issues.length === 0;
      o.arrumar = o.issues.concat(o.avisos);
      o.provisorio = o.ok && o.avisos.length > 0;
      o.backlog = PEND.indexOf(o.fila) >= 0;
      o.terceiros = TERC.indexOf(o.fila) >= 0;
    });
    return list;
  }

  // Frases padrão do planejamento (22/11/26):
  //   TRATATIVA SUPERVISÃO 22/11/26 · TRATATIVA COMPRADOR 22/11/26 · TRATATIVA PLANEJAMENTO 22/11/26
  //   PROGRAMADO PARA 29/11/26 (FIM DE SEMANA) · EM EXECUÇÃO 22/11/26 · SERVIÇO REALIZADO, AGUARDANDO FECHAMENTO 22/11/26
  // + frases antigas que o planejamento já usava. O que não bate com nenhuma = recado do solicitante (não é tratativa).
  var REGRAS_PADRAO = [
    ['Supervisão', ['TRATATIVA SUPERVISAO', 'TRATATIVA (SUPERVIS', 'TRATATIVA DA SUPERVIS', 'AGUARDAR SUPERVISOR', 'AGUARDANDO SUPERVISOR', '(SUPERVISOR)', '(SUPERVISÃO)']],
    ['Comprador', ['TRATATIVA COMPRADOR', 'TRATATIVA DE COMPRA', '(COMPRADOR)', 'TRATATIVA (COMPRA', 'TRATATIVA DO COMPRADOR', 'AGUARDANDO COMPRADOR']],
    ['Planejador', ['TRATATIVA PLANEJAMENTO', 'PLANEJADOR', 'A AGENDAR', 'MATERIAL ENTREGUE']],
    ['Gestor', ['(GESTOR)', 'TRATATIVA (GESTOR', 'TRATATIVA DO GESTOR', 'AGUARDANDO GESTOR']],
    ['Externo', ['TRATATIVA EXTERNA', 'SERVIÇO EXTERNO', 'SERVICO EXTERNO', 'TRATATIVA DE SERVIÇO EXTERNO']],
    ['Material', ['AGUARDANDO MATERIAL', 'MATERIAL SOLICITADO', 'SOLICITADO MATERIAL', 'PEDIDO FEITO']],
    ['Feito, falta fechar', ['AGUARDANDO FECHAMENTO']],
    ['Em execução', ['EM EXECUCAO']],
    ['Programado', ['PROGRAMADO PARA']]
  ];
  var RX_D = /(\d{1,2})[\/.](\d{1,2})(?:[\/.](\d{2,4}))?(?![\d\/.]*\d)/g;
  function dataTxt(m) { if (m[0].indexOf('.') > 0 && !m[3]) return null; var y = m[3] ? +m[3] : new Date().getFullYear(); if (y < 100) y += 2000; var d = new Date(y, +m[2] - 1, +m[1]); return isNaN(d) || +m[2] > 12 || +m[1] > 31 ? null : d; }
  // normaliza: maiúsculas, sem acento, sem pontuação
  function norm(x) { return (x || '').toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^A-Z0-9/.\s]/g, ' ').replace(/\s+/g, ' ').trim(); }
  function lev(a, b) {
    var m = a.length, n = b.length, d = [], i, j;
    if (!m) return n; if (!n) return m;
    for (j = 0; j <= n; j++) d[j] = j;
    for (i = 1; i <= m; i++) { var prev = d[0]; d[0] = i; for (j = 1; j <= n; j++) { var tmp = d[j]; d[j] = Math.min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1)); prev = tmp; } }
    return d[n];
  }
  // posição da última ocorrência "parecida" (>= 80%) da expressão k no trecho; -1 se não achar
  function achar(sg, k, tol) {
    var kw = norm(k).split(' ').filter(Boolean), w = sg.split(' '), n = kw.length, best = -1, kj = kw.join(' ');
    if (!n) return -1;
    for (var i = 0; i + n <= w.length; i++) {
      var ok = true;
      for (var t = 0; t < n && ok; t++) {
        var a = w[i + t], b = kw[t];
        if (a === b) continue;
        if (b.length <= 3 || a.length <= 3) { ok = false; continue; }
        // aceita palavra cortada/encurtada no fim (ex.: SUPERVIS) e erro de digitação de até 20%
        if (a.indexOf(b) === 0 && b.length >= 5) continue;
        ok = 1 - lev(a, b) / Math.max(a.length, b.length) >= tol;
      }
      if (ok) best = i;
    }
    return best;
  }
  // descobre com quem a OS está parada: divide a observação em trechos e usa o trecho mais recente
  function classificar(obs, regras, tol) {
    tol = tol || 0.8;
    var raw = (obs || '').toUpperCase();
    if (!raw.trim()) return { resp: 'Sem observação', em: null };
    var segs = raw.split(/\s+-\s+|\s*\|\s*|;\s*|\/(?=\s*[A-ZÀ-Ú]{3})/), best = null, bestKey = null, ultEm = null, m;
    segs.forEach(function (sgRaw, idx) {
      var sg = norm(sgRaw), resp = null, pos = -1;
      (regras || REGRAS_PADRAO).forEach(function (r) { r[1].forEach(function (k) { var x = achar(sg, k, tol); if (x >= 0 && x >= pos) { pos = x; resp = r[0]; } }); });
      var em = null; RX_D.lastIndex = 0;
      while ((m = RX_D.exec(sgRaw))) { var d = dataTxt(m); if (d && (!em || d > em)) em = d; }
      var proprio = !!em;
      if (!em) em = ultEm; else ultEm = em;
      if (!resp && proprio && best && (!best.em || em > best.em)) best.em = em;
      if (resp) {
        var key = [em ? +em : 0, proprio ? 1 : 0, idx];
        if (!bestKey || key[0] > bestKey[0] || (key[0] === bestKey[0] && (key[1] > bestKey[1] || (key[1] === bestKey[1] && key[2] > bestKey[2])))) { best = { resp: resp, em: em }; bestKey = key; }
      }
    });
    return best || { resp: 'Outro', em: ultEm };
  }

  function median(a) { if (!a.length) return null; a = a.slice().sort(function (x, y) { return x - y; }); var m = a.length >> 1; return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; }
  function mean(a) { return a.length ? a.reduce(function (s, x) { return s + x; }, 0) / a.length : null; }
  function count(list, key) { var m = {}; list.forEach(function (o) { var k = typeof key === 'function' ? key(o) : o[key]; m[k] = (m[k] || 0) + 1; }); return Object.keys(m).map(function (k) { return [k, m[k]]; }).sort(function (a, b) { return b[1] - a[1]; }); }

  // Backlog numa data de corte: aberto até a data e ainda pendente para a equipe
  function backlogAt(list, cut) {
    var end = new Date(cut.getFullYear(), cut.getMonth(), cut.getDate(), 23, 59, 59);
    return list.filter(function (o) {
      if (!o.pedido || o.pedido > end) return false;
      if (o.backlog) return true;
      if ((o.fila === 'concluída' || o.fila === 'cancelada') && o.termino && o.termino > end) return true;
      return false;
    });
  }
  function terceirosAt(list, cut) {
    var end = new Date(cut.getFullYear(), cut.getMonth(), cut.getDate(), 23, 59, 59);
    return list.filter(function (o) { return o.terceiros && o.pedido && o.pedido <= end; });
  }
  function ageBand(d) { return d <= 7 ? '0–7 dias' : d <= 15 ? '8–15 dias' : d <= 30 ? '16–30 dias' : 'Mais de 30 dias'; }

  // ---- possíveis OS repetidas (mesmo setor, descrição parecida, ainda pendentes) ----
  var STOPW = 'SOLICITO SOLICITAMOS SOLICITA SOLICITACAO FAVOR GENTILEZA PARA COM DOS DAS NOS NAS QUE UMA UNS UMAS ESTA ESTAO ESTAR MESMA MESMO MANUTENCAO REALIZAR VERIFICAR VERIFICACAO NECESSARIO PRECISA PRECISAMOS PELO PELA AOS SEU SUA SEM MAIS MUITO URGENTE URGENCIA ENCONTRA POR BOM DIA TARDE NOITE PFV FMS VMS DEPARTAMENTO VISTO CONCERTO SAINDO OBRIGADO AGRADECO EVIDENCIADO EVIDENCIADA ADEQUACAO ADEQUAR DANIFICADO DANIFICADA DANIFICADOS DANIFICADAS QUEBRADO QUEBRADA QUEBRADOS QUEBRADAS CONSERTO CONSERTAR REPARO REPARAR TROCA TROCAR AJUSTE AJUSTAR ARRUMAR PROBLEMA DEFEITO ESTRAGADO ESTRAGADA SOLTO SOLTA LOCAL SETOR FUNCIONANDO NAO APRESENTANDO APRESENTA'.split(' ');
  function palavras(x) { return norm(x).replace(/[\/.]/g, ' ').split(' ').filter(function (w) { return (w.length >= 3 && STOPW.indexOf(w) < 0) || /^\d+$/.test(w); }).filter(function (w, i, a) { return a.indexOf(w) === i; }); }
  function pareceW(a, b) { if (a === b) return true; if (/^\d+$/.test(a) || /^\d+$/.test(b)) return false; if (a.length > 3 && b.length > 3 && 1 - lev(a, b) / Math.max(a.length, b.length) >= 0.8) return true; return a.length >= 5 && b.length >= 5 && a.slice(0, 5) === b.slice(0, 5); }
  function simDesc(A, B) { if (!A.length || !B.length) return 0; var nA = A.filter(function (w) { return /^\d+$/.test(w); }), nB = B.filter(function (w) { return /^\d+$/.test(w); });
    if (nA.length && nB.length && !nA.some(function (n) { return nB.indexOf(n) >= 0; })) return 0; // leito 3 x leito 5: não é a mesma coisa
    if (lugarDif(A, B)) return 0; // sala de equipamentos x WC funcionários
    // cada palavra pesa pela raridade: palavra que aparece em muitas OS (PINTURA, PORTA…) vale pouco;
    // o que diferencia (SALA DE EQUIPAMENTOS x WC FUNCIONÁRIOS) vale muito
    var P = function (w) { return TIRA.indexOf(w) >= 0 ? 0.3 : (PESO[w.slice(0, 5)] || 1); };
    var k = 0, kt = 0, sm = 0, sa = 0, sb = 0;
    A.forEach(function (a) { sa += P(a); if (B.some(function (b) { return pareceW(a, b); })) { k++; sm += P(a); if (!/^\d+$/.test(a)) kt++; } });
    B.forEach(function (b) { sb += P(b); });
    if (kt < 2) return 0;
    var sim = 2 * sm / (sa + sb);
    return sim; }
  var PESO = {}, TIRA = [];
  // lugares: se as duas OS dizem o lugar e os lugares são diferentes, não é a mesma coisa
  var LUGAR = 'CORREDOR BANHEIRO BANHEIROS SANITARIO WC SALA QUARTO LEITO LEITOS PORTA RECEPCAO COPA POSTO EXPURGO VESTIARIO ESCADA ELEVADOR CONSULTORIO DML ALMOXARIFADO CORREDORES HALL ENTRADA JANELA TETO FORRO PISO PAREDE COZINHA REFEITORIO LAVABO ENFERMARIA BOX ISOLAMENTO'.split(' ');
  function lugarDif(A, B) { var la = A.filter(function (w) { return LUGAR.indexOf(w) >= 0; }), lb = B.filter(function (w) { return LUGAR.indexOf(w) >= 0; });
    return la.length && lb.length && !la.some(function (w) { return lb.indexOf(w) >= 0 || lb.indexOf(w + 'S') >= 0 || lb.indexOf(w.replace(/S$/, '')) >= 0; }); }
  var RX_LINK = /REALIZAD[OA]\s+(?:NA|PELA|PELO|ATRAV[EÉ]S\s+DA)\s+O\.?\s?S\.?\s*N?[º°.]?\s*(\d{5,6})/i;
  Core_sim = function (a, b) { TIRA = palavras((a.setor || '') + ' ' + (a.localidade || '') + ' ' + (b.localidade || '')); return simDesc(a._w, b._w); };
  function repetidas(list) {
    var by = {}, pai = {}, motivo = {};
    list.forEach(function (o) { by[o.os] = o; pai[o.os] = o.os; o.repGrupo = null; o.repDe = null; o._w = palavras(o.desc); });
    var df = {}; list.forEach(function (o) { o._w.map(function (w) { return w.slice(0, 5); }).filter(function (w, i, a) { return a.indexOf(w) === i; }).forEach(function (w) { df[w] = (df[w] || 0) + 1; }); });
    PESO = {}; Object.keys(df).forEach(function (w) { PESO[w] = Math.log((list.length + 1) / df[w]); });
    function raiz(x) { while (pai[x] !== x) x = pai[x] = pai[pai[x]]; return x; }
    function une(a, b, m) { pai[raiz(a)] = raiz(b); motivo[a + '|' + b] = m; }
    var ativa = function (o) { return o.backlog || o.terceiros; };
    // 1) a equipe já escreveu "serviço será realizado na O.S nº X"
    list.forEach(function (o) { var m = ((o.obs || '') + ' ' + (o.desc || '')).match(RX_LINK); if (m && m[1] !== o.os) { o.repDe = m[1]; if (by[m[1]]) une(o.os, m[1], 'Observação: realizado na OS ' + m[1]); } });
    // 2) pendentes no mesmo setor com descrição parecida
    var A = list.filter(ativa);
    for (var i = 0; i < A.length; i++) for (var j = i + 1; j < A.length; j++) {
      var a = A[i], b = A[j]; if (a.setor !== b.setor) continue;
      TIRA = palavras((a.setor || '') + ' ' + (a.localidade || '') + ' ' + (b.localidade || '')); // nome do setor repetido na descrição pesa pouco
      var s = simDesc(a._w, b._w), loc = a.localidade && a.localidade === b.localidade;
      if (s >= 0.6 || (s >= 0.45 && loc)) une(a.os, b.os, 'Descrição parecida');
    }
    var g = {}; list.forEach(function (o) { var r = raiz(o.os); (g[r] = g[r] || []).push(o); });
    // fechadas/canceladas não impactam: só ficam as que ainda estão em aberto
    var grupos = Object.keys(g).map(function (k) { return g[k].filter(ativa); }).filter(function (a) { return a.length > 1; });
    // a que fica é a mais adiantada: terceiros/feito > em execução/programado/compra > supervisão/planejamento > sem tratativa
    var peso = function (o) { var p = o.pendente || ''; return o.terceiros || p === 'Feito, falta fechar' ? 0 : /Em execução|Programado|Comprador|Externo|Material/.test(p) ? 1 : /Supervisão|Planejador|Gestor/.test(p) ? 2 : 3; };
    var onde = function (o) { var p = o.pendente || ''; return o.terceiros ? o.fila : /Sem observação|Outro/.test(p) ? '' : p === 'Planejador' ? 'Planejamento' : p; };
    grupos.forEach(function (a, n) {
      a.sort(function (x, y) { return peso(x) - peso(y) || (x.pedido || 0) - (y.pedido || 0); });
      var p0 = a[0], anda = peso(p0) <= 2, ond = onde(p0);
      a.andamento = anda;
      a.forEach(function (o, i) {
        o.repGrupo = n + 1; o.repPrincipal = p0.os;
        o.repAcao = i === 0 ? (anda ? 'Manter: já em andamento' + (ond ? ' (' + ond + ')' : '') : 'Manter: tratar esta (mais antiga)')
          : anda ? 'Fechar: informar que já está sendo tratada na OS ' + p0.os + (ond ? ' (' + ond + ')' : '') : 'Fechar: juntar na OS ' + p0.os;
      });
      a.mesmoSolic = a.every(function (o) { return o.solicitante && o.solicitante === a[0].solicitante; });
      a.mesmaLoc = a.every(function (o) { return o.localidade && o.localidade === a[0].localidade; });
      a.link = a.some(function (o) { return o.repDe; });
    });
    grupos.sort(function (x, y) { return peso(x[0]) - peso(y[0]) || y.length - x.length; });
    return grupos;
  }

  var Core_sim;
  return { CAMPOS: CAMPOS, chuteCampo: chuteCampo, acharCabecalho: acharCabecalho, assinatura: assinatura, lerGenerico: lerGenerico, isDet: isDet, parseDet: parseDet, histView: histView, sim: function (a, b) { return Core_sim(a, b); }, REGRAS_PADRAO: REGRAS_PADRAO, classificar: classificar, decode: decode, parseCSV: parseCSV, parseMV: parseMV, merge: merge, enrich: enrich, median: median, mean: mean, count: count, backlogAt: backlogAt, terceirosAt: terceirosAt, ageBand: ageBand, repetidas: repetidas, PEND: PEND, TERC: TERC };
})();
if (typeof module !== 'undefined') module.exports = Core;
