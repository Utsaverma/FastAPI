from starlette import status

from .utils import *
from ..database import get_db
from ..routers.auth import get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_user(test_user):
    response = client.get('/users')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'utsaverma'
    assert response.json()['email'] == 'utsaverma@gmail.com'
    assert response.json()['first_name'] == 'utsav'
    assert response.json()['last_name'] == 'verma'
    assert response.json()['username'] == 'utsaverma'
    assert response.json()['phone_number'] == '1234567890'

def test_change_password_success(test_user):
    response = client.put('/users/password', json={'password': 'testpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    user_model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify('newpassword', user_model.hashed_password)

def test_change_password_failure(test_user):
    response = client.put('/users/password', json={'password': 'incorrectpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}

def test_phone_number_change_success(test_user):
    response = client.put('/users/phone_number/0987654321')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    user_model = db.query(Users).filter(Users.id == 1).first()
    assert user_model.phone_number == '0987654321'
