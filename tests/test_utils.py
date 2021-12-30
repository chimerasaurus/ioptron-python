"""A set of tests to test the utils module."""

# Imports
import unittest
from ioptron import utils

class Test_CoordinateFunctions(unittest.TestCase):
    """Class to test the coordinate functions in utils."""
    def test_convert_arc_seconds_to_degrees(self):
        """Test the conversion of arc seconds (0.01 precision) to degrees."""
        fourty_five_fourty_five_deg = 16362000
        twenty_five_deg = 9000000

        # Run two tests
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_degrees(fourty_five_fourty_five_deg), 45.45)
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_degrees(twenty_five_deg), 25)


    def test_convert_arc_seconds_to_hms(self):
        """Test the conversion of arc seconds with 0.01 precision - mid day
        to HH:MM:SS."""
        twelve_hours = 64800000
        twenty_four_hours = 129600000

        # Run two tests
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_hms(twelve_hours), (12, 0, 0, 0.0))
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_hms(twenty_four_hours), (24, 0, 0, 0.0))

        #TODO: More tests to see if this actually works

if __name__ == '__main__':
    unittest.main()
