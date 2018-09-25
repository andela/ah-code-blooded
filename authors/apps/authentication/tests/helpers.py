import json

def register_user(self):
    """
    Helper function for registering a new user.

    """
    return self.client.post(
        'api/users',
        data = json.dumps(
            dict(username='testuser',email='testuser@gmail.com',password='testuser1234')
        ),
        content_type='application/json'
    )

def login_user(self):
    """
    Helper function for login.

    """
    return self.client.post(
        'api/users/login',
        data = json.dumps(
            dict(email='testuser@gmail.com',password='testuser1234')
        ),
        content_type='application/json'
    )