/* ═══════════════════════════════════════════════════════════
   CLIENTES
═══════════════════════════════════════════════════════════ */
async function loadClientes() {
  const box = document.getElementById('clientes-list');
  box.innerHTML = '<div class="spinner-ring"></div>';
  try {
    _clientes = await apiFetch('/clientes');
    renderClientesList(_clientes);
  } catch (err) {
    box.innerHTML = `<div class="empty-state" style="padding:2rem 0">
      <i class="bi bi-people"></i><p>Erro ao carregar clientes</p></div>`;
  }
}

function renderClientesList(clientes) {
  const box = document.getElementById('clientes-list');
  if (!clientes.length) {
    box.innerHTML = `<div class="empty-state" style="padding:2rem 0">
      <i class="bi bi-person-plus"></i><p style="font-size:.85rem">Nenhum cliente cadastrado ainda.</p></div>`;
    return;
  }
  box.innerHTML = `<div class="table-wrap"><table class="data-table">
    <thead><tr>
      <th>#</th><th>Nome</th><th>E-mail</th><th>Status</th><th></th>
    </tr></thead>
    <tbody>
    ${clientes.map(c => `
    <tr>
      <td style="color:var(--muted);font-family:var(--mono)">${c.id}</td>
      <td><strong>${esc(c.nome_completo)}</strong></td>
      <td style="color:var(--muted-hi)">${esc(c.email)}</td>
      <td>${c.ativo
      ? '<span class="badge-active"><i class="bi bi-check2"></i> Ativo</span>'
      : '<span class="badge-inactive"><i class="bi bi-dash"></i> Inativo</span>'}</td>
      <td>${c.ativo 
        ? `<button class="btn-danger-ghost" onclick="inativarCliente(${c.id})">Inativar</button>` 
        : `<button class="btn-ghost" onclick="reativarCliente(${c.id})">Reativar</button>`}</td>
    </tr>`).join('')}
    </tbody>
  </table></div>`;
}

async function criarCliente() {
  const nome = document.getElementById('c-nome').value.trim();
  const doc = document.getElementById('c-doc').value.replace(/\D/g, '');
  const nasc = document.getElementById('c-nasc').value;
  const email = document.getElementById('c-email').value.trim();
  const tel = document.getElementById('c-tel').value.trim();
  const btn = document.getElementById('btn-cliente');

  if (!nome) { toast('Informe o nome completo.', 'error'); return; }
  if (!doc || doc.length < 11) { toast('CPF inválido (mínimo 11 dígitos).', 'error'); return; }
  if (!nasc) { toast('Informe a data de nascimento.', 'error'); return; }
  if (!email || !email.includes('@')) { toast('E-mail inválido.', 'error'); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spin-sm" style="display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin-fast .6s linear infinite;"></span> Cadastrando…';

  try {
    const body = { nome_completo: nome, documento: doc, data_nascimento: nasc, email };
    if (tel) body.telefone = tel;
    const c = await apiFetch('/clientes', { method: 'POST', body: JSON.stringify(body) });
    toast(`Cliente "${c.nome_completo}" cadastrado com sucesso! ✓`, 'success');
    ['c-nome', 'c-doc', 'c-nasc', 'c-email', 'c-tel'].forEach(id => document.getElementById(id).value = '');
    _clientes = [];
    loadClientes();
  } catch (err) {
    toast('Erro: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-person-plus-fill"></i> Cadastrar cliente';
  }
}

async function inativarCliente(id) {
  if (!confirm('Deseja inativar este cliente? Ele não poderá mais fazer pedidos.')) return;
  try {
    await apiFetch(`/clientes/${id}/inativar`, { method: 'PATCH' });
    toast('Cliente inativado.', 'success');
    _clientes = [];
    loadClientes();
  } catch (err) {
    toast('Erro: ' + err.message, 'error');
  }
}

async function reativarCliente(id) {
  try {
    await apiFetch(`/clientes/${id}/reativar`, { method: 'PATCH' });
    toast('Cliente reativado.', 'success');
    _clientes = [];
    loadClientes();
  } catch (err) {
    toast('Erro: ' + err.message, 'error');
  }
}