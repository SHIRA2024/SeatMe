// Injects sidebar + topbar. Call: renderShell({ active, pageTitle, pageSubtitle, topbarRight })
function renderShell({ active='dashboard', pageTitle='', pageSubtitle='', topbarRight='' } = {}) {
  const navMain = [
    { id:'dashboard', label:'דאשבורד',       href:'screen6-dashboard.html',
      icon:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>' },
    { id:'settings',  label:'הגדרות אירוע',  href:'screen-event-settings.html',
      icon:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>' },
    { id:'seating',   label:'עורך ישיבה',    href:'screen9-seating-editor.html',
      icon:'<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>' },
    { id:'tables',    label:'ניהול שולחנות', href:'screen-table-setup.html',
      icon:'<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>' },
    { id:'drag',      label:'תצוגת מפה',     href:'screen10-seating-drag.html',
      icon:'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>' },
    { id:'export',    label:'יצוא ושיתוף',   href:'screen12-export.html',
      icon:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>' },
  ];

  const navGuests = [
    { id:'guests',      label:'רשימת אורחים',   href:'screen7-guest-list.html',    badge:4,
      icon:'<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>' },
    { id:'add-guest',   label:'הוסף אורח',       href:'screen-add-guest.html',
      icon:'<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>' },
    { id:'import',      label:'ייבוא מקובץ',     href:'screen-import-guests.html',
      icon:'<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>' },
    { id:'profile',     label:'פרטי אורח',       href:'screen8-guest-profile.html',
      icon:'<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>' },
    { id:'send-invite', label:'שלח הזמנה',       href:'screen-send-invite.html',
      icon:'<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>' },
    { id:'send-seating',label:'שלח סידורי ישיבה',href:'screen-send-seating.html',
      icon:'<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>' },
    { id:'assign',      label:'שיוך מושב',       href:'screen11-assign-seat.html',
      icon:'<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>' },
    { id:'preview',     label:'תצוגת אורח',      href:'screen13-guest-preview.html',
      icon:'<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>' },
  ];

  const mkNav = (items) => items.map(n => `
    <a class="nav-item${n.id===active?' active':''}" href="${n.href}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${n.icon}</svg>
      ${n.label}
      ${n.badge ? `<span class="nav-badge">${n.badge}</span>` : ''}
    </a>`).join('');

  document.getElementById('app-sidebar').innerHTML = `
    <div class="sidebar-logo">
      <div class="logo-icon">⚡</div>
      <div class="logo-name">EventFlow</div>
    </div>
    <div style="padding:10px 12px 0">
      <div class="sidebar-event" style="cursor:pointer" onclick="location='screen-event-settings.html'">
        <div class="ev-badge">פעיל</div>
        <div class="ev-name">החתונה של נועה וגיא</div>
        <div class="ev-date">📅 15 בספטמבר 2024</div>
      </div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section-title">ניהול</div>
      ${mkNav(navMain)}
      <div class="nav-section-title" style="margin-top:8px">אורחים</div>
      ${mkNav(navGuests)}
    </nav>
    <div class="sidebar-footer">
      <div class="user-avatar">👤</div>
      <div class="user-info">
        <div class="user-name">נועה כהן</div>
        <div class="user-role">מארגן ראשי</div>
      </div>
    </div>
  `;

  document.getElementById('topbar-title').innerHTML = `
    <div class="breadcrumb">
      <span class="crumb-parent">EventFlow</span>
      <span class="sep">›</span>
      <span class="crumb-current">${pageTitle}</span>
    </div>
  `;
  if (pageSubtitle && document.getElementById('topbar-subtitle')) {
    document.getElementById('topbar-subtitle').textContent = pageSubtitle;
  }
  if (topbarRight) {
    document.getElementById('topbar-right').innerHTML = topbarRight;
  }
}
