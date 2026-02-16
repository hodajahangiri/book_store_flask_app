import unittest
from app import create_app
from app.models import db, Categories

class TestCategories(unittest.TestCase):
	def setUp(self):
		self.app = create_app('TestingConfig')
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			# Create a category
			self.category = Categories(title="Fiction")
			db.session.add(self.category)
			db.session.commit()
			self.category_id = self.category.id
		self.client = self.app.test_client()

	def test_add_category(self):
		payload = {"title": "Science"}
		response = self.client.post("/categories", json=payload)
		self.assertEqual(response.status_code, 201)
		self.assertIn("title", response.get_json())
		# Duplicate title
		response_dup = self.client.post("/categories", json=payload)
		self.assertEqual(response_dup.status_code, 400)
		self.assertIn("error", response_dup.get_json())
		# Validation error (missing title)
		response_invalid = self.client.post("/categories", json={})
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error_message", response_invalid.get_json())

	def test_get_categories(self):
		response = self.client.get("/categories")
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIsInstance(data, list)
		self.assertGreaterEqual(len(data), 1)
		self.assertIn("title", data[0])

	def test_update_category(self):
		payload = {"title": "Updated Fiction"}
		url = f"/categories/{self.category_id}"
		response = self.client.put(url, json=payload)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Not found
		response_nf = self.client.put("/categories/9999", json=payload)
		self.assertEqual(response_nf.status_code, 404)
		self.assertIn("error", response_nf.get_json())
		# Duplicate title
		with self.app.app_context():
			cat2 = Categories(title="UniqueCat")
			db.session.add(cat2)
			db.session.commit()
			cat2_id = cat2.id
		payload_dup = {"title": "Updated Fiction"}
		response_dup = self.client.put(f"/categories/{cat2_id}", json=payload_dup)
		self.assertEqual(response_dup.status_code, 400)
		self.assertIn("error", response_dup.get_json())
		# Validation error
		response_invalid = self.client.put(url, json={})
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error message", response_invalid.get_json())

	def test_delete_category(self):
		url = f"/categories/{self.category_id}"
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Try to delete again
		response2 = self.client.delete(url)
		self.assertEqual(response2.status_code, 404)
		self.assertIn("error", response2.get_json())
