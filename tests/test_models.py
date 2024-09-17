# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
    
    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        new_product["description"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "unknown")

    ######################################################################
    # UPDATE AN EXISTING PRODUCT
    ######################################################################
        @app.route("/products/<int:product_id>", methods=["PUT"])
        def update_products(product_id):
            """
            Update a Product

            This endpoint will update a Product based the body that is posted
            """
            app.logger.info("Request to Update a product with id [%s]", product_id)
            check_content_type("application/json")

            product = Product.find(product_id)
            if not product:
                abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

            product.deserialize(request.get_json())
            product.id = product_id
            product.update()
            return product.serialize(), status.HTTP_200_OK
    def test_delete_product(self):
        """It should Delete a Product"""
        products = self._create_products(5)
        product_count = self.get_product_count()
        test_product = products[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)
    ######################################################################
    # DELETE A PRODUCT
    ######################################################################
    @app.route("/products/<int:product_id>", methods=["DELETE"])
    def delete_products(product_id):
            """
            Delete a Product

             This endpoint will delete a Product based the id specified in the path
            """
            app.logger.info("Request to Delete a product with id [%s]", product_id)

             product = Product.find(product_id)
             if product:
                product.delete()

            return "", status.HTTP_204_NO_CONTENT
    
        def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
    ######################################################################
    # LIST PRODUCTS
    ######################################################################
        @app.route("/products", methods=["GET"])
        def list_products():
            """Returns a list of Products"""
            app.logger.info("Request to list Products...")

            products = Product.all()

            results = [product.serialize() for product in products]
            app.logger.info("[%s] Products returned", len(results))
            return results, status.HTTP_200_OK
           
        def test_query_by_name(self):
            """It should Query Products by name"""
            products = self._create_products(5)
            test_name = products[0].name
            name_count = len([product for product in products if product.name == test_name])
            response = self.client.get(
                BASE_URL, query_string=f"name={quote_plus(test_name)}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(len(data), name_count)
            # check the data just to be sure
            for product in data:
                self.assertEqual(product["name"], test_name)
    ######################################################################
    # LIST PRODUCTS
    ######################################################################
        @app.route("/products", methods=["GET"])
        def list_products():
        """Returns a list of Products"""
        app.logger.info("Request to list Products...")

        products = []
        name = request.args.get("name")

        if name:
            app.logger.info("Find by name: %s", name)
            products = Product.find_by_name(name)
        else:
            app.logger.info("Find all")
            products = Product.all()

        results = [product.serialize() for product in products]
        app.logger.info("[%s] Products returned", len(results))
        return results, status.HTTP_200_OK    
        def test_query_by_category(self):
            """It should Query Products by category"""
            products = self._create_products(10)
            category = products[0].category
            found = [product for product in products if product.category == category]
            found_count = len(found)
            logging.debug("Found Products [%d] %s", found_count, found)

            # test for available
            response = self.client.get(BASE_URL, query_string=f"category={category.name}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(len(data), found_count)
            # check the data just to be sure
            for product in data:
                self.assertEqual(product["category"], category.name)
    ######################################################################
    # LIST PRODUCTS
    ######################################################################
        @app.route("/products", methods=["GET"])
        def list_products():
            """Returns a list of Products"""
            app.logger.info("Request to list Products...")

            products = []
            name = request.args.get("name")
            category = request.args.get("category")

            if name:
                app.logger.info("Find by name: %s", name)
                products = Product.find_by_name(name)
            elif category:
                app.logger.info("Find by category: %s", category)
                # create enum from string
                category_value = getattr(Category, category.upper())
                products = Product.find_by_category(category_value)
            else:
                app.logger.info("Find all")
                products = Product.all()

            results = [product.serialize() for product in products]
            app.logger.info("[%s] Products returned", len(results))
            return results, status.HTTP_200_OK
        def test_query_by_availability(self):
            """It should Query Products by availability"""
            products = self._create_products(10)
            available_products = [product for product in products if product.available is True]
            available_count = len(available_products)        
            # test for available
            response = self.client.get(
                BASE_URL, query_string="available=true"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.get_json()
            self.assertEqual(len(data), available_count)
            # check the data just to be sure
            for product in data:
                self.assertEqual(product["available"], True)
    ######################################################################
    # LIST PRODUCTS
    ######################################################################
        @app.route("/products", methods=["GET"])
        def list_products():
        """Returns a list of Products"""
        app.logger.info("Request to list Products...")

        products = []
        name = request.args.get("name")
        category = request.args.get("category")
        available = request.args.get("available")

        if name:
            app.logger.info("Find by name: %s", name)
            products = Product.find_by_name(name)
        elif category:
            app.logger.info("Find by category: %s", category)
            # create enum from string
            category_value = getattr(Category, category.upper())
            products = Product.find_by_category(category_value)
        elif available:
            app.logger.info("Find by available: %s", available)
             # create bool from string
            available_value = available.lower() in ["true", "yes", "1"]
            products = Product.find_by_availability(available_value)
        else:
            app.logger.info("Find all")
            products = Product.all()

        results = [product.serialize() for product in products]
        app.logger.info("[%s] Products returned", len(results))
        return results, status.HTTP_200_OK
