from app import app
from models import User, db

with app.app_context():
    db.drop_all()
    db.create_all()
    user = User(username='tester', email='tester@example.com', full_name='Tester')
    user.set_password('secret123')
    db.session.add(user)
    db.session.commit()

client = app.test_client()
resp = client.post('/login', data={'email': 'tester@example.com', 'password': 'secret123'}, follow_redirects=False)
print('status', resp.status_code)
print('location', resp.headers.get('Location'))
print(resp.get_data(as_text=True)[:2000])
