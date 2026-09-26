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

    def test_identity_patch_updates_only_supplied_fields(self):
        wf.AUTH_ENABLED = False

        original = self.client.get("/identity").json()
        response = self.client.patch("/identity", json={"lore": "new lore"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], original["name"])
        self.assertEqual(body["tone"], original["tone"])
        self.assertEqual(body["lore"], "new lore")

    def test_knowledge_base_routes_return_seeded_entries(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()}

        self.assertIn("bytedanabe", ids)
        self.assertIn("lark", ids)
        self.assertIn("wix", ids)
        self.assertIn("website-building", ids)

    def test_knowledge_base_route_supports_alias_lookup(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases/bytedance")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "bytedanabe")

    def test_knowledge_base_route_returns_404_for_unknown_entry(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Knowledge base not found.")

    def test_knowledge_base_route_returns_wix_content(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases/wix")
        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(body["id"], "wix")
        self.assertTrue(any(section["heading"] == "Wix platform fundamentals" for section in body["sections"]))

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

    def test_story_crossover_route_failure_and_success(self):
        wf.AUTH_ENABLED = False

        u1 = self.client.post("/universes", json={"name": "u1"}).json()
        u2 = self.client.post("/universes", json={"name": "u2"}).json()
        character = self.client.post("/characters", json={"universe_id": u2["id"], "name": "guest"}).json()

        failure = self.client.post(
            "/stories",
            json={
                "universe_id": u1["id"],
                "title": "bad",
                "arc": "arc",
                "character_ids": [character["id"]],
            },
        )
        self.assertEqual(failure.status_code, 400)

        success = self.client.post(
            "/stories",
            json={
                "universe_id": u1["id"],
                "title": "ok",
                "arc": "arc",
                "character_ids": [character["id"]],
                "allow_crossover": True,
                "crossover_universe_ids": [u2["id"]],
            },
        )
        self.assertEqual(success.status_code, 200)
        self.assertTrue(success.json()["continuity_notes"])

    def test_restore_asset_route_restores_prior_metadata(self):
        wf.AUTH_ENABLED = False

        universe = self.client.post("/universes", json={"name": "u1"}).json()
        asset = self.client.post(
            "/merch-designs",
            json={
                "universe_id": universe["id"],
                "product_type": "hoodie",
                "theme_prompt": "v1",
                "print_area": "front",
            },
        ).json()

        with wf.store.lock:
            wf.store.assets[asset["id"]].metadata["theme_prompt"] = "v2"
            wf.store.append_asset_version(
                asset["id"],
                "updated",
                metadata_snapshot=dict(wf.store.assets[asset["id"]].metadata),
            )

        restored = self.client.post(f"/assets/{asset['id']}/versions/1/restore")

        self.assertEqual(restored.status_code, 200)
        body = restored.json()
        self.assertEqual(body["metadata"]["theme_prompt"], "v1")
        self.assertEqual(body["versions"][-1]["source_version"], 1)

    def test_asset_version_summaries_do_not_echo_raw_prompts(self):
        wf.AUTH_ENABLED = False

        universe = self.client.post("/universes", json={"name": "u1"}).json()
        merch_asset = self.client.post(
            "/merch-designs",
            json={
                "universe_id": universe["id"],
                "product_type": "hoodie",
                "theme_prompt": "secret launch plan",
                "print_area": "front",
            },
        ).json()
        image_asset = self.client.post(
            "/image-edits",
            json={
                "universe_id": universe["id"],
                "source_asset_id": merch_asset["id"],
                "operation": "iterative_revision",
                "instructions": "replace the logo with project ember",
            },
        ).json()

        self.assertNotIn("secret launch plan", merch_asset["versions"][0]["content_summary"])
        self.assertNotIn("project ember", image_asset["versions"][0]["content_summary"])


if __name__ == "__main__":
    unittest.main()
