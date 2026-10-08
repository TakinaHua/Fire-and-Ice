"""Run with: python -m unittest discover -s tests -v"""
import unittest

from engine.collision import Rect, overlaps, player_hitbox, ghost_hitbox, hazard_rectangles
from engine.physics import advance_vertical


class CollisionTests(unittest.TestCase):
    def test_overlapping_rectangles(self):
        self.assertTrue(overlaps(Rect(0, 0, 10, 10), Rect(9, 9, 10, 10)))

    def test_touching_edge_is_not_collision(self):
        self.assertFalse(overlaps(Rect(0, 0, 10, 10), Rect(10, 0, 10, 10)))

    def test_separated_rectangles(self):
        self.assertFalse(overlaps(Rect(0, 0, 10, 10), Rect(100, 100, 10, 10)))

    def test_invalid_hitbox(self):
        with self.assertRaises(ValueError):
            Rect(0, 0, -1, 3)

    def test_ghost_collision_does_not_require_equal_centers(self):
        self.assertTrue(overlaps(player_hitbox(200, 300), ghost_hitbox(210, 300)))

    def test_character_specific_pool(self):
        fire_pool = hazard_rectangles("level1", "fireboy")[0]
        ice_pool = hazard_rectangles("level1", "icegirl")[0]
        self.assertNotEqual(fire_pool.x, ice_pool.x)

    def test_no_hazards_in_menu(self):
        self.assertEqual(hazard_rectangles("levelSelection", "fireboy"), ())


class PhysicsTests(unittest.TestCase):
    def test_gravity_applies(self):
        self.assertEqual(advance_vertical(100, 0, 1, 400), (101, 1, False))

    def test_landing_clamps_at_ground(self):
        self.assertEqual(advance_vertical(390, 15, 1, 400), (400, 0, True))

    def test_jump_moves_upward(self):
        self.assertEqual(advance_vertical(300, -15, 1, 400), (286, -14, False))


if __name__ == "__main__":
    unittest.main()
