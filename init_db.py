from werkzeug.security import generate_password_hash

from app import app, db, User, Trip

STUDENTS = [
{"email": "25bcs200@iiitdmj.ac.in", "password": "campus@200"},
{"email": "25bcs201@iiitdmj.ac.in", "password": "campus@201"},
{"email": "25bcs202@iiitdmj.ac.in", "password": "campus@202"},
{"email": "25bcs203@iiitdmj.ac.in", "password": "campus@203"},
{"email": "25bcs204@iiitdmj.ac.in", "password": "campus@204"},
{"email": "25bcs205@iiitdmj.ac.in", "password": "campus@205"},
{"email": "25bcs206@iiitdmj.ac.in", "password": "campus@206"},
{"email": "25bcs207@iiitdmj.ac.in", "password": "campus@207"},
{"email": "25bcs208@iiitdmj.ac.in", "password": "campus@208"},
{"email": "25bcs209@iiitdmj.ac.in", "password": "campus@209"},
{"email": "25bcs210@iiitdmj.ac.in", "password": "campus@210"},
{"email": "25bcs211@iiitdmj.ac.in", "password": "campus@211"},
{"email": "25bcs212@iiitdmj.ac.in", "password": "campus@212"},
{"email": "25bcs213@iiitdmj.ac.in", "password": "campus@213"},
{"email": "25bcs214@iiitdmj.ac.in", "password": "campus@214"},
{"email": "25bcs215@iiitdmj.ac.in", "password": "campus@215"},
{"email": "25bcs216@iiitdmj.ac.in", "password": "campus@216"},
{"email": "25bcs217@iiitdmj.ac.in", "password": "campus@217"},
{"email": "25bcs218@iiitdmj.ac.in", "password": "campus@218"},
{"email": "25bcs219@iiitdmj.ac.in", "password": "campus@219"},
{"email": "25bcs220@iiitdmj.ac.in", "password": "campus@220"},
{"email": "25bcs221@iiitdmj.ac.in", "password": "campus@221"},
{"email": "25bcs222@iiitdmj.ac.in", "password": "campus@222"},
{"email": "25bcs223@iiitdmj.ac.in", "password": "campus@223"},
{"email": "25bcs224@iiitdmj.ac.in", "password": "campus@224"},
{"email": "25bcs225@iiitdmj.ac.in", "password": "campus@225"},
{"email": "25bcs226@iiitdmj.ac.in", "password": "campus@226"},
{"email": "25bcs227@iiitdmj.ac.in", "password": "campus@227"},
{"email": "25bcs228@iiitdmj.ac.in", "password": "campus@228"},
{"email": "25bcs229@iiitdmj.ac.in", "password": "campus@229"},
{"email": "25bcs230@iiitdmj.ac.in", "password": "campus@230"},
{"email": "25bcs231@iiitdmj.ac.in", "password": "campus@231"},
{"email": "25bcs232@iiitdmj.ac.in", "password": "campus@232"},
{"email": "25bcs233@iiitdmj.ac.in", "password": "campus@233"},
{"email": "25bcs234@iiitdmj.ac.in", "password": "campus@234"},
{"email": "25bcs235@iiitdmj.ac.in", "password": "campus@235"},
{"email": "25bcs236@iiitdmj.ac.in", "password": "campus@236"},
{"email": "25bcs237@iiitdmj.ac.in", "password": "campus@237"},
{"email": "25bcs238@iiitdmj.ac.in", "password": "campus@238"},
{"email": "25bcs239@iiitdmj.ac.in", "password": "campus@239"},
{"email": "25bcs240@iiitdmj.ac.in", "password": "campus@240"},
{"email": "25bcs241@iiitdmj.ac.in", "password": "campus@241"},
{"email": "25bcs242@iiitdmj.ac.in", "password": "campus@242"},
{"email": "25bcs243@iiitdmj.ac.in", "password": "campus@243"},
{"email": "25bcs244@iiitdmj.ac.in", "password": "campus@244"},
{"email": "25bcs245@iiitdmj.ac.in", "password": "campus@245"},
{"email": "25bcs246@iiitdmj.ac.in", "password": "campus@246"},
{"email": "25bcs247@iiitdmj.ac.in", "password": "campus@247"},
{"email": "25bcs248@iiitdmj.ac.in", "password": "campus@248"},
{"email": "25bcs249@iiitdmj.ac.in", "password": "campus@249"},
{"email": "25bcs250@iiitdmj.ac.in", "password": "campus@250"},
{"email": "25bcs251@iiitdmj.ac.in", "password": "campus@251"},
{"email": "25bcs252@iiitdmj.ac.in", "password": "campus@252"},
{"email": "25bcs253@iiitdmj.ac.in", "password": "campus@253"},
{"email": "25bcs254@iiitdmj.ac.in", "password": "campus@254"},
{"email": "25bcs255@iiitdmj.ac.in", "password": "campus@255"},
{"email": "25bcs256@iiitdmj.ac.in", "password": "campus@256"},
{"email": "25bcs257@iiitdmj.ac.in", "password": "campus@257"},
{"email": "25bcs258@iiitdmj.ac.in", "password": "campus@258"},
{"email": "25bcs259@iiitdmj.ac.in", "password": "campus@259"},
{"email": "25bcs260@iiitdmj.ac.in", "password": "campus@260"},
{"email": "25bcs261@iiitdmj.ac.in", "password": "campus@261"},
{"email": "25bcs262@iiitdmj.ac.in", "password": "campus@262"},
{"email": "25bcs263@iiitdmj.ac.in", "password": "campus@263"},
{"email": "25bcs264@iiitdmj.ac.in", "password": "campus@264"},
{"email": "25bcs265@iiitdmj.ac.in", "password": "campus@265"},
{"email": "25bcs266@iiitdmj.ac.in", "password": "campus@266"},
{"email": "25bcs267@iiitdmj.ac.in", "password": "campus@267"},
{"email": "25bcs268@iiitdmj.ac.in", "password": "campus@268"},
{"email": "25bcs269@iiitdmj.ac.in", "password": "campus@269"},
{"email": "25bcs270@iiitdmj.ac.in", "password": "campus@270"},
{"email": "25bcs271@iiitdmj.ac.in", "password": "campus@271"},
{"email": "25bcs272@iiitdmj.ac.in", "password": "campus@272"},
{"email": "25bcs273@iiitdmj.ac.in", "password": "campus@273"},
{"email": "25bcs274@iiitdmj.ac.in", "password": "campus@274"},
{"email": "25bcs275@iiitdmj.ac.in", "password": "campus@275"},
{"email": "25bcs276@iiitdmj.ac.in", "password": "campus@276"},
{"email": "25bcs277@iiitdmj.ac.in", "password": "campus@277"},
{"email": "25bcs278@iiitdmj.ac.in", "password": "campus@278"},
{"email": "25bcs279@iiitdmj.ac.in", "password": "campus@279"},
{"email": "25bcs280@iiitdmj.ac.in", "password": "campus@280"},
{"email": "25bcs281@iiitdmj.ac.in", "password": "campus@281"},
{"email": "25bcs282@iiitdmj.ac.in", "password": "campus@282"},
{"email": "25bcs283@iiitdmj.ac.in", "password": "campus@283"},
{"email": "25bcs284@iiitdmj.ac.in", "password": "campus@284"},
{"email": "25bcs285@iiitdmj.ac.in", "password": "campus@285"},
{"email": "25bcs286@iiitdmj.ac.in", "password": "campus@286"},
{"email": "25bcs287@iiitdmj.ac.in", "password": "campus@287"},
{"email": "25bcs288@iiitdmj.ac.in", "password": "campus@288"},
{"email": "25bcs289@iiitdmj.ac.in", "password": "campus@289"},
{"email": "25bcs290@iiitdmj.ac.in", "password": "campus@290"},
{"email": "25bcs291@iiitdmj.ac.in", "password": "campus@291"},
{"email": "25bcs292@iiitdmj.ac.in", "password": "campus@292"},
{"email": "25bcs293@iiitdmj.ac.in", "password": "campus@293"},
{"email": "25bcs294@iiitdmj.ac.in", "password": "campus@294"},
{"email": "25bcs295@iiitdmj.ac.in", "password": "campus@295"},
{"email": "25bcs296@iiitdmj.ac.in", "password": "campus@296"},
{"email": "25bcs297@iiitdmj.ac.in", "password": "campus@297"},
{"email": "25bcs298@iiitdmj.ac.in", "password": "campus@298"},
{"email": "25bcs299@iiitdmj.ac.in", "password": "campus@299"},
{"email": "25bcs300@iiitdmj.ac.in", "password": "campus@300"}
]

WEEKDAY_TRIPS = [
    {"id": "wd-b1-1", "bus": 1, "route": "Institute→Sadar", "time": "15:40", "purpose": "Staff/Student"},
    {"id": "wd-b1-2", "bus": 1, "route": "Sadar→Institute", "time": "16:30", "purpose": "Staff/Student"},
    {"id": "wd-b1-3", "bus": 1, "route": "Institute→Sadar", "time": "17:15", "purpose": "Staff/Student"},
    {"id": "wd-b1-4", "bus": 1, "route": "Sadar→Institute", "time": "18:00", "purpose": "Staff/Student"},
    {"id": "wd-b1-5", "bus": 1, "route": "Institute→Sadar", "time": "19:00", "purpose": "Staff/Student"},
    {"id": "wd-b1-6", "bus": 1, "route": "Sadar→Institute", "time": "19:40", "purpose": "Staff/Student"},
    {"id": "wd-b1-7", "bus": 1, "route": "Institute→Sadar", "time": "20:20", "purpose": "Staff/Student"},
    {"id": "wd-b1-8", "bus": 1, "route": "Sadar→Institute", "time": "21:00", "purpose": "Staff/Student", "last": True},
    {"id": "wd-b2-1", "bus": 2, "route": "Institute→Sadar", "time": "15:00", "purpose": "Staff/Student"},
    {"id": "wd-b2-2", "bus": 2, "route": "Sadar→Institute", "time": "15:45", "purpose": "Staff/Student"},
    {"id": "wd-b2-3", "bus": 2, "route": "Institute→Sadar", "time": "18:00", "purpose": "Staff/Student"},
    {"id": "wd-b2-4", "bus": 2, "route": "Sadar→Institute", "time": "18:30", "purpose": "Staff/Student"},
    {"id": "wd-b2-5", "bus": 2, "route": "Institute→Sadar", "time": "20:50", "purpose": "Staff/Student"},
    {"id": "wd-b2-6", "bus": 2, "route": "Sadar→Institute", "time": "21:30", "purpose": "Staff/Student", "last": True},
]

WEEKEND_TRIPS = [
    {"id": "we-b1-1", "bus": 1, "route": "Institute→Sadar", "time": "15:30", "purpose": "via Russel Chowk"},
    {"id": "we-b1-2", "bus": 1, "route": "Sadar→Institute", "time": "17:20", "purpose": "Direct"},
    {"id": "we-b1-3", "bus": 1, "route": "Institute→Sadar", "time": "18:00", "purpose": "Direct"},
    {"id": "we-b1-4", "bus": 1, "route": "Sadar→Institute", "time": "18:30", "purpose": "Direct"},
    {"id": "we-b1-5", "bus": 1, "route": "Institute→Sadar", "time": "19:00", "purpose": "Direct"},
    {"id": "we-b1-6", "bus": 1, "route": "Sadar→Institute", "time": "21:15", "purpose": "via Russel Chowk", "last": True},
    {"id": "we-b2-1", "bus": 2, "route": "Institute→Sadar", "time": "15:00", "purpose": "Direct"},
    {"id": "we-b2-2", "bus": 2, "route": "Sadar→Institute", "time": "16:30", "purpose": "Direct"},
    {"id": "we-b2-3", "bus": 2, "route": "Institute→Sadar", "time": "17:30", "purpose": "Direct"},
    {"id": "we-b2-4", "bus": 2, "route": "Sadar→Institute", "time": "19:30", "purpose": "via Russel Chowk"},
    {"id": "we-b2-5", "bus": 2, "route": "Institute→Sadar", "time": "20:50", "purpose": "Direct"},
    {"id": "we-b2-6", "bus": 2, "route": "Sadar→Institute", "time": "21:30", "purpose": "Direct", "last": True},
]


def seed_users():
    for student in STUDENTS:
        existing = User.query.filter_by(email=student["email"]).first()
        if existing:
            continue
        db.session.add(User(email=student["email"], password_hash=generate_password_hash(student["password"])))


def seed_trips():
    for item in WEEKDAY_TRIPS + WEEKEND_TRIPS:
        existing = Trip.query.get(item["id"])
        if existing:
            continue
        db.session.add(
            Trip(
                id=item["id"],
                bus=item["bus"],
                route=item["route"],
                time=item["time"],
                purpose=item["purpose"],
                day_type="weekday" if item["id"].startswith("wd-") else "weekend",
                is_last=item.get("last", False),
                capacity=32,
            )
        )


with app.app_context():
    db.create_all()
    seed_users()
    seed_trips()
    db.session.commit()
    print("Database initialized with users and trips.")


if __name__ == "__main__":
    pass