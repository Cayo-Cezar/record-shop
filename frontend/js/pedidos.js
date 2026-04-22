/* ═══════════════════════════════════════════════════════════
   PEDIDOS
═══════════════════════════════════════════════════════════ */
async function populatePedidoSelects() {
  const selC = document.getElementById('p-cliente');
  const selD = document.getElementById('p-disco');
  selC.innerHTML = '<option value="">Carregando…</option>';
  selD.innerHTML = '<option value="">Carregando…</option>';

  try {
    const [clientes, discosResp] = await Promise.all([
      _clientes.length ? Promise.resolve(_clientes) : apiFetch('/clientes'),
      _discos.length ? Promise.resolve({ items: _discos }) : apiFetch('/discos?page_size=100'),
    ]);
    _clientes = clientes;
    _discos = discosResp.items || discosResp;

    const ativos = _clientes.filter(c => c.ativo);
    selC.innerHTML = '<option value="">Selecione um cliente…</option>' +
      ativos.map(c => `<option value="${c.id}">${esc(c.nome_completo)} — ${esc(c.email)}</option>`).join('');

    const comEstoque = _discos.filter(d => d.quantidade > 0 && (d.nome !== 'We Are Reactive' || _isLaunchLive));
    selD.innerHTML = '<option value="">Selecione um disco…</option>' +
      comEstoque.map(d =>
        `<option value="${d.id}" data-qtd="${d.quantidade}">
          ${esc(d.artista || '')} — ${esc(d.nome || 'Sem título')} (${d.quantidade} un.)
        </option>`
      ).join('');

    selD.onchange = atualizarPreview;
    document.getElementById('p-qtd').oninput = atualizarPreview;

    loadPedidos();
  } catch (err) {
    selC.innerHTML = '<option value="">Erro ao carregar</option>';
    toast('Erro ao carregar dados: ' + err.message, 'error');
  }
}

function atualizarPreview() {
  const selD = document.getElementById('p-disco');
  const qtd = parseInt(document.getElementById('p-qtd').value) || 1;
  const prev = document.getElementById('p-preview');
  const opt = selD.selectedOptions[0];
  if (!opt || !opt.value) { prev.style.display = 'none'; return; }
  const max = parseInt(opt.dataset.qtd) || 0;
  const txt = document.getElementById('p-preview-text');
  txt.innerHTML = `<strong>${qtd}x</strong> "${esc(opt.text.trim())}"
    ${qtd > max ? `<span style="color:var(--danger)"> — ⚠ excede estoque (${max})</span>` : ''}`;
  prev.style.display = 'block';
}

async function criarPedido() {
  const clienteId = document.getElementById('p-cliente').value;
  const discoId = document.getElementById('p-disco').value;
  const qtd = parseInt(document.getElementById('p-qtd').value);
  const btn = document.getElementById('btn-pedido');

  if (!clienteId) { toast('Selecione um cliente.', 'error'); return; }
  if (!discoId) { toast('Selecione um disco.', 'error'); return; }
  if (!qtd || qtd < 1) { toast('Quantidade inválida.', 'error'); return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spin-sm" style="display:inline-block;width:14px;height:14px;border:2px solid rgba(0,0,0,.3);border-top-color:#111;border-radius:50%;animation:spin-fast .6s linear infinite;margin-right:8px"></span>Enfileirando…';

  try {
    const pedido = await apiFetch('/pedidos', {
      method: 'POST',
      body: JSON.stringify({
        cliente_id: +clienteId,
        itens: [{ disco_id: +discoId, quantidade: qtd }]
      }),
    });

    toast(`Pedido #${pedido.pedido_id} enfileirado! Processando… 🎵`, 'success');

    // Show polling indicator
    document.getElementById('p-enqueued').style.display = 'flex';
    document.getElementById('q-id').value = pedido.pedido_id;

    // Reset form
    ['p-cliente', 'p-disco'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('p-qtd').value = '1';
    document.getElementById('p-preview').style.display = 'none';

    // Start polling for completion
    pollPedidoStatus(pedido.pedido_id);
    _discos = [];

    loadPedidos();
  } catch (err) {
    toast('Erro ao criar pedido: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-bag-check-fill"></i> Confirmar pedido';
  }
}

async function pollPedidoStatus(id, attempts = 0) {
  if (attempts > 20) {
    document.getElementById('p-enqueued').style.display = 'none';
    return;
  }
  await new Promise(r => setTimeout(r, 1500));
  try {
    const p = await apiFetch(`/pedidos/${id}`);
    if (p.status === 'COMPLETED') {
      document.getElementById('p-enqueued').style.display = 'none';
      toast(`✅ Pedido #${id} CONCLUÍDO com sucesso!`, 'success');
      consultarPedidoById(id);
      loadPedidos();
    } else if (p.status === 'FAILED') {
      document.getElementById('p-enqueued').style.display = 'none';
      toast(`❌ Pedido #${id} falhou: ${p.motivo_falha || 'Estoque insuficiente'}`, 'error');
      consultarPedidoById(id);
      loadPedidos();
    } else {
      pollPedidoStatus(id, attempts + 1);
    }
  } catch (_) { }
}

async function consultarPedido() {
  const id = document.getElementById('q-id').value.trim();
  if (!id) { toast('Informe o ID do pedido.', 'error'); return; }
  consultarPedidoById(+id);
}

async function consultarPedidoById(id) {
  const box = document.getElementById('pedido-result');
  try {
    const p = await apiFetch(`/pedidos/${id}`);
    const icons = {
      COMPLETED: 'bi-check-circle-fill', FAILED: 'bi-x-circle-fill',
      PENDING: 'bi-hourglass-split', PROCESSING: 'bi-gear'
    };
    const itens = p.itens.map(i => `${i.quantidade}× Disco #${i.disco_id}`).join(', ');
    box.innerHTML = `
      <div class="status-card ${p.status}" style="margin-top:1rem">
        <span class="status-badge ${p.status}">
          <i class="bi ${icons[p.status] || 'bi-question'}"></i> ${p.status}
        </span>
        <div class="status-row"><span class="key">Pedido</span><span class="val">#${p.id}</span></div>
        <div class="status-row"><span class="key">Cliente</span><span class="val">#${p.cliente_id}</span></div>
        <div class="status-row"><span class="key">Itens</span><span class="val">${esc(itens)}</span></div>
        <div class="status-row"><span class="key">Data</span><span class="val">${new Date(p.criado_em).toLocaleString('pt-BR')}</span></div>
        ${p.motivo_falha ? `<div class="status-row"><span class="key">Motivo</span><span class="val" style="color:var(--danger)">${esc(p.motivo_falha)}</span></div>` : ''}
      </div>`;
  } catch (err) {
    box.innerHTML = `<p style="color:var(--danger);font-size:.82rem;margin-top:.75rem">
      <i class="bi bi-exclamation-triangle"></i> ${esc(err.message)}</p>`;
  }
}

async function loadPedidos() {
  const box = document.getElementById('pedidos-list');
  try {
    const data = await apiFetch('/pedidos?page_size=10');
    const pedidos = data.items || [];
    if (!pedidos.length) {
      box.innerHTML = `<div style="font-size:.82rem;color:var(--muted);padding:.5rem 0">Nenhum pedido ainda.</div>`;
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
        <button class="btn btn-ghost btn-sm" onclick="consultarPedidoById(${p.id});document.getElementById('q-id').value=${p.id}">
          <i class="bi bi-eye"></i>
        </button>
      </div>
    `).join('');
  } catch (_) { }
}