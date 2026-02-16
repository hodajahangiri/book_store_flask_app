import unittest
from app import create_app
from app.models import db, Users, Carts, Cart_books, Book_descriptions
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestCarts(unittest.TestCase):
	def setUp(self):
		self.app = create_app('TestingConfig')
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			# Create user
			self.user = Users(first_name="CartTest", last_name="User", email="carttest@email.com", password=generate_password_hash('1234'), phone="+1234567890")
			db.session.add(self.user)
			db.session.commit()
			self.user_id = self.user.id
			# Create book
			self.book = Book_descriptions(title="Book1", subtitle="Sub1", author="Author1", publisher="Pub1", published_date="2020-01-01", description="Desc", isbn="1234567890123", image_link="img", language="EN", price=10.0, stock_quantity=10, averageRating=5.0, ratingsCount=1)
			db.session.add(self.book)
			db.session.commit()
			self.book_id = self.book.id
		self.token = encode_token(self.user_id)
		self.client = self.app.test_client()

	def test_get_cart_books(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		# No cart yet
		response = self.client.get("/carts", headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Add a book to cart
		self.client.put(f"/carts/add_book/{self.book_id}", headers=headers)
		response2 = self.client.get("/carts", headers=headers)
		self.assertEqual(response2.status_code, 200)
		data = response2.get_json()
		self.assertIn("cart_info", data)
		self.assertIn("cart_books", data)
		# Remove book so cart is empty
		self.client.put(f"/carts/remove_book/{self.book_id}", headers=headers)
		response3 = self.client.get("/carts", headers=headers)
		self.assertEqual(response3.status_code, 200)
		self.assertIn("message", response3.get_json())
		# Unauthorized
		response_unauth = self.client.get("/carts")
		self.assertEqual(response_unauth.status_code, 401)

	def test_add_book_to_cart(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		url = f"/carts/add_book/{self.book_id}"
		response = self.client.put(url, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Add again (should increase quantity)
		response2 = self.client.put(url, headers=headers)
		self.assertEqual(response2.status_code, 200)
		self.assertIn("message", response2.get_json())
		# Book not found
		response_nf = self.client.put("/carts/add_book/9999", headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		# Unauthorized
		response_unauth = self.client.put(url)
		self.assertEqual(response_unauth.status_code, 401)

	def test_remove_book_from_cart(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		# Add a book to cart
		self.client.put(f"/carts/add_book/{self.book_id}", headers=headers)
		# Remove book (should remove)
		response = self.client.put(f"/carts/remove_book/{self.book_id}", headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Remove again (should error)
		response2 = self.client.put(f"/carts/remove_book/{self.book_id}", headers=headers)
		self.assertEqual(response2.status_code, 404)
		self.assertIn("error", response2.get_json())
		# Add two, then decrease quantity
		self.client.put(f"/carts/add_book/{self.book_id}", headers=headers)
		self.client.put(f"/carts/add_book/{self.book_id}", headers=headers)
		response3 = self.client.put(f"/carts/remove_book/{self.book_id}", headers=headers)
		self.assertEqual(response3.status_code, 200)
		self.assertIn("message", response3.get_json())
		# Book not found
		response_nf = self.client.put("/carts/remove_book/9999", headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		# Unauthorized
		response_unauth = self.client.put(f"/carts/remove_book/{self.book_id}")
		self.assertEqual(response_unauth.status_code, 401)
