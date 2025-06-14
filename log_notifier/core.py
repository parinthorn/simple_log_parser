import logging
import datetime
from abc import ABC, abstractmethod

# Configure logger
logger = logging.getLogger(__name__)


# Time in seconds. Should be env
TIME_WARN_SECOND = 5 * 60
TIME_ERROR_SECOND = 15 * 60


class BaseLogProcessor(ABC):
    """
    Abstract base class for log processors.
    """

    @abstractmethod
    def __init__(self):
        """Initialize the log processor."""
        pass

    @abstractmethod
    def process_log_entry(self, timestamp, job_description, entry_type, pid):
        """
        Process a single log entry.

        Args:
            job_description (dict): Dictionary containing log entry metadata
        """
        pass


class StandardLogProcessor(BaseLogProcessor):
    """
    Standard implementation of log processor that maintains internal state of all processes.
    """

    def __init__(self):
        """
        Initialize an empty log dictionary."""
        self.log_dict = {}

    def process_log_entry(self, timestamp, job_description, entry_type, pid):
        """
        Process a single log entry and update the internal log dictionary.

        Args:
            job_description (dict): Dictionary containing the following keys:
                - timestamp: The second of the time (Can be converted into unix timestamp)
                - crontype: The type of cron job
                - action_type: The type of action
                - action_id: The identifier of the process (renamed from 'id')
                - entry_type: The type of entry (START or END)
                - pid: The process ID
        """
        # Extract fields from the job_description dictionary
        crontype = job_description.get("crontype")
        action_type = job_description.get("action_type")
        action_id = job_description.get("action_id")  # Renamed from 'id'

        # Validate required fields
        if not all([timestamp, job_description, pid]):
            logger.error(
                "Missing required fields in job_description: %s",
                job_description,
            )
            return

        # Update log dictionary
        if pid not in self.log_dict:
            self.log_dict[pid] = {
                "job_description": f"{crontype} {action_type} {action_id}",
                "time_start": None,
                "time_end": None,
                "success_flag": False,
                "crontype": crontype,
                "action_type": action_type,
                "action_id": action_id,  # Renamed from 'id'
            }
            logger.debug("Created new entry for PID %s", pid)

        if entry_type == "START":
            self.log_dict[pid]["time_start"] = timestamp
            logger.debug("Recorded START time for PID %s: %s", pid, timestamp)
        elif entry_type == "END":
            self.log_dict[pid]["time_end"] = timestamp
            logger.debug("Recorded END time for PID %s: %s", pid, timestamp)
            self.post_process(pid)
        else:
            raise ValueError("Invalid entry_type")

    def post_process(self, pid):
        """
        Post-process a single pid entry:
        1. Calculate process time by subtracting end time from start time
        2. Delete pid from the dictionary to save memory

        Args:
            pid (str): The process ID to post-process

        Returns:
            dict: The processed entry data or None if pid not found
        """
        if pid not in self.log_dict:
            logger.warning("PID %s not found in log dictionary", pid)
            return None

        # Set success_flag to True if both start and end times are set
        if self.log_dict[pid]["time_start"] is not None:
            self.log_dict[pid]["success_flag"] = True
            logger.debug("Process with PID %s completed successfully", pid)

        # Get the process data
        process_data = self.log_dict[pid]

        # Calculate process time for completed processes
        if (
            process_data["success_flag"]
            and process_data["time_start"]
            and process_data["time_end"]
        ):
            process_data["process_time"] = (
                process_data["time_end"] - process_data["time_start"]
            )

            _process_time = process_data["process_time"]
            if _process_time >= TIME_ERROR_SECOND:
                logger.error(
                    "PID: %s used time %s seconds, exceeding error threshold",
                    pid,
                    _process_time,
                )
            elif process_data["process_time"] >= TIME_WARN_SECOND:
                logger.warning(
                    "PID: %s used time %s seconds, exceeding warning threshold",
                    pid,
                    _process_time,
                )

            logger.debug(
                "Calculated process time for PID %s: %.2f seconds",
                pid,
                process_data["process_time"],
            )
        else:
            process_data["process_time"] = None
            logger.debug(
                "Could not calculate process time for PID %s (incomplete process)",
                pid,
            )

        # Delete the pid entry to save memory
        del self.log_dict[pid]
        logger.debug("Deleted PID %s from log dictionary to save memory", pid)
