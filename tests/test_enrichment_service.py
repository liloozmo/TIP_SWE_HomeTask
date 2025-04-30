import unittest
from unittest.mock import patch, MagicMock
from app.enrichment_service import EnrichmentService
from app.alert import Alert

class TestEnrichmentService(unittest.TestCase):

    def setUp(self):
        """
        Initialize the EnrichmentService before each test.
        """
        # Arrange
        self.enrichment_service = EnrichmentService()

    @patch("app.enrichment_service.requests.get")
    def test_query_virustotal_success(self, mock_get):
        """
        Test querying VirusTotal successfully returns parsed JSON.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": "some_data"}
        mock_get.return_value = mock_response

        # Act
        result = self.enrichment_service.query_virustotal("1.2.3.4")

        # Assert
        self.assertEqual(result, {"data": "some_data"})

    @patch("app.enrichment_service.requests.get")
    def test_query_virustotal_failure(self, mock_get):
        """
        Test querying VirusTotal handles exceptions properly.
        """
        # Arrange
        mock_get.side_effect = Exception("API failed")

        # Act
        result = self.enrichment_service.query_virustotal("1.2.3.4")

        # Assert
        self.assertEqual(result, {}, "Should return empty dict on failure")

    def test_is_ioc_malicious_from_response_true(self):
        """
        Test determining an IoC is malicious.
        """
        # Arrange
        mock_response = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 5
                    }
                }
            }
        }

        # Act
        result = self.enrichment_service.is_ioc_malicious_from_response(mock_response)

        # Assert
        self.assertTrue(result)

    def test_is_ioc_malicious_from_response_false(self):
        """
        Test that determine if an IoC is not malicious.
        """
        # Arrange
        mock_response = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 0
                    }
                }
            }
        }

        # Act
        result = self.enrichment_service.is_ioc_malicious_from_response(mock_response)

        # Assert
        self.assertFalse(result)

    @patch.object(EnrichmentService, 'query_virustotal')
    @patch.object(EnrichmentService, 'is_ioc_malicious_from_response')
    def test_analyze_response(self, mock_is_malicious, mock_query_vt):
        """
        Test analyzing an alert and building the report.
        """
        # Arrange
        alert = Alert(["1.1.1.1", "2.2.2.2"])
        mock_query_vt.return_value = {}  #simulate API call
        mock_is_malicious.side_effect = [True, False]  # first IOC malicious, second not

        # Act
        report = self.enrichment_service.analyze_response(alert)

        # Assert
        self.assertEqual(report["Severity"], 50)
        self.assertEqual(len(report["IoCs"]), 2)
        self.assertEqual(report["IoCs"][0]["IsMalicious"], True)
        self.assertEqual(report["IoCs"][1]["IsMalicious"], False)
        self.assertEqual(report["AlertId"], alert.id)

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("app.enrichment_service.ensure_output_directory")
    def test_save_report_to_file(self, mock_ensure_output, mock_open_file):
        """
        Test saving report to a JSON file without crashing.
        """
        # Arrange
        report = {
            "AlertId": "test-id",
            "Severity": 100,
            "IoCs": [{"IoC": "1.2.3.4", "IsMalicious": True}]
        }

        # Act
        self.enrichment_service.save_report_to_file(report)

        # Assert
        mock_open_file.assert_called()
        mock_ensure_output.assert_called_once()
