import unittest

from pydantic import ValidationError

from fastapi import HTTPException

from WrapperFunction.actor_context import reset_current_actor, set_current_actor
from WrapperFunction.models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRequestCreate,
    AssistantIdentity,
    ImageEditRequest,
    LearningPolicyUpdate,
    MerchDesignCreate,
    PlaybookCreate,
    PluginDraftCreate,
    PluginToggleRequest,
    PluginVersionUpdate,
    SkillCreate,
    SkillToggleRequest,
    UniverseCreate,
)
from WrapperFunction.services import KarmaService
from WrapperFunction.storage import InMemoryStore


class KarmaServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.actor_token = set_current_actor("owner")
        self.store = InMemoryStore()
        self.service = KarmaService(
            store=self.store,
            identity=AssistantIdentity(name="Karma", tone="direct"),
        )
        self.universe = self.service.create_universe(UniverseCreate(name="Test Universe"))

    def tearDown(self) -> None:
        reset_current_actor(self.actor_token)

    def test_merch_design_creates_initial_version_with_snapshot_and_reference(self) -> None:
        asset = self.service.create_merch_design(
            MerchDesignCreate(
                universe_id=self.universe.id,
                product_type="hoodie",
                print_area="front",
                theme_prompt="launch art",
                variants=["black"],
                export_formats=["png", "svg"],
            )
        )

        self.assertEqual(asset.current_version, 1)
        self.assertEqual(len(asset.versions), 1)
        self.assertEqual(asset.versions[0].metadata_snapshot["theme_prompt"], "launch art")
        self.assertEqual(asset.versions[0].reference_id_snapshot, asset.reference_id)

    def test_image_edit_creates_initial_version_with_source_reference(self) -> None:
        source_asset = self.service.create_merch_design(
            MerchDesignCreate(
                universe_id=self.universe.id,
                product_type="hoodie",
                print_area="front",
                theme_prompt="source art",
            )
        )

        edited_asset = self.service.edit_image(
            ImageEditRequest(
                universe_id=self.universe.id,
                source_asset_id=source_asset.id,
                operation="iterative_revision",
                instructions="make it brighter",
            )
        )

        self.assertEqual(edited_asset.current_version, 1)
        self.assertEqual(len(edited_asset.versions), 1)
        self.assertEqual(edited_asset.reference_id, source_asset.id)
        self.assertEqual(edited_asset.versions[0].reference_id_snapshot, source_asset.id)
        self.assertEqual(edited_asset.versions[0].metadata_snapshot["instructions"], "make it brighter")

    def test_restore_replays_snapshot_and_records_restore_provenance(self) -> None:
        asset = self.service.create_merch_design(
            MerchDesignCreate(
                universe_id=self.universe.id,
                product_type="hoodie",
                print_area="front",
                theme_prompt="launch art",
            )
        )
        original_reference = asset.reference_id

        asset.metadata["theme_prompt"] = "updated art"
        asset.reference_id = "design_override"
        self.store.append_asset_version(asset.id, "manual update")

        restored_asset = self.service.restore_asset_version(asset.id, 1)

        self.assertEqual(restored_asset.metadata["theme_prompt"], "launch art")
        self.assertEqual(restored_asset.reference_id, original_reference)
        self.assertEqual(restored_asset.current_version, 4)
        self.assertEqual(restored_asset.versions[-1].source_version, 1)
        self.assertEqual(restored_asset.versions[-1].restored_from_version, 1)
        self.assertEqual(restored_asset.versions[-1].reference_id_snapshot, original_reference)

    def test_tshirt_sleeve_print_area_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            MerchDesignCreate(
                universe_id=self.universe.id,
                product_type="tshirt",
                print_area="sleeve",
                theme_prompt="invalid combo",
            )

    def test_plugin_promotion_requires_owner_approval(self) -> None:
        plugin = self.service.draft_plugin(
            PluginDraftCreate(
                name="shop-sync",
                owner="owner",
                plugin_type="integration",
                capabilities=["read_data", "run_workflow"],
            )
        )
        self.service.validate_plugin(plugin.id)
        self.service.stage_plugin(plugin.id)
        approval = self.service.submit_plugin_for_approval(plugin.id)

        with self.assertRaises(HTTPException):
            self.service.toggle_plugin(plugin.id, PluginToggleRequest(enabled=True, requested_by="owner"))

        decided = self.service.decide_approval(approval.id, ApprovalDecision(approve=True, decided_by="not-owner"))
        self.assertEqual(decided.decided_by, "owner")
        enabled = self.service.toggle_plugin(plugin.id, PluginToggleRequest(enabled=True, requested_by="owner"))
        self.assertEqual(enabled.lifecycle_state, "enabled")

    def test_default_social_and_research_plugins_are_seeded(self) -> None:
        plugin_ids = set(self.store.plugins)
        self.assertIn("plugin_facebook_pages", plugin_ids)
        self.assertIn("plugin_instagram_business", plugin_ids)
        self.assertIn("plugin_web_research", plugin_ids)

        facebook = self.store.plugins["plugin_facebook_pages"]
        instagram = self.store.plugins["plugin_instagram_business"]
        web_research = self.store.plugins["plugin_web_research"]

        self.assertEqual(facebook.lifecycle_state, "draft")
        self.assertEqual(instagram.lifecycle_state, "draft")
        self.assertEqual(web_research.lifecycle_state, "draft")
        self.assertTrue(facebook.external_api_access)
        self.assertTrue(instagram.external_api_access)
        self.assertTrue(web_research.external_api_access)
        self.assertEqual(web_research.config["platform"], "open-web")

    def test_plugin_cannot_enable_without_approved_request(self) -> None:
        plugin = self.service.draft_plugin(
            PluginDraftCreate(
                name="metrics-sync",
                owner="owner",
                plugin_type="analytics",
                capabilities=["read_data", "analyze_metrics"],
            )
        )
        self.service.validate_plugin(plugin.id)
        self.service.stage_plugin(plugin.id)

        with self.assertRaises(HTTPException):
            self.service.toggle_plugin(plugin.id, PluginToggleRequest(enabled=True, requested_by="owner"))

    def test_plugin_cannot_enable_with_non_owner_gated_approval(self) -> None:
        plugin = self.service.draft_plugin(
            PluginDraftCreate(
                name="approval-bypass",
                owner="owner",
                plugin_type="integration",
                capabilities=["read_data", "run_workflow"],
            )
        )
        self.service.validate_plugin(plugin.id)
        self.service.stage_plugin(plugin.id)

        bypass_approval = self.store.add_approval(
            ApprovalRequest(
                action_type="plugin_publish",
                target_type="plugin",
                target_id=plugin.id,
                requested_by="reviewer",
                required_owner_approval=False,
                status="approved",
                decided_by="reviewer",
            )
        )

        plugin = self.store.plugins[plugin.id]
        plugin.approval_request_id = bypass_approval.id
        plugin.lifecycle_state = "staged"

        with self.assertRaises(HTTPException):
            self.service.toggle_plugin(plugin.id, PluginToggleRequest(enabled=True, requested_by="owner"))

    def test_owner_gated_actions_require_actor_context(self) -> None:
        token = set_current_actor("")
        try:
            with self.assertRaises(HTTPException) as context:
                self.service.request_learning_policy_change()
        finally:
            reset_current_actor(token)

        self.assertEqual(context.exception.status_code, 403)

    def test_plugin_version_update_requires_live_or_rolled_back_state(self) -> None:
        plugin = self.service.draft_plugin(
            PluginDraftCreate(
                name="shop-sync",
                owner="owner",
                plugin_type="integration",
                capabilities=["read_data", "run_workflow"],
            )
        )
        self.service.validate_plugin(plugin.id)
        self.service.stage_plugin(plugin.id)

        with self.assertRaises(HTTPException) as context:
            self.service.update_plugin_version(plugin.id, PluginVersionUpdate(version="0.2.0"))

        self.assertEqual(context.exception.status_code, 400)

    def test_rejected_plugin_update_preserves_live_version_and_state(self) -> None:
        plugin = self.service.draft_plugin(
            PluginDraftCreate(
                name="shop-sync",
                owner="owner",
                plugin_type="integration",
                capabilities=["read_data", "run_workflow"],
            )
        )
        self.service.validate_plugin(plugin.id)
        self.service.stage_plugin(plugin.id)
        publish_approval = self.service.submit_plugin_for_approval(plugin.id)
        self.service.decide_approval(publish_approval.id, ApprovalDecision(approve=True, decided_by="not-owner"))

        updated_plugin = self.store.plugins[plugin.id]
        self.assertEqual(publish_approval.requested_by, "owner")
        self.assertEqual(updated_plugin.lifecycle_state, "enabled")

        update_approval = self.service.update_plugin_version(
            plugin.id,
            PluginVersionUpdate(version="0.2.0", requested_by="not-owner"),
        )
        updated_plugin = self.store.plugins[plugin.id]
        self.assertEqual(update_approval.requested_by, "owner")
        self.assertEqual(updated_plugin.version, "0.1.0")
        self.assertEqual(updated_plugin.pending_version, "0.2.0")
        self.assertEqual(updated_plugin.lifecycle_state, "pending_approval")

        self.service.decide_approval(update_approval.id, ApprovalDecision(approve=False, decided_by="not-owner"))

        updated_plugin = self.store.plugins[plugin.id]
        self.assertEqual(updated_plugin.version, "0.1.0")
        self.assertIsNone(updated_plugin.pending_version)
        self.assertEqual(updated_plugin.lifecycle_state, "enabled")
        self.assertEqual(updated_plugin.approval_request_id, publish_approval.id)

        disabled = self.service.toggle_plugin(plugin.id, PluginToggleRequest(enabled=False, requested_by="owner"))
        self.assertEqual(disabled.lifecycle_state, "disabled")
        reenabled = self.service.toggle_plugin(plugin.id, PluginToggleRequest(enabled=True, requested_by="owner"))
        self.assertEqual(reenabled.lifecycle_state, "enabled")

    def test_approved_plugin_update_applies_pending_version(self) -> None:
        plugin = self.service.draft_plugin(
            PluginDraftCreate(
                name="shop-sync",
                owner="owner",
                plugin_type="integration",
                capabilities=["read_data", "run_workflow"],
            )
        )
        self.service.validate_plugin(plugin.id)
        self.service.stage_plugin(plugin.id)
        publish_approval = self.service.submit_plugin_for_approval(plugin.id)
        self.service.decide_approval(publish_approval.id, ApprovalDecision(approve=True, decided_by="owner"))

        update_approval = self.service.update_plugin_version(
            plugin.id,
            PluginVersionUpdate(version="0.2.0", requested_by="owner"),
        )
        self.service.decide_approval(update_approval.id, ApprovalDecision(approve=True, decided_by="owner"))

        updated_plugin = self.store.plugins[plugin.id]
        self.assertEqual(updated_plugin.version, "0.2.0")
        self.assertIsNone(updated_plugin.pending_version)
        self.assertEqual(updated_plugin.approval_request_id, update_approval.id)
        self.assertEqual(updated_plugin.lifecycle_state, "enabled")

    def test_skill_external_access_requires_approval(self) -> None:
        skill = self.service.create_skill(
            SkillCreate(
                name="tiktok-analytics",
                owner="owner",
                skill_type="analytics",
                capabilities=["analyze_metrics", "use_external_api"],
                external_api_access=True,
            )
        )
        self.assertFalse(skill.enabled)
        self.assertIsNotNone(skill.approval_request_id)

        with self.assertRaises(HTTPException):
            self.service.toggle_skill(skill.id, SkillToggleRequest(enabled=True, requested_by="owner"))

        assert skill.approval_request_id is not None
        self.service.decide_approval(skill.approval_request_id, ApprovalDecision(approve=True, decided_by="owner"))
        enabled = self.service.toggle_skill(skill.id, SkillToggleRequest(enabled=True, requested_by="owner"))
        self.assertTrue(enabled.enabled)

    def test_skill_is_not_enabled_by_unrelated_approval_decision(self) -> None:
        skill = self.service.create_skill(
            SkillCreate(
                name="guardian",
                owner="owner",
                skill_type="analytics",
                capabilities=["analyze_metrics", "use_external_api"],
                external_api_access=True,
            )
        )
        unrelated = self.service.create_approval_request(
            ApprovalRequestCreate(
                action_type="skill_external_access",
                target_type="skill",
                target_id=skill.id,
                required_owner_approval=False,
            )
        )

        self.service.decide_approval(unrelated.id, ApprovalDecision(approve=True, decided_by="reviewer"))

        self.assertFalse(self.store.skills[skill.id].enabled)

    def test_learning_policy_change_requires_approved_request(self) -> None:
        with self.assertRaises(HTTPException):
            self.service.update_learning_policy(
                LearningPolicyUpdate(auto_approve_low_risk_tuning=True, approval_request_id=None)
            )

        policy_approval = self.service.request_learning_policy_change()
        self.service.decide_approval(policy_approval.id, ApprovalDecision(approve=True, decided_by="owner"))
        updated = self.service.update_learning_policy(
            LearningPolicyUpdate(auto_approve_low_risk_tuning=True, approval_request_id=policy_approval.id)
        )
        self.assertTrue(updated["learning_policy"].auto_approve_low_risk_tuning)

    def test_learning_policy_approval_cannot_be_reused(self) -> None:
        policy_approval = self.service.request_learning_policy_change()
        self.service.decide_approval(policy_approval.id, ApprovalDecision(approve=True, decided_by="owner"))
        self.service.update_learning_policy(
            LearningPolicyUpdate(auto_approve_low_risk_tuning=True, approval_request_id=policy_approval.id)
        )

        with self.assertRaises(HTTPException) as context:
            self.service.update_learning_policy(
                LearningPolicyUpdate(auto_approve_low_risk_tuning=False, approval_request_id=policy_approval.id)
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_learning_policy_rejects_non_owner_gated_approval(self) -> None:
        bypass = self.store.add_approval(
            ApprovalRequest(
                action_type="learning_rule_change",
                target_type="learning_policy",
                target_id="learning_policy",
                requested_by="reviewer",
                required_owner_approval=False,
                status="approved",
                decided_by="reviewer",
            )
        )

        with self.assertRaises(HTTPException):
            self.service.update_learning_policy(
                LearningPolicyUpdate(auto_approve_low_risk_tuning=True, approval_request_id=bypass.id)
            )

    def test_low_risk_playbook_can_auto_activate_when_policy_enabled(self) -> None:
        policy_approval = self.service.request_learning_policy_change()
        self.service.decide_approval(policy_approval.id, ApprovalDecision(approve=True, decided_by="owner"))
        self.service.update_learning_policy(
            LearningPolicyUpdate(auto_approve_low_risk_tuning=True, approval_request_id=policy_approval.id)
        )

        playbook = self.service.propose_playbook(
            PlaybookCreate(
                title="Campaign recap",
                trigger="positive campaign outcomes",
                actions=["save template", "reuse hooks"],
                risk_level="low",
                requested_by="owner",
            )
        )
        self.assertEqual(playbook.status, "active")


if __name__ == "__main__":
    unittest.main()
