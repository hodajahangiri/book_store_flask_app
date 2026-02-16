import unittest
from app import create_app
from app.models import db, Users, Favorites, Book_descriptions
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestFavorites(unittest.TestCase):
	def setUp(self):
		self.app = create_app('TestingConfig')
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			# Create user
			self.user = Users(first_name="FavoriteTest", last_name="User", email="favtest@email.com", password=generate_password_hash('1234'), phone="+1234567890")
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

	def test_add_favorite(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		url = f"/favorites/{self.book_id}"
		response = self.client.post(url, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Duplicate add
		response_dup = self.client.post(url, headers=headers)
		self.assertEqual(response_dup.status_code, 400)
		self.assertIn("error", response_dup.get_json())
		# Book not found
		response_nf = self.client.post("/favorites/9999", headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		# Unauthorized
		response_unauth = self.client.post(url)
		self.assertEqual(response_unauth.status_code, 401)

	def test_get_book_favorites(self):
		# Add favorite first
		with self.app.app_context():
			fav = Favorites(user_id=self.user_id, book_description_id=self.book_id)
			db.session.add(fav)
			db.session.commit()
		url = f"/favorites/book/{self.book_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIn("book_info", data)
		self.assertIn("favorites", data)
		self.assertIsInstance(data["favorites"], list)
		# Book not found
		response_nf = self.client.get("/favorites/book/9999")
		self.assertEqual(response_nf.status_code, 404)

	def test_delete_favorite(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		# Add favorite first
		with self.app.app_context():
			fav = Favorites(user_id=self.user_id, book_description_id=self.book_id)
			db.session.add(fav)
			db.session.commit()
			fav_id = fav.id
		url = f"/favorites/{fav_id}"
		response = self.client.delete(url, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Try to delete again
		response2 = self.client.delete(url, headers=headers)
		self.assertEqual(response2.status_code, 404)
		# Unauthorized
		response3 = self.client.delete(url)
		self.assertEqual(response3.status_code, 401)
		# Not your favorite
		with self.app.app_context():
			other_user = Users(first_name="Other", last_name="User", email="other@email.com", password=generate_password_hash('1234'), phone="+1111111111")
			db.session.add(other_user)
			db.session.commit()
			other_fav = Favorites(user_id=other_user.id, book_description_id=self.book_id)
			db.session.add(other_fav)
			db.session.commit()
			other_token = encode_token(other_user.id)
			url_other = f"/favorites/{other_fav.id}"
			response4 = self.client.delete(url_other, headers=headers)
			self.assertEqual(response4.status_code, 403)
			self.assertIn("error", response4.get_json())

	def test_toggle_favorite(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		url = f"/favorites/{self.book_id}"
		# Add (should add)
		response = self.client.put(url, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Remove (should remove)
		response2 = self.client.put(url, headers=headers)
		self.assertEqual(response2.status_code, 200)
		self.assertIn("message", response2.get_json())
		# Book not found
		response_nf = self.client.put("/favorites/9999", headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		# Unauthorized
		response_unauth = self.client.put(url)
		self.assertEqual(response_unauth.status_code, 401)
