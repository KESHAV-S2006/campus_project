// HOME PAGE
const searchInput = document.getElementById("searchInput");
const cards = document.querySelectorAll(".service-card");
const serviceCount = document.getElementById("serviceCount");
const noResult = document.getElementById("noResult");

function filterServices() {
    if (!searchInput) return;
    const query = searchInput.value.toLowerCase().trim();
    let visibleCards = 0;

    cards.forEach((card) => {
        const name = (card.dataset.name || "").toLowerCase();
        const description = (card.dataset.description || "").toLowerCase();
        const matches = name.includes(query) || description.includes(query);

        card.style.display = matches ? "flex" : "none";
        if (matches) visibleCards++;
    });

    if (serviceCount) {
        serviceCount.textContent = visibleCards === 1 ? "1 service found" : `${visibleCards} services found`;
    }

    if (noResult) {
        noResult.classList.toggle("show", visibleCards === 0);
    }
}

if (searchInput) {
    searchInput.addEventListener("input", filterServices);
    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") filterServices();
    });
}

cards.forEach((card) => {
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
    logoutBtn.addEventListener("click", async function () {
        if (!confirm("Are you sure you want to log out of your session?")) return;

        try {
            await fetch('/api/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error', error);
        }

        window.location.href = 'login.html';
    });
}

async function loadCurrentUser() {
    const userEmail = document.getElementById('userEmail');
    if (!userEmail) return;

    try {
        const res = await fetch('/api/me');
        const data = await res.json();

        if (!data.loggedIn) {
            window.location.href = 'login.html';
            return;
        }

        userEmail.textContent = data.email || 'student@email.com';
    } catch (error) {
        console.error('User session lookup failed', error);
        window.location.href = 'login.html';
    }
}

if (document.getElementById('userEmail')) {
    loadCurrentUser();
}

// BUS BOOKING - GLOBALS
let WEEKDAY_TRIPS = [];
let WEEKEND_TRIPS = [];
let CAPACITY = 32;
let selectedRoute = 'Institute→Sadar';
let myTickets = [];

function isWeekend(date) {
    const d = date.getDay();
    return d === 0 || d === 6;
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

async function loadMyTickets() {
    try {
        const res = await fetch('/api/my-tickets');
        if (res.status === 401) {
            window.location.href = 'login.html';
            return;
        }
        const data = await res.json();
        myTickets = Array.isArray(data.tickets) ? data.tickets : [];
    } catch (error) {
        console.error('Failed to load user tickets', error);
        myTickets = [];
    }
}

async function loadTrips() {
    try {
        const res = await fetch('/api/trips');
        if (res.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        const data = await res.json();
        WEEKDAY_TRIPS = data.weekday;
        WEEKEND_TRIPS = data.weekend;
        if (WEEKDAY_TRIPS.length > 0) CAPACITY = WEEKDAY_TRIPS[0].capacity;

        await loadMyTickets();
        render();
    } catch (e) {
        console.error('Failed to load trips', e);
    }
}

function render() {
    const boardRows = document.getElementById('boardRows');
    if (!boardRows) return;

    const now = new Date();
    const weekend = isWeekend(now);
    const trips = weekend ? WEEKEND_TRIPS : WEEKDAY_TRIPS;

    const dayLabel = document.getElementById('dayLabel');
    const dateLabel = document.getElementById('dateLabel');
    if (dayLabel) dayLabel.textContent = weekend ? 'Saturday & Sunday schedule' : 'Weekday schedule (Mon–Fri)';
    if (dateLabel) dateLabel.textContent = now.toDateString();

    const rows = trips
        .filter((t) => t.route === selectedRoute)
        .sort((a, b) => toMinutes(a.time) - toMinutes(b.time));

    boardRows.innerHTML = '';

    rows.forEach((trip) => {
        const nowMinutes = toMinutes(new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }));
        const departed = toMinutes(trip.time) < nowMinutes;
        const available = trip.available;
        const bookedByUser = myTickets.some((ticket) => ticket.tripId === trip.id && ['valid', 'checked_in'].includes(ticket.status));

        const row = document.createElement('div');
        row.className = 'row';

        const busClass = trip.bus === 1 ? 'bus1' : 'bus2';
        const buttonDisabled = departed || available <= 0 || bookedByUser;

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
      <button class="action-btn ${departed ? 'departed' : (available <= 0 ? 'full' : (bookedByUser ? 'booked' : 'book'))}"
              ${buttonDisabled ? 'disabled' : ''}
              data-trip="${trip.id}">
        ${departed ? 'Departed' : (available <= 0 ? 'Full' : (bookedByUser ? 'Booked ✓' : 'Book seat'))}
      </button>
    `;
        boardRows.appendChild(row);
    });

    if (rows.length === 0) {
        boardRows.innerHTML = '<p style="color:#B9C2D6; padding:1.25rem;">No trips found for this direction.</p>';
    }
}

const routeTabs = document.getElementById('routeTabs');
if (routeTabs) {
    routeTabs.addEventListener('click', (e) => {
        const tab = e.target.closest('.tab');
        if (!tab) return;
        document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
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
    loadTrips();
    setInterval(loadTrips, 30000);

    boardRows.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-trip]');
        if (!btn || btn.disabled) return;

        const tripId = btn.dataset.trip;
        window.location.href = `booking.html?tripId=${tripId}`;
    });
}

const myTicketsList = document.getElementById('myTicketsList');
if (myTicketsList) {
    function statusLabel(status) {
        if (status === 'valid') return 'Booked';
        if (status === 'checked_in') return 'Checked in';
        if (status === 'cancelled') return 'Cancelled';
        return status;
    }

    async function renderMyTickets() {
        try {
            const res = await fetch('/api/my-tickets');
            if (res.status === 401) {
                window.location.href = 'login.html';
                return;
            }

            const data = await res.json();
            const tickets = Array.isArray(data.tickets) ? data.tickets : [];

            if (tickets.length === 0) {
                myTicketsList.innerHTML = '<div class="empty-state">You haven\'t booked any tickets yet.</div>';
                return;
            }

            myTicketsList.innerHTML = tickets.map((t) => `
                <div class="my-ticket-row" data-code="${t.code}">
                    <div class="my-ticket-info">
                        <strong>${formatTime(t.time)}</strong> · Bus ${t.bus} · ${t.route}
                        <div class="my-ticket-meta">
                            ${t.name} · ${t.rollNo} · <span style="font-family:'IBM Plex Mono', monospace;">${t.code}</span>
                        </div>
                    </div>
                    <div class="my-ticket-actions">
                        <span class="pill ${t.status}">${statusLabel(t.status)}</span>
                        <a href="ticket.html?code=${t.code}" class="btn btn-secondary" style="padding:0.4rem 0.8rem; font-size:0.78rem;">View</a>
                        <button class="btn btn-danger my-cancel-btn" style="padding:0.4rem 0.8rem; font-size:0.78rem;"
                            data-code="${t.code}" ${t.status !== 'valid' ? 'disabled' : ''}>
                            ${t.status === 'valid' ? '✖ Cancel & Refund' : 'Unavailable'}
                        </button>
                    </div>
                </div>
            `).join('');

            myTicketsList.querySelectorAll('.my-cancel-btn').forEach((btn) => {
                btn.addEventListener('click', async () => {
                    if (btn.disabled) return;
                    if (!confirm('Cancel this ticket and refund the payment? This cannot be undone.')) return;

                    const code = btn.dataset.code;
                    btn.disabled = true;
                    btn.textContent = 'Cancelling...';

                    try {
                        const res = await fetch('/api/cancel-ticket', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ code })
                        });
                        const data = await res.json();

                        if (data.error) {
                            alert(data.error);
                            btn.disabled = false;
                            btn.textContent = '✖ Cancel & Refund';
                            return;
                        }

                        alert(data.message || 'Ticket cancelled and refund initiated.');
                        await loadTrips();
                        await renderMyTickets();
                    } catch (error) {
                        console.error('Cancel request failed', error);
                        alert('Could not reach the server to cancel this ticket.');
                        btn.disabled = false;
                        btn.textContent = '✖ Cancel & Refund';
                    }
                });
            });
        } catch (error) {
            console.error('Failed to render tickets', error);
            myTicketsList.innerHTML = '<div class="empty-state">Could not load your tickets.</div>';
        }
    }

    renderMyTickets();
    setInterval(renderMyTickets, 30000);

    const refreshLink = document.getElementById('myTicketsRefresh');
    if (refreshLink) {
        refreshLink.addEventListener('click', renderMyTickets);
    }
}

const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    const tripId = new URLSearchParams(window.location.search).get('tripId');
    let trip = null;

    fetch(`/api/trip/${tripId}`)
        .then((res) => {
            if (res.status === 401) {
                window.location.href = 'login.html';
                return res.json();
            }
            return res.json();
        })
        .then((data) => {
            if (data.error) {
                alert('That trip could not be found. Please pick a trip again.');
                window.location.href = 'avalableBUS.html';
                return;
            }
            trip = data;
            document.getElementById('summaryTime').textContent = formatTime(trip.time);
            document.getElementById('summaryRoute').textContent = `Bus ${trip.bus} · ${trip.route} · ${trip.purpose}`;
        })
        .catch((err) => {
            alert('Error loading trip details.');
            console.error(err);
        });

    bookingForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!trip) return;

        const name = document.getElementById('passengerName').value.trim();
        const rollNo = document.getElementById('rollNo').value.trim().toUpperCase();
        if (!name || !rollNo) return;

        const payBtn = bookingForm.querySelector('button[type="submit"]');
        payBtn.disabled = true;
        payBtn.textContent = 'Processing payment...';

        try {
            const orderRes = await fetch('/api/create-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tripId, rollNo })
            });
            const orderData = await orderRes.json();

            if (orderRes.status === 409) {
                alert('Sorry, this trip is no longer available. Please pick another one.');
                window.location.href = 'avalableBUS.html';
                return;
            }
            if (orderData.error) throw new Error(orderData.error);

            const options = {
                key: orderData.keyId,
                amount: orderData.amount,
                currency: orderData.currency,
                name: 'IIITDM Bus Service',
                description: 'Bus Ticket Booking',
                order_id: orderData.orderId,
                handler: async function (response) {
                    payBtn.textContent = 'Verifying payment...';

                    const verifyRes = await fetch('/api/verify-and-book', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            tripId,
                            name,
                            rollNo,
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature
                        })
                    });

                    const ticketData = await verifyRes.json();

                    if (verifyRes.status === 409) {
                        alert(ticketData.error || 'Seat sold out during payment. You have been refunded.');
                        window.location.href = 'avalableBUS.html';
                        return;
                    }
                    if (ticketData.error) throw new Error(ticketData.error);

                    window.location.href = `ticket.html?code=${ticketData.code}`;
                },
                theme: { color: '#FFCC00' }
            };

            const rzp = new window.Razorpay(options);
            rzp.on('payment.failed', function (response) {
                alert('Payment failed. ' + response.error.description);
                payBtn.disabled = false;
                payBtn.textContent = 'Pay & Generate Ticket';
            });
            rzp.open();

        } catch (err) {
            alert('Error during checkout: ' + err.message);
            payBtn.disabled = false;
            payBtn.textContent = 'Pay & Generate Ticket';
        }
    });
}