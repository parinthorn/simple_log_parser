import sys
import re
import csv
import logging
from log_notifier.core import StandardLogProcessor
from utils.time import time_to_seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log_processing.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def read_log_file(file_path):
    """
    Read and parse the log file using the CSV library.

    Args:
        file_path (str): The path to the log file.

    Returns:
        list: A list of tuples containing (time_str, job_description, entry_type, pid).
    """
    log_entries = []

    try:
        with open(file_path, "r", newline="") as file:
            # Create a CSV reader with comma as delimiter
            csv_reader = csv.reader(file, delimiter=",", quotechar='"')

            for line_num, row in enumerate(csv_reader, 1):
                if len(row) != 4:
                    continue
                if len(row) == 4:
                    time_str = row[0].strip()
                    job_description_str = row[1].strip()
                    entry_type = row[2].strip()
                    pid = row[3].strip()
                    log_entries.append(
                        (time_str, job_description_str, entry_type, pid)
                    )
                else:
                    logger.warning(
                        "Invalid log format at line %d: %s",
                        line_num,
                        ",".join(row),
                    )

        logger.info(
            "Successfully read %d log entries from %s",
            len(log_entries),
            file_path,
        )
        return log_entries

    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return []
    except csv.Error as e:
        logger.error(
            "CSV parsing error in file %s, line %d: %s",
            file_path,
            line_num if "line_num" in locals() else "?",
            str(e),
        )
        return []
    except Exception as e:
        logger.error("Error reading log file: %s", str(e))
        return []


def parse_job_description(job_description):
    """
    Parse the job_description string into component parts.

    Args:
        job_description (str): The job description string in format "crontype action_type action_id"

    Returns:
        tuple: A tuple containing (crontype, action_type, action_id)
    """

    regex_pattern = r"(.*?) (.*?) (.*)"
    match = re.match(regex_pattern, job_description)

    if match:
        crontype, action_type, action_id = match.groups()
        return crontype, action_type, action_id
    else:
        logger.warning("Failed to parse job_description: %s", job_description)
        return "unknown", "unknown", "unknown"


def main():
    """
    Main function to process log files.

    Reads the log file specified as a command line argument,
    parses each entry, and processes it using StandardLogProcessor.

    Command line usage:
        python process_job_log.py <log_file>
    """
    if len(sys.argv) != 2:
        logger.error("Usage: python process_job_log.py <log_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    logger.info("Starting to process log file: %s", file_path)

    # Read raw log entries using CSV parser
    raw_log_entries = read_log_file(file_path)

    if not raw_log_entries:
        logger.error("No valid log entries found. Exiting.")
        sys.exit(1)

    # Create log processor
    log_processor = StandardLogProcessor()

    # Process each log entry
    for time_str, raw_job_description, entry_type, pid in raw_log_entries:
        # Parse the job_description
        crontype, action_type, action_id = parse_job_description(
            raw_job_description
        )

        # Create metadata dictionary
        timestamp = time_to_seconds(time_str)
        job_description = {
            "crontype": crontype,
            "action_type": action_type,
            "action_id": action_id,
        }

        # Process the entry using the core processor
        log_processor.process_log_entry(
            timestamp=timestamp,
            job_description=job_description,
            entry_type=entry_type,
            pid=pid,
        )


if __name__ == "__main__":
    main()
