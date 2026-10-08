"""Continuous collision and gameplay integration regressions."""
import unittest
from engine.collision import Rect, Collider, Layer, sweep, overlaps, translated, swept_overlap
from engine.physics import move_body, platform_motion, supporting_platform
from engine.world import move_horizontal, move_player, jump, carry_players, ghost_collisions, body
from engine.runtime import onStep
from entities.platforms import moveTrap
from entities.players import applyContinuousMovement
from levels.geometry import moving_platforms, hazards
from input.keyboard import onKeyPress, onKeyHold
from test_architecture import new_game


class SweepTests(unittest.TestCase):
    def test_fast_motion_hits_thin_wall(self):
        hit = sweep(Rect(0, 0, 10, 10), 1000, 0, Rect(30, 0, 1, 50))
        self.assertAlmostEqual(hit.time, .02)
        self.assertEqual((hit.normal_x, hit.normal_y), (-1, 0))

    def test_resting_slide_and_separating_are_not_collisions(self):
        a, b = Rect(0, 0, 10, 10), Rect(10, 0, 10, 10)
        self.assertIsNone(sweep(a, -10, 0, b))
        self.assertIsNone(sweep(a, 0, 10, b))
        self.assertEqual(sweep(a, 10, 0, b).time, 0)

    def test_touch_at_end_does_not_trigger_hazard(self):
        start = Rect(0, 0, 10, 10)
        self.assertFalse(swept_overlap(start, translated(start, 10, 0), Rect(20, 0, 10, 10)))
        self.assertTrue(swept_overlap(start, translated(start, 100, 0), Rect(20, 0, 10, 10)))

    def test_landing_and_ceiling(self):
        floor = Collider(Rect(0, 100, 100, 2), 'floor')
        result = move_body(Rect(10, 0, 10, 10), 0, 1000, [floor])
        self.assertEqual(result.rect.y, 90)
        self.assertTrue(result.grounded)
        result = move_body(Rect(10, 130, 10, 10), 0, -1000, [floor])
        self.assertEqual(result.rect.y, 102)
        self.assertIn(('floor', 0, 1), result.contacts)

    def test_side_collision_both_directions(self):
        wall = Collider(Rect(50, 0, 10, 100), 'wall')
        self.assertEqual(move_body(Rect(0, 20, 10, 10), 200, 0, [wall]).rect.x, 40)
        self.assertEqual(move_body(Rect(100, 20, 10, 10), -200, 0, [wall]).rect.x, 60)

    def test_diagonal_slides_without_tunneling(self):
        wall = Collider(Rect(50, 0, 10, 500), 'wall')
        floor = Collider(Rect(0, 100, 500, 10), 'floor')
        result = move_body(Rect(0, 0, 10, 10), 200, 200, [wall, floor])
        self.assertEqual(result.rect, Rect(40, 90, 10, 10))

    def test_edge_landing_requires_positive_horizontal_overlap(self):
        floor = Collider(Rect(50, 100, 100, 10), 'floor')
        self.assertFalse(move_body(Rect(40, 0, 10, 10), 0, 200, [floor]).grounded)
        self.assertTrue(move_body(Rect(40.01, 0, 10, 10), 0, 200, [floor]).grounded)

    def test_initial_overlap_is_resolved(self):
        floor = Collider(Rect(0, 100, 100, 10), 'floor')
        result = move_body(Rect(20, 95, 10, 10), 0, 1, [floor])
        self.assertFalse(overlaps(result.rect, floor.rect))
        self.assertEqual(result.rect.y, 90)

    def test_one_way_passes_up_catches_down(self):
        ledge = Collider(Rect(0, 100, 100, 10), 'ledge', one_way=True)
        self.assertEqual(move_body(Rect(20, 120, 10, 10), 0, -100, [ledge]).rect.y, 20)
        self.assertEqual(move_body(Rect(20, 20, 10, 10), 0, 100, [ledge]).rect.y, 90)

    def test_masks_filter_solids(self):
        wall = Collider(Rect(50, 0, 10, 100), 'fire-only', mask=Layer.FIRE)
        self.assertEqual(move_body(Rect(0, 0, 10, 10), 100, 0, [wall], Layer.ICE).rect.x, 100)
        self.assertEqual(move_body(Rect(0, 0, 10, 10), 100, 0, [wall], Layer.FIRE).rect.x, 40)


class MovingPlatformTests(unittest.TestCase):
    def test_rider_follows_up_down_and_horizontal(self):
        old = Collider(Rect(0, 100, 100, 10), 'lift')
        rider = Rect(20, 90, 10, 10)
        for dx, dy in [(0, -20), (0, 20), (50, 0)]:
            new = Collider(translated(old.rect, dx, dy), 'lift')
            result = platform_motion(rider, old, new, [])
            self.assertEqual(result.rect, translated(rider, dx, dy))
            self.assertFalse(result.crushed)

    def test_nearby_player_is_not_teleported(self):
        old = Collider(Rect(0, 100, 100, 10), 'lift')
        new = Collider(Rect(0, 105, 100, 10), 'lift')
        person = Rect(20, 20, 10, 10)
        self.assertEqual(platform_motion(person, old, new, []).rect, person)

    def test_platform_sweeps_into_stationary_body(self):
        old = Collider(Rect(0, 100, 100, 10), 'lift')
        new = Collider(Rect(0, 50, 100, 10), 'lift')
        self.assertEqual(platform_motion(Rect(20, 70, 10, 10), old, new, []).rect.y, 40)

    def test_crushing_against_ceiling(self):
        old = Collider(Rect(0, 100, 100, 10), 'lift')
        new = Collider(Rect(0, 80, 100, 10), 'lift')
        ceiling = Collider(Rect(0, 0, 100, 85), 'ceiling')
        self.assertTrue(platform_motion(Rect(20, 90, 10, 10), old, new, [ceiling]).crushed)


class StageOneIntegrationTests(unittest.TestCase):
    def test_walking_off_edge_removes_jump_support(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 790, 355
        move_horizontal(app, 'fireboy', 30)
        self.assertFalse(app.fireboyCanJump)
        jump(app, 'fireboy')
        self.assertEqual(app.fireboyVelY, 0)
        onStep(app)
        self.assertGreater(app.fireboyy, 355)

    def test_fast_fall_lands_on_middle_floor(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 100, 250
        app.fireboyVelY = 1000
        onStep(app)
        self.assertEqual(app.fireboyy, 355)
        self.assertEqual(app.fireboyVelY, 0)

    def test_jump_hits_middle_floor_underside(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 100, 450
        app.fireboyVelY = -100
        onStep(app)
        self.assertEqual(app.fireboyy, 425)
        self.assertEqual(app.fireboyVelY, 0)

    def test_world_bounds_apply_to_all_control_paths(self):
        for control in ('press', 'hold', 'gesture'):
            app = new_game()
            app.fireboyx, app.fireboyy = 987, 655
            if control == 'press': onKeyPress(app, 'right')
            elif control == 'hold': onKeyHold(app, ['right'])
            else:
                app.fireboyMovingDirection = 'right'
                applyContinuousMovement(app)
            self.assertEqual(app.fireboyx, 989, control)

    def test_water_fire_immunity_and_acid(self):
        for name, x, y, dead in [('fireboy',440,655,True),('icegirl',440,655,False),
                                 ('fireboy',640,655,False),('icegirl',640,655,True),
                                 ('fireboy',410,355,True),('icegirl',410,355,True)]:
            app = new_game()
            setattr(app,name+'x',x);setattr(app,name+'y',y)
            move_player(app,name)
            self.assertEqual(app.gameFrozen,dead,(name,x,y))

    def test_high_speed_player_crossing_hazard_is_detected(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 300,655
        move_horizontal(app,'fireboy',300)
        self.assertTrue(app.gameFrozen)

    def test_high_speed_ghost_crossing_player_is_detected(self):
        from engine.collision import ghost_hitbox
        app = new_game('level1');app.ghostActive=True
        app.fireboyx,app.fireboyy=200,655
        app.ghostX,app.ghostY=400,655
        ghost_collisions(app,ghost_hitbox(0,655))
        self.assertTrue(app.gameFrozen)

    def test_switch_works_in_both_first_levels(self):
        for mode in ('level0','level1'):
            app=new_game(mode);app.fireboyx,app.fireboyy=570,355
            moveTrap(app)
            self.assertEqual(app.platformY,185)

    def test_fan_reaches_upper_walkway(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 900,655
        for _ in range(160): onStep(app)
        self.assertLess(app.fireboyy,155)
        move_horizontal(app,'fireboy',-100)
        for _ in range(40): onStep(app)
        self.assertEqual(app.fireboyy,155)
        self.assertTrue(app.fireboyCanJump)
        self.assertFalse(app.gameFrozen)

    def test_level2_lift_carries_and_keeps_bounds(self):
        app=new_game('level2')
        app.platformY1=400
        app.fireboyx,app.fireboyy=100,375
        old=moving_platforms(app);moveTrap(app);carry_players(app,old)
        self.assertEqual(app.fireboyy,370)
        for _ in range(100): moveTrap(app)
        self.assertEqual(app.platformY1,204)

    def test_level2_fan_exits_above_upper_bridge(self):
        app = new_game('level2')
        app.fireboyx, app.fireboyy = 390, 650
        for _ in range(160): onStep(app)
        self.assertLess(app.fireboyy, 185)
        move_horizontal(app, 'fireboy', -90)
        for _ in range(40): onStep(app)
        self.assertEqual(app.fireboyy, 185)
        self.assertFalse(app.gameFrozen)

    def test_jump_detaches_from_moving_platform(self):
        app = new_game('level2')
        app.platformY1 = 400
        app.fireboyx, app.fireboyy = 100, 375
        jump(app, 'fireboy')
        previous = moving_platforms(app)
        moveTrap(app)
        carry_players(app, previous)
        self.assertEqual(app.fireboyy, 375)
        self.assertEqual(app.fireboyVelY, -15)
