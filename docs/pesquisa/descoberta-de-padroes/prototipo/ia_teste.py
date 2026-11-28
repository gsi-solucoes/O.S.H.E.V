"""Teste: o script é o cérebro (junta as pistas), a IA pequena é o neurônio (decide e pede o que faltar).
Pergunta testada: "qual data é esta?", nos 20 casos do gabarito_datas.json.
A IA NÃO recebe a conclusão das regras; só o dossiê e as ferramentas para pedir mais."""
import sys, os, json, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import formula as F
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA, MODELO = sys.argv[1], sys.argv[2]
torch.set_num_threads(4)
tok = AutoTokenizer.from_pretrained(MODELO)
mod = AutoModelForCausalLM.from_pretrained(MODELO, torch_dtype=torch.bfloat16)
mod.eval()

OPCOES = ['Abertura / pedido', 'Compra / nota', 'Início do serviço', 'Fim do serviço / executado', 'Encerramento / baixa',
          'Previsão / programada', 'Competência / período', 'Nascimento', 'Outra', '?']
SISTEMA = ("Você decide o significado de uma coluna de datas de um relatório. Um programa leu o relatório e te mostra um grupo de "
           "células que são datas. Diga QUAL data é, escolhendo exatamente uma destas opções: " + '; '.join(OPCOES) + ". "
           "Use 'Outra' se for uma data com outro significado e '?' se não der para saber. "
           "Se precisar, peça informação ao programa usando as ferramentas (no máximo 4 pedidos). "
           "No fim, responda SOMENTE com JSON: {\"qual_data\": \"<opção>\", \"confianca\": \"alta|média|baixa\", \"porque\": \"<curto>\"}.")
FERRAMENTAS = [
    {'type': 'function', 'function': {'name': 'exemplos', 'description': 'Mostra mais exemplos de valores do grupo.', 'parameters': {'type': 'object', 'properties': {'grupo': {'type': 'string'}}, 'required': ['grupo']}}},
    {'type': 'function', 'function': {'name': 'vizinhos', 'description': 'Mostra os rótulos/textos que ficam perto deste grupo no relatório (mesma linha ou cabeçalho).', 'parameters': {'type': 'object', 'properties': {'grupo': {'type': 'string'}}, 'required': ['grupo']}}},
    {'type': 'function', 'function': {'name': 'ordem_no_tempo', 'description': 'Compara este grupo de datas com os outros grupos de datas do mesmo registro: quem vem antes e a diferença típica.', 'parameters': {'type': 'object', 'properties': {'grupo': {'type': 'string'}}, 'required': ['grupo']}}},
    {'type': 'function', 'function': {'name': 'arredores', 'description': 'Mostra o que tem antes e depois na mesma linha, e a linha de cima e de baixo, para alguns exemplos do grupo, como está no arquivo.', 'parameters': {'type': 'object', 'properties': {'grupo': {'type': 'string'}}, 'required': ['grupo']}}},
    {'type': 'function', 'function': {'name': 'trecho', 'description': 'Mostra um trecho cru do arquivo (5 linhas) em volta de um exemplo do grupo.', 'parameters': {'type': 'object', 'properties': {'grupo': {'type': 'string'}}, 'required': ['grupo']}}},
    {'type': 'function', 'function': {'name': 'numeros', 'description': 'Quanto o grupo está preenchido, quantos valores diferentes e quantas vezes aparece por registro.', 'parameters': {'type': 'object', 'properties': {'grupo': {'type': 'string'}}, 'required': ['grupo']}}},
]

def ferramenta(r, nome, grupo):
    g = next((x for x in r['grupos'] if x['nome'] == grupo), None)
    if not g: return 'grupo não encontrado; grupos de data existentes: ' + ', '.join(x['nome'] for x in r['grupos'] if x.get('tipo_maioria') == 'data')
    if nome == 'exemplos': return ', '.join(list(dict.fromkeys(c[3] for c in g['cel']))[:10])
    if nome == 'vizinhos':
        v = [x.rstrip(':') for x, _ in (g.get('viz_todos') or {}).items() if x.rstrip(':') != grupo]
        return ('rótulos por perto: ' + ', '.join(v)) if v else 'nenhum rótulo por perto (o relatório não tem cabeçalho nessa parte)'
    if nome == 'ordem_no_tempo':
        ls = ['"%s" vem antes de "%s" (diferença típica %s)' % (n['antes'], n['depois'], n['tipico']) for n in r['datas'] if grupo in (n['antes'], n['depois'])]
        outras = [x['nome'] for x in r['grupos'] if x.get('tipo_maioria') == 'data' and x['nome'] != grupo]
        return ('; '.join(ls) if ls else 'sem comparação de tempo disponível') + ' | outros grupos de data: ' + (', '.join(outras) or 'nenhum')
    if nome in ('arredores', 'trecho'):
        L = r['_linhas']; cels = [c for c in g['cel'] if c[1]][:: max(1, len(g['cel']) // 3)][:3]
        if not cels: return 'sem posição no arquivo (valor de contexto)'
        if nome == 'trecho':
            li = cels[0][1]; return '\n'.join(' | '.join(x for x in L[i] if x) for i in range(max(0, li - 3), min(len(L), li + 2)))
        out = []
        for _, li, co, v in cels:
            lin = L[li - 1]; ant = [x for x in lin[:co - 1] if x][-2:]; dep = [x for x in lin[co:] if x][:2]
            cima = ' | '.join(x for x in L[li - 2] if x) if li >= 2 else ''; baixo = ' | '.join(x for x in L[li] if x) if li < len(L) else ''
            out.append('em cima: [%s] / antes: [%s] VALOR: %s depois: [%s] / embaixo: [%s]' % (cima[:120], ' | '.join(ant), v, ' | '.join(dep), baixo[:120]))
        return '\n'.join(out)
    if nome == 'numeros':
        return 'preenchido em %d%% dos registros; %d valores diferentes; até %d por registro' % (g['preenchido'] * 100, len(set(c[3] for c in g['cel'])), g['lista'])
    return 'ferramenta desconhecida'

def gerar(msgs):
    txt = tok.apply_chat_template(msgs, tools=FERRAMENTAS, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    ids = tok(txt, return_tensors='pt')
    with torch.no_grad():
        out = mod.generate(**ids, max_new_tokens=400, do_sample=False)
    return tok.decode(out[0][ids['input_ids'].shape[1]:], skip_special_tokens=True).strip()

def conferir_tempo(r, grupo, sig):
    antes = [n['antes'] for n in r['datas'] if n['depois'] == grupo]
    depois = [n['depois'] for n in r['datas'] if n['antes'] == grupo]
    if sig == 'Abertura / pedido' and antes: return '"%s" tem data ANTES dele (%s), então não pode ser a abertura.' % (grupo, ', '.join(antes))
    if sig == 'Encerramento / baixa' and depois: return '"%s" tem data DEPOIS dele (%s), então não pode ser o encerramento.' % (grupo, ', '.join(depois))
    return None

def decidir(r, grupo):
    g = next(x for x in r['grupos'] if x['nome'] == grupo)
    sem_nome = '(sem nome)' in grupo
    dossie = ('Relatório: %s (%d registros).\nGrupo: "%s"%s.\nExemplos: %s.\nOutros grupos de data no relatório: %s.' %
              (r['arquivo'], r['registros'], grupo, ' — este grupo NÃO tem rótulo no relatório' if sem_nome else ' — este é o rótulo escrito no relatório',
               ', '.join(list(dict.fromkeys(c[3] for c in g['cel']))[:4]),
               ', '.join(x['nome'] for x in r['grupos'] if x.get('tipo_maioria') == 'data' and x['nome'] != grupo) or 'nenhum'))
    msgs = [{'role': 'system', 'content': SISTEMA}, {'role': 'user', 'content': dossie}]
    pedidos = []; voltas = 0
    for _ in range(8):
        resp = gerar(msgs)
        chamadas = re.findall(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', resp, re.S)
        if not chamadas:                                   # pedido "solto", sem etiqueta
            try:
                jj = json.loads(re.search(r'\{.*\}', resp, re.S).group(0))
                if 'name' in jj and 'arguments' in jj: chamadas = [json.dumps(jj)]
            except Exception: pass
        if chamadas and len(pedidos) < 4:
            msgs.append({'role': 'assistant', 'content': resp})
            for c in chamadas[:2]:
                try: cj = json.loads(c); nome, arg = cj['name'], cj.get('arguments', {}).get('grupo', grupo)
                except Exception: nome, arg = '?', grupo
                res = ferramenta(r, nome, arg); pedidos.append('%s(%s)' % (nome, arg))
                msgs.append({'role': 'tool', 'content': res})
            continue
        m = re.search(r'\{.*\}', resp, re.S)
        try: j = json.loads(m.group(0)) if m else {}
        except Exception: j = {}
        sig = j.get('qual_data', '?')
        if sig not in OPCOES and voltas < 2:
            voltas += 1; msgs += [{'role': 'assistant', 'content': resp}, {'role': 'user', 'content': 'Resposta inválida: "%s" não é uma das opções. Escolha EXATAMENTE uma: %s. Responda só o JSON.' % (sig, '; '.join(OPCOES))}]; continue
        prob = conferir_tempo(r, grupo, sig)
        if prob and voltas < 2:
            voltas += 1; pedidos.append('REJEITADA:' + sig); msgs += [{'role': 'assistant', 'content': resp}, {'role': 'user', 'content': 'O programa conferiu e rejeitou: ' + prob + ' Pense de novo e responda só o JSON.'}]; continue
        return sig, j.get('confianca', '?'), j.get('porque', resp[:120]), pedidos
    return '?', 'baixa', 'passou do limite de pedidos', pedidos

gab = json.load(open(os.path.join(AQUI, 'gabarito_datas.json'), encoding='utf-8'))
ia_ok = re_ok = tot = 0
t0 = time.time()
for arq, esp in gab.items():
    cam = os.path.join(PASTA, arq)
    if not os.path.exists(cam): cam = os.path.join(PASTA, '..', 'cegas', 'arq', arq)
    L = F.ler(cam)[0]; r = F.montar(L, cam); r['_linhas'] = L
    print('==', arq, flush=True)
    for grupo, certo in esp.items():
        t = time.time()
        sig, conf, porque, pedidos = decidir(r, grupo)
        regra = next((x['qual_data']['sig'] for x in r['grupos'] if x['nome'] == grupo and 'qual_data' in x), '?')
        tot += 1; ia_ok += sig == certo; re_ok += regra == certo
        print('  %-20s certo: %-27s | IA: %s %-27s [%s] | regras: %s | pediu: %s | %.0fs\n      porquê (IA): %s' % (
            grupo, certo, '✅' if sig == certo else '❌', sig, conf, '✅' if regra == certo else '❌', ', '.join(pedidos) or 'nada', time.time() - t, porque[:150]), flush=True)
print('\nIA: %d de %d | regras: %d de %d | tempo total %.0f min' % (ia_ok, tot, re_ok, tot, (time.time() - t0) / 60), flush=True)
