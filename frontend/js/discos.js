/* ═══════════════════════════════════════════════════════════
   DISCOS
═══════════════════════════════════════════════════════════ */
async function loadDiscos() {
  const box = document.getElementById('disco-container');
  box.innerHTML = '<div class="spinner-ring"></div>';
  try {
    const data = await apiFetch('/discos?page_size=100');
    _discos = data.items || [];
    buildFilters(_discos);
    updateStats(_discos);
    renderDiscos(_discos);
    document.getElementById('disco-stats').style.display = 'grid';
  } catch (err) {
    box.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-wifi-off"></i>
        <p>Não foi possível carregar os discos.<br>
        <small>Verifique se a API está em <code>${API}</code></small></p>
        <button class="btn btn-ghost btn-sm" onclick="loadDiscos()" style="margin-top:1rem">
          <i class="bi bi-arrow-clockwise"></i> Tentar novamente
        </button>
      </div>`;
    toast('Erro ao carregar catálogo: ' + err.message, 'error');
  }
}

function buildFilters(discos) {
  const sel = document.getElementById('f-estilo');
  const estilos = [...new Set(discos.map(d => d.estilo).filter(Boolean))].sort();
  sel.innerHTML = '<option value="">Todos os estilos</option>' +
    estilos.map(e => `<option value="${esc(e)}">${esc(e)}</option>`).join('');
}

function updateStats(discos) {
  document.getElementById('stat-total').textContent = discos.length;
  document.getElementById('stat-instock').textContent = discos.filter(d => d.quantidade > 0).length;
  const styles = new Set(discos.map(d => d.estilo).filter(Boolean));
  document.getElementById('stat-styles').textContent = styles.size;
}

function applyFilters() {
  const q = document.getElementById('f-search').value.toLowerCase();
  const est = document.getElementById('f-estilo').value.toLowerCase();
  const ano = document.getElementById('f-ano').value;
  const stock = document.getElementById('f-stock').value;

  const filtered = _discos.filter(d => {
    if (q && !`${d.nome} ${d.artista}`.toLowerCase().includes(q)) return false;
    if (est && (d.estilo || '').toLowerCase() !== est) return false;
    if (ano && String(d.ano_lancamento) !== ano) return false;
    if (stock === 'in' && d.quantidade <= 0) return false;
    if (stock === 'out' && d.quantidade > 0) return false;
    return true;
  });
  renderDiscos(filtered);
}

function renderDiscos(discos) {
  const box = document.getElementById('disco-container');
  if (!discos.length) {
    box.innerHTML = '<div class="empty-state"><i class="bi bi-disc"></i><p>Nenhum disco encontrado.</p></div>';
    return;
  }
  box.innerHTML = `<div class="disco-grid">` + discos.map(d => {
    let inStock = d.quantidade > 0;
    let low = d.quantidade > 0 && d.quantidade <= 5;
    let badgeCls = inStock ? (low ? 'badge-low' : 'badge-ok') : 'badge-out';
    let badgeTx = inStock ? (low ? `Últimas ${d.quantidade}` : 'Disponível') : 'Esgotado';
    let stockCls = inStock ? (low ? 'low' : 'ok') : 'out';
    let stockIco = inStock ? (low ? 'bi-exclamation-circle' : 'bi-check-circle') : 'bi-x-circle';
    let stockText = `${d.quantidade} ${d.quantidade === 1 ? 'unidade' : 'unidades'} disponíveis`;

    if (d.nome === 'We Are Reactive' && !_isLaunchLive) {
      badgeCls = 'badge-upcoming';
      badgeTx = 'Em breve';
      stockCls = 'upcoming';
      stockIco = 'bi-clock-history';
      stockText = 'Disponível na próxima sexta-feira';
    }

    return `
    <div class="disco-card">
      <div class="disco-top">
        <div class="disco-artist">${esc(d.artista || '—')}</div>
        <span class="badge-pill ${badgeCls}">${badgeTx}</span>
      </div>
      <div class="disco-name">${esc(d.nome || 'Sem título')}</div>
      <div class="disco-meta">
        <div class="disco-style">${esc(d.estilo || '—')}</div>
        <div class="disco-year">${d.ano_lancamento || '—'}</div>
      </div>
      <div class="disco-stock-row ${stockCls}">
        <i class="bi ${stockIco}"></i>
        ${stockText}
      </div>
    </div>`;
  }).join('') + '</div>';
}