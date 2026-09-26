import unittest

from fastapi.testclient import TestClient

from product_hub import app


class ProductHubTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_sales_ios_filter_returns_mobile_sales_products(self):
        response = self.client.get("/api/products", params={"platform": "iOS", "use_case": "sales"})
        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertGreaterEqual(body["summary"]["total_products"], 1)
        self.assertTrue(all("iOS" in item["platforms"] for item in body["items"]))
        self.assertTrue(all("sales" in item["use_cases"] for item in body["items"]))

    def test_available_only_respects_subscriptions(self):
        locked_response = self.client.get("/api/products", params={"available_only": "true"})
        unlocked_response = self.client.get(
            "/api/products",
            params=[
                ("available_only", "true"),
                ("entitlement", "azure"),
                ("entitlement", "dynamics-365-sales"),
                ("entitlement", "microsoft-365"),
                ("entitlement", "microsoft-365-copilot"),
                ("entitlement", "power-bi-pro"),
            ],
        )

        self.assertEqual(locked_response.status_code, 200)
        self.assertEqual(unlocked_response.status_code, 200)
        self.assertLess(locked_response.json()["summary"]["total_products"], unlocked_response.json()["summary"]["total_products"])
        self.assertTrue(all(item["accessible"] for item in unlocked_response.json()["items"]))

    def test_product_detail_returns_404_for_unknown_product(self):
        response = self.client.get("/api/products/missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Product not found.")

    def test_dashboard_renders_product_hub_page(self):
        response = self.client.get("/", params={"use_case": "sales", "platform": "iOS"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Product Hub", response.text)
        self.assertIn("Microsoft Edge", response.text)
        self.assertIn("Dynamics 365 Sales", response.text)


if __name__ == "__main__":
    unittest.main()
