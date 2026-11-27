"""Regressão do Revisor da E2: contas lineares nos achados e sem estouro de pilha (A-1, M-1, B-1)."""
import json, subprocess, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def node(js):
    r = subprocess.run(["node", "-e", js], cwd=RAIZ, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    return r.stdout.strip()


PRE = """const C=require('./src/core.js');
const base=(regs,campos)=>({regs,campos,cd:'D',sit:'S',aberto:r=>r.v.S==='Aberto',hoje:'2026-11-28',hojeMs:new Date(2026,10,28).getTime(),par:null,pares:0});
const campos=[{n:'Cod',t:'codigo'},{n:'D',t:'data'},{n:'S',t:'situacao'},{n:'G',t:'categoria'},{n:'V',t:'numero'}];
"""


def test_achados_72mil_registros_5000_grupos_em_menos_de_2s():
    js = PRE + """const regs=[];for(let i=0;i<72000;i++){const m=i%2?'09':'10';regs.push({codigo:'C'+i,v:{D:'2026-'+m+'-'+String(1+i%27).padStart(2,'0'),S:i%3?'Aberto':'Concluido',G:'g'+(i%5000),V:String(i%100+1)}});}
const t=Date.now();const r=C.achadosDe(base(regs,campos));console.log(Date.now()-t,r.length);"""
    ms = int(node(js).split()[0])
    assert ms < 2000, ms


def test_estat_e_achados_com_100mil_valores_sem_rangeerror():
    js = PRE + """const v=[];for(let i=0;i<100000;i++)v.push(i+1);const e=C.estat(v);
const regs=[];for(let i=0;i<100000;i++)regs.push({codigo:'C'+i,v:{D:'2026-10-0'+(1+i%9),S:'Aberto',G:'a',V:String(i+1)}});
C.achadosDe(base(regs,campos));console.log(JSON.stringify([e.min,e.max]));"""
    assert json.loads(node(js)) == [1, 100000]


def test_valor_proto_conta_normalmente():
    js = PRE + """const regs=[];for(let i=0;i<40;i++)regs.push({codigo:'C'+i,v:{D:'2026-09-0'+(1+i%9),S:'Aberto',G:i<30?'__proto__':'x',V:'1'}});
for(let i=0;i<40;i++)regs.push({codigo:'D'+i,v:{D:'2026-10-0'+(1+i%9),S:'Aberto',G:i<5?'__proto__':'x',V:'1'}});
const r=C.achadosDe(base(regs,campos));console.log(JSON.stringify(r.filter(a=>a.regra==='A6').map(a=>a.frase)));"""
    f = json.loads(node(js))
    assert any(x.startswith("__proto__ foi de 75,0%") for x in f), f
