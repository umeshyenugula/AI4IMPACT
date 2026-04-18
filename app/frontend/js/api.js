/* ============================================================
   ARTISAN AI — API Client
   Connects to FastAPI backend at localhost:8000
   ============================================================ */

const API_HOST =  'https://ai4impact.onrender.com';
const API_BASE = `${API_HOST}/api/v1`;
const TRUST_BASE = `${API_HOST}/api/v1/trust`;

const api = {
  /* ─── Artisans ─────────────────────────────────────────── */
  async registerArtisan(data) {
    return await request('POST', '/artisans', data);
  },
  async getArtisan(id) {
    return await request('GET', `/artisans/${id}`);
  },

  /* ─── Portfolio ────────────────────────────────────────── */
  async uploadPortfolio(artisanId, file, title = '', description = '') {
    const form = new FormData();
    form.append('file', file);
    if (title) form.append('title', title);
    if (description) form.append('description', description);
    return await request('POST', `/artisans/${artisanId}/portfolio`, form, true);
  },
  async getPortfolio(artisanId) {
    return await request('GET', `/artisans/${artisanId}/portfolio`);
  },

  /* ─── Learning Paths ───────────────────────────────────── */
  async createLearningPath(artisanId, title = '') {
    const query = title ? `?title=${encodeURIComponent(title)}` : '';
    return await request('POST', `/artisans/${artisanId}/learning-paths${query}`);
  },
  async getLearningPaths(artisanId) {
    return await request('GET', `/artisans/${artisanId}/learning-paths`);
  },

  /* ─── Market Pivots ────────────────────────────────────── */
  async getMarketPivots(artisanId) {
    return await request('GET', `/artisans/${artisanId}/market-pivots`);
  },
  async getMarketInsights(artisanId) {
    return await request('GET', `/artisans/${artisanId}/market-insights`);
  },
  async getDemandForecast(artisanId) {
    return await request('GET', `/artisans/${artisanId}/demand-forecast`);
  },
  async getB2BCatalog(artisanId) {
    return await request('GET', `/artisans/${artisanId}/b2b/catalog`);
  },
  async createB2BQuote(artisanId, payload) {
    return await request('POST', `/artisans/${artisanId}/b2b/quotes`, payload);
  },

  /* ─── Edge Summary ─────────────────────────────────────── */
  async getEdgeSummary(artisanId) {
    return await request('GET', `/artisans/${artisanId}/edge-summary`);
  },

  /* ─── Workspace ────────────────────────────────────────── */
  async getWorkspace(artisanId) {
    return await request('GET', `/artisans/${artisanId}/workspace`);
  },

  /* ─── Telemetry ────────────────────────────────────────── */
  async syncTelemetry(deviceId, jobs) {
    return await request('POST', '/telemetry/sync', { device_id: deviceId, jobs });
  },

  /* ─── Dashboard ────────────────────────────────────────── */
  async getDashboard() {
    return await request('GET', '/dashboard-summary');
  },

  /* ─── Provenance ────────────────────────────────────────── */
  async mintProvenance(artisanId, productId, buyerName) {
    return await request('POST', '/provenance', {
      artisan_id: artisanId,
      product_id: productId,
      buyer_name: buyerName
    }, false, TRUST_BASE);
  },

  /* ─── Escrow ────────────────────────────────────────────── */
  async createEscrowContract(orderId, artisanId, buyerName, totalAmountUsd, milestones) {
    return await request('POST', '/escrow/contracts', {
      order_id: orderId,
      artisan_id: artisanId,
      buyer_name: buyerName,
      total_amount_usd: totalAmountUsd,
      milestones
    }, false, TRUST_BASE);
  },
  async releaseEscrow(orderId, milestoneName) {
    return await request('POST', `/escrow/contracts/${encodeURIComponent(orderId)}/release/${encodeURIComponent(milestoneName)}`, null, false, TRUST_BASE);
  }
};

async function request(method, path, body = null, isForm = false, base = API_BASE) {
  const opts = {
    method,
    headers: {}
  };

  if (body) {
    if (isForm) {
      opts.body = body; // FormData — no Content-Type header
    } else {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
  }

  try {
    const res = await fetch(`${base}${path}`, opts);
    const contentType = res.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await res.json() : await res.text();
    if (!res.ok) {
      throw new Error(data?.detail || data || `HTTP ${res.status}`);
    }
    return { ok: true, data };
  } catch (err) {
    console.error(`[API] ${method} ${path}`, err);
    return { ok: false, error: err.message };
  }
}

/* ─── State Management ─────────────────────────────────── */
const AppState = {
  currentArtisan: null,

  save(artisan) {
    this.currentArtisan = artisan;
    sessionStorage.setItem('artisan', JSON.stringify(artisan));
  },
  load() {
    try {
      const raw = sessionStorage.getItem('artisan');
      if (raw) this.currentArtisan = JSON.parse(raw);
    } catch (e) { /* ignore */ }
    return this.currentArtisan;
  },
  clear() {
    this.currentArtisan = null;
    sessionStorage.removeItem('artisan');
  },
  get id() {
    return this.currentArtisan?.id ?? null;
  }
};

/* ─── Toast Notifications ──────────────────────────────── */
function showToast(message, type = 'default') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3600);
}

/* ─── Reveal on Scroll ──────────────────────────────────── */
function initReveal() {
  const els = document.querySelectorAll('.reveal');
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(el => obs.observe(el));
}

/* ─── Navbar Scroll ─────────────────────────────────────── */
function initNavbar() {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 30);
  });
}

/* ─── Mobile Navigation / Sidebar ─────────────────────── */
function closeMobileUi() {
  document.body.classList.remove('nav-open', 'sidebar-open', 'no-scroll');
  const burger = document.querySelector('.nav-hamburger');
  if (burger) burger.classList.remove('active');
}

function ensureMobileBackdrop() {
  let backdrop = document.querySelector('.mobile-backdrop');
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.className = 'mobile-backdrop';
    backdrop.addEventListener('click', closeMobileUi);
    document.body.appendChild(backdrop);
  }
}

function toggleMobileNav(event) {
  if (event && typeof event.preventDefault === 'function') {
    event.preventDefault();
  }

  const isMobile = window.matchMedia('(max-width: 1024px)').matches;
  if (!isMobile) return;

  ensureMobileBackdrop();
  const burger = document.querySelector('.nav-hamburger');
  const hasSidebar = Boolean(document.querySelector('.layout-sidebar .sidebar'));

  if (hasSidebar) {
    const opening = !document.body.classList.contains('sidebar-open');
    document.body.classList.toggle('sidebar-open', opening);
    document.body.classList.toggle('no-scroll', opening);
  } else {
    const opening = !document.body.classList.contains('nav-open');
    document.body.classList.toggle('nav-open', opening);
    document.body.classList.toggle('no-scroll', opening);
  }

  if (burger) {
    const active = document.body.classList.contains('sidebar-open') || document.body.classList.contains('nav-open');
    burger.classList.toggle('active', active);
  }
}

function initMobileNavigation() {
  ensureMobileBackdrop();

  const burger = document.querySelector('.nav-hamburger');
  if (burger) {
    burger.addEventListener('click', toggleMobileNav);
  }

  document.querySelectorAll('.nav-links a, .sidebar-nav a').forEach(link => {
    link.addEventListener('click', () => closeMobileUi());
  });

  window.addEventListener('resize', () => {
    if (!window.matchMedia('(max-width: 1024px)').matches) {
      closeMobileUi();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeMobileUi();
    }
  });
}

/* ─── Format Helpers ────────────────────────────────────── */
function fmtPct(val) { return `${Math.round((val || 0) * 100)}%`; }
function fmtDate(str) {
  try {
    return new Date(str).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch { return str; }
}
function fmtScore(val) { return (val || 0).toFixed(2); }
function initials(name = '') {
  return name.split(' ').slice(0, 2).map(w => w[0] || '').join('').toUpperCase() || 'A';
}

/* ─── Init ──────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  AppState.load();
  initNavbar();
  initMobileNavigation();
  initReveal();
});
