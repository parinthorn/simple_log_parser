"""
Time-related utility functions for the log processing application.
"""

import re

# Compile regex pattern for better performance
TIME_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2}$")


def time_to_seconds(time_str: str) -> int:
    """
    Convert a time string in format "HH:MM:SS" to seconds since midnight.

    # NOTE: This is a given requirement for the application.
    # If we had full timestamps with timezone information, we could extend this
    # to use Unix timestamps instead, which would provide better compatibility
    # and enable cross-day log analysis.

    Args:
        time_str: Time string in format "HH:MM:SS"

    Returns:
        int: Number of seconds since midnight

    Raises:
        ValueError: If the time string is not in the expected format
    """
    if not TIME_PATTERN.match(time_str):
        raise ValueError(
            f"Invalid time format: '{time_str}'. Expected format: 'HH:MM:SS'"
        )

    try:
        # Split the time string into hours, minutes, and seconds
        hours, minutes, seconds = time_str.split(":")

        # Convert to integers
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        # Validate time components
        if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
            raise ValueError(f"Invalid time components in '{time_str}'")

        # Calculate total seconds since midnight
        total_seconds = hours * 3600 + minutes * 60 + seconds

        return total_seconds

    except ValueError as e:
        # Handle cases where splitting fails or conversion to int fails
        if str(e).startswith("Invalid time components"):
            raise  # Re-raise our custom validation error
        raise ValueError(
            f"Invalid time format: '{time_str}'. Expected format: 'HH:MM:SS'"
        ) from e


def seconds_to_time(seconds: int) -> str:
    """
    Convert seconds since midnight to a time string in format "HH:MM:SS".

    Args:
        seconds: Number of seconds since midnight

    Returns:
        str: Time string in format "HH:MM:SS"

    Raises:
        ValueError: If seconds is negative or exceeds one day
    """
    if seconds < 0 or seconds >= 86400:  # 86400 = 24 * 60 * 60
        raise ValueError(f"Seconds must be between 0 and 86399, got {seconds}")

    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format as HH:MM:SS
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
