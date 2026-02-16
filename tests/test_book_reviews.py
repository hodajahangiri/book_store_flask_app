import unittest
from app import create_app
from app.models import db, Users, Reviews, Book_descriptions
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestBookReviews(unittest.TestCase):
	def setUp(self):
		self.app = create_app('TestingConfig')
		with self.app.app_context():
			db.drop_all()
			db.create_all()
			# Create user
			self.user = Users(first_name="ReviewTest", last_name="User", email="reviewtest@email.com", password=generate_password_hash('1234'), phone="+1234567890")
			db.session.add(self.user)
			db.session.commit()
			self.user_id = self.user.id
			# Create book
			self.book = Book_descriptions(title="Book1", subtitle="Sub1", author="Author1", publisher="Pub1", published_date="2020-01-01", description="Desc", isbn="1234567890", image_link="img", language="EN", price=10.0, stock_quantity=10, averageRating=5.0, ratingsCount=1)
			db.session.add(self.book)
			db.session.commit()
			self.book_id = self.book.id
			# Create book2
			self.book2 = Book_descriptions(title="Book2", subtitle="Sub2", author="Author2", publisher="Pub2", published_date="2020-01-01", description="Desc2", isbn="1234567891", image_link="img", language="EN", price=10.0, stock_quantity=10, averageRating=5.0, ratingsCount=1)
			db.session.add(self.book2)
			db.session.commit()
			self.book2_id = self.book2.id
			# Create a review for book2
			self.review = Reviews(user_id=self.user_id, book_description_id=self.book2_id, rating=5.0, comment="Nice!")
			db.session.add(self.review)
			db.session.commit()
			self.review_id = self.review.id
		self.token = encode_token(self.user_id)
		self.client = self.app.test_client()

	def test_create_review(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		url = f"/reviews/{self.book_id}"
		payload = {"rating": 4.5, "comment": "Great book!"}
		response = self.client.post(url, json=payload, headers=headers)
		self.assertEqual(response.status_code, 201)
		self.assertIn("rating", response.get_json())
		# Duplicate review
		response_dup = self.client.post(url, json=payload, headers=headers)
		self.assertEqual(response_dup.status_code, 400)
		self.assertIn("error", response_dup.get_json())
		# Book not found
		response_nf = self.client.post("/reviews/9999", json=payload, headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		# Validation error
		response_invalid = self.client.post(url, json={}, headers=headers)
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error_message", response_invalid.get_json())
		# Unauthorized
		response_unauth = self.client.post(url, json=payload)
		self.assertEqual(response_unauth.status_code, 401)

	def test_get_reviews_by_book(self):
		url = f"/reviews/book/{self.book2_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIn("book_info", data)
		self.assertIn("reviews", data)
		self.assertIsInstance(data["reviews"], list)
		# Book not found
		response_nf = self.client.get("/reviews/book/9999")
		self.assertEqual(response_nf.status_code, 404)

	def test_get_all_reviews(self):
		response = self.client.get("/reviews/all")
		self.assertEqual(response.status_code, 200)
		self.assertIsInstance(response.get_json(), list)

	def test_get_review(self):
		url = f"/reviews/{self.review_id}"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		data = response.get_json()
		self.assertIsInstance(data, dict)
		self.assertIn("id", data)
		self.assertIn("rating", data)

	def test_update_review(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		with self.app.app_context():
			review = Reviews(user_id=self.user_id, book_description_id=self.book_id, rating=5.0, comment="Nice!")
			db.session.add(review)
			db.session.commit()
			review_id = review.id
		url = f"/reviews/{review_id}"
		payload = {"rating": 3.0, "comment": "Updated comment"}
		response = self.client.put(url, json=payload, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Not found
		response_nf = self.client.put("/reviews/9999", json=payload, headers=headers)
		self.assertEqual(response_nf.status_code, 404)
		# Not your review
		with self.app.app_context():
			other_user = Users(first_name="Other", last_name="User", email="other@email.com", password=generate_password_hash('1234'), phone="+1111111111")
			db.session.add(other_user)
			db.session.commit()
			other_review = Reviews(user_id=other_user.id, book_description_id=self.book_id, rating=4.0, comment="Other's review")
			db.session.add(other_review)
			db.session.commit()
			other_token = encode_token(other_user.id)
			url_other = f"/reviews/{other_review.id}"
			response2 = self.client.put(url_other, json=payload, headers=headers)
			self.assertEqual(response2.status_code, 404)
		# Validation error
		response_invalid = self.client.put(url, json={}, headers=headers)
		self.assertEqual(response_invalid.status_code, 400)
		self.assertIn("error_message", response_invalid.get_json())
		# Unauthorized
		response_unauth = self.client.put(url, json=payload)
		self.assertEqual(response_unauth.status_code, 401)

	def test_delete_review(self):
		headers = {"Authorization": f"Bearer {self.token}"}
		with self.app.app_context():
			review = Reviews(user_id=self.user_id, book_description_id=self.book_id, rating=5.0, comment="Nice!")
			db.session.add(review)
			db.session.commit()
			review_id = review.id
		url = f"/reviews/{review_id}"
		response = self.client.delete(url, headers=headers)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.get_json())
		# Try to delete again
		response2 = self.client.delete(url, headers=headers)
		self.assertEqual(response2.status_code, 404)
		# Not your review
		with self.app.app_context():
			other_user = Users(first_name="Other", last_name="User", email="other@email.com", password=generate_password_hash('1234'), phone="+1111111111")
			db.session.add(other_user)
			db.session.commit()
			other_review = Reviews(user_id=other_user.id, book_description_id=self.book_id, rating=4.0, comment="Other's review")
			db.session.add(other_review)
			db.session.commit()
			other_token = encode_token(other_user.id)
			url_other = f"/reviews/{other_review.id}"
			response3 = self.client.delete(url_other, headers=headers)
			self.assertEqual(response3.status_code, 200)
		# Unauthorized
		response_unauth = self.client.delete(url)
		self.assertEqual(response_unauth.status_code, 401)
