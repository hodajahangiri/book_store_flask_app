import unittest
from app import create_app
from app.models import Users, db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token


class TestUsers(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        self.user = Users(first_name="FirstTest", last_name="LastTest", email="tester@email.com", password=generate_password_hash('1234'), phone="+19999999")
        with self.app.app_context():
            db.drop_all() #removing any lingering tables
            db.create_all() #creating fresh tables for another round of testing
            db.session.add(self.user)
            db.session.commit()
        self.token = encode_token(1) #encoding a token for my starter designed user
        self.client = self.app.test_client()

    def test_create_user(self):
        # Valid user creation
        user_payload = {
            "first_name": "FirstTest",
            "last_name": "LastTest",
            "email": "test@email.com",
            "password": "12345",
            "phone": "+1234567890"
        }
        response = self.client.post("/users", json=user_payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("user_data", data)
        self.assertIn("token", data)
        self.assertEqual(data["user_data"]["email"], user_payload["email"])
        self.assertTrue(check_password_hash(data["user_data"]["password"], user_payload["password"]))

        # Duplicate email
        response_dup = self.client.post("/users", json=user_payload)
        self.assertEqual(response_dup.status_code, 400)
        data_dup = response_dup.get_json()
        self.assertIn("error", data_dup)
        self.assertIn(user_payload["email"], data_dup["error"])

        # Validation error (missing required field)
        invalid_user_payload = {
            "first_name": "NoEmail",
            "last_name": "LastTest",
            "password": "12345",
            "phone": "+1234567890"
        }
        response_invalid = self.client.post("/users", json=invalid_user_payload)
        self.assertEqual(response_invalid.status_code, 400)
        data_invalid = response_invalid.get_json()
        self.assertIn("error_message", data_invalid)

    def test_login(self):
        # Valid login
        login_payload = {
            "email": "tester@email.com",
            "password": "1234"
        }
        response = self.client.post("/users/login", json=login_payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("user_data", data)
        self.assertIn("token", data)
        self.assertEqual(data["user_data"]["email"], login_payload["email"])

        # Invalid password
        invalid_password_payload = {
            "email": "tester@email.com",
            "password": "wrongpassword"
        }
        response_invalid_pwd = self.client.post("/users/login", json=invalid_password_payload)
        self.assertEqual(response_invalid_pwd.status_code, 400)
        data_invalid_pwd = response_invalid_pwd.get_json()
        self.assertIn("error message", data_invalid_pwd)
        self.assertIn("Invalid", data_invalid_pwd["error message"])

        # Invalid email
        invalid_email_payload = {
            "email": "nonexistent@email.com",
            "password": "1234"
        }
        response_invalid_email = self.client.post("/users/login", json=invalid_email_payload)
        self.assertEqual(response_invalid_email.status_code, 400)
        data_invalid_email = response_invalid_email.get_json()
        self.assertIn("error message", data_invalid_email)

        # Missing required field
        missing_field_payload = {
            "email": "tester@email.com"
        }
        response_missing = self.client.post("/users/login", json=missing_field_payload)
        self.assertEqual(response_missing.status_code, 400)
        data_missing = response_missing.get_json()
        self.assertIn("error_message", data_missing)

    def test_get_all_users(self):
        # Get all users
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["email"], "tester@email.com")

    def test_get_user_profile(self):
        # Valid request with token
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/users/profile", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("user_data", data)
        self.assertIn("user_payments", data)
        self.assertIn("user_addresses", data)
        self.assertEqual(data["user_data"]["email"], "tester@email.com")

        # Missing token
        response_no_token = self.client.get("/users/profile")
        self.assertEqual(response_no_token.status_code, 401)

        # Invalid token
        invalid_headers = {"Authorization": "Bearer invalidtoken123"}
        response_invalid_token = self.client.get("/users/profile", headers=invalid_headers)
        self.assertEqual(response_invalid_token.status_code, 401)

    def test_delete_user(self):
        # Create a new user to delete
        new_user_payload = {
            "first_name": "DeleteTest",
            "last_name": "User",
            "email": "delete@email.com",
            "password": "12345",
            "phone": "+1234567890"
        }
        create_response = self.client.post("/users", json=new_user_payload)
        self.assertEqual(create_response.status_code, 201)
        new_token = create_response.get_json()["token"]

        # Valid deletion with token
        headers = {"Authorization": f"Bearer {new_token}"}
        response = self.client.delete("/users", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"])

        # Try to get deleted user profile
        response_after_delete = self.client.get("/users/profile", headers=headers)
        self.assertEqual(response_after_delete.status_code, 404)

        # Missing token
        response_no_token = self.client.delete("/users")
        self.assertEqual(response_no_token.status_code, 401)

    def test_update_user_profile(self):
        # Valid update
        headers = {"Authorization": f"Bearer {self.token}"}
        update_payload = {
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "email": "updated@email.com",
            "password": "newpassword",
            "phone": "+1111111111"
        }
        response = self.client.put("/users", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("user_data", data)
        self.assertEqual(data["user_data"]["email"], update_payload["email"])
        self.assertEqual(data["user_data"]["first_name"], update_payload["first_name"])
        self.assertTrue(check_password_hash(data["user_data"]["password"], update_payload["password"]))

        # Try to update with existing email (create another user first)
        other_user_payload = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@email.com",
            "password": "12345",
            "phone": "+1234567890"
        }
        self.client.post("/users", json=other_user_payload)
        
        duplicate_email_payload = {
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "email": "other@email.com",
            "password": "newpassword",
            "phone": "+1111111111"
        }
        response_dup = self.client.put("/users", json=duplicate_email_payload, headers=headers)
        self.assertEqual(response_dup.status_code, 400)
        data_dup = response_dup.get_json()
        self.assertIn("error", data_dup)
        self.assertIn("other@email.com", data_dup["error"])

        # Missing token
        response_no_token = self.client.put("/users", json=update_payload)
        self.assertEqual(response_no_token.status_code, 401)

        # Invalid payload (missing required field)
        invalid_payload = {
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast"
        }
        response_invalid = self.client.put("/users", json=invalid_payload, headers=headers)
        self.assertEqual(response_invalid.status_code, 400)
        data_invalid = response_invalid.get_json()
        self.assertIn("error message", data_invalid)

    def test_get_user_reviews(self):
        # Valid request with token
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/users/reviews", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("user", data)
        self.assertIn("user_reviews", data)
        self.assertIsInstance(data["user_reviews"], list)
        self.assertEqual(data["user"]["email"], "tester@email.com")

        # Missing token
        response_no_token = self.client.get("/users/reviews")
        self.assertEqual(response_no_token.status_code, 401)

    def test_get_user_favorites(self):
        # Valid request with token
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/users/favorites", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("user", data)
        self.assertIn("user_favorites", data)
        self.assertIsInstance(data["user_favorites"], list)
        self.assertEqual(data["user"]["email"], "tester@email.com")

        # Missing token
        response_no_token = self.client.get("/users/favorites")
        self.assertEqual(response_no_token.status_code, 401)

    def test_get_user_orders(self):
        # Valid request with token
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/users/orders", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("user", data)
        self.assertIn("user_orders", data)
        self.assertIsInstance(data["user_orders"], list)
        self.assertEqual(data["user"]["email"], "tester@email.com")

        # Missing token
        response_no_token = self.client.get("/users/orders")
        self.assertEqual(response_no_token.status_code, 401)

    def test_get_user_cart(self):
        # Valid request with token
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/users/carts", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # The user might not have a cart yet, so check for appropriate response
        if "user" in data:
            self.assertEqual(data["user"]["email"], "tester@email.com")
        else:
            # Could be a message saying no cart exists
            self.assertIn("message", data)

        # Missing token
        response_no_token = self.client.get("/users/carts")
        self.assertEqual(response_no_token.status_code, 401)