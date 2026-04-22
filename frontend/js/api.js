/* ═══════════════════════════════════════════════════════════
   API HELPER
═══════════════════════════════════════════════════════════ */
async function apiFetch(path, opts = {}) {
  const url = path.startsWith('http') ? path : API + path;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    let msg = `Erro ${res.status}`;
    try { const e = await res.json(); msg = e.detail || e.message || msg; } catch (_) { }
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}