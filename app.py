import logging
import os
import random
import string
import threading
from datetime import datetime, time as dtime
from functools import wraps

import razorpay
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, session

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('bus-booking')

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'test_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret')

if RAZORPAY_KEY_ID == 'test_key' or RAZORPAY_KEY_SECRET == 'test_secret':
    logging.warning(
        'RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET is not set — using placeholder values. '
        'Set these in a .env file before accepting real payments.'
    )

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Bus operator / owner login. Set these in .env — do not ship the defaults.
OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'owner')
OWNER_PASSWORD = os.environ.get('OWNER_PASSWORD', 'changeme123')

if OWNER_USERNAME == 'owner' and OWNER_PASSWORD == 'changeme123':
    logging.warning(
        'OWNER_USERNAME / OWNER_PASSWORD are not set — using placeholder owner credentials. '
        'Set these in your .env file before deploying.'
    )

# By default, Flask looks for templates in ./templates and static files in ./static.
app = Flask(__name__)

# Session signing key. A random one is generated per-process if not set, which means
# owner sessions won't survive a server restart unless FLASK_SECRET_KEY is set in .env.
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or ''.join(
    random.choices(string.ascii_letters + string.digits, k=32)
)

# ---------------------------------------------------------------- data & state

CAPACITY = 32
TICKET_PRICE_PAISE = 2000  # ₹20

WEEKDAY_TRIPS = [
    {'id': 'wd-b1-1', 'bus': 1, 'route': 'Institute→Sadar', 'time': '15:40', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-2', 'bus': 1, 'route': 'Sadar→Institute', 'time': '16:30', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-3', 'bus': 1, 'route': 'Institute→Sadar', 'time': '17:15', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-4', 'bus': 1, 'route': 'Sadar→Institute', 'time': '18:00', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-5', 'bus': 1, 'route': 'Institute→Sadar', 'time': '19:00', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-6', 'bus': 1, 'route': 'Sadar→Institute', 'time': '19:40', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-7', 'bus': 1, 'route': 'Institute→Sadar', 'time': '20:20', 'purpose': 'Staff/Student'},
    {'id': 'wd-b1-8', 'bus': 1, 'route': 'Sadar→Institute', 'time': '21:00', 'purpose': 'Staff/Student', 'last': True},

    {'id': 'wd-b2-1', 'bus': 2, 'route': 'Institute→Sadar', 'time': '15:00', 'purpose': 'Staff/Student'},
    {'id': 'wd-b2-2', 'bus': 2, 'route': 'Sadar→Institute', 'time': '15:45', 'purpose': 'Staff/Student'},
    {'id': 'wd-b2-3', 'bus': 2, 'route': 'Institute→Sadar', 'time': '18:00', 'purpose': 'Staff/Student'},
    {'id': 'wd-b2-4', 'bus': 2, 'route': 'Sadar→Institute', 'time': '18:30', 'purpose': 'Staff/Student'},
    {'id': 'wd-b2-5', 'bus': 2, 'route': 'Institute→Sadar', 'time': '20:50', 'purpose': 'Staff/Student'},
    {'id': 'wd-b2-6', 'bus': 2, 'route': 'Sadar→Institute', 'time': '21:30', 'purpose': 'Staff/Student', 'last': True},
]

WEEKEND_TRIPS = [
    {'id': 'we-b1-1', 'bus': 1, 'route': 'Institute→Sadar', 'time': '15:30', 'purpose': 'via Russel Chowk'},
    {'id': 'we-b1-2', 'bus': 1, 'route': 'Sadar→Institute', 'time': '17:20', 'purpose': 'Direct'},
    {'id': 'we-b1-3', 'bus': 1, 'route': 'Institute→Sadar', 'time': '18:00', 'purpose': 'Direct'},
    {'id': 'we-b1-4', 'bus': 1, 'route': 'Sadar→Institute', 'time': '18:30', 'purpose': 'Direct'},
    {'id': 'we-b1-5', 'bus': 1, 'route': 'Institute→Sadar', 'time': '19:00', 'purpose': 'Direct'},
    {'id': 'we-b1-6', 'bus': 1, 'route': 'Sadar→Institute', 'time': '21:15', 'purpose': 'via Russel Chowk', 'last': True},

    {'id': 'we-b2-1', 'bus': 2, 'route': 'Institute→Sadar', 'time': '15:00', 'purpose': 'Direct'},
    {'id': 'we-b2-2', 'bus': 2, 'route': 'Sadar→Institute', 'time': '16:30', 'purpose': 'Direct'},
    {'id': 'we-b2-3', 'bus': 2, 'route': 'Institute→Sadar', 'time': '17:30', 'purpose': 'Direct'},
    {'id': 'we-b2-4', 'bus': 2, 'route': 'Sadar→Institute', 'time': '19:30', 'purpose': 'via Russel Chowk'},
    {'id': 'we-b2-5', 'bus': 2, 'route': 'Institute→Sadar', 'time': '20:50', 'purpose': 'Direct'},
    {'id': 'we-b2-6', 'bus': 2, 'route': 'Sadar→Institute', 'time': '21:30', 'purpose': 'Direct', 'last': True},
]

# Tag each trip with which kind of day it runs on, so the backend (not just the
# frontend) can refuse bookings for the wrong day or after departure.
for _t in WEEKDAY_TRIPS:
    _t['day_type'] = 'weekday'
for _t in WEEKEND_TRIPS:
    _t['day_type'] = 'weekend'

ALL_TRIPS = {t['id']: t for t in WEEKDAY_TRIPS + WEEKEND_TRIPS}

_booking_lock = threading.Lock()
seats_booked = {}      # trip_id -> count
tickets = {}            # code -> ticket dict
active_by_roll = {}     # rollNo -> ticket code (one active ticket per person)


def find_trip(trip_id):
    return ALL_TRIPS.get(trip_id)


def seats_available(trip_id):
    with _booking_lock:
        return CAPACITY - seats_booked.get(trip_id, 0)


def try_reserve_seat(trip_id):
    with _booking_lock:
        taken = seats_booked.get(trip_id, 0)
        if taken >= CAPACITY:
            return False
        seats_booked[trip_id] = taken + 1
        return True


def release_seat(trip_id):
    with _booking_lock:
        if seats_booked.get(trip_id, 0) > 0:
            seats_booked[trip_id] -= 1


def get_day_type(now=None):
    now = now or datetime.now()
    return 'weekend' if now.weekday() >= 5 else 'weekday'  # Mon=0 ... Sat=5, Sun=6


def trip_departure_dt(trip, ref_date=None):
    ref_date = ref_date or datetime.now().date()
    h, m = map(int, trip['time'].split(':'))
    return datetime.combine(ref_date, dtime(h, m))


def is_trip_departed(trip, now=None):
    """True if this trip's slot for 'today' is over or doesn't apply to today at all."""
    now = now or datetime.now()
    if trip['day_type'] != get_day_type(now):
        return True
    return now >= trip_departure_dt(trip, now.date())


def is_trip_bookable(trip):
    """Returns (ok: bool, reason: str|None)."""
    now = datetime.now()
    if trip['day_type'] != get_day_type(now):
        return False, 'This trip does not run today.'
    if now >= trip_departure_dt(trip, now.date()):
        return False, 'This bus has already departed.'
    return True, None


def roll_has_active_ticket(roll_no):
    """Enforces one active ticket per roll number. A ticket stops being 'active'
    once it's cancelled/checked-in, or once its trip has departed."""
    code = active_by_roll.get(roll_no)
    if not code:
        return False, None
    ticket = tickets.get(code)
    if not ticket or ticket.get('status') != 'valid':
        active_by_roll.pop(roll_no, None)
        return False, None
    trip = find_trip(ticket['tripId'])
    if trip and is_trip_departed(trip):
        active_by_roll.pop(roll_no, None)
        return False, None
    return True, code


# ---------------------------------------------------------------- error handlers

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return e


@app.errorhandler(500)
def handle_500(e):
    if request.path.startswith('/api/'):
        log.exception('Unhandled server error')
        return jsonify({'error': 'Internal server error'}), 500
    return e


# ---------------------------------------------------------------- frontend routes

@app.route('/')
def serve_home():
    return render_template('home.html')


@app.route('/avalableBUS.html')
def serve_available_bus():
    return render_template('avalableBUS.html')


@app.route('/booking.html')
def serve_booking():
    return render_template('booking.html')


@app.route('/ticket.html')
def serve_ticket():
    return render_template('ticket.html')


@app.route('/owner.html')
def serve_owner():
    return render_template('owner.html')


# ---------------------------------------------------------------- api routes

@app.route('/api/trips')
def get_trips():
    def enrich(trips_list):
        return [
            {
                **t,
                'available': seats_available(t['id']),
                'capacity': CAPACITY,
                'departed': is_trip_departed(t),
            }
            for t in trips_list
        ]

    return jsonify({
        'weekday': enrich(WEEKDAY_TRIPS),
        'weekend': enrich(WEEKEND_TRIPS)
    })


@app.route('/api/trip/<trip_id>')
def get_trip(trip_id):
    trip = find_trip(trip_id)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404

    return jsonify({
        **trip,
        'capacity': CAPACITY,
        'seatsAvailable': seats_available(trip_id),
        'departed': is_trip_departed(trip),
    })


@app.route('/api/create-order', methods=['POST'])
def create_order():
    try:
        data = request.get_json(force=True) or {}
        trip_id = data.get('tripId')
        roll_no = (data.get('rollNo') or '').strip().upper()

        if not trip_id or not roll_no:
            return jsonify({'error': 'tripId and rollNo are required'}), 400

        trip = find_trip(trip_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        bookable, reason = is_trip_bookable(trip)
        if not bookable:
            return jsonify({'error': reason}), 409

        if seats_available(trip_id) <= 0:
            log.info('create-order rejected: trip=%s is full', trip_id)
            return jsonify({'error': 'This trip is fully booked'}), 409

        has_active, existing_code = roll_has_active_ticket(roll_no)
        if has_active:
            return jsonify({
                'error': f'You already have an active ticket ({existing_code}). '
                         'Cancel it or wait until that bus departs before booking another.'
            }), 409

        order = razorpay_client.order.create({
            'amount': TICKET_PRICE_PAISE,
            'currency': 'INR',
            'receipt': f'{trip_id}-{datetime.utcnow().timestamp():.0f}',
            'notes': {'tripId': trip_id, 'rollNo': roll_no},
        })

        log.info('order created: order_id=%s trip=%s amount=%s', order['id'], trip_id, TICKET_PRICE_PAISE)

        return jsonify({
            'orderId': order['id'],
            'amount': TICKET_PRICE_PAISE,
            'currency': 'INR',
            'keyId': RAZORPAY_KEY_ID,
        })

    except razorpay.errors.BadRequestError as e:
        log.exception('Razorpay rejected the order request')
        return jsonify({'error': f'Razorpay error: {str(e)}'}), 400

    except Exception:
        log.exception('create_order failed unexpectedly')
        return jsonify({'error': 'Could not create order. Check server logs / Razorpay credentials.'}), 500


@app.route('/api/verify-and-book', methods=['POST'])
def verify_and_book():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'Invalid request body'}), 400

        trip_id = data.get('tripId')
        name = (data.get('name') or '').strip()
        roll_no = (data.get('rollNo') or '').strip().upper()
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')

        trip = find_trip(trip_id)
        if not trip or not name or not roll_no:
            return jsonify({'error': 'Missing or invalid booking details'}), 400

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': data.get('razorpay_signature'),
            })
        except razorpay.errors.SignatureVerificationError:
            log.warning('signature verification FAILED for order=%s', order_id)
            return jsonify({'error': 'Payment verification failed'}), 400

        # Re-check departure & one-ticket rule in case time passed / a race happened
        # while the payment popup was open. Refund if we now have to reject.
        bookable, reason = is_trip_bookable(trip)
        if not bookable:
            log.warning('trip no longer bookable after payment: trip=%s payment=%s — refunding', trip_id, payment_id)
            _safe_refund(payment_id)
            return jsonify({'error': f'{reason} You have been refunded.'}), 409

        has_active, existing_code = roll_has_active_ticket(roll_no)
        if has_active:
            log.warning('roll %s already has ticket %s — refunding duplicate payment', roll_no, existing_code)
            _safe_refund(payment_id)
            return jsonify({'error': f'You already have an active ticket ({existing_code}). You have been refunded.'}), 409

        if not try_reserve_seat(trip_id):
            log.error('SOLD OUT after payment: trip=%s payment=%s — issuing refund', trip_id, payment_id)
            _safe_refund(payment_id)
            return jsonify({'error': 'Seat sold out during payment. You have been refunded.'}), 409

        code = 'IIITDM' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        ticket = {
            'code': code,
            'name': name,
            'rollNo': roll_no,
            'tripId': trip_id,
            'route': trip['route'],
            'bus': trip['bus'],
            'time': trip['time'],
            'date': datetime.now().strftime('%a %b %d %Y'),
            'status': 'valid',           # valid | cancelled | checked_in
            'orderId': order_id,
            'paymentId': payment_id,
            'amount': TICKET_PRICE_PAISE,
        }
        tickets[code] = ticket
        active_by_roll[roll_no] = code
        log.info('ticket issued: code=%s trip=%s roll=%s', code, trip_id, roll_no)

        return jsonify(_public_ticket(ticket))

    except Exception:
        log.exception('verify_and_book failed unexpectedly')
        return jsonify({'error': 'Booking failed due to a server error.'}), 500


def _safe_refund(payment_id):
    if not payment_id:
        return
    try:
        razorpay_client.payment.refund(payment_id, {'amount': TICKET_PRICE_PAISE})
    except Exception:
        log.exception('Refund attempt failed for payment=%s', payment_id)


def _public_ticket(ticket):
    """Strip internal payment fields before sending a ticket to the browser."""
    return {
        'code': ticket['code'],
        'name': ticket['name'],
        'rollNo': ticket['rollNo'],
        'route': ticket['route'],
        'bus': ticket['bus'],
        'time': ticket['time'],
        'date': ticket['date'],
        'status': ticket['status'],
    }


@app.route('/api/ticket/<code>')
def get_ticket(code):
    ticket = tickets.get(code.strip().upper())
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    return jsonify(_public_ticket(ticket))


@app.route('/api/cancel-ticket', methods=['POST'])
def cancel_ticket():
    try:
        data = request.get_json(force=True) or {}
        code = (data.get('code') or '').strip().upper()
        ticket = tickets.get(code)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        if ticket['status'] == 'cancelled':
            return jsonify({'error': 'This ticket is already cancelled'}), 409
        if ticket['status'] == 'checked_in':
            return jsonify({'error': 'This ticket has already been checked in and cannot be cancelled'}), 409

        trip = find_trip(ticket['tripId'])
        if trip and is_trip_departed(trip):
            return jsonify({'error': 'Cannot cancel — this bus has already departed.'}), 409

        try:
            razorpay_client.payment.refund(ticket['paymentId'], {'amount': ticket['amount']})
        except Exception:
            log.exception('Refund failed for payment=%s (ticket=%s)', ticket['paymentId'], code)
            return jsonify({'error': 'Refund could not be processed. Please contact support.'}), 500

        ticket['status'] = 'cancelled'
        release_seat(ticket['tripId'])
        active_by_roll.pop(ticket['rollNo'], None)
        log.info('ticket cancelled & refunded: code=%s', code)

        return jsonify({'success': True, 'message': 'Ticket cancelled. Refund has been initiated.'})

    except Exception:
        log.exception('cancel_ticket failed unexpectedly')
        return jsonify({'error': 'Server error while cancelling the ticket.'}), 500


# ---------------------------------------------------------------- owner (bus operator) routes

def owner_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_owner'):
            return jsonify({'error': 'Not authorized. Please log in.'}), 401
        return f(*args, **kwargs)
    return wrapper


@app.route('/api/owner/login', methods=['POST'])
def owner_login():
    data = request.get_json(force=True) or {}
    if data.get('username') == OWNER_USERNAME and data.get('password') == OWNER_PASSWORD:
        session['is_owner'] = True
        log.info('owner logged in')
        return jsonify({'success': True})
    log.warning('failed owner login attempt for username=%r', data.get('username'))
    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/api/owner/logout', methods=['POST'])
def owner_logout():
    session.pop('is_owner', None)
    return jsonify({'success': True})


@app.route('/api/owner/status')
def owner_status():
    return jsonify({'loggedIn': bool(session.get('is_owner'))})


@app.route('/api/owner/tickets')
@owner_required
def owner_tickets():
    grouped = {}
    for code, t in tickets.items():
        trip = find_trip(t['tripId'])
        key = t['tripId']
        if key not in grouped:
            grouped[key] = {
                'tripId': key,
                'route': trip['route'] if trip else 'Unknown route',
                'bus': trip['bus'] if trip else '?',
                'time': trip['time'] if trip else '??:??',
                'dayType': trip['day_type'] if trip else '?',
                'passengers': [],
            }
        grouped[key]['passengers'].append({
            'code': code,
            'name': t['name'],
            'rollNo': t['rollNo'],
            'status': t['status'],
        })

    result = sorted(grouped.values(), key=lambda g: g['time'])
    return jsonify({'trips': result})


@app.route('/api/owner/checkin', methods=['POST'])
@owner_required
def owner_checkin():
    data = request.get_json(force=True) or {}
    code = (data.get('code') or '').strip().upper()
    ticket = tickets.get(code)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    if ticket['status'] == 'cancelled':
        return jsonify({'error': 'This ticket was cancelled and cannot be checked in'}), 409
    ticket['status'] = 'checked_in'
    log.info('passenger checked in: code=%s', code)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
