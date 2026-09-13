import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta

from app import app, Booking, Trip, db, reset_database_if_needed


class DailyResetTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_path = os.path.join(self.temp_dir.name, 'db_reset_state.json')
        app.config['TESTING'] = True
        app.DB_RESET_STATE_PATH = self.state_path

        with app.app_context():
            db.drop_all()
            db.create_all()
            trip = Trip(
                id='test-trip-1',
                bus=1,
                route='Institute→Sadar',
                time='15:40',
                purpose='Test',
                day_type='weekday',
                capacity=32,
            )
            db.session.add(trip)
            booking = Booking(
                ticket_code='TEST-001',
                user_id=1,
                trip_id='test-trip-1',
                name='Test Student',
                roll_no='TEST-001',
            )
            db.session.add(booking)
            db.session.commit()

            with open(self.state_path, 'w', encoding='utf-8') as state_file:
                json.dump({'last_reset_date': (datetime.now().date() - timedelta(days=1)).isoformat()}, state_file)

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        self.temp_dir.cleanup()

    def test_reset_database_if_needed_clears_old_bookings_and_rebuilds_trips(self):
        with app.app_context():
            reset_database_if_needed()
            self.assertEqual(Booking.query.count(), 0)
            self.assertGreater(Trip.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
