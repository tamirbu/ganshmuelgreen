import unittest
import json
import os
from flask import Flask
from weight_service import app, init_db, load_data

class WeightServiceTest(unittest.TestCase):
    """
    Unit test suite for the WeightService API.

    This suite includes tests for the following scenarios:
    - Posting a weight record for "in" and "out" directions.
    - Error handling for invalid requests.
    - Retrieving weight records using GET requests with and without filters.
    - Verifying data loading from CSV and JSON files.

    The test suite uses Flask's test client to interact with the application
    and MySQL queries to validate data persistence.
    """

    @classmethod
    def setUpClass(cls):
        """
        Initialize the application and database before running tests.
        """
        init_db()
        load_data()
        cls.client = app.test_client()

    def test_post_weight_in(self):
        """
        Test posting a weight record with direction "in".

        This test verifies that the API successfully creates a weight session
        with the correct parameters and returns the expected response.
        """
        payload = {
            "direction": "in",
            "truck": "T-14409",
            "containers": "C-123,C-124",
            "weight": 1000,
            "unit": "kg",
            "produce": "orange",
            "force": False
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn("id", data)
        self.assertEqual(data["truck"], "T-14409")
        self.assertEqual(data["bruto"], 1000)

    def test_post_weight_out(self):
        """
        Test posting a weight record with direction "out".

        This test first posts an "in" record for the same truck, then posts
        an "out" record, verifying that the net weight and other calculations
        are correct.
        """
        payload_in = {
            "direction": "in",
            "truck": "T-14409",
            "containers": "C-123,C-124",
            "weight": 1000,
            "unit": "kg",
            "produce": "orange",
            "force": False
        }
        self.client.post('/weight', json=payload_in)

        payload_out = {
            "direction": "out",
            "truck": "T-14409",
            "containers": "C-123,C-124",
            "weight": 900,
            "unit": "kg",
            "force": False
        }
        response = self.client.post('/weight', json=payload_out)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn("id", data)
        self.assertEqual(data["truck"], "T-14409")
        self.assertEqual(data["truckTara"], 900)
        self.assertEqual(data["neto"], 100)

    def test_post_weight_error_handling(self):
        """
        Test error handling for posting a weight record with no prior "in" record.

        This test sends a request for direction "out" without a corresponding "in"
        record for the truck and verifies the appropriate error response.
        """
        payload = {
            "direction": "out",
            "truck": "T-99999",
            "containers": "C-123,C-124",
            "weight": 900,
            "unit": "kg",
            "force": False
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn("error", data)

    def test_get_weight(self):
        """
        Test retrieving all weight records.

        This test ensures that the API returns a list of weight records
        with the correct structure and content.
        """
        response = self.client.get('/weight')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_weight_filter(self):
        """
        Test retrieving weight records with a specific filter.

        This test verifies that only records matching the specified
        direction (e.g., "in") are returned by the API.
        """
        response = self.client.get('/weight?filter=in')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertTrue(all(item['direction'] == 'in' for item in data))

    def test_load_containers_csv(self):
        """
        Test loading container data from CSV files.

        This test validates that container data from the CSV files is
        correctly inserted into the database.
        """
        connection = app.config['MYSQL'].connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Containers_registered")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0)

    def test_load_trucks_json(self):
        """
        Test loading truck data from JSON files.

        This test ensures that truck data from the JSON file is
        accurately added to the database.
        """
        connection = app.config['MYSQL'].connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Containers_registered WHERE container_id LIKE 'T-%'")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0)

    def test_invalid_request(self):
        """
        Test handling of invalid request payloads.

        This test sends a request with an invalid direction and verifies
        that the API responds with an appropriate error message.
        """
        payload = {
            "direction": "invalid",
            "truck": "T-14409",
            "containers": "C-123,C-124",
            "weight": 1000,
            "unit": "kg",
            "force": False
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn("error", data)

    def test_missing_fields(self):
        """
        Test handling of requests with missing required fields.

        This test verifies that the API returns an error when a required
        field is missing from the payload.
        """
        payload = {
            "direction": "in",
            "truck": "T-14409"
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn("error", data)

if __name__ == '__main__':
    unittest.main()
