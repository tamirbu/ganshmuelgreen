import unittest
import json
import csv
from flask import Flask
from weight_rervice import app

class WeightServiceTest(unittest.TestCase):
    """
    Unit test suite for the WeightService API.

    This suite uses mock data from provided CSV and JSON files to simulate
    real-world inputs and validate API functionality without relying on
    a live database.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the Flask test client and load mock data from CSV and JSON files.
        Ensure the file paths match the provided structure.
        """
        cls.client = app.test_client()
        cls.mock_containers = []
        cls.mock_trucks = []

        # Load mock data from containers1.csv
        with open('./sample_files/sample_uploads/containers1.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.mock_containers.append({
                    "id": row['id'],
                    "weight": float(row['kg']),
                    "unit": "kg"
                })

        # Load mock data from containers2.csv
        with open('./sample_files/sample_uploads/containers2.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.mock_containers.append({
                    "id": row['id'],
                    "weight": float(row['lbs']) * 0.453592,  # Convert lbs to kg
                    "unit": "kg"
                })

        # Load mock data from trucks.json
        with open('./sample_files/sample_uploads/trucks.json', 'r') as f:
            cls.mock_trucks = json.load(f)

    def test_post_weight_in(self):
        """
        Test posting a weight record with direction "in" using mock data.
        """
        truck = self.mock_trucks[0]
        containers = self.mock_containers[:2]

        # Calculate Bruto
        sum_container_weights = sum(container['weight'] for container in containers)
        bruto = 1000 + truck['weight'] * 0.453592 + sum_container_weights  # Convert truck weight to kg

        payload = {
            "direction": "in",
            "truck": truck['id'],
            "containers": ",".join([container['id'] for container in containers]),
            "weight": bruto,
            "unit": "kg",
            "produce": "apples",
            "force": False
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn("id", data)
        self.assertEqual(data["truck"], truck['id'])
        self.assertEqual(data["bruto"], bruto)

    def test_post_weight_out(self):
        """
        Test posting a weight record with direction "out" using mock data.
        """
        truck = self.mock_trucks[1]
        containers = self.mock_containers[2:4]

        # Simulate a prior "in" request
        sum_container_weights_in = sum(container['weight'] for container in containers)
        bruto_in = 1200 + truck['weight'] * 0.453592 + sum_container_weights_in  # Convert truck weight to kg

        payload_in = {
            "direction": "in",
            "truck": truck['id'],
            "containers": ",".join([container['id'] for container in containers]),
            "weight": bruto_in,
            "unit": "kg",
            "produce": "oranges",
            "force": False
        }
        self.client.post('/weight', json=payload_in)

        # Now simulate an "out" request
        sum_container_weights_out = sum(container['weight'] for container in containers)
        bruto_out = 1100 + truck['weight'] * 0.453592 + sum_container_weights_out  # Convert truck weight to kg

        payload_out = {
            "direction": "out",
            "truck": truck['id'],
            "containers": ",".join([container['id'] for container in containers]),
            "weight": bruto_out,
            "unit": "kg",
            "force": False
        }
        response = self.client.post('/weight', json=payload_out)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn("id", data)
        self.assertEqual(data["truck"], truck['id'])
        self.assertEqual(data["truckTara"], truck['weight'] * 0.453592)
        self.assertEqual(data["neto"], 1100)

    def test_get_weight(self):
        """
        Test retrieving all weight records (mock data only).
        """
        response = self.client.get('/weight')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_invalid_request(self):
        """
        Test handling of invalid request payloads using mock data.
        """
        payload = {
            "direction": "invalid",
            "truck": self.mock_trucks[0]['id'],
            "containers": ",".join([container['id'] for container in self.mock_containers[:2]]),
            "weight": 1500,
            "unit": "kg",
            "force": False
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn("error", data)

    def test_missing_fields(self):
        """
        Test handling of requests with missing required fields using mock data.
        """
        payload = {
            "direction": "in",
            "truck": self.mock_trucks[0]['id']
        }
        response = self.client.post('/weight', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn("error", data)

if __name__ == '__main__':
    unittest.main()
