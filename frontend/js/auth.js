/* ═══════════════════════════════════════════════════════════
   LOGIN
═══════════════════════════════════════════════════════════ */
function doLogin() {
  const nome = document.getElementById('login-nome').value.trim();
  if (!nome) {
    toast('Por favor informe seu nome.', 'error');
    document.getElementById('login-nome').focus();
    return;
  }
  currentUser = nome;
  document.getElementById('user-display').textContent = nome;

  // Spin the vinyl
  document.getElementById('login-vinyl').classList.add('spinning');
  setTimeout(() => {
    document.getElementById('screen-login').classList.remove('active');
    document.getElementById('screen-app').classList.add('active');
    loadDiscos();
    loadClientes();
    startCountdown();
  }, 600);
}

function doLogout() {
  currentUser = null;
  document.getElementById('screen-app').classList.remove('active');
  document.getElementById('screen-login').classList.add('active');
  document.getElementById('login-nome').value = '';
  document.getElementById('login-vinyl').classList.remove('spinning');
  clearInterval(_cdInterval);
  if (typeof resetLaunchState === 'function') resetLaunchState();
}