import unittest

from fastapi import HTTPException

from WrapperFunction.models import (
    AssistantIdentity,
    CharacterCreate,
    MerchDesignCreate,
    StoryCreate,
    UniverseCreate,
)
from WrapperFunction.services import KarmaService
from WrapperFunction.storage import InMemoryStore


class KarmaServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryStore()
        self.service = KarmaService(
            store=self.store,
            identity=AssistantIdentity(
                name="Karma",
                tone="direct",
                authority_rule="User is the final decision-maker; assistant advises and executes.",
            ),
        )

    def _create_universe(self, name: str):
        return self.service.create_universe(UniverseCreate(name=name))

    def test_create_story_same_universe(self):
        universe = self._create_universe("u1")
        character = self.service.create_character(
            CharacterCreate(universe_id=universe.id, name="hero")
        )

        story = self.service.create_story(
            StoryCreate(
                universe_id=universe.id,
                title="story",
                arc="arc",
                character_ids=[character.id],
            )
        )

        self.assertEqual(story.universe_id, universe.id)
        self.assertEqual(story.continuity_notes, [])

    def test_create_story_allows_crossover_when_enabled(self):
        primary = self._create_universe("primary")
        secondary = self._create_universe("secondary")
        character = self.service.create_character(
            CharacterCreate(universe_id=secondary.id, name="guest")
        )

        story = self.service.create_story(
            StoryCreate(
                universe_id=primary.id,
                title="crossover",
                arc="arc",
                character_ids=[character.id],
                allow_crossover=True,
                crossover_universe_ids=[secondary.id],
            )
        )

        self.assertEqual(story.universe_id, primary.id)
        self.assertTrue(story.continuity_notes)

    def test_create_story_rejects_invalid_crossover(self):
        primary = self._create_universe("primary")
        secondary = self._create_universe("secondary")
        character = self.service.create_character(
            CharacterCreate(universe_id=secondary.id, name="guest")
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_story(
                StoryCreate(
                    universe_id=primary.id,
                    title="bad crossover",
                    arc="arc",
                    character_ids=[character.id],
                )
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_merch_design_rejects_invalid_print_area(self):
        universe = self._create_universe("primary")

        with self.assertRaises(HTTPException) as context:
            self.service.create_merch_design(
                MerchDesignCreate(
                    universe_id=universe.id,
                    product_type="tshirt",
                    theme_prompt="clean design",
                    print_area="sleeve",
                )
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_merch_design_allows_supported_print_areas(self):
        universe = self._create_universe("primary")

        hoodie_asset = self.service.create_merch_design(
            MerchDesignCreate(
                universe_id=universe.id,
                product_type="hoodie",
                theme_prompt="clean design",
                print_area="sleeve",
            )
        )
        tshirt_asset = self.service.create_merch_design(
            MerchDesignCreate(
                universe_id=universe.id,
                product_type="tshirt",
                theme_prompt="clean design",
                print_area="front",
            )
        )

        self.assertEqual(hoodie_asset.current_version, 1)
        self.assertEqual(tshirt_asset.current_version, 1)


if __name__ == "__main__":
    unittest.main()
