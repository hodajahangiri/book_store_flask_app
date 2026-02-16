import unittest
from app import create_app
from app.models import db, Users
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestPayments(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create a user
            self.user = Users(first_name="FirstTestCustomer", last_name="LastTestCustomer", email="custmer_test@email.com", password=generate_password_hash('1234'), phone="+1234567890")
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
        self.token = encode_token(self.user_id)
        self.client = self.app.test_client()

    def test_create_payment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payment_payload = {
            "card_number": "5152333344445555", 
            "cvv": 123, 
            "expiry_month": 1,
            "expiry_year": 2030
        }
        # Valid payment creation
        response = self.client.post("/payments", json=payment_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["card_number"], payment_payload["card_number"])

        # Duplicate payment creation
        response_dup = self.client.post("/payments", json=payment_payload, headers=headers)
        self.assertEqual(response_dup.status_code, 400)
        self.assertIn("error", response_dup.get_json())

        # Unauthorized
        response_unauth = self.client.post("/payments", json=payment_payload)
        self.assertEqual(response_unauth.status_code, 401)

        # Invalid payload (missing required field)
        invalid_payload = {
            "card_number": "1234567890123456",
            "cvv": 123
        }
        response_invalid = self.client.post("/payments", json=invalid_payload, headers=headers)
        self.assertEqual(response_invalid.status_code, 400)
        self.assertIn("error_message", response_invalid.get_json())

    def test_get_payments(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        # Initially empty
        response = self.client.get("/payments", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

        # Add a payment and check
        payment_payload = {
            "card_number": "5152333344445555", 
            "cvv": 123, 
            "expiry_month": 1,
            "expiry_year": 2030
        }
        self.client.post("/payments", json=payment_payload, headers=headers)
        response_after = self.client.get("/payments", headers=headers)
        self.assertEqual(response_after.status_code, 200)
        self.assertIsInstance(response_after.get_json(), list)
        self.assertEqual(response_after.get_json()[0]["card_number"], payment_payload["card_number"])

        # Unauthorized
        response_unauth = self.client.get("/payments")
        self.assertEqual(response_unauth.status_code, 401)

    def test_get_all_payments(self):
        # Add a payment
        headers = {"Authorization": f"Bearer {self.token}"}
        payment_payload = {
            "card_number": "5152333344445555", 
            "cvv": 123, 
            "expiry_month": 1,
            "expiry_year": 2030
        }
        self.client.post("/payments", json=payment_payload, headers=headers)
        response = self.client.get("/payments/all")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(response.get_json()[0]["card_number"], payment_payload["card_number"])

    def test_update_payment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payment_payload = {
            "card_number": "5152333344445555", 
            "cvv": 123, 
            "expiry_month": 1,
            "expiry_year": 2030
        }
        create_resp = self.client.post("/payments", json=payment_payload, headers=headers)
        payment_id = create_resp.get_json()["id"]

        update_payload = {
            "card_number": "5152333344445556", 
            "cvv": 321, 
            "expiry_month": 2,
            "expiry_year": 2031
        }
        response = self.client.put(f"/payments/{payment_id}", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())

        # Unauthorized
        response_unauth = self.client.put(f"/payments/{payment_id}", json=update_payload)
        self.assertEqual(response_unauth.status_code, 401)

        # Invalid payment id
        response_invalid = self.client.put("/payments/9999", json=update_payload, headers=headers)
        self.assertEqual(response_invalid.status_code, 404)
        self.assertIn("error", response_invalid.get_json())

        # Invalid payload
        invalid_payload = {
            "card_number": "5152333344445556"
        }
        response_invalid_payload = self.client.put(f"/payments/{payment_id}", json=invalid_payload, headers=headers)
        self.assertEqual(response_invalid_payload.status_code, 400)
        self.assertIn("error_message", response_invalid_payload.get_json())

    def test_delete_payment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payment_payload = {
            "card_number": "5152333344445555", 
            "cvv": 123, 
            "expiry_month": 1,
            "expiry_year": 2030
        }
        create_resp = self.client.post("/payments", json=payment_payload, headers=headers)
        payment_id = create_resp.get_json()["id"]

        response = self.client.delete(f"/payments/{payment_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())

        # Unauthorized
        response_unauth = self.client.delete(f"/payments/{payment_id}")
        self.assertEqual(response_unauth.status_code, 401)

        # Invalid payment id
        response_invalid = self.client.delete("/payments/9999", headers=headers)
        self.assertEqual(response_invalid.status_code, 404)
        self.assertIn("error", response_invalid.get_json())
         