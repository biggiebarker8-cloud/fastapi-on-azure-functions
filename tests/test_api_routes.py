import unittest

from fastapi.testclient import TestClient

import WrapperFunction as wf


class KarmaApiRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(wf.app)
        self.original_auth_enabled = wf.AUTH_ENABLED
        self.original_auth_token = wf.AUTH_BEARER_TOKEN

        with wf.store.lock:
            wf.store.universes.clear()
            wf.store.characters.clear()
            wf.store.stories.clear()
            wf.store.assets.clear()

    def tearDown(self):
        wf.AUTH_ENABLED = self.original_auth_enabled
        wf.AUTH_BEARER_TOKEN = self.original_auth_token

    def test_auth_is_enforced_for_new_routes(self):
        wf.AUTH_ENABLED = True
        wf.AUTH_BEARER_TOKEN = "secret"

        response = self.client.get("/universes")
        self.assertEqual(response.status_code, 401)

        authed_response = self.client.get(
            "/universes",
            headers={"Authorization": "Bearer " + wf.AUTH_BEARER_TOKEN},
        )
        self.assertEqual(authed_response.status_code, 200)

    def test_get_universe_returns_404_for_missing_id(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/universes/missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Universe not found.")

    def test_characters_route_filters_by_universe(self):
        wf.AUTH_ENABLED = False

        u1 = self.client.post("/universes", json={"name": "u1"}).json()
        u2 = self.client.post("/universes", json={"name": "u2"}).json()

        self.client.post("/characters", json={"universe_id": u1["id"], "name": "c1"})
        self.client.post("/characters", json={"universe_id": u2["id"], "name": "c2"})

        all_items = self.client.get("/characters").json()
        filtered_items = self.client.get("/characters", params={"universe_id": u1["id"]}).json()

        self.assertEqual(len(all_items), 2)
        self.assertEqual(len(filtered_items), 1)
        self.assertEqual(filtered_items[0]["universe_id"], u1["id"])


if __name__ == "__main__":
    unittest.main()
