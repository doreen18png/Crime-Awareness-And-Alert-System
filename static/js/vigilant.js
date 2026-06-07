/* Vigilant — Main JS */

// Mobile menu
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
  });
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
}

// Auto-dismiss alerts after 5s
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => alert.remove(), 5000);
});

// Geolocation helper (called by forms that need coords)
function getLocationAndFill(latField, lngField, addrField) {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(pos => {
    if (latField) latField.value = pos.coords.latitude;
    if (lngField) lngField.value = pos.coords.longitude;
    // Reverse geocode via Nominatim
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`)
      .then(r => r.json())
      .then(data => {
        if (addrField && data.display_name) {
          addrField.value = data.display_name.split(',').slice(0, 3).join(',');
        }
      })
      .catch(() => {});
  }, () => {});
}

// Initialize map on report list / detail pages
function initCrimeMap(elementId, reportsData, options = {}) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const defaultCenter = options.center || [-1.286389, 36.817223]; // Nairobi
  const map = L.map(elementId, { zoomControl: true }).setView(defaultCenter, options.zoom || 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);

  const colorMap = {
    critical: '#8b5cf6', high: '#dc2828', medium: '#f59e0b', low: '#22c55e'
  };

  if (reportsData && reportsData.length) {
    const markers = [];
    reportsData.forEach(r => {
      if (!r.latitude || !r.longitude) return;
      const color = colorMap[r.severity] || '#3b82f6';
      const marker = L.circleMarker([r.latitude, r.longitude], {
        radius: r.severity === 'critical' ? 10 : r.severity === 'high' ? 8 : 6,
        fillColor: color,
        color: color,
        weight: 1,
        opacity: 0.9,
        fillOpacity: 0.5
      }).addTo(map);

      marker.bindPopup(`
        <div style="min-width:200px;font-family:var(--font-body,sans-serif)">
          <div style="font-weight:700;margin-bottom:4px">${r.title}</div>
          <div style="font-size:0.8rem;color:#888;margin-bottom:8px">${r.address || ''}</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
            <span style="background:${color}22;color:${color};border:1px solid ${color}44;padding:2px 8px;border-radius:20px;font-size:0.7rem">${r.severity}</span>
            <span style="background:#1a2236;color:#8892a4;border:1px solid rgba(255,255,255,0.1);padding:2px 8px;border-radius:20px;font-size:0.7rem">${r.category}</span>
          </div>
          <a href="/reports/${r.id}/" style="color:#dc2828;font-size:0.8rem">View details →</a>
        </div>
      `);
      markers.push(marker);
    });
    if (markers.length && !options.center) {
      const group = new L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }
  }
  return map;
}

// Safe zone map
function initSafeZoneMap(elementId, safeZones, userLat, userLng) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const center = (userLat && userLng) ? [userLat, userLng] : [-1.286389, 36.817223];
  const map = L.map(elementId).setView(center, 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);

  if (userLat && userLng) {
    L.circleMarker([userLat, userLng], {
      radius: 8, fillColor: '#dc2828', color: '#dc2828', weight: 2, fillOpacity: 0.8
    }).addTo(map).bindPopup('Your location');
  }

  const icons = { police_station: '🚓', hospital: '🏥', fire_station: '🚒', community_center: '🏘️', school: '🏫' };
  safeZones.forEach(z => {
    const marker = L.marker([z.latitude, z.longitude], {
      icon: L.divIcon({
        html: `<div style="font-size:1.5rem">${icons[z.zone_type] || '📍'}</div>`,
        className: '', iconSize: [30, 30], iconAnchor: [15, 15]
      })
    }).addTo(map);
    marker.bindPopup(`<strong>${z.name}</strong><br>${z.address}${z.phone ? '<br>📞 ' + z.phone : ''}`);
  });
  return map;
}
