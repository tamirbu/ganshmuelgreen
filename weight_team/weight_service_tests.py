import unittest,sys,json
from flask import Flask
from flask.testing import FlaskClient 
from pathlib import Path
from weight_service import app, calculate_neto 
sys.path.append(str(Path(__file__).parent.resolve()))


class TestWeightAPI(unittest.TestCase):

    def setUp(self):
        """
        Set up the Flask test client before each test.
        """
        self.client = app.test_client()
        self.client.testing = True

    def test_health_endpoint(self):
        """
        Test the /health endpoint to ensure the service health.
        """
        tester = app.test_client(self)
        response = tester.get('/health')
        self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
        self.assertEqual(response.data.decode('utf-8'), "OK")  # Check the raw response data

    def test_get_weight_no_filters(self):
        """
        Test the /weight endpoint without filters (default behavior).
        """
        response = self.client.get('/weight')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_weight_with_filters(self):
        """
        Test the /weight endpoint with from, to, and filter query parameters.
        """
        params = {
            'from': '20250101000000',
            'to': '20250101235959',
            'filter': 'in,out'
        }
        response = self.client.get('/weight', query_string=params)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_post_weight_in(self):
        """
        Test the /weight endpoint for direction "in".
        """
        data = {
            "direction": "in",
            "truck": "T-12345",
            "containers": "C-123,C-456",
            "weight": 25000,
            "unit": "kg",
            "produce": "oranges"
        }
        response = self.client.post('/weight', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("session_id", response.json)

    def test_post_weight_out(self):
        """
        Test the /weight endpoint for direction "out".
        """
        data = {
            "direction": "out",
            "truck": "T-12345",
            "containers": "C-123,C-456",
            "weight": 15000,
            "unit": "kg",
            "produce": "oranges"
        }
        response = self.client.post('/weight', data=json.dumps(data), content_type='application/json')
        self.assertIn(response.status_code, [200, 400])  # Depending on session existence

    def test_post_weight_invalid_direction(self):
        """
        Test the /weight endpoint with an invalid direction.
        """
        data = {
            "direction": "invalid_direction",
            "truck": "T-12345",
            "containers": "C-123",
            "weight": 25000,
            "unit": "kg",
            "produce": "apples"
        }
        response = self.client.post('/weight', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_get_unknown_containers(self):
        """
        Test the /unknown endpoint to retrieve unknown containers.
        """
        response = self.client.get('/unknown')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_item_valid_id(self):
        """
        Test the /item/<id> endpoint with a valid ID.
        """
        item_id = "T-12345"
        response = self.client.get(f'/item/{item_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json)

    def test_get_item_invalid_id(self):
        """
        Test the /item/<id> endpoint with an invalid ID.
        """
        item_id = "INVALID_ID"
        response = self.client.get(f'/item/{item_id}')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    def test_post_batch_weight(self):
        """
        Test the /batch-weight endpoint with a valid file from Docker volume.
        """
        test_file_path = Path('/app/in/containers1.csv')  # File mounted from Docker volume
        data = {
            'file': str(test_file_path)
        }
        with open(test_file_path, 'rb') as test_file:
            response = self.client.post('/batch-weight', data={"file": test_file})
        self.assertIn(response.status_code, [200, 404])  # File might not exist
        self.assertIsInstance(response.json, dict)

    def test_session_valid_id(self):
        """
        Test the /session/<id> endpoint with a valid session ID.
        """
        session_id = 1  # Assume this ID exists in the database
        response = self.client.get(f'/session/{session_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json)
        self.assertIn("truck", response.json)
        self.assertIn("bruto", response.json)

    def test_session_invalid_id(self):
        """
        Test the /session/<id> endpoint with an invalid session ID.
        """
        session_id = 9999  # Assume this ID does not exist in the database
        response = self.client.get(f'/session/{session_id}')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    # def test_calculate_neto_valid_data(self):
    #     """
    #     Test the calculate_neto function with valid data.
    #     """
    #     bruto = 25000
    #     truck_tara = 10000
    #     container_taras = [3000, 2000]
    #     expected_neto = 25000 - 10000 - 5000
    #     response = self.client.post('/weight', data=json.dumps({
    #         "bruto": bruto,
    #         "truck_tara": truck_tara,
    #         "container_taras": container_taras
    #     }), content_type='application/json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json.get("neto"), expected_neto)
    
    def test_calculate_neto_function(self):
      bruto = 25000
      truck_tara = 10000
      container_taras = [3000, 2000]
      expected_neto = 25000 - 10000 - 5000
      self.assertEqual(calculate_neto(bruto, truck_tara, container_taras), expected_neto)

    def test_post_weight_force_override(self):
        """
        Test the /weight endpoint with force override enabled.
        """
        data = {
            "direction": "in",
            "truck": "T-54321",
            "containers": "C-789,C-101",
            "weight": 20000,
            "unit": "kg",
            "produce": "apples",
            "force": True
        }
        response = self.client.post('/weight', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("session_id", response.json)

    def test_post_weight_none(self):
        """
        Test the /weight endpoint for direction "none".
        """
        data = {
            "direction": "none",
            "truck": "na",
            "containers": "C-202,C-303",
            "weight": 10000,
            "unit": "kg"
        }
        response = self.client.post('/weight', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("session_id", response.json)


if __name__ == '__main__':
    # Define the output file for the test results
    output_file = Path("/app/outputs/test_results.log")

    # Run the tests and save results to the file
    with output_file.open("w") as f:
        test_runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=test_runner, exit=True)
