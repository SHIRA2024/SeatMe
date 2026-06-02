// Injects sidebar + topbar. Call: renderShell({ active, pageTitle, pageSubtitle, topbarRight })
function renderShell({ active='dashboard', pageTitle='', pageSubtitle='', topbarRight='' } = {}) {
  const navMain = [
    { id:'dashboard', label:'דאשבורד',       href:'SC2B1E~1.HTM',
      icon:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>' },
    { id:'settings',  label:'הגדרות אירוע',  href:'SCE754~1.HTM',
      icon:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>' },
    { id:'seating',   label:'עורך ישיבה',    href:'SC8099~1.HTM',
      icon:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>' },
    { id:'tables',    label:'ניהול שולחנות', href:'SC61AB~1.HTM',
      icon:'<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>' },
    { id:'drag',      label:'תצוגת מפה',     href:'SC5DD8~1.HTM',
      icon:'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>' },
    { id:'export',    label:'יצוא ושיתוף',   href:'SC72CE~1.HTM',
      icon:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>' },
  ];

  const navGuests = [
    { id:'guests',      label:'רשימת אורחים',    href:'SC9376~1.HTM',
      icon:'<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>' },
    { id:'add-guest',   label:'הוסף אורח',        href:'SC2133~1.HTM',
      icon:'<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>' },
    { id:'import',      label:'ייבוא מקובץ',      href:'SC2D24~1.HTM',
      icon:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>' },
    { id:'send-invite', label:'שלח הזמנה',        href:'SCB0EE~1.HTM',
      icon:'<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>' },
    { id:'send-seating',label:'שלח סידורי ישיבה', href:'SC6AE5~1.HTM',
      icon:'<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>' },
    { id:'assign',      label:'שיוך מושב',        href:'SC1782~1.HTM',
      icon:'<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>' },
    { id:'preview',     label:'תצוגת אורח',       href:'SCE5BC~1.HTM',
      icon:'<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>' },
  ];

  const mkNav = (items) => items.map(n => `
    <a class="nav-item${n.id===active?' active':''}" href="${n.href}">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${n.icon}</svg>
      ${n.label}
      ${n.badge ? `<span class="nav-badge">${n.badge}</span>` : ''}
    </a>`).join('');

  document.getElementById('app-sidebar').innerHTML = `
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon">⚡</div>
      <div class="sidebar-logo-name">SeatMe</div>
    </div>
    <div style="padding:10px 12px 0">
      <div class="sidebar-event" style="cursor:pointer" onclick="location='SCE754~1.HTM'">
        <div class="sidebar-event-badge" id="sb-event-status">פעיל</div>
        <div class="sidebar-event-name" id="sb-event-name">טוען...</div>
        <div class="sidebar-event-date" id="sb-event-date"></div>
      </div>
    </div>
    <nav class="sidebar-nav">
      <div class="sidebar-nav-section">ניהול</div>
      ${mkNav(navMain)}
      <div class="sidebar-nav-section" style="margin-top:8px">אורחים</div>
      ${mkNav(navGuests)}
    </nav>
    <div class="sidebar-footer">
      <div style="font-size:24px">👤</div>
      <div>
        <div style="font-size:13px;font-weight:700;color:var(--white)" id="sb-host-name">...</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.5)">מארגן ראשי</div>
      </div>
    </div>
  `;

  document.getElementById('topbar-title').innerHTML = `
    <div class="breadcrumb">
      <span class="crumb-parent">SeatMe</span>
      <span class="crumb-sep">›</span>
      <span class="crumb-cur">${pageTitle}</span>
    </div>
  `;
  if (pageSubtitle && document.getElementById('topbar-subtitle')) {
    document.getElementById('topbar-subtitle').textContent = pageSubtitle;
  }
  if (topbarRight) {
    document.getElementById('topbar-right').innerHTML = topbarRight;
  }
  _loadSidebarData();
}

async function _loadSidebarData() {
  const email = sessionStorage.getItem('host_email');
  if (!email) return;

  let host;
  const cached = sessionStorage.getItem('_seatme_host');
  if (cached) {
    try { host = JSON.parse(cached); } catch(e) {}
  }

  if (!host) {
    const base = window.SEATME_API_BASE || (typeof API_BASE !== 'undefined' ? API_BASE : '');
    if (!base || base.includes('REPLACE')) return;
    try {
      const r = await fetch(`${base}/hosts?host_email=${encodeURIComponent(email)}`);
      host = await r.json();
      if (host && host.email) sessionStorage.setItem('_seatme_host', JSON.stringify(host));
    } catch(e) { return; }
  }

  if (!host) return;

  const months = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
  const nm = document.getElementById('sb-event-name');
  const dt = document.getElementById('sb-event-date');
  const hn = document.getElementById('sb-host-name');

  if (nm) nm.textContent = host.event_name || host.name || 'האירוע שלי';
  if (hn) hn.textContent = host.name || email;
  if (dt && host.event_date) {
    const parts = host.event_date.split('-');
    if (parts.length === 3)
      dt.textContent = `📅 ${parseInt(parts[2])} ב${months[parseInt(parts[1])-1]} ${parts[0]}`;
  }
}
