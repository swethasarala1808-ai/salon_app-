// ── SHARED SALON PORTAL FUNCTIONS ──
const SALON_API = (method, params={}) => {
  const qs = Object.entries(params).map(([k,v])=>`${k}=${encodeURIComponent(v)}`).join('&');
  return fetch(`/api/method/${method}${qs?'?'+qs:''}`, {
    headers: {'Accept':'application/json','X-Frappe-CSRF-Token':'fetch'}
  }).then(r=>r.json()).catch(()=>({message:[]}));
};

const ICONS = {
  'haircut':'✂️','hair':'💇','beard':'🧔','shave':'🪒','facial':'✨',
  'wax':'🌸','thread':'🪡','makeup':'💄','bridal':'👰','nail':'💅',
  'spa':'💆','keratin':'🌟','massage':'🤲','color':'🎨','treatment':'🌿',
  'package':'📦','default':'💈'
};

function getSvcIcon(name) {
  const l = (name||'').toLowerCase();
  for (const [k,v] of Object.entries(ICONS)) if(l.includes(k)) return v;
  return ICONS.default;
}

function formatPrice(p) {
  return '₹' + Number(p||0).toLocaleString('en-IN');
}

function toast(msg, dur=3000) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#1a1a2e;color:white;padding:12px 24px;border-radius:30px;font-size:.88em;z-index:9999;transition:opacity .3s;font-family:Manrope,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.4)';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.opacity = '1';
  setTimeout(() => el.style.opacity = '0', dur);
}

async function submitBooking(salonType, accentColor) {
  const name = (document.getElementById('b-name')||{}).value?.trim();
  const phone = (document.getElementById('b-phone')||{}).value?.trim();
  const service = (document.getElementById('b-service')||{}).value;
  const stylist = (document.getElementById('b-stylist')||{}).value || '';
  const date = (document.getElementById('b-date')||{}).value;
  const time = (document.getElementById('b-time')||{}).value;
  const notes = (document.getElementById('b-notes')||{}).value || '';

  if (!name || !phone || !service || !date || !time) {
    toast('⚠ Please fill all required fields'); return;
  }
  if (!/^[6-9]\d{9}$/.test(phone)) {
    toast('⚠ Enter valid 10-digit phone'); return;
  }

  const btn = document.getElementById('b-submit');
  if (btn) { btn.disabled = true; btn.textContent = 'Booking...'; }

  try {
    const r = await SALON_API('salon_app.salon_app.api.book_appointment', {
      customer_name: name, customer_phone: phone, salon_type: salonType,
      service, stylist, appointment_date: date, appointment_time: time, notes
    });
    const data = r.message || {};

    if (data.success) {
      // Show success
      const form = document.getElementById('bookForm');
      const panel = document.getElementById('successPanel');
      if (form) form.style.display = 'none';
      if (panel) {
        panel.style.display = 'block';
        const el = document.getElementById('conf-ref');
        if (el) el.textContent = data.appointment;
        const sn = document.getElementById('conf-service');
        if (sn) sn.textContent = service;
        const nn = document.getElementById('conf-name');
        if (nn) nn.textContent = name;
      }
      // Save to localStorage for owner dashboard
      const all = JSON.parse(localStorage.getItem('salon_bookings') || '[]');
      all.push({ name, phone, service, stylist, date, time, salonType, id: data.appointment, ts: new Date().toISOString() });
      localStorage.setItem('salon_bookings', JSON.stringify(all));
      // Broadcast to owner
      try {
        const bc = new BroadcastChannel('salon_owner');
        bc.postMessage({ type: 'new_booking', name, phone, service, salonType });
        bc.close();
      } catch(e) {}
    } else {
      toast('❌ Booking failed. Please try again.');
    }
  } catch(e) {
    toast('❌ Network error. Please try again.');
  }
  if (btn) { btn.disabled = false; btn.textContent = '✦ Confirm Appointment'; }
}

function resetBookingForm() {
  const form = document.getElementById('bookForm');
  const panel = document.getElementById('successPanel');
  if (form) { form.reset(); form.style.display = 'block'; }
  if (panel) panel.style.display = 'none';
  document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
}

function setService(name) {
  const sel = document.getElementById('b-service');
  if (sel) {
    for (let i = 0; i < sel.options.length; i++) {
      if (sel.options[i].value === name) { sel.selectedIndex = i; break; }
    }
  }
  document.getElementById('booking')?.scrollIntoView({ behavior: 'smooth' });
}
