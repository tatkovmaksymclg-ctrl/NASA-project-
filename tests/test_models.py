import unittest
from models.health_model import assess_measurement
from models.resource_optimizer import allocate_medical_kits

class ModelTests(unittest.TestCase):
    def test_normal_measurement(self):
        result = assess_measurement({
            "heart_rate": 72, "spo2": 98, "temperature": 36.7,
            "systolic": 118, "diastolic": 76, "respiration": 15
        })
        self.assertEqual(result["risk_level"], "Норма")

    def test_critical_measurement(self):
        result = assess_measurement({
            "heart_rate": 145, "spo2": 85, "temperature": 39,
            "systolic": 175, "diastolic": 110, "respiration": 30
        })
        self.assertEqual(result["risk_level"], "Критичний")

    def test_resource_allocation(self):
        result = allocate_medical_kits({"A": 1, "B": 5, "C": 3}, 2)
        self.assertEqual(result["assigned"], ["B", "C"])

if __name__ == "__main__":
    unittest.main()
