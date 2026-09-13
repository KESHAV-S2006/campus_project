import logging
import os
import random
import string
from datetime import datetime, time as dtime
from functools import wraps

import razorpay
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

log = logging.getLogger('bus-booking')

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'test_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret')

OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'owner')
OWNER_PASSWORD = os.environ.get('OWNER_PASSWORD', 'changeme123')

CAPACITY = 32
TICKET_PRICE_PAISE = 2000

# ---------------------------------------------------------
# APP
# ---------------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    'FLASK_SECRET_KEY',
    'campusconnect-secret-key-change-this'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------
# RAZORPAY
# ---------------------------------------------------------

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)

# ---------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    bookings = db.relationship(
        'Booking',
        backref='user',
        lazy=True
    )


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(
        db.String(50),
        primary_key=True
    )

    bus = db.Column(
        db.Integer,
        nullable=False
    )

    route = db.Column(
        db.String(100),
        nullable=False
    )

    time = db.Column(
        db.String(10),
        nullable=False
    )

    purpose = db.Column(
        db.String(150),
        nullable=False
    )

    day_type = db.Column(
        db.String(20),
        nullable=False
    )

    is_last = db.Column(
        db.Boolean,
        default=False
    )

    capacity = db.Column(
        db.Integer,
        default=CAPACITY
    )

    bookings = db.relationship(
        'Booking',
        backref='trip',
        lazy=True
    )


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_code = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    trip_id = db.Column(
        db.String(50),
        db.ForeignKey('trips.id'),
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    roll_no = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default='valid'
    )

    order_id = db.Column(
        db.String(100)
    )

    payment_id = db.Column(
        db.String(100)
    )

    amount = db.Column(
        db.Integer,
        default=TICKET_PRICE_PAISE
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ---------------------------------------------------------
# TRIP DATA
# ---------------------------------------------------------

WEEKDAY_TRIPS = [
    {
        'id': 'wd-b1-1',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '15:40',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-2',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '16:30',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-3',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '17:15',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-4',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '18:00',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-5',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '19:00',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-6',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '19:40',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-7',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '20:20',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b1-8',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '21:00',
        'purpose': 'Staff/Student',
        'last': True
    },

    {
        'id': 'wd-b2-1',
        'bus': 2,
        'route': 'Institute→Sadar',
        'time': '15:00',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b2-2',
        'bus': 2,
        'route': 'Sadar→Institute',
        'time': '15:45',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b2-3',
        'bus': 2,
        'route': 'Institute→Sadar',
        'time': '18:00',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b2-4',
        'bus': 2,
        'route': 'Sadar→Institute',
        'time': '18:30',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b2-5',
        'bus': 2,
        'route': 'Institute→Sadar',
        'time': '20:50',
        'purpose': 'Staff/Student'
    },
    {
        'id': 'wd-b2-6',
        'bus': 2,
        'route': 'Sadar→Institute',
        'time': '21:30',
        'purpose': 'Staff/Student',
        'last': True
    }
]

WEEKEND_TRIPS = [
    {
        'id': 'we-b1-1',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '15:30',
        'purpose': 'via Russel Chowk'
    },
    {
        'id': 'we-b1-2',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '17:20',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b1-3',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '18:00',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b1-4',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '18:30',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b1-5',
        'bus': 1,
        'route': 'Institute→Sadar',
        'time': '19:00',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b1-6',
        'bus': 1,
        'route': 'Sadar→Institute',
        'time': '21:15',
        'purpose': 'via Russel Chowk',
        'last': True
    },

    {
        'id': 'we-b2-1',
        'bus': 2,
        'route': 'Institute→Sadar',
        'time': '15:00',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b2-2',
        'bus': 2,
        'route': 'Sadar→Institute',
        'time': '16:30',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b2-3',
        'bus': 2,
        'route': 'Institute→Sadar',
        'time': '17:30',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b2-4',
        'bus': 2,
        'route': 'Sadar→Institute',
        'time': '19:30',
        'purpose': 'via Russel Chowk'
    },
    {
        'id': 'we-b2-5',
        'bus': 2,
        'route': 'Institute→Sadar',
        'time': '20:50',
        'purpose': 'Direct'
    },
    {
        'id': 'we-b2-6',
        'bus': 2,
        'route': 'Sadar→Institute',
        'time': '21:30',
        'purpose': 'Direct',
        'last': True
    }
]

# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------

def initialize_database():

    db.create_all()

    for item in WEEKDAY_TRIPS:

        existing = Trip.query.get(item['id'])

        if not existing:

            trip = Trip(
                id=item['id'],
                bus=item['bus'],
                route=item['route'],
                time=item['time'],
                purpose=item['purpose'],
                day_type='weekday',
                is_last=item.get('last', False),
                capacity=CAPACITY
            )

            db.session.add(trip)

    for item in WEEKEND_TRIPS:

        existing = Trip.query.get(item['id'])

        if not existing:

            trip = Trip(
                id=item['id'],
                bus=item['bus'],
                route=item['route'],
                time=item['time'],
                purpose=item['purpose'],
                day_type='weekend',
                is_last=item.get('last', False),
                capacity=CAPACITY
            )

            db.session.add(trip)

    db.session.commit()


with app.app_context():
    initialize_database()


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def find_trip(trip_id):

    return Trip.query.get(trip_id)


def get_day_type(now=None):

    now = now or datetime.now()

    if now.weekday() >= 5:
        return 'weekend'

    return 'weekday'


def trip_departure_dt(trip, ref_date=None):

    ref_date = ref_date or datetime.now().date()

    h, m = map(int, trip.time.split(':'))

    return datetime.combine(
        ref_date,
        dtime(h, m)
    )


def is_trip_departed(trip, now=None):

    now = now or datetime.now()

    if trip.day_type != get_day_type(now):
        return True

    return now >= trip_departure_dt(
        trip,
        now.date()
    )


def is_trip_bookable(trip):

    now = datetime.now()

    if trip.day_type != get_day_type(now):
        return False, 'This trip does not run today.'

    if now >= trip_departure_dt(trip, now.date()):
        return False, 'This bus has already departed.'

    return True, None


def seats_booked_count(trip_id):

    return Booking.query.filter(
        Booking.trip_id == trip_id,
        Booking.status.in_(['valid', 'checked_in'])
    ).count()


def seats_available(trip_id):

    trip = find_trip(trip_id)

    if not trip:
        return 0

    booked = seats_booked_count(trip_id)

    return max(
        0,
        trip.capacity - booked
    )


def generate_ticket_code():

    while True:

        code = (
            'IIITDM' +
            ''.join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=6
                )
            )
        )

        if not Booking.query.filter_by(
            ticket_code=code
        ).first():

            return code


def get_current_user():

    user_id = session.get('user_id')

    if not user_id:
        return None

    return User.query.get(user_id)


# ---------------------------------------------------------
# AUTH DECORATOR
# ---------------------------------------------------------

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if not session.get('user_id'):

            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Please login first.'
                }), 401

            return redirect('/login.html')

        return f(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------

@app.errorhandler(404)
def handle_404(e):

    if request.path.startswith('/api/'):

        return jsonify({
            'error': 'Not found'
        }), 404

    return e


@app.errorhandler(500)
def handle_500(e):

    if request.path.startswith('/api/'):

        log.exception('Unhandled server error')

        return jsonify({
            'error': 'Internal server error'
        }), 500

    return e


# ---------------------------------------------------------
# FRONTEND ROUTES
# ---------------------------------------------------------

@app.route('/')
def serve_home():

    if not session.get('user_id'):
        return render_template('login.html')

    return render_template('home.html')


@app.route('/login.html')
def serve_login():

    return render_template('login.html')


@app.route('/avalableBUS.html')
@login_required
def serve_available_bus():

    return render_template('avalableBUS.html')


@app.route('/booking.html')
@login_required
def serve_booking():

    return render_template('booking.html')


@app.route('/ticket.html')
@login_required
def serve_ticket():

    return render_template('ticket.html')


@app.route('/owner.html')
def serve_owner():

    return render_template('owner.html')


# ---------------------------------------------------------
# USER LOGIN
# ---------------------------------------------------------

@app.route('/login', methods=['POST'])
def login_form():

    email = (
        request.form.get('email')
        or request.form.get('username')
        or ''
    ).strip().lower()
    password = request.form.get('password') or ''

    if not email or not password:
        return redirect('/login.html?error=empty')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return redirect('/login.html?error=invalid')

    session.clear()
    session['user_id'] = user.id
    session['email'] = user.email

    return redirect('/')


@app.route('/api/login', methods=['POST'])
def user_login():

    data = request.get_json(force=True) or {}

    email = (
        data.get('email')
        or data.get('username')
        or ''
    ).strip().lower()

    password = (
        data.get('password') or ''
    )

    if not email or not password:

        return jsonify({
            'error': 'Email and password are required.'
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:

        return jsonify({
            'error': 'Invalid email or password.'
        }), 401

    if not check_password_hash(
        user.password_hash,
        password
    ):

        return jsonify({
            'error': 'Invalid email or password.'
        }), 401

    session.clear()

    session['user_id'] = user.id
    session['email'] = user.email

    return jsonify({
        'success': True,
        'email': user.email
    })


@app.route('/api/logout', methods=['POST'])
def user_logout():

    session.clear()

    return jsonify({
        'success': True
    })


@app.route('/api/me')
def current_user():

    user = get_current_user()

    if not user:

        return jsonify({
            'loggedIn': False
        })

    return jsonify({
        'loggedIn': True,
        'id': user.id,
        'email': user.email
    })


# ---------------------------------------------------------
# TRIPS
# ---------------------------------------------------------

def trip_to_json(trip):

    return {
        'id': trip.id,
        'bus': trip.bus,
        'route': trip.route,
        'time': trip.time,
        'purpose': trip.purpose,
        'day_type': trip.day_type,
        'last': trip.is_last,
        'capacity': trip.capacity,
        'available': seats_available(trip.id),
        'departed': is_trip_departed(trip)
    }


@app.route('/api/trips')
@login_required
def get_trips():

    weekday = Trip.query.filter_by(
        day_type='weekday'
    ).all()

    weekend = Trip.query.filter_by(
        day_type='weekend'
    ).all()

    return jsonify({

        'weekday': [
            trip_to_json(t)
            for t in weekday
        ],

        'weekend': [
            trip_to_json(t)
            for t in weekend
        ]

    })


@app.route('/api/trip/<trip_id>')
@login_required
def get_trip(trip_id):

    trip = find_trip(trip_id)

    if not trip:

        return jsonify({
            'error': 'Trip not found'
        }), 404

    return jsonify(
        trip_to_json(trip)
    )


# ---------------------------------------------------------
# CREATE RAZORPAY ORDER
# ---------------------------------------------------------

@app.route('/api/create-order', methods=['POST'])
@login_required
def create_order():

    try:

        data = request.get_json(force=True) or {}

        trip_id = data.get('tripId')

        roll_no = (
            data.get('rollNo') or ''
        ).strip().upper()

        if not trip_id or not roll_no:

            return jsonify({
                'error': 'tripId and rollNo are required.'
            }), 400

        trip = find_trip(trip_id)

        if not trip:

            return jsonify({
                'error': 'Trip not found.'
            }), 404

        bookable, reason = is_trip_bookable(trip)

        if not bookable:

            return jsonify({
                'error': reason
            }), 409

        # -------------------------------------------------
        # CHECK SEATS
        # -------------------------------------------------

        if seats_available(trip_id) <= 0:

            return jsonify({
                'error': 'This trip is fully booked.'
            }), 409

        # -------------------------------------------------
        # CHECK SAME USER + SAME TRIP
        # -------------------------------------------------

        user_id = session['user_id']

        existing = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.trip_id == trip_id,
            Booking.status.in_([
                'valid',
                'checked_in'
            ])
        ).first()

        if existing:

            return jsonify({
                'error':
                    f'You already booked this trip '
                    f'({existing.ticket_code}). '
                    f'Cancel it before booking this trip again.'
            }), 409

        # -------------------------------------------------
        # CHECK SAME ROLL NUMBER FOR THIS TRIP
        # -------------------------------------------------

        existing_roll = Booking.query.filter(
            Booking.trip_id == trip_id,
            Booking.roll_no == roll_no,
            Booking.status.in_([
                'valid',
                'checked_in'
            ])
        ).first()

        if existing_roll:

            return jsonify({
                'error':
                    'This roll number already has a ticket '
                    'for this trip.'
            }), 409

        # -------------------------------------------------
        # RAZORPAY ORDER
        # -------------------------------------------------

        order = razorpay_client.order.create({

            'amount': TICKET_PRICE_PAISE,

            'currency': 'INR',

            'receipt':
                f'{trip_id}-{datetime.utcnow().timestamp():.0f}',

            'notes': {
                'tripId': trip_id,
                'rollNo': roll_no,
                'userId': str(user_id)
            }
        })

        return jsonify({

            'orderId': order['id'],

            'amount': TICKET_PRICE_PAISE,

            'currency': 'INR',

            'keyId': RAZORPAY_KEY_ID
        })

    except razorpay.errors.BadRequestError as e:

        log.exception(
            'Razorpay rejected order'
        )

        return jsonify({
            'error': f'Razorpay error: {str(e)}'
        }), 400

    except Exception:

        log.exception(
            'create_order failed'
        )

        return jsonify({
            'error':
                'Could not create payment order.'
        }), 500


# ---------------------------------------------------------
# VERIFY PAYMENT + CREATE BOOKING
# ---------------------------------------------------------

@app.route('/api/verify-and-book', methods=['POST'])
@login_required
def verify_and_book():

    try:

        data = request.get_json(force=True)

        if not data:

            return jsonify({
                'error': 'Invalid request body.'
            }), 400

        trip_id = data.get('tripId')

        name = (
            data.get('name') or ''
        ).strip()

        roll_no = (
            data.get('rollNo') or ''
        ).strip().upper()

        payment_id = data.get(
            'razorpay_payment_id'
        )

        order_id = data.get(
            'razorpay_order_id'
        )

        signature = data.get(
            'razorpay_signature'
        )

        trip = find_trip(trip_id)

        if not trip or not name or not roll_no:

            return jsonify({
                'error':
                    'Missing or invalid booking details.'
            }), 400

        # -------------------------------------------------
        # VERIFY RAZORPAY SIGNATURE
        # -------------------------------------------------

        try:

            razorpay_client.utility.verify_payment_signature({

                'razorpay_order_id':
                    order_id,

                'razorpay_payment_id':
                    payment_id,

                'razorpay_signature':
                    signature

            })

        except razorpay.errors.SignatureVerificationError:

            return jsonify({
                'error':
                    'Payment verification failed.'
            }), 400

        # -------------------------------------------------
        # CHECK TRIP
        # -------------------------------------------------

        bookable, reason = is_trip_bookable(trip)

        if not bookable:

            _safe_refund(payment_id)

            return jsonify({
                'error':
                    f'{reason} You have been refunded.'
            }), 409

        # -------------------------------------------------
        # CHECK SEAT AGAIN
        # -------------------------------------------------

        if seats_available(trip_id) <= 0:

            _safe_refund(payment_id)

            return jsonify({
                'error':
                    'Seat sold out during payment. '
                    'You have been refunded.'
            }), 409

        # -------------------------------------------------
        # CHECK SAME USER + SAME TRIP AGAIN
        # -------------------------------------------------

        user_id = session['user_id']

        existing = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.trip_id == trip_id,
            Booking.status.in_([
                'valid',
                'checked_in'
            ])
        ).first()

        if existing:

            _safe_refund(payment_id)

            return jsonify({
                'error':
                    f'You already have ticket '
                    f'{existing.ticket_code}. '
                    f'You have been refunded.'
            }), 409

        # -------------------------------------------------
        # CHECK ROLL NUMBER AGAIN
        # -------------------------------------------------

        existing_roll = Booking.query.filter(
            Booking.trip_id == trip_id,
            Booking.roll_no == roll_no,
            Booking.status.in_([
                'valid',
                'checked_in'
            ])
        ).first()

        if existing_roll:

            _safe_refund(payment_id)

            return jsonify({
                'error':
                    'This roll number already has a '
                    'ticket for this trip. '
                    'You have been refunded.'
            }), 409

        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------

        ticket_code = generate_ticket_code()

        booking = Booking(

            ticket_code=ticket_code,

            user_id=user_id,

            trip_id=trip_id,

            name=name,

            roll_no=roll_no,

            status='valid',

            order_id=order_id,

            payment_id=payment_id,

            amount=TICKET_PRICE_PAISE
        )

        db.session.add(booking)

        db.session.commit()

        log.info(
            'Ticket created: %s',
            ticket_code
        )

        return jsonify(
            public_ticket(booking)
        )

    except Exception:

        db.session.rollback()

        log.exception(
            'verify_and_book failed'
        )

        return jsonify({
            'error':
                'Booking failed due to a server error.'
        }), 500


# ---------------------------------------------------------
# REFUND
# ---------------------------------------------------------

def _safe_refund(payment_id):

    if not payment_id:
        return

    try:

        razorpay_client.payment.refund(
            payment_id,
            {
                'amount':
                    TICKET_PRICE_PAISE
            }
        )

    except Exception:

        log.exception(
            'Refund failed for payment=%s',
            payment_id
        )


# ---------------------------------------------------------
# PUBLIC TICKET
# ---------------------------------------------------------

def public_ticket(booking):

    return {

        'code':
            booking.ticket_code,

        'name':
            booking.name,

        'rollNo':
            booking.roll_no,

        'tripId':
            booking.trip_id,

        'route':
            booking.trip.route,

        'bus':
            booking.trip.bus,

        'time':
            booking.trip.time,

        'date':
            booking.booking_date.strftime(
                '%a %b %d %Y'
            ),

        'status':
            booking.status
    }


# ---------------------------------------------------------
# MY TICKETS
# ---------------------------------------------------------

@app.route('/api/my-tickets')
@login_required
def my_tickets():

    user_id = session['user_id']

    bookings = Booking.query.filter(
        Booking.user_id == user_id
    ).order_by(
        Booking.booking_date.desc()
    ).all()

    return jsonify({

        'tickets': [
            public_ticket(b)
            for b in bookings
        ]

    })


# ---------------------------------------------------------
# SINGLE TICKET
# ---------------------------------------------------------

@app.route('/api/ticket/<code>')
@login_required
def get_ticket(code):

    code = code.strip().upper()

    booking = Booking.query.filter_by(
        ticket_code=code
    ).first()

    if not booking:

        return jsonify({
            'error': 'Ticket not found.'
        }), 404

    # IMPORTANT:
    # Student can only see their own ticket.

    if booking.user_id != session['user_id']:

        return jsonify({
            'error': 'You are not authorized to view this ticket.'
        }), 403

    return jsonify(
        public_ticket(booking)
    )


# ---------------------------------------------------------
# CANCEL TICKET
# ---------------------------------------------------------

@app.route('/api/cancel-ticket', methods=['POST'])
@login_required
def cancel_ticket():

    try:

        data = request.get_json(force=True) or {}

        code = (
            data.get('code') or ''
        ).strip().upper()

        if not code:

            return jsonify({
                'error': 'Ticket code is required.'
            }), 400

        booking = Booking.query.filter_by(
            ticket_code=code
        ).first()

        if not booking:

            return jsonify({
                'error': 'Ticket not found.'
            }), 404

        # -------------------------------------------------
        # OWNER CHECK
        # -------------------------------------------------

        if booking.user_id != session['user_id']:

            return jsonify({
                'error':
                    'You cannot cancel another user\'s ticket.'
            }), 403

        # -------------------------------------------------
        # STATUS CHECK
        # -------------------------------------------------

        if booking.status == 'cancelled':

            return jsonify({
                'error':
                    'This ticket is already cancelled.'
            }), 409

        if booking.status == 'checked_in':

            return jsonify({
                'error':
                    'This ticket has already been checked in '
                    'and cannot be cancelled.'
            }), 409

        trip = booking.trip

        # -------------------------------------------------
        # DEPARTURE CHECK
        # -------------------------------------------------

        if trip and is_trip_departed(trip):

            return jsonify({
                'error':
                    'Cannot cancel — this bus has already departed.'
            }), 409

        # -------------------------------------------------
        # REFUND
        # -------------------------------------------------

        try:

            razorpay_client.payment.refund(
                booking.payment_id,
                {
                    'amount':
                        booking.amount
                }
            )

        except Exception:

            log.exception(
                'Refund failed for ticket=%s',
                code
            )

            return jsonify({
                'error':
                    'Refund could not be processed. '
                    'Please contact support.'
            }), 500

        # -------------------------------------------------
        # CANCEL
        # -------------------------------------------------

        booking.status = 'cancelled'

        db.session.commit()

        log.info(
            'Ticket cancelled: %s',
            code
        )

        return jsonify({

            'success': True,

            'message':
                'Ticket cancelled. '
                'Refund has been initiated.'
        })

    except Exception:

        db.session.rollback()

        log.exception(
            'cancel_ticket failed'
        )

        return jsonify({
            'error':
                'Server error while cancelling ticket.'
        }), 500


# ---------------------------------------------------------
# OWNER LOGIN
# ---------------------------------------------------------

def owner_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if not session.get('is_owner'):

            return jsonify({
                'error':
                    'Not authorized. Please log in.'
            }), 401

        return f(*args, **kwargs)

    return wrapper


@app.route('/api/owner/login', methods=['POST'])
def owner_login():

    data = request.get_json(force=True) or {}

    username = data.get('username')
    password = data.get('password')

    if (
        username == OWNER_USERNAME
        and
        password == OWNER_PASSWORD
    ):

        session['is_owner'] = True

        return jsonify({
            'success': True
        })

    return jsonify({
        'error':
            'Invalid username or password.'
    }), 401


@app.route('/api/owner/logout', methods=['POST'])
def owner_logout():

    session.pop(
        'is_owner',
        None
    )

    return jsonify({
        'success': True
    })


@app.route('/api/owner/status')
def owner_status():

    return jsonify({

        'loggedIn':
            bool(
                session.get(
                    'is_owner'
                )
            )

    })


# ---------------------------------------------------------
# OWNER TICKETS
# ---------------------------------------------------------

@app.route('/api/owner/tickets')
@owner_required
def owner_tickets():

    bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).all()

    grouped = {}

    for booking in bookings:

        trip = booking.trip

        key = booking.trip_id

        if key not in grouped:

            grouped[key] = {

                'tripId':
                    key,

                'route':
                    trip.route,

                'bus':
                    trip.bus,

                'time':
                    trip.time,

                'dayType':
                    trip.day_type,

                'passengers':
                    []

            }

        grouped[key]['passengers'].append({

            'code':
                booking.ticket_code,

            'name':
                booking.name,

            'rollNo':
                booking.roll_no,

            'status':
                booking.status

        })

    result = sorted(
        grouped.values(),
        key=lambda x: x['time']
    )

    return jsonify({

        'trips':
            result

    })


# ---------------------------------------------------------
# OWNER CHECK-IN
# ---------------------------------------------------------

@app.route('/api/owner/checkin', methods=['POST'])
@owner_required
def owner_checkin():

    data = request.get_json(force=True) or {}

    code = (
        data.get('code') or ''
    ).strip().upper()

    booking = Booking.query.filter_by(
        ticket_code=code
    ).first()

    if not booking:

        return jsonify({
            'error':
                'Ticket not found.'
        }), 404

    if booking.status == 'cancelled':

        return jsonify({
            'error':
                'This ticket was cancelled and '
                'cannot be checked in.'
        }), 409

    if booking.status == 'checked_in':

        return jsonify({
            'error':
                'This ticket is already checked in.'
        }), 409

    booking.status = 'checked_in'

    db.session.commit()

    return jsonify({
        'success': True
    })


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == '__main__':

    app.run(
        debug=True
    )