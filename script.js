// ---- Schedule data, taken from the printed IIITDM bus time table ----
// Two scribbled-out rows on Bus No. 2's weekday schedule were unreadable
// in the source photo and are left out on purpose.

const WEEKDAY_TRIPS = [
    { id: 'wd-b1-1', bus: 1, route: 'Institute→Sadar', time: '15:40', purpose: 'Staff/Student' },
    { id: 'wd-b1-2', bus: 1, route: 'Sadar→Institute', time: '16:30', purpose: 'Staff/Student' },
    { id: 'wd-b1-3', bus: 1, route: 'Institute→Sadar', time: '17:15', purpose: 'Staff/Student' },
    { id: 'wd-b1-4', bus: 1, route: 'Sadar→Institute', time: '18:00', purpose: 'Staff/Student' },
    { id: 'wd-b1-5', bus: 1, route: 'Institute→Sadar', time: '19:00', purpose: 'Staff/Student' },
    { id: 'wd-b1-6', bus: 1, route: 'Sadar→Institute', time: '19:40', purpose: 'Staff/Student' },
    { id: 'wd-b1-7', bus: 1, route: 'Institute→Sadar', time: '20:20', purpose: 'Staff/Student' },
    { id: 'wd-b1-8', bus: 1, route: 'Sadar→Institute', time: '21:00', purpose: 'Staff/Student', last: true },

    { id: 'wd-b2-1', bus: 2, route: 'Institute→Sadar', time: '15:00', purpose: 'Staff/Student' },
    { id: 'wd-b2-2', bus: 2, route: 'Sadar→Institute', time: '15:45', purpose: 'Staff/Student' },
    { id: 'wd-b2-3', bus: 2, route: 'Institute→Sadar', time: '18:00', purpose: 'Staff/Student' },
    { id: 'wd-b2-4', bus: 2, route: 'Sadar→Institute', time: '18:30', purpose: 'Staff/Student' },
    { id: 'wd-b2-5', bus: 2, route: 'Institute→Sadar', time: '20:50', purpose: 'Staff/Student' },
    { id: 'wd-b2-6', bus: 2, route: 'Sadar→Institute', time: '21:30', purpose: 'Staff/Student', last: true },
];

const WEEKEND_TRIPS = [
    { id: 'we-b1-1', bus: 1, route: 'Institute→Sadar', time: '15:30', purpose: 'via Russel Chowk' },
    { id: 'we-b1-2', bus: 1, route: 'Sadar→Institute', time: '17:20', purpose: 'Direct' },
    { id: 'we-b1-3', bus: 1, route: 'Institute→Sadar', time: '18:00', purpose: 'Direct' },
    { id: 'we-b1-4', bus: 1, route: 'Sadar→Institute', time: '18:30', purpose: 'Direct' },
    { id: 'we-b1-5', bus: 1, route: 'Institute→Sadar', time: '19:00', purpose: 'Direct' },
    { id: 'we-b1-6', bus: 1, route: 'Sadar→Institute', time: '21:15', purpose: 'via Russel Chowk', last: true },

    { id: 'we-b2-1', bus: 2, route: 'Institute→Sadar', time: '15:00', purpose: 'Direct' },
    { id: 'we-b2-2', bus: 2, route: 'Sadar→Institute', time: '16:30', purpose: 'Direct' },
    { id: 'we-b2-3', bus: 2, route: 'Institute→Sadar', time: '17:30', purpose: 'Direct' },
    { id: 'we-b2-4', bus: 2, route: 'Sadar→Institute', time: '19:30', purpose: 'via Russel Chowk' },
    { id: 'we-b2-5', bus: 2, route: 'Institute→Sadar', time: '20:50', purpose: 'Direct' },
    { id: 'we-b2-6', bus: 2, route: 'Sadar→Institute', time: '21:30', purpose: 'Direct', last: true },
];

const CAPACITY = 32;

let selectedRoute = 'Institute→Sadar';
let bookings = JSON.parse(localStorage.getItem('bus-bookings') || '{}');

function todayKey() {
    return new Date().toISOString().slice(0, 10);
}

function isWeekend(date) {
    const d = date.getDay();
    return d === 0 || d === 6;
}

// Deterministic "random" seats-taken figure so everyone sees the same
// board on a given day, without needing a real backend.
function seededSeatsTaken(tripId, dateKey) {
    let hash = 0;
    const str = tripId + dateKey;
    for (let i = 0; i < str.length; i++) {
        hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
    }
    return hash % (CAPACITY + 1);
}

function toMinutes(hhmm) {
    const [h, m] = hhmm.split(':').map(Number);
    return h * 60 + m;
}

function formatTime(hhmm) {
    const [h, m] = hhmm.split(':').map(Number);
    const period = h >= 12 ? 'PM' : 'AM';
    const h12 = ((h + 11) % 12) + 1;
    return `${h12}:${String(m).padStart(2, '0')} ${period}`;
}

function render() {
    const now = new Date();
    const dateKey = todayKey();
    const weekend = isWeekend(now);
    const trips = weekend ? WEEKEND_TRIPS : WEEKDAY_TRIPS;
    const nowMinutes = now.getHours() * 60 + now.getMinutes();

    document.getElementById('dayLabel').textContent = weekend ? 'Saturday & Sunday schedule' : 'Weekday schedule (Mon–Fri)';
    document.getElementById('dateLabel').textContent = now.toDateString();

    const rows = trips
        .filter(t => t.route === selectedRoute)
        .sort((a, b) => toMinutes(a.time) - toMinutes(b.time));

    const container = document.getElementById('boardRows');
    container.innerHTML = '';

    rows.forEach(trip => {
        const departed = toMinutes(trip.time) < nowMinutes;
        const takenBase = seededSeatsTaken(trip.id, dateKey);
        const bookedByUser = bookings[dateKey + trip.id] || 0;
        const taken = Math.min(CAPACITY, takenBase + bookedByUser);
        const available = CAPACITY - taken;

        const row = document.createElement('div');
        row.className = 'row';

        const busClass = trip.bus === 1 ? 'bus1' : 'bus2';

        row.innerHTML = `
      <div class="time">${formatTime(trip.time)}</div>
      <div class="route-info">
        <span class="bus-tag ${busClass}">Bus ${trip.bus}</span>
        <span class="via">${trip.purpose}</span>
        ${trip.last ? '<span class="last-bus">Last bus this route</span>' : ''}
      </div>
      <div class="seats">
        <span>${departed ? '—' : available + ' / ' + CAPACITY}</span>
        <div class="seat-bar"><div class="seat-bar-fill" style="width:${departed ? 0 : (available / CAPACITY * 100)}%"></div></div>
      </div>
      <button class="action-btn ${departed ? 'departed' : (available <= 0 ? 'full' : (bookedByUser > 0 ? 'booked' : 'book'))}"
              ${departed || available <= 0 ? 'disabled' : ''}
              data-trip="${trip.id}">
        ${departed ? 'Departed' : (available <= 0 ? 'Full' : (bookedByUser > 0 ? 'Booked ✓' : 'Book seat'))}
      </button>
    `;
        container.appendChild(row);
    });

    if (rows.length === 0) {
        container.innerHTML = '<p style="color:#B9C2D6; padding:1.25rem;">No trips found for this direction.</p>';
    }
}

document.getElementById('boardRows').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-trip]');
    if (!btn || btn.disabled) return;
    const dateKey = todayKey();
    const key = dateKey + btn.dataset.trip;
    bookings[key] = (bookings[key] || 0) + 1;
    localStorage.setItem('bus-bookings', JSON.stringify(bookings));
    render();
});

document.getElementById('routeTabs').addEventListener('click', (e) => {
    const tab = e.target.closest('.tab');
    if (!tab) return;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    selectedRoute = tab.dataset.route;
    render();
});

function tickClock() {
    document.getElementById('clock').textContent = new Date().toLocaleTimeString();
}

tickClock();
setInterval(tickClock, 1000);
render();
setInterval(render, 30000);