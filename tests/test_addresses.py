import unittest
from app import create_app
from app.models import db, Users, Addresses
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestAddresses(unittest.TestCase):
	def setUp(self):
		self.app = create_app('TestingConfig')
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			# Create user
			self.user = Users(first_name="AddressTest", last_name="User", email="addresstest@email.com", password=generate_password_hash('1234'), phone="+1234567890")
			db.session.add(self.user)
			db.session.commit()
			self.user_id = self.user.id
		self.token = encode_token(self.user_id)
		self.client = self.app.test_client()

	def address_payload(self, line1="123 Main St", line2=None, number=None, city="TestCity", state="TS", country="TestLand", zipcode="12345"):
		return {"line1": line1, "line2": line2, "number": number, "city": city, "state": state, "country": country, "zipcode": zipcode}

	def test_create_address(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		payload = self.address_payload()
		response = self.client.post("/addresses", json=payload, headers=headers)
		self.assertEqual(response.status_code, 201)
		self.assertIn("message", response.get_json())
		# Duplicate address for same user
		response_dup = self.client.post("/addresses", json=payload, headers=headers)
		self.assertEqual(response_dup.status_code, 400)
		self.assertIn("error", response_dup.get_json())
		# Add same address for another user
		with self.app.app_context():
			other_user = Users(first_name="Other", last_name="User", email="other@email.com", password=generate_password_hash('1234'), phone="+1111111111")
			db.session.add(other_user)
			db.session.commit()
			other_token = encode_token(other_user.id)
		response_other = self.client.post("/addresses", json=payload, headers={"Authorization": f"Bearer {other_token}"})
		self.assertEqual(response_other.status_code, 201)
		# Validation error
		response_invalid = self.client.post("/addresses", json={}, headers=headers)
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error_message", response_invalid.get_json())
		# Unauthorized
		response_unauth = self.client.post("/addresses", json=payload)
		self.assertEqual(response_unauth.status_code, 401)

	def test_get_user_addresses(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		# Add address
		payload = self.address_payload()
		self.client.post("/addresses", json=payload, headers=headers)
		response = self.client.get("/addresses", headers=headers)
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIsInstance(data, list)
		self.assertGreaterEqual(len(data), 1)
		self.assertIn("line1", data[0])
		# Unauthorized
		response_unauth = self.client.get("/addresses")
		self.assertEqual(response_unauth.status_code, 401)

	def test_get_all_addresses(self):
		# Add address
		headers = {"Authorization": f"Bearer {self.token}"}
		payload = self.address_payload()
		self.client.post("/addresses", json=payload, headers=headers)
		response = self.client.get("/addresses/all")
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIsInstance(data, list)
		self.assertGreaterEqual(len(data), 1)
		self.assertIn("line1", data[0])

	def test_update_address(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		payload = self.address_payload()
		# Add address
		add_resp = self.client.post("/addresses", json=payload, headers=headers)
		# Get address id
		with self.app.app_context():
			address = db.session.query(Addresses).filter_by(line1=payload["line1"]).first()
			address_id = address.id
		update_payload = self.address_payload(line1="456 New St")
		url = f"/addresses/{address_id}"
		response = self.client.put(url, json=update_payload, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Not found
		response_nf = self.client.put("/addresses/9999", json=update_payload, headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		self.assertIn("error", response_nf.get_json())
		# Validation error
		response_invalid = self.client.put(url, json={}, headers=headers)
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error_message", response_invalid.get_json())
		# Unauthorized
		response_unauth = self.client.put(url, json=update_payload)
		self.assertEqual(response_unauth.status_code, 401)

	def test_delete_address(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		payload = self.address_payload()
		# Add address
		self.client.post("/addresses", json=payload, headers=headers)
		with self.app.app_context():
			address = db.session.query(Addresses).filter_by(line1=payload["line1"]).first()
			address_id = address.id
		url = f"/addresses/{address_id}"
		response = self.client.delete(url, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Try to delete again
		response2 = self.client.delete(url, headers=headers)
		self.assertEqual(response2.status_code, 404)
		# Unauthorized
		response_unauth = self.client.delete(url)
		self.assertEqual(response_unauth.status_code, 401)
