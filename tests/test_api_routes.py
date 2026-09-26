import unittest

from fastapi.testclient import TestClient

import WrapperFunction as wf


class AssistantApiRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(wf.app)
        self.original_auth_enabled = wf.AUTH_ENABLED
        self.original_auth_token = wf.AUTH_BEARER_TOKEN

        with wf.store.lock:
            wf.store.universes.clear()
            wf.store.characters.clear()
            wf.store.stories.clear()
            wf.store.assets.clear()
            wf.store.plugins.clear()
            wf.store.skills.clear()
            wf.store.approvals.clear()
            wf.store.learning_events.clear()
            wf.store.playbooks.clear()

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

    def test_approval_routes_always_use_request_actor_context(self):
        wf.AUTH_ENABLED = False

        response = self.client.post(
            "/approvals",
            headers={"X-Actor-Id": "reviewer-1"},
            json={
                "action_type": "learning_rule_change",
                "target_type": "learning_policy",
                "target_id": "learning_policy",
                "requested_by": "spoofed",
                "required_owner_approval": False,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["requested_by"], "reviewer-1")

    def test_authenticated_requests_ignore_actor_spoofing_headers(self):
        wf.AUTH_ENABLED = True
        wf.AUTH_BEARER_TOKEN = "secret"

        response = self.client.post(
            "/approvals",
            headers={"Authorization": "Bearer " + wf.AUTH_BEARER_TOKEN, "X-Actor-Id": "attacker"},
            json={
                "action_type": "learning_rule_change",
                "target_type": "learning_policy",
                "target_id": "learning_policy",
                "requested_by": "spoofed",
                "required_owner_approval": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["requested_by"], "owner")

    def test_plugin_approval_request_uses_request_actor_context(self):
        wf.AUTH_ENABLED = False

        plugin = self.client.post(
            "/plugins/drafts",
            json={
                "name": "shop-sync",
                "owner": "owner",
                "plugin_type": "integration",
                "capabilities": ["read_data", "run_workflow"],
            },
        ).json()
        self.client.post(f"/plugins/{plugin['id']}/validate")
        self.client.post(f"/plugins/{plugin['id']}/staging-test")

        response = self.client.post(
            f"/plugins/{plugin['id']}/approval-request",
            headers={"X-Actor-Id": "reviewer-2"},
            json={"reason": "ship it"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["requested_by"], "reviewer-2")

    def test_plugin_kill_route_uses_request_actor_context_for_audit(self):
        wf.AUTH_ENABLED = False

        plugin = self.client.post(
            "/plugins/drafts",
            json={
                "name": "kill-switch",
                "owner": "owner",
                "plugin_type": "integration",
                "capabilities": ["read_data", "run_workflow"],
            },
        ).json()

        response = self.client.post(
            f"/plugins/{plugin['id']}/kill",
            headers={"X-Actor-Id": "reviewer-3"},
            json={"requested_by": "spoofed", "reason": "safety stop"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("reviewer-3: kill switch - safety stop", response.json()["rollback_history"][-1])

    def test_authenticated_kill_requests_ignore_actor_spoofing_headers(self):
        wf.AUTH_ENABLED = True
        wf.AUTH_BEARER_TOKEN = "secret"

        plugin = self.client.post(
            "/plugins/drafts",
            headers={"Authorization": "Bearer " + wf.AUTH_BEARER_TOKEN},
            json={
                "name": "kill-auth",
                "owner": "owner",
                "plugin_type": "integration",
                "capabilities": ["read_data", "run_workflow"],
            },
        ).json()

        response = self.client.post(
            f"/plugins/{plugin['id']}/kill",
            headers={"Authorization": "Bearer " + wf.AUTH_BEARER_TOKEN, "X-Actor-Id": "attacker"},
            json={"requested_by": "spoofed", "reason": "safety stop"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("owner: kill switch - safety stop", response.json()["rollback_history"][-1])

    def test_knowledge_base_routes_return_seeded_entries(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases")
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()}

        self.assertIn("bytedanabe", ids)
        self.assertIn("lark", ids)
        self.assertIn("wix", ids)
        self.assertIn("website-building", ids)
        self.assertIn("shopify", ids)
        self.assertIn("amazon", ids)
        self.assertIn("sales-strategies-analytics", ids)

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

    def test_knowledge_base_route_returns_shopify_content(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases/shopify")
        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(body["id"], "shopify")
        self.assertTrue(any(section["heading"] == "Store analytics and experimentation" for section in body["sections"]))

    def test_knowledge_base_route_supports_amazon_alias_lookup(self):
        wf.AUTH_ENABLED = False

        response = self.client.get("/knowledge-bases/seller-central")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "amazon")

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
