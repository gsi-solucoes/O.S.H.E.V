// Raio X do Relatório: funciona sem internet depois da primeira abertura
const V = 'raiox-v3';
const ARQS = ['./', 'index.html', 'manifest.webmanifest', 'vendor/jszip.min.js', 'vendor/exceljs.min.js', 'icons/icon-192.png', 'icons/icon-512.png', 'excel/RaioX_Relatorio.bas'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(ARQS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('raiox-') && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url); if (u.origin !== location.origin) return; // nada fora da própria origem
  // a página e a macro: tenta a versão nova na internet; sem internet, usa a guardada
  if (r.mode === 'navigate' || /\/(index\.html|RaioX_Relatorio\.bas)?$/.test(u.pathname)) {
    const chave = /\.bas$/.test(u.pathname) ? r : 'index.html';
    e.respondWith(fetch(r).then(res => { if (res.ok) { const cp = res.clone(); caches.open(V).then(c => c.put(chave, cp)); } return res; }).catch(() => caches.match(chave, { ignoreSearch: true })));
    return;
  }
  // o resto (bibliotecas, ícones): guardado primeiro, internet se não tiver
  e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { if (res.ok) { const cp = res.clone(); caches.open(V).then(c => c.put(r, cp)); } return res; })));
});
