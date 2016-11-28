
from mpf.tests.MpfTestCase import MpfTestCase
from unittest.mock import MagicMock


class TestBallDeviceNoPlungerSwitch(MpfTestCase):

    def getConfigFile(self):
        return 'test_ball_device_no_plunger_switch.yaml'

    def getMachinePath(self):
        return 'tests/machine_files/ball_device/'

    def put_ball_in_trough(self):
        self.machine.switch_controller.process_switch('s_trough_1', 1)
        self.advance_time_and_run(1)
        self.assertEqual(self.machine.ball_devices.trough.balls, 1)

        self.trough_coil = self.machine.coils.trough_eject
        self.trough_coil.pulse = MagicMock()

    def test_add_ball_to_pf(self):
        self.put_ball_in_trough()

        # Request ball to pf which puts it in the plunger lane
        self.machine.playfield.add_ball(player_controlled=True)
        self.advance_time_and_run(.1)

        self.assertEqual(1, self.trough_coil.pulse.called)

        self.machine.switch_controller.process_switch('s_trough_1', 0)

        self.advance_time_and_run(11)

        self.assertEqual(self.machine.ball_devices.trough.balls, 0)
        self.assertEqual(self.machine.ball_devices.playfield.balls, 1)

        # hit some playfield switches
        self.advance_time_and_run(1)
        self.machine.switch_controller.process_switch('s_playfield', 1)
        self.machine.switch_controller.process_switch('s_playfield', 0)

        self.advance_time_and_run(1)
        self.machine.switch_controller.process_switch('s_playfield', 1)
        self.machine.switch_controller.process_switch('s_playfield', 0)

        # drain
        self.advance_time_and_run(1)
        self.machine.switch_controller.process_switch('s_trough_1', 1)
        self.advance_time_and_run(1)

        self.assertEqual(self.machine.ball_devices.trough.balls, 1)
        self.assertEqual(self.machine.ball_devices.playfield.balls, 0)

    def test_game_start_with_ball_in_plunger_lane(self):
        self.trough_coil = self.machine.coils.trough_eject
        self.trough_coil.pulse = MagicMock()

        # add fake ball to launcher
        self.post_event("initial_ball")
        self.advance_time_and_run(10)

        self.assertEqual(self.machine.ball_devices.trough.balls, 0)
        self.assertEqual(self.machine.ball_devices.plunger.balls, 1)
        self.assertEqual(self.machine.ball_devices.playfield.balls, 0)

        # game start should work
        self.hit_and_release_switch('s_start')
        self.advance_time_and_run()
        self.assertIsNotNone(self.machine.game)
        self.assertEqual(self.machine.game.player.ball, 1)

        # playfield switch hit indicates that ball has been plunged
        self.hit_and_release_switch('s_playfield')
        self.advance_time_and_run()
        self.assertEqual(self.machine.ball_devices.playfield.balls, 1)
        self.assertEqual(self.machine.ball_devices.plunger.balls, 0)
        self.hit_and_release_switch('s_playfield')
        self.advance_time_and_run()
        self.hit_and_release_switch('s_playfield')
        self.advance_time_and_run()

        # drain the ball
        self.machine.switch_controller.process_switch('s_trough_1', 1)
        self.advance_time_and_run(1)
        self.assertEqual(1, self.trough_coil.pulse.called)
        self.machine.switch_controller.process_switch('s_trough_1', 0)
        self.advance_time_and_run(.5)

        self.assertEqual(self.machine.ball_devices.trough.balls, 0)
        # self.assertEqual(self.machine.ball_devices.playfield.balls, 1)

        self.assertEqual(self.machine.game.player.ball, 2)

        self.hit_and_release_switch('s_playfield')
        self.advance_time_and_run()
        self.hit_and_release_switch('s_playfield')
        self.advance_time_and_run()
        self.hit_and_release_switch('s_playfield')
        self.advance_time_and_run()

        self.machine.switch_controller.process_switch('s_trough_1', 1)
        self.advance_time_and_run(1)
        self.assertEqual(1, self.trough_coil.pulse.called)
        self.machine.switch_controller.process_switch('s_trough_1', 0)
        self.advance_time_and_run(.5)

        self.assertEqual(self.machine.ball_devices.trough.balls, 0)
        # self.assertEqual(self.machine.ball_devices.playfield.balls, 1)

        self.assertEqual(self.machine.game.player.ball, 3)