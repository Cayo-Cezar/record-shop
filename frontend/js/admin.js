/* ═══════════════════════════════════════════════════════════
   ADMIN
═══════════════════════════════════════════════════════════ */

async function seedData() {
  try {
    const resp = await apiFetch('/seed', { method: 'POST' });
    toast('Dados populados com sucesso!', 'success');
    if (typeof resetLaunchState === 'function') resetLaunchState();
    // Reload data
    await Promise.all([
      loadDiscos(),
      loadClientes(),
      loadAdminPedidos()
    ]);
  } catch (err) {
    toast('Erro ao popular dados: ' + err.message, 'error');
  }
}

async function restaurarEstoque() {
  if(!confirm("Tem certeza que deseja apagar todos os pedidos e restaurar os estoques originais?")) return;
  try {
    const resp = await apiFetch('/pedidos/reset', { method: 'POST' });
    toast('Pedidos apagados e estoque restaurado com sucesso!', 'success');
    if (typeof resetLaunchState === 'function') resetLaunchState();
    // Reload data
    await Promise.all([
      loadDiscos(),
      loadAdminPedidos()
    ]);
  } catch (err) {
    toast('Erro ao restaurar estoque: ' + err.message, 'error');
  }
}

async function loadAdminPedidos() {
  const box = document.getElementById('admin-pedidos-list');
  try {
    const data = await apiFetch('/pedidos?page_size=50');
    const pedidos = data.items || [];
    if (!pedidos.length) {
      box.innerHTML = `<div style="font-size:.82rem;color:var(--muted);padding:.5rem 0">Nenhum pedido.</div>`;
      return;
    }
    const icons = { COMPLETED: '✅', FAILED: '❌', PENDING: '⏳', PROCESSING: '⚙️' };
    box.innerHTML = pedidos.map(p => `
      <div class="pedido-row ${p.status}">
        <div class="pedido-id">
          <strong>#${p.id}</strong>
        </div>
        <div class="pedido-info">
          <div style="font-size:.82rem">
            ${icons[p.status] || '•'} <strong>${p.status}</strong>
            · Cliente #${p.cliente_id}
            · ${p.itens.length} item(ns)
          </div>
          <div class="pedido-date">${new Date(p.criado_em).toLocaleString('pt-BR')}</div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="consultarPedidoById(${p.id});document.getElementById('q-id').value=${p.id};switchTab('pedidos')">
          <i class="bi bi-eye"></i>
        </button>
      </div>
    `).join('');
  } catch (err) {
    box.innerHTML = `<div style="font-size:.82rem;color:var(--danger);padding:.5rem 0">Erro ao carregar pedidos.</div>`;
  }
}



// Load admin data when tab is switched
document.addEventListener('tabSwitched', (e) => {
  if (e.detail === 'admin') {
    loadAdminPedidos();
    loadClientes();
  }
});