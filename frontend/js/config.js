/* ═══════════════════════════════════════════════════════════
   CONFIG & STATE
═══════════════════════════════════════════════════════════ */
const API = 'http://localhost:8000';

// Global state
let currentUser = null;
let _discos = [];
let _clientes = [];
let _launchTarget = null;   // Date object for launch
let _cdInterval = null;
let _simulated = false;
let _isLaunchLive = false;