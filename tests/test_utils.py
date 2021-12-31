"""
A set of tests to test the utils module.
@author - James Malone
"""

# Imports
import unittest
import time
from ioptron import utils

class Test_CoordinateFunctions(unittest.TestCase):
    """Class to test the coordinate functions in utils."""
    def test_convert_arc_seconds_to_degrees(self):
        """Test the conversion of arc seconds (0.01 precision) to degrees."""
        fourty_five_fourty_five_deg = 16362000
        twenty_five_deg = 9000000

        # Run two tests
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_degrees( \
                fourty_five_fourty_five_deg), 45.45)
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_degrees(twenty_five_deg), 25)

    def test_convert_arc_seconds_to_dms(self):
        """Test the conversion of centi-arcseconds with to dms."""
        eighty_five_ish = 30829224
        negative_eighty_five_ish = eighty_five_ish * -1

        # Run a few tests
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_dms(eighty_five_ish), (85, 38, 12))
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_dms(negative_eighty_five_ish), \
                (-85, 38, 12))

    def test_convert_arc_seconds_to_hms(self):
        """Test the conversion of arc seconds with 0.01 precision - mid day
        to HH:MM:SS."""
        twelve_hours = 64800000
        twenty_four_hours = 129600000
        five_point_eight_three = 31526820

        # Run a few tests
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_hms(twelve_hours), (12, 0, 0))
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_hms(twenty_four_hours), (24, 0, 0))
        with self.subTest():
            self.assertEqual(utils.convert_arc_seconds_to_hms(five_point_eight_three), (5, 50, 17))

    def test_get_utc_time_in_j2k(self):
        """Test getting the UTC time in j2k. This only tests for a reasonable return."""
        j2k_time = utils.get_utc_time_in_j2k()
        utc = time.time()
        # j2k time is returned at 1000x
        self.assertGreater(utc, (j2k_time / 1000))

    def test_offset_utc_time(self):
        """Test offsetting the UTC time with a specified time zone offset in min."""
        offset_min_neg = -480
        offset_min_pos = 180
        utc = 0

        unix_time = time.time()

        # Run a few tests
        with self.subTest():
            self.assertEqual(utils.offset_utc_time(unix_time, \
                offset_min_neg), (unix_time + (offset_min_neg * 60)))
        with self.subTest():
            self.assertEqual(utils.offset_utc_time(unix_time, \
                offset_min_pos), (unix_time + (offset_min_pos * 60)))
        with self.subTest():
            self.assertEqual(utils.offset_utc_time(unix_time, utc), (unix_time))

if __name__ == '__main__':
    unittest.main()
