import logging
import os
import random
import string
import threading
from datetime import datetime

import razorpay
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template

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

# By default, Flask looks for templates in ./templates and static files in ./static.
app = Flask(__name__)

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

ALL_TRIPS = {t['id']: t for t in WEEKDAY_TRIPS + WEEKEND_TRIPS}

_booking_lock = threading.Lock()
seats_booked = {}
tickets = {}

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


# ---------------------------------------------------------------- api routes

@app.route('/api/trips')
def get_trips():
    # Provide the trip lists along with their current dynamic availability.
    # This avoids duplication of WEEKDAY_TRIPS and WEEKEND_TRIPS in the frontend JS.
    def enrich(trips_list):
        return [
            {
                **t,
                'available': seats_available(t['id']),
                'capacity': CAPACITY
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
    })

@app.route('/api/create-order', methods=['POST'])
def create_order():
    data = request.get_json(force=True)
    trip_id = data.get('tripId')

    trip = find_trip(trip_id)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404

    if seats_available(trip_id) <= 0:
        log.info('create-order rejected: trip=%s is full', trip_id)
        return jsonify({'error': 'This trip is fully booked'}), 409

    order = razorpay_client.order.create({
        'amount': TICKET_PRICE_PAISE,
        'currency': 'INR',
        'receipt': f'{trip_id}-{datetime.utcnow().timestamp():.0f}',
        'notes': {'tripId': trip_id},
    })

    log.info('order created: order_id=%s trip=%s amount=%s', order['id'], trip_id, TICKET_PRICE_PAISE)

    return jsonify({
        'orderId': order['id'],
        'amount': TICKET_PRICE_PAISE,
        'currency': 'INR',
        'keyId': RAZORPAY_KEY_ID,   # safe to send public key to frontend
    })

@app.route('/api/verify-and-book', methods=['POST'])
def verify_and_book():
    data = request.get_json(force=True)

    trip_id = data.get('tripId')
    name = (data.get('name') or '').strip()
    roll_no = (data.get('rollNo') or '').strip().upper()

    trip = find_trip(trip_id)
    if not trip or not name or not roll_no:
        return jsonify({'error': 'Missing or invalid booking details'}), 400

    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature'),
        })
    except razorpay.errors.SignatureVerificationError:
        log.warning('signature verification FAILED for order=%s', data.get('razorpay_order_id'))
        return jsonify({'error': 'Payment verification failed'}), 400

    if not try_reserve_seat(trip_id):
        log.error('SOLD OUT after payment: trip=%s payment=%s — issuing refund', trip_id, data.get('razorpay_payment_id'))
        razorpay_client.payment.refund(data.get('razorpay_payment_id'), {'amount': TICKET_PRICE_PAISE})
        return jsonify({'error': 'Seat sold out during payment. You have been refunded.'}), 409

    code = 'IIITDM' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    ticket = {
        'code': code,
        'name': name,
        'rollNo': roll_no,
        'route': trip['route'],
        'bus': trip['bus'],
        'time': trip['time'],
        'date': datetime.now().strftime('%a %b %d %Y'),
    }
    tickets[code] = ticket
    log.info('ticket issued: code=%s trip=%s roll=%s', code, trip_id, roll_no)

    return jsonify(ticket)

@app.route('/api/ticket/<code>')
def get_ticket(code):
    ticket = tickets.get(code)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    return jsonify(ticket)

if __name__ == '__main__':
    app.run(debug=True)
