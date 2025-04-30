from app.alert import Alert
import unittest

class TestAlert(unittest.TestCase):
    def test_alert_creation(self):
        ioc = ["1.2.3.4","10.20.30.40"]
        alert = Alert(ioc=ioc)

        self.assertEqual(alert.ioc, ioc, "iocs were not assigned correctly")
        self.assertIsNone(alert.severity,"alert severity should be none")
        self.assertIsInstance(alert.id,str,"alert id should be string")

    def test_alert_severity(self):
        alert = Alert(["1.1.1.1"])
        alert.severity = 80

        self.assertEqual(alert.severity,80,"alert severity is not updated correctly")

if __name__ == "__main__":
    unittest.main()