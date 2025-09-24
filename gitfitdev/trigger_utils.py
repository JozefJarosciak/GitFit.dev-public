"""Utilities for calculating trigger minutes."""

from typing import List, Tuple


def get_valid_trigger_minutes(interval_minutes: int) -> List[Tuple[int, str]]:
    """
    Get valid trigger minute options for a given interval.
    Returns list of (minute, display_string) tuples.

    Examples:
    - 60 min interval: can trigger at any minute 0-59
    - 30 min interval: can trigger at 0-29 (hits :00/:30 or :15/:45, etc.)
    - 15 min interval: can trigger at 0-14 (hits :00/:15/:30/:45, etc.)
    - 10 min interval: can trigger at 0-9 (hits :00/:10/:20/:30/:40/:50, etc.)
    """
    if interval_minutes <= 0:
        return [(0, "Every minute")]

    if interval_minutes >= 60:
        # For hourly or longer, can pick any minute
        options = []
        for m in range(0, 60, 5):  # Show in 5-minute increments for UI simplicity
            times = get_trigger_times_preview(interval_minutes, m)
            preview = ", ".join(times[:3])
            if len(times) > 3:
                preview += "..."
            options.append((m, f":{m:02d} ({preview})"))
        return options

    # For intervals less than 60 minutes
    valid_minutes = []

    # Find which minutes would work consistently
    for minute in range(min(interval_minutes, 60)):
        # Check if this minute would create a consistent pattern
        times = []
        current_min = minute
        while current_min < 60:
            times.append(current_min)
            current_min += interval_minutes

        # Only include if it creates a pattern that repeats each hour
        if minute < interval_minutes:
            preview = get_trigger_times_preview(interval_minutes, minute)
            display = ", ".join(preview[:4])
            if len(preview) > 4:
                display += "..."
            valid_minutes.append((minute, f"at :{minute:02d} ({display})"))

    return valid_minutes


def get_trigger_times_preview(interval_minutes: int, trigger_minute: int,
                             start_hour: int = 9, count: int = 6) -> List[str]:
    """
    Get a preview of when breaks would occur.
    Returns list of time strings (HH:MM format).
    """
    times = []

    if interval_minutes >= 60:
        # Hourly or longer intervals
        hours_per_trigger = interval_minutes // 60
        current_hour = start_hour

        # Find first valid hour
        while len(times) < count:
            times.append(f"{current_hour:02d}:{trigger_minute:02d}")
            current_hour += hours_per_trigger
            if current_hour >= 24:
                break
    else:
        # Sub-hourly intervals
        total_minutes = start_hour * 60 + trigger_minute

        while len(times) < count:
            hour = total_minutes // 60
            minute = total_minutes % 60
            if hour >= 24:
                break
            times.append(f"{hour:02d}:{minute:02d}")
            total_minutes += interval_minutes

    return times


def calculate_next_trigger_time(interval_minutes: int, trigger_minute: int,
                               from_hour: int, from_minute: int) -> Tuple[int, int]:
    """
    Calculate the next trigger time based on interval and trigger minute.
    Returns (hour, minute) tuple.
    """
    current_total = from_hour * 60 + from_minute

    if interval_minutes >= 60:
        # For hourly+ intervals, find next hour that matches
        hours_per_interval = interval_minutes // 60

        # Find the next matching hour
        if from_minute <= trigger_minute:
            # Can trigger this hour
            next_hour = from_hour
        else:
            # Need to wait for next interval hour
            next_hour = from_hour + hours_per_interval

        # Align to interval pattern
        hours_since_midnight = next_hour
        while hours_since_midnight % hours_per_interval != 0:
            next_hour += 1
            hours_since_midnight = next_hour

        return (next_hour % 24, trigger_minute)
    else:
        # For sub-hourly intervals
        # Find next occurrence of trigger_minute pattern
        target = trigger_minute
        while target <= current_total:
            target += interval_minutes

        return (target // 60, target % 60)


def format_trigger_description(interval_minutes: int, trigger_minute: int) -> str:
    """
    Create a human-readable description of when breaks will occur.
    """
    if interval_minutes >= 60:
        hours = interval_minutes // 60
        if hours == 1:
            return f"Every hour at :{trigger_minute:02d}"
        else:
            return f"Every {hours} hours at :{trigger_minute:02d}"
    else:
        times = get_trigger_times_preview(interval_minutes, trigger_minute, 9, 4)
        preview = ", ".join(times)
        return f"Every {interval_minutes} min ({preview}...)"