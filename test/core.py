import os
import sys
import unittest
from unittest.mock import patch
import logging

# Add the parent directory to the path so we can import utils
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
# Import the module to test
# Assuming the code is in a module named 'log_notifier.core'
from log_notifier.core import (
    StandardLogProcessor,
    TIME_WARN_SECOND,
    TIME_ERROR_SECOND,
)


class TestStandardLogProcessor(unittest.TestCase):
    def setUp(self):
        """Set up a new processor instance for each test."""
        self.processor = StandardLogProcessor()

    @patch("log_notifier.core.logger")
    def test_basic_happy_path(self, mock_logger):
        """Test the basic happy path: START followed by END with normal processing."""
        # Create timestamps
        start_time = 1000  # Unix timestamp
        end_time = 1100  # Normal processing time (< warning threshold)

        # Job description
        job_description = {
            "crontype": "daily",
            "action_type": "backup",
            "action_id": "123",
        }
        pid = "12345"

        # Process START entry
        self.processor.process_log_entry(
            start_time, job_description, "START", pid
        )

        # Process END entry with normal processing time
        self.processor.process_log_entry(end_time, job_description, "END", pid)

        # Verify logs for END and post-processing
        mock_logger.debug.assert_any_call(
            "Recorded END time for PID %s: %s", pid, end_time
        )
        mock_logger.debug.assert_any_call(
            "Process with PID %s completed successfully", pid
        )

        # Verify process time calculation was logged
        process_time = end_time - start_time
        mock_logger.debug.assert_any_call(
            "Calculated process time for PID %s: %.2f seconds",
            pid,
            process_time,
        )

        # Verify pid was removed from log_dict after processing
        self.assertNotIn(pid, self.processor.log_dict)

    @patch("log_notifier.core.logger")
    def test_warning_threshold_exceeded(self, mock_logger):
        """Test logging when warning threshold is exceeded."""
        # Create timestamps
        start_time = 1000  # Unix timestamp

        # Job description
        job_description = {
            "crontype": "daily",
            "action_type": "backup",
            "action_id": "123",
        }
        pid = "12345"

        # Process START entry
        self.processor.process_log_entry(
            start_time, job_description, "START", pid
        )

        # Process END entry - set end time to trigger warning threshold
        end_time = (
            start_time + TIME_WARN_SECOND + 10
        )  # 10 seconds over warning threshold
        self.processor.process_log_entry(end_time, job_description, "END", pid)

        # Verify warning threshold logging
        process_time = TIME_WARN_SECOND + 10
        mock_logger.warning.assert_called_with(
            "PID: %s used time %s seconds, exceeding warning threshold",
            pid,
            process_time,
        )

    @patch("log_notifier.core.logger")
    def test_error_threshold_exceeded(self, mock_logger):
        """Test logging when error threshold is exceeded."""
        # Create timestamps
        start_time = 1000  # Unix timestamp

        # Job description
        job_description = {
            "crontype": "daily",
            "action_type": "backup",
            "action_id": "123",
        }
        pid = "12345"

        # Process START entry
        self.processor.process_log_entry(
            start_time, job_description, "START", pid
        )

        # Process END entry - set end time to trigger error threshold
        end_time = (
            start_time + TIME_ERROR_SECOND + 10
        )  # 10 seconds over error threshold
        self.processor.process_log_entry(end_time, job_description, "END", pid)

        # Verify error threshold logging
        process_time = TIME_ERROR_SECOND + 10
        mock_logger.error.assert_called_with(
            "PID: %s used time %s seconds, exceeding error threshold",
            pid,
            process_time,
        )

        # Verify pid was removed from log_dict after processing
        self.assertNotIn(pid, self.processor.log_dict)

    def test_invalid_entry_type(self):
        """Test that an invalid entry_type raises ValueError."""
        # Create test data
        timestamp = 1000
        job_description = {
            "crontype": "daily",
            "action_type": "backup",
            "action_id": "123",
        }
        pid = "12345"

        # Process with invalid entry_type should raise ValueError
        with self.assertRaises(ValueError):
            self.processor.process_log_entry(
                timestamp, job_description, "INVALID", pid
            )

    @patch("log_notifier.core.logger")
    def test_start_after_end(self, mock_logger):
        """Test behavior when START entry comes after END entry."""
        # Create timestamps
        end_time = 1000  # Unix timestamp
        start_time = 1300  # Later timestamp

        # Job description
        job_description = {
            "crontype": "daily",
            "action_type": "backup",
            "action_id": "123",
        }
        pid = "12345"

        # Process END entry first
        self.processor.process_log_entry(end_time, job_description, "END", pid)

        # Verify post-processing for incomplete process
        mock_logger.debug.assert_any_call("Created new entry for PID %s", pid)
        mock_logger.debug.assert_any_call(
            "Recorded END time for PID %s: %s", pid, end_time
        )
        mock_logger.error.assert_any_call(
            "Could not calculate process time for PID %s (incomplete process)",
            pid,
        )
        mock_logger.debug.assert_any_call(
            "Deleted PID %s from log dictionary to save memory", pid
        )

        # Process START entry later (should create a new entry since the previous was deleted)
        self.processor.process_log_entry(
            start_time, job_description, "START", pid
        )

        # Verify a new entry was created with only START time
        mock_logger.debug.assert_any_call("Created new entry for PID %s", pid)
        mock_logger.debug.assert_any_call(
            "Recorded START time for PID %s: %s", pid, start_time
        )

        # Verify the new entry exists in log_dict
        self.assertIn(pid, self.processor.log_dict)
        self.assertEqual(
            self.processor.log_dict[pid]["time_start"], start_time
        )
        self.assertIsNone(self.processor.log_dict[pid]["time_end"])


if __name__ == "__main__":
    unittest.main()
