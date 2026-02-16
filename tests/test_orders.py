import unittest
from app import create_app
from app.models import db, Users, Carts, Cart_books, Addresses, Payments, Book_descriptions
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestOrders(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create user
            self.user = Users(first_name="OrderTest", last_name="User", email="ordertest@email.com", password=generate_password_hash('1234'), phone="+1234567890")
            db.session.add(self.user)
            db.session.commit()
            self.user_id = self.user.id
            # Create address
            self.address = Addresses(line1="123 Main St", city="TestCity", state="TS", country="TestLand", zipcode="12345")
            self.address.users.append(self.user)
            db.session.add(self.address)
            db.session.commit()
            self.address_id = self.address.id
            # Create payment
            self.payment = Payments(user_id=self.user_id, card_number="4111111111111111", cvv=123, expiry_month=1, expiry_year=2030)
            db.session.add(self.payment)
            db.session.commit()
            self.payment_id = self.payment.id
            # Create book
            self.book = Book_descriptions(title="Book1", subtitle="Sub1", author="Author1", publisher="Pub1", published_date="2020-01-01", description="Desc", isbn="1234567890123", image_link="img", language="EN", price=10.0, stock_quantity=10, averageRating=5.0, ratingsCount=1)
            db.session.add(self.book)
            db.session.commit()
            self.book_id = self.book.id
            # Create cart and cart_books
            self.cart = Carts(user_id=self.user_id)
            db.session.add(self.cart)
            db.session.commit()
            self.cart_id = self.cart.id
            self.cart_book = Cart_books(cart_id=self.cart_id, book_description_id=self.book_id, quantity=2)
            db.session.add(self.cart_book)
            db.session.commit()
        self.token = encode_token(self.user_id)
        self.client = self.app.test_client()

    def test_create_order(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        order_payload = {"shipping_method": "InStore", "subtotal": 20.0, "tax": 2.0, "shipping_cost": 5.0, "total": 27.0, "status": "Pending"}
        url = f"/orders/{self.cart_id}/address/{self.address_id}/payment/{self.payment_id}"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("order_info", data)
        self.assertIn("order_books", data)
        self.assertEqual(data["order_books"][0]["quantity"], 2)
        # Cart should be deleted after order
        with self.app.app_context():
            cart = db.session.get(Carts, self.cart_id)
            self.assertIsNone(cart)

    def test_create_order_errors(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        order_payload = {"shipping_method": "InStore", "subtotal": 20.0, "tax": 2.0, "shipping_cost": 5.0, "total": 27.0, "status": "Pending"}
        # Invalid cart
        url = f"/orders/999/address/{self.address_id}/payment/{self.payment_id}"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        # Invalid address
        url = f"/orders/{self.cart_id}/address/999/payment/{self.payment_id}"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        # Invalid payment
        url = f"/orders/{self.cart_id}/address/{self.address_id}/payment/999"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        # Cart does not belong to user
        with self.app.app_context():
            other_user = Users(first_name="Other", last_name="User", email="other@email.com", password=generate_password_hash('1234'), phone="+1111111111")
            db.session.add(other_user)
            db.session.commit()
            other_cart = Carts(user_id=other_user.id)
            db.session.add(other_cart)
            db.session.commit()
            other_cart_id = other_cart.id
        url = f"/orders/{other_cart_id}/address/{self.address_id}/payment/{self.payment_id}"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        # Payment does not belong to user
        with self.app.app_context():
            other_payment = Payments(user_id=999, card_number="4222222222222", cvv=123, expiry_month=1, expiry_year=2030)
            db.session.add(other_payment)
            db.session.commit()
            other_payment_id = other_payment.id
        url = f"/orders/{self.cart_id}/address/{self.address_id}/payment/{other_payment_id}"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        # Address does not belong to user
        with self.app.app_context():
            other_address = Addresses(line1="Other", city="Other", state="OT", country="Other", zipcode="00000")
            db.session.add(other_address)
            db.session.commit()
            other_address_id = other_address.id
        url = f"/orders/{self.cart_id}/address/{other_address_id}/payment/{self.payment_id}"
        response = self.client.post(url, json=order_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        # Missing token
        url = f"/orders/{self.cart_id}/address/{self.address_id}/payment/{self.payment_id}"
        response = self.client.post(url, json=order_payload)
        self.assertEqual(response.status_code, 401)
        # Invalid payload
        headers = {"Authorization": f"Bearer {self.token}"}
        invalid_payload = {"shipping_method": "InStore"}
        response = self.client.post(url, json=invalid_payload, headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_delete_order(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        # Create order first
        order_payload = {"shipping_method": "InStore", "subtotal": 20.0, "tax": 2.0, "shipping_cost": 5.0, "status": "Pending"}
        url = f"/orders/{self.cart_id}/address/{self.address_id}/payment/{self.payment_id}"
        create_resp = self.client.post(url, json=order_payload, headers=headers)
        order_id = create_resp.get_json()["order_info"]["id"]
        # Delete order
        del_url = f"/orders/{order_id}"
        response = self.client.delete(del_url, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())
        # Try to delete again
        response2 = self.client.delete(del_url, headers=headers)
        self.assertEqual(response2.status_code, 404)
        # Unauthorized
        response3 = self.client.delete(del_url)
        self.assertEqual(response3.status_code, 401)

    def test_delete_order_not_owned(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        # Create order for another user and test deletion inside app context
        with self.app.app_context():
            other_user = Users(first_name="Other", last_name="User", email="other@email.com", password=generate_password_hash('1234'), phone="+1111111111")
            db.session.add(other_user)
            db.session.commit()
            other_cart = Carts(user_id=other_user.id)
            db.session.add(other_cart)
            db.session.commit()
            other_address = Addresses(line1="Other", city="Other", state="OT", country="Other", zipcode="00000")
            other_address.users.append(other_user)
            db.session.add(other_address)
            db.session.commit()
            other_payment = Payments(user_id=other_user.id, card_number="4222222222222", cvv=123, expiry_month=1, expiry_year=2030)
            db.session.add(other_payment)
            db.session.commit()
            other_book = Book_descriptions(title="Book2", subtitle="Sub2", author="Author2", publisher="Pub2", published_date="2021-01-01", description="Desc2", isbn="9876543210987", image_link="img2", language="EN", price=15.0, stock_quantity=5, averageRating=4.0, ratingsCount=2)
            db.session.add(other_book)
            db.session.commit()
            other_cart_book = Cart_books(cart_id=other_cart.id, book_description_id=other_book.id, quantity=1)
            db.session.add(other_cart_book)
            db.session.commit()
            other_token = encode_token(other_user.id)
            order_payload = {"shipping_method": "InStore", "subtotal": 15.0, "tax": 1.5, "shipping_cost": 3.0, "total": 19.5, "status": "Pending"}
            url = f"/orders/{other_cart.id}/address/{other_address.id}/payment/{other_payment.id}"
            create_resp = self.client.post(url, json=order_payload, headers={"Authorization": f"Bearer {other_token}"})
            order_id = create_resp.get_json()["order_info"]["id"]
            # Try to delete with wrong user
            del_url = f"/orders/{order_id}"
            response = self.client.delete(del_url, headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.get_json())

    def test_get_all_orders(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        # Create order
        order_payload = {"shipping_method": "InStore", "subtotal": 20.0, "tax": 2.0, "shipping_cost": 5.0, "total": 27.0, "status": "Pending"}
        url = f"/orders/{self.cart_id}/address/{self.address_id}/payment/{self.payment_id}"
        self.client.post(url, json=order_payload, headers=headers)
        # Get all orders
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("order_info", data[0])
        self.assertIn("order_books", data[0])

if __name__ == "__main__":
    unittest.main()
