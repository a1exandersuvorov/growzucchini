import unittest
from unittest.mock import patch
from datetime import time

# Assuming zucchini.py and base.py are in growzucchini.config
from growzucchini.config.zucchini import Zucchini, Germination
from growzucchini.config.base import BaseConfig


class TestConfigDayNight(unittest.TestCase):

    def test_day_parameters_are_used_during_day(self):
        config = Zucchini() # Initializes with default Germination phase
        # Default Germination has NIGHT_TEMP_FLOOR = None, NIGHT_TEMP_CEIL = None

        with patch.object(BaseConfig, 'is_night', return_value=False): # Day time
            # Should use day values from Germination class definition
            self.assertEqual(config.growth_phase.TEMP_FLOOR, 24.0)
            self.assertEqual(config.growth_phase.TEMP_CEIL, 30.0)
            self.assertEqual(config.growth_phase.HUM_FLOOR, 70.0)

    def test_night_parameters_are_used_during_night_if_defined(self):
        config = Zucchini()
        # Create a Germination instance with specific NIGHT values
        phase_with_night_params = Germination(
            NIGHT_TEMP_FLOOR=18.0,
            NIGHT_TEMP_CEIL=22.0,
            NIGHT_HUM_CEIL=90.0
            # NIGHT_HUM_FLOOR is not specified, so it's None on this instance (from class default)
        )
        config.switch_growth_phase(phase_with_night_params)

        with patch.object(BaseConfig, 'is_night', return_value=True): # Night time
            self.assertEqual(config.growth_phase.TEMP_FLOOR, 18.0) # Uses NIGHT_TEMP_FLOOR
            self.assertEqual(config.growth_phase.TEMP_CEIL, 22.0) # Uses NIGHT_TEMP_CEIL
            self.assertEqual(config.growth_phase.HUM_CEIL, 90.0)  # Uses NIGHT_HUM_CEIL
            # NIGHT_HUM_FLOOR on phase_with_night_params is None, so fallback to day value
            self.assertEqual(config.growth_phase.HUM_FLOOR, 70.0)


    def test_day_parameters_are_used_during_night_if_night_not_defined(self):
        config = Zucchini() # Initializes with default Germination phase
        # Default Germination has NIGHT_TEMP_FLOOR = None, NIGHT_TEMP_CEIL = None,
        # NIGHT_HUM_FLOOR = None, NIGHT_HUM_CEIL = None

        with patch.object(BaseConfig, 'is_night', return_value=True): # Night time
            # All night parameters are None, so should fallback to day values
            self.assertEqual(config.growth_phase.TEMP_FLOOR, 24.0)
            self.assertEqual(config.growth_phase.TEMP_CEIL, 30.0)
            self.assertEqual(config.growth_phase.HUM_FLOOR, 70.0)
            self.assertEqual(config.growth_phase.HUM_CEIL, 80.0)

    def test_is_night_method_logic(self):
        # Need an instance of BaseConfig or a subclass to test is_night
        # Zucchini is a subclass, so it's fine.
        config_instance = Zucchini()
        self.assertTrue(config_instance.is_night(current_time=time(22, 0)))
        self.assertTrue(config_instance.is_night(current_time=time(0, 0)))
        self.assertTrue(config_instance.is_night(current_time=time(5, 59)))
        self.assertFalse(config_instance.is_night(current_time=time(6, 0)))
        self.assertFalse(config_instance.is_night(current_time=time(12, 0)))
        self.assertFalse(config_instance.is_night(current_time=time(21, 59)))

    def test_accessing_non_growth_phase_attributes(self):
        config = Zucchini()
        self.assertEqual(config.SERIAL_PORT, "/dev/ttyACM0")
        self.assertEqual(config.BAUD_RATE, 9600)
        # Test direct access to _actual_growth_phase (implementation detail, but good to be aware)
        self.assertIsInstance(config._actual_growth_phase, Germination)

    def test_switching_phases_and_night_params(self):
        config = Zucchini() # Starts with default Germination

        # Define a new phase instance (can be any phase class) with specific night params
        # For simplicity, using Germination class but with different values
        switched_phase_instance = Germination(
            NIGHT_TEMP_FLOOR=17.0,
            NIGHT_TEMP_CEIL=21.0,
            NIGHT_HUM_FLOOR=55.0
        )
        config.switch_growth_phase(switched_phase_instance)

        # Check night params for the new phase
        with patch.object(BaseConfig, 'is_night', return_value=True): # Night
            self.assertEqual(config.growth_phase.TEMP_FLOOR, 17.0)
            self.assertEqual(config.growth_phase.TEMP_CEIL, 21.0)
            self.assertEqual(config.growth_phase.HUM_FLOOR, 55.0)
            # NIGHT_HUM_CEIL is None on switched_phase_instance, fallback to day Germination.HUM_CEIL
            self.assertEqual(config.growth_phase.HUM_CEIL, 80.0)


        # Check day params for the new phase (should be Germination class defaults)
        with patch.object(BaseConfig, 'is_night', return_value=False): # Day
            self.assertEqual(config.growth_phase.TEMP_FLOOR, 24.0) # Germination class default
            self.assertEqual(config.growth_phase.TEMP_CEIL, 30.0) # Germination class default
            self.assertEqual(config.growth_phase.HUM_FLOOR, 70.0) # Germination class default
            self.assertEqual(config.growth_phase.HUM_CEIL, 80.0) # Germination class default

if __name__ == '__main__':
    unittest.main()
