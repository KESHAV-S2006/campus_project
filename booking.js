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

// Get trip ID from query parameter
const urlParams = new URLSearchParams(window.location.search);
const tripId = urlParams.get('tripId');

const isWeekend = (d) => d.getDay() === 0 || d.getDay() === 6;
const allTrips = [...WEEKDAY_TRIPS, ...WEEKEND_TRIPS];
const trip = allTrips.find(t => t.id === tripId);

if (!trip) {
    alert('Invalid Trip Selected');
    window.location.href = 'avalableBUS.html';
}

function formatTime(hhmm) {
    const [h, m] = hhmm.split(':').map(Number);
    const period = h >= 12 ? 'PM' : 'AM';
    const h12 = ((h + 11) % 12) + 1;
    return `${h12}:${String(m).padStart(2, '0')} ${period}`;
}

// Render Trip Summary
document.getElementById('summaryTime').textContent = formatTime(trip.time);
document.getElementById('summaryRoute').textContent = `${trip.route} (Bus ${trip.bus} · ${trip.purpose})`;

// Generate Unique Verification Code
function generateTicketCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = 'BUS-';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

// Handle Form Submission (Simulating Payment & Booking)
document.getElementById('bookingForm').addEventListener('submit', (e) => {
    e.preventDefault();

    const name = document.getElementById('passengerName').value.trim();
    const rollNo = document.getElementById('rollNo').value.trim().toUpperCase();

    if (!name || !rollNo) return;

    const todayKey = new Date().toISOString().slice(0, 10);
    const ticketCode = generateTicketCode();

    // 1. Store Seat Booking in counter
    let bookings = JSON.parse(localStorage.getItem('bus-bookings') || '{}');
    const bookingKey = todayKey + trip.id;
    bookings[bookingKey] = (bookings[bookingKey] || 0) + 1;
    localStorage.setItem('bus-bookings', JSON.stringify(bookings));

    // 2. Save Full Ticket Record
    const ticketData = {
        code: ticketCode,
        name: name,
        rollNo: rollNo,
        route: trip.route,
        bus: trip.bus,
        time: formatTime(trip.time),
        date: new Date().toDateString(),
        paid: true
    };

    let tickets = JSON.parse(localStorage.getItem('issued-tickets') || '{}');
    tickets[ticketCode] = ticketData;
    localStorage.setItem('issued-tickets', JSON.stringify(tickets));

    // 3. Redirect to Ticket Display Page
    window.location.href = `ticket.html?code=${ticketCode}`;
});