import re
from app import app
from models import User, Trip, TripMember, db

client = app.test_client()
with app.app_context():
    db.drop_all()
    db.create_all()
    user = User(username='tester', email='tester@example.com', full_name='Tester')
    user.set_password('secret123')
    db.session.add(user)
    db.session.commit()

login_get = client.get('/login')
print('login status', login_get.status_code)
html = login_get.get_data(as_text=True)
csrf = None
start = html.find('name="csrf_token" type="hidden" value="')
if start != -1:
    start += len('name="csrf_token" type="hidden" value="')
    end = html.find('"', start)
    csrf = html[start:end]
print('csrf login', bool(csrf), csrf)
if not csrf:
    raise SystemExit(1)
login_post = client.post('/login', data={
    'email': 'tester@example.com',
    'password': 'secret123',
    'csrf_token': csrf,
}, follow_redirects=True)
print('login post status', login_post.status_code)

explore_get = client.get('/explore')
print('explore status', explore_get.status_code)
explore_html = explore_get.get_data(as_text=True)
print('explore csrf present', 'csrf_token' in explore_html)
start = explore_html.find('name="csrf_token" type="hidden" value="')
csrf2 = None
if start != -1:
    start += len('name="csrf_token" type="hidden" value="')
    end = explore_html.find('"', start)
    csrf2 = explore_html[start:end]
print('csrf explore', bool(csrf2), csrf2)
print('member_name count in explore page', explore_html.count('member_name_'))
print('explore form action', 'action="' in explore_html and explore_html[explore_html.find('action="'):explore_html.find('"', explore_html.find('action="') + 8)])
if not csrf2:
    raise SystemExit(1)

response = client.post('/explore', data={
    'csrf_token': csrf2,
    'name': 'Group Trip Test',
    'destination': 'Goa',
    'start_date': '2026-09-01',
    'end_date': '2026-09-05',
    'budget': '1500',
    'status': 'Planning',
    'trip_type': 'group',
    'member_name_0': 'Alice',
    'member_name_1': 'Bob',
}, follow_redirects=True)
print('create status', response.status_code)
print('created page len', len(response.get_data()))
with app.app_context():
    print('trips', Trip.query.count())
    print('members', TripMember.query.count())
    for m in TripMember.query.all():
        print('member', m.id, m.trip_id, m.user_id, m.display_name)
