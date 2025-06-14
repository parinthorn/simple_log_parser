import unittest
import sys
import os

# Add the parent directory to the path so we can import utils
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from utils.time import time_to_seconds, seconds_to_time


class TimeUtilsTestCase(unittest.TestCase):
    """Test cases for time utility functions."""

    def test_time_to_seconds_valid(self):
        """Test valid time string conversions."""
        test_cases = [
            ("00:00:00", 0),  # Midnight
            ("01:00:00", 3600),  # 1 hour
            ("00:01:00", 60),  # 1 minute
            ("00:00:01", 1),  # 1 second
            ("01:30:45", 5445),  # Mixed time
            ("12:00:00", 43200),  # Noon
            ("23:59:59", 86399),  # End of day
        ]

        for time_str, expected_seconds in test_cases:
            with self.subTest(time_str=time_str):
                result = time_to_seconds(time_str)
                self.assertEqual(result, expected_seconds)

    def test_time_to_seconds_invalid_format(self):
        """Test invalid time string formats."""
        invalid_formats = [
            "",  # Empty string
            "12:34",  # Missing seconds
            "12:34:56:78",  # Too many components
            "12-34-56",  # Wrong delimiter
            "12:34:5a",  # Non-numeric components
            "1:2:3",  # Missing leading zeros
            "24:00:00",  # Hour out of range
            "23:60:00",  # Minute out of range
            "23:59:60",  # Second out of range
            "-01:00:00",  # Negative hour
            "garbage",  # Random text
        ]

        for invalid_format in invalid_formats:
            with self.subTest(invalid_format=invalid_format):
                with self.assertRaises(ValueError):
                    time_to_seconds(invalid_format)

    def test_seconds_to_time_valid(self):
        """Test valid second conversions."""
        test_cases = [
            (0, "00:00:00"),  # Midnight
            (3600, "01:00:00"),  # 1 hour
            (60, "00:01:00"),  # 1 minute
            (1, "00:00:01"),  # 1 second
            (5445, "01:30:45"),  # Mixed time
            (43200, "12:00:00"),  # Noon
            (86399, "23:59:59"),  # End of day
        ]

        for seconds, expected_time_str in test_cases:
            with self.subTest(seconds=seconds):
                result = seconds_to_time(seconds)
                self.assertEqual(result, expected_time_str)

    def test_seconds_to_time_invalid(self):
        """Test invalid second values."""
        invalid_seconds = [
            -1,  # Negative
            86400,  # Equal to 24 hours (should be 00:00:00 of next day)
            100000,  # Too large
            1.5,  # Not an integer
        ]

        for invalid_second in invalid_seconds:
            with self.subTest(invalid_second=invalid_second):
                with self.assertRaises(ValueError):
                    seconds_to_time(invalid_second)

    def test_roundtrip_conversion(self):
        """Test that conversion in both directions is consistent."""
        # Test a range of times throughout the day
        for hour in range(0, 24):
            for minute in [0, 15, 30, 45]:
                for second in [0, 15, 30, 45]:
                    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
                    seconds = time_to_seconds(time_str)
                    roundtrip_time_str = seconds_to_time(seconds)

                    with self.subTest(time_str=time_str):
                        self.assertEqual(time_str, roundtrip_time_str)


if __name__ == "__main__":
    unittest.main()
