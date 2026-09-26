import unittest

from WrapperFunction.models import AssistantIdentity, ImageEditRequest, MerchDesignCreate, UniverseCreate
from WrapperFunction.services import KarmaService
from WrapperFunction.storage import InMemoryStore


class KarmaServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.service = KarmaService(
            store=self.store,
            identity=AssistantIdentity(name="Karma", tone="direct"),
        )
        self.universe = self.service.create_universe(UniverseCreate(name="Test Universe"))

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
        self.assertEqual(restored_asset.current_version, 3)
        self.assertEqual(restored_asset.versions[-1].restored_from_version, 1)
        self.assertEqual(restored_asset.versions[-1].reference_id_snapshot, original_reference)


if __name__ == "__main__":
    unittest.main()
