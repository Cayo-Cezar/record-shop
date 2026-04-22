/* ═══════════════════════════════════════════════════════════
   COUNTDOWN — próxima sexta-feira às 00:00
═══════════════════════════════════════════════════════════ */
function nextFridayMidnight() {
  const now = new Date();
  const day = now.getDay(); // 0=sun … 5=fri
  const daysUntil = (5 - day + 7) % 7 || 7; // force next friday
  const target = new Date(now);
  target.setDate(now.getDate() + daysUntil);
  target.setHours(0, 0, 0, 0);
  return target;
}

function startCountdown() {
  if (!_simulated) _launchTarget = nextFridayMidnight();
  updateCountdown();
  clearInterval(_cdInterval);
  _cdInterval = setInterval(updateCountdown, 1000);
}

function updateCountdown() {
  const now = Date.now();
  let diff = _launchTarget - now;

  if (diff <= 0) {
    if (!_isLaunchLive) {
      showLaunchLive();
    }
    // Set target to next Friday and recalculate diff so the counter never stops
    _simulated = false; // reset simulation flag so it correctly picks next friday
    _launchTarget = nextFridayMidnight();
    diff = _launchTarget - Date.now();
  }

  const days = Math.floor(diff / 86400000);
  const hours = Math.floor((diff % 86400000) / 3600000);
  const mins = Math.floor((diff % 3600000) / 60000);
  const secs = Math.floor((diff % 60000) / 1000);

  const pad = n => String(n).padStart(2, '0');
  document.getElementById('cd-days').textContent = pad(days);
  document.getElementById('cd-hours').textContent = pad(hours);
  document.getElementById('cd-mins').textContent = pad(mins);
  document.getElementById('cd-secs').textContent = pad(secs);
}

function simulateLaunch() {
  _simulated = true;
  _launchTarget = new Date(Date.now() + 5000); // 5 seconds from now
  startCountdown();
  toast('Simulação iniciada — lançamento em 5 segundos! 🎵', 'info');
}

function showLaunchLive() {
  _isLaunchLive = true;
  document.getElementById('launch-banner').style.display = 'none';
  const live = document.getElementById('launch-live');
  live.classList.add('visible');
  toast('🎉 Lançamento ao vivo! Disco disponível agora!', 'success');
  // Refresh UI to show the album
  if (typeof applyFilters === 'function') applyFilters();
  if (typeof populatePedidoSelects === 'function') populatePedidoSelects();
}

function resetLaunchState() {
  _isLaunchLive = false;
  _simulated = false;
  
  // Show banner, hide live state
  const banner = document.getElementById('launch-banner');
  if (banner) banner.style.display = 'flex';
  
  const live = document.getElementById('launch-live');
  if (live) live.classList.remove('visible');
  
  // Restart countdown normally
  clearInterval(_cdInterval);
  _launchTarget = nextFridayMidnight();
  startCountdown();
  
  // Refresh UI to hide the album
  if (typeof applyFilters === 'function') applyFilters();
  if (typeof populatePedidoSelects === 'function') populatePedidoSelects();
}