/* ═══════════════════════════════════════════════════════════
   NAVIGATION
═══════════════════════════════════════════════════════════ */
function switchTab(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === name);
  });
  document.getElementById(`tab-${name}`).classList.add('active');
  if (name === 'pedidos') populatePedidoSelects();
  if (name === 'clientes') loadClientes();
  if (name === 'admin') {
    loadAdminPedidos();
    loadClientes();
  }
  // Dispatch for any other listeners
  document.dispatchEvent(new CustomEvent('tabSwitched', { detail: name }));
}