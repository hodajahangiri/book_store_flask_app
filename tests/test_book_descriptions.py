import unittest
from app import create_app
from app.models import db, Book_descriptions

class TestBookDescriptions(unittest.TestCase):
	def setUp(self):
		self.app = create_app('TestingConfig')
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			# Create a book
			self.book = Book_descriptions(title="Book1", subtitle="Sub1", author="Author1", publisher="Pub1", published_date="2020-01-01", description="Desc", isbn="1234567890123", image_link="img", language="EN", price=10.0, stock_quantity=10, averageRating=5.0, ratingsCount=1)
			db.session.add(self.book)
			db.session.commit()
			self.book_id = self.book.id
		self.client = self.app.test_client()

	def test_add_book_description(self):
		payload = {
			"title": "Book2", "subtitle": "Sub2", "author": "Author2", "publisher": "Pub2", "published_date": "2021-01-01", "description": "Desc2", "isbn": "1234567890999", "image_link": "img2", "language": "EN", "price": 15.0, "stock_quantity": 5, "averageRating": 4.0, "ratingsCount": 2
		}
		response = self.client.post("/book_descriptions", json=payload)
		self.assertIn(response.status_code, [200, 201])
		self.assertIn("title", response.get_json())
		# Duplicate ISBN
		payload_dup = dict(payload)
		payload_dup["isbn"] = "1234567890123"
		response_dup = self.client.post("/book_descriptions", json=payload_dup)
		self.assertEqual(response_dup.status_code, 201)
		self.assertIn("title", response_dup.get_json())
		# Validation error (missing title)
		response_invalid = self.client.post("/book_descriptions", json={})
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error_message", response_invalid.get_json())

	def test_get_book_descriptions(self):
		response = self.client.get("/book_descriptions")
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIsInstance(data, list)
		self.assertGreaterEqual(len(data), 1)
		self.assertIn("title", data[0])

	def test_get_single_book_description(self):
		url = f"/book_descriptions/{self.book_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIsInstance(data, dict)
		self.assertIn("Book1", data["data"]["title"])
		# Not found
		response_nf = self.client.get("/book_descriptions/9999")
		self.assertEqual(response_nf.status_code, 404)
		self.assertIn("error", response_nf.get_json())

	def test_update_book_description(self):
		payload = {"title": "Updated Book", "subtitle": "Updated Sub", "author": "Updated Author", "publisher": "Updated Pub", "published_date": "2022-01-01", "description": "Updated Desc", "isbn": "1234567890123", "image_link": "img", "language": "EN", "price": 20.0, "stock_quantity": 8, "averageRating": 4.5, "ratingsCount": 3}
		url = f"/book_descriptions/{self.book_id}"
		response = self.client.put(url, json=payload)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Not found
		response_nf = self.client.put("/book_descriptions/9999", json=payload)
		self.assertEqual(response_nf.status_code, 404)
		self.assertIn("error", response_nf.get_json())
		# Duplicate ISBN (if route checks for it)
		with self.app.app_context():
			book2 = Book_descriptions(title="Book3", subtitle="Sub3", author="Author3", publisher="Pub3", published_date="2023-01-01", description="Desc3", isbn="1234567890998", image_link="img3", language="EN", price=12.0, stock_quantity=7, averageRating=3.5, ratingsCount=1)
			db.session.add(book2)
			db.session.commit()
			book2_id = book2.id
		payload_dup = dict(payload)
		payload_dup["isbn"] = "1234567890123"
		response_dup = self.client.put(f"/book_descriptions/{book2_id}", json=payload_dup)
		# Accept 400 or 409 for duplicate
		self.assertIn(response_dup.status_code, [400, 409])
		# Validation error
		response_invalid = self.client.put(url, json={})
		self.assertEqual(response_invalid.status_code, 400)
		data_invalid = response_invalid.get_json()
		self.assertIsInstance(data_invalid, dict)
		self.assertIn("error_message", data_invalid)

	def test_delete_book_description(self):
		url = f"/book_descriptions/{self.book_id}"
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Try to delete again
		response2 = self.client.delete(url)
		self.assertEqual(response2.status_code, 404)
		self.assertIn("error", response2.get_json())
