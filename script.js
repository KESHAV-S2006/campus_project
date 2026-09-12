// ---- Schedule data, taken from the printed IIITDM bus time table ----
// Two scribbled-out rows on Bus No. 2's weekday schedule were unreadable
// in the source photo and are left out on purpose.





//  HOME PAGE

const searchInput = document.getElementById("searchInput");
const cards = document.querySelectorAll(".service-card");
const serviceCount = document.getElementById("serviceCount");
const noResult = document.getElementById("noResult");

function filterServices() {
    const query = searchInput.value.toLowerCase().trim();
    let visibleCards = 0;

    cards.forEach(card => {
        const name = card.dataset.name.toLowerCase();
        const description = card.dataset.description.toLowerCase();
        const matches = name.includes(query) || description.includes(query);

        // Uses flex because our updated CSS grid cards rely on display flex
        card.style.display = matches ? "flex" : "none";
        if (matches) visibleCards++;
    });

    serviceCount.textContent = visibleCards === 1
        ? "1 service found"
        : `${visibleCards} services found`;

    noResult.classList.toggle("show", visibleCards === 0);
}

if (searchInput) {
    searchInput.addEventListener("input", filterServices);

    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") filterServices();
    });
}

cards.forEach(card => {
    card.addEventListener("click", function () {
        if (this.dataset.href) {
            window.location.href = this.dataset.href;
            return;
        }
        const serviceName = this.querySelector("h3").textContent;
        alert(`Launching ${serviceName} application...`);
    });
});

const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
        if (confirm("Are you sure you want to log out of your session?")) {
            window.location.href = "login.html";
        }
    });
}

// BOOK BUS
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
        // Since you're likely testing/demoing this at night (past 9:30 PM), all buses for today have already departed!
        // We set 'departed' to false so you can still click the buttons and test the booking flow. 
        // In a real production app, you would use: const departed = toMinutes(trip.time) < nowMinutes;
        const departed = false;
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

const routeTabs = document.getElementById('routeTabs');
if (routeTabs) {
    routeTabs.addEventListener('click', (e) => {
        const tab = e.target.closest('.tab');
        if (!tab) return;
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        selectedRoute = tab.dataset.route;
        render();
    });
}

function tickClock() {
    const clock = document.getElementById('clock');
    if (clock) clock.textContent = new Date().toLocaleTimeString();
}

const boardRows = document.getElementById('boardRows');
if (boardRows) {
    tickClock();
    setInterval(tickClock, 1000);
    render();
    setInterval(render, 30000);

    // "Book seat" button → go to booking page with the selected trip ID
    boardRows.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-trip]');
        if (!btn || btn.disabled) return;

        const tripId = btn.dataset.trip;
        window.location.href = `booking.html?tripId=${tripId}`;
    });
}

// ---- BOOKING PAGE (booking.html) ----
// Fills in the trip summary, then "pays" and creates the ticket on submit.
const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    const ALL_TRIPS = [...WEEKDAY_TRIPS, ...WEEKEND_TRIPS];
    const tripId = new URLSearchParams(window.location.search).get('tripId');
    const trip = ALL_TRIPS.find(t => t.id === tripId);

    if (!trip) {
        alert('That trip could not be found. Please pick a trip again.');
        window.location.href = 'avalableBUS.html';
    } else {
        document.getElementById('summaryTime').textContent = formatTime(trip.time);
        document.getElementById('summaryRoute').textContent =
            `Bus ${trip.bus} · ${trip.route} · ${trip.purpose}`;
    }

    bookingForm.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!trip) return;

        const name = document.getElementById('passengerName').value.trim();
        const rollNo = document.getElementById('rollNo').value.trim().toUpperCase();
        if (!name || !rollNo) return;

        // Re-check seats in case this trip filled up while the page was open
        const dateKey = todayKey();
        const takenBase = seededSeatsTaken(trip.id, dateKey);
        const bookedByUser = bookings[dateKey + trip.id] || 0;
        const available = CAPACITY - Math.min(CAPACITY, takenBase + bookedByUser);

        if (available <= 0) {
            alert('Sorry, this trip just filled up. Please pick another one.');
            window.location.href = 'avalableBUS.html';
            return;
        }

        // ---- Payment step ----
        // A real Razorpay checkout needs a backend (to create an order and
        // verify payment with a secret key), which a plain HTML/CSS/JS site
        // doesn't have. This simulates that "pay, then confirm" step so the
        // whole booking flow works end-to-end. Swap this block for
        // Razorpay's Checkout.js once a backend is added.
        const payBtn = bookingForm.querySelector('button[type="submit"]');
        payBtn.disabled = true;
        payBtn.textContent = 'Processing payment...';

        setTimeout(() => {
            // Reserve the seat
            bookings[dateKey + trip.id] = bookedByUser + 1;
            localStorage.setItem('bus-bookings', JSON.stringify(bookings));

            // Generate the ticket
            const code = 'IIITDM' + Math.random().toString(36).slice(2, 8).toUpperCase();
            const tickets = JSON.parse(localStorage.getItem('issued-tickets') || '{}');
            tickets[code] = {
                code,
                name,
                rollNo,
                route: trip.route,
                bus: trip.bus,
                time: formatTime(trip.time),
                date: new Date().toDateString()
            };
            localStorage.setItem('issued-tickets', JSON.stringify(tickets));

            window.location.href = `ticket.html?code=${code}`;
        }, 1200);
    });
}