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
      loadAdminPedidos(),
      loadAdminClientes()
    ]);
  } catch (err) {
    toast('Erro ao popular dados: ' + err.message, 'error');
  }
}

async function restaurarEstoque() {
  if (!confirm("Tem certeza que deseja apagar todos os pedidos e restaurar os estoques originais?")) return;
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
    loadAdminDiscos();
  }
});

async function loadAdminDiscos() {
  const box = document.getElementById('admin-discos-list');
  box.innerHTML = '<div class="spinner-ring"></div>';
  try {
    const data = await apiFetch('/discos?page_size=100');
    const discos = data.items || [];
    if (!discos.length) {
      box.innerHTML = `<div style="font-size:.82rem;color:var(--muted);padding:.5rem 0">Nenhum disco cadastrado.</div>`;
      return;
    }
    box.innerHTML = discos.map(d => `
      <div class="pedido-row" style="padding:.6rem 1rem">
        <div style="flex:1;min-width:0">
          <div style="font-size:.82rem;font-weight:600;color:${d.ativo ? 'var(--cream)' : 'var(--muted)'};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
            ${esc(d.nome)}
          </div>
          <div style="font-size:.72rem;color:var(--muted)">
            ${esc(d.artista)} · ${d.ano_lancamento} · ${esc(d.estilo)}
          </div>
          <div style="font-size:.72rem;margin-top:2px;color:${d.ativo && d.quantidade > 0 ? 'var(--success)' : 'var(--danger)'}">
            ${d.ativo ? `${d.quantidade} un.` : '<em>Inativo</em>'}
          </div>
        </div>
        ${d.ativo
          ? `<button class="btn-danger-ghost" onclick="deletarDisco(${d.id}, '${esc(d.nome).replace(/'/g, "\\'")}')"><i class="bi bi-trash"></i></button>`
          : `<button class="btn btn-ghost btn-sm" style="color:var(--success);border-color:rgba(76,175,130,.4)" onclick="reativarDisco(${d.id}, '${esc(d.nome).replace(/'/g, "\\'")}')" title="Reativar"><i class="bi bi-arrow-counterclockwise"></i></button>`
        }
      </div>
    `).join('');
  } catch (err) {
    box.innerHTML = `<div style="font-size:.82rem;color:var(--danger);padding:.5rem 0">Erro ao carregar discos.</div>`;
  }
}

async function deletarDisco(id, nome) {
  if (!confirm(`Deseja inativar o disco "${nome}"?\n\nEle não aparecerá mais no catálogo (soft delete).`)) return;
  try {
    await apiFetch(`/discos/${id}`, { method: 'DELETE' });
    toast(`Disco "${nome}" inativado com sucesso.`, 'success');
    loadAdminDiscos();
    loadDiscos();
  } catch (err) {
    toast('Erro ao inativar disco: ' + err.message, 'error');
  }
}

async function reativarDisco(id, nome) {
  if (!confirm(`Deseja reativar o disco "${nome}"?\n\nEle voltará a aparecer no catálogo.`)) return;
  try {
    await apiFetch(`/discos/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ ativo: true }),
    });
    toast(`Disco "${nome}" reativado com sucesso!`, 'success');
    loadAdminDiscos();
    loadDiscos();
  } catch (err) {
    toast('Erro ao reativar disco: ' + err.message, 'error');
  }
}