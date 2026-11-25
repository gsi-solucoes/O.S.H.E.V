// Raio X do Relatório: funciona sem internet depois da primeira abertura
const V = 'raiox-v1';
const ARQS = ['./', 'index.html', 'manifest.webmanifest', 'vendor/jszip.min.js', 'vendor/exceljs.min.js', 'icons/icon-192.png', 'icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(ARQS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url);
  // a página: tenta a versão nova na internet; sem internet, usa a guardada
  if (r.mode === 'navigate' || (u.origin === location.origin && /\/(index\.html)?$/.test(u.pathname))) {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(V).then(c => c.put('index.html', cp)); return res; }).catch(() => caches.match('index.html')));
    return;
  }
  // o resto (bibliotecas, ícones, fontes): guardado primeiro, internet se não tiver
  e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { if (res.ok && (u.origin === location.origin || /fonts\.(googleapis|gstatic)\.com/.test(u.host))) { const cp = res.clone(); caches.open(V).then(c => c.put(r, cp)); } return res; })));
});
