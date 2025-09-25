"""
English language pack for GitFit.dev
Complete translations for all UI text, exercises, stretches, and motivational messages
"""

# UI Translations
UI_TRANSLATIONS = {
    # Application
    "app_name": "GitFit.dev",
    "app_tagline": "Stay fit while you code!",

    # Disclaimer Dialog
    "disclaimer_title": "GitFit.dev - Important Disclaimer",
    "disclaimer_header": "⚠️ IMPORTANT HEALTH & SAFETY DISCLAIMER",
    "disclaimer_checkbox": "☑️ I have read and understood the full disclaimer above",
    "disclaimer_accept": "I Agree and Accept - Continue",
    "disclaimer_decline": "I Disagree - Exit Application",

    # Body Map Window
    "body_map_title": "GitFit.dev - Daily Fitness Progress",
    "body_map_header": "Daily Fitness Progress",
    "body_map_muscle_groups": "Muscle Groups Worked",
    "body_map_coverage": "Body Coverage Map",
    "body_map_refresh": "Refresh",
    "body_map_reset": "Reset Daily Data",
    "body_map_close": "Close",
    "body_map_no_data": "No exercises completed today.\nStart moving to see your progress!",
    "total_exercise_time": "Total Time",

    # Settings Summary
    "settings_summary": "You'll have {breaks} breaks every {interval} min for {duration} seconds ({total_minutes} min total daily {activity}) in {position} from {from_time} to {to_time}",
    "settings_summary_compact": "{breaks} breaks every {interval}min × {duration}s = {total_minutes}min daily ({from_time}-{to_time})",

    # Settings Window
    "settings_title": "GitFit.dev Settings",
    "settings_schedule": "Schedule",
    "settings_active_hours": "Active Hours",
    "settings_from": "From",
    "settings_to": "To",
    "settings_time_format": "Time Format",
    "settings_24h": "24-hour",
    "settings_12h": "12-hour (AM/PM)",
    "settings_break_settings": "Break Settings",
    "settings_interval": "Interval (minutes)",
    "settings_trigger_minute": "Trigger at minute",
    "settings_lock_duration": "Lock duration (sec)",
    "settings_activity_type": "Activity Type",
    "settings_position_pref": "Position Preference",
    "settings_theme": "Theme",
    "settings_notifications": "Notifications",
    "settings_pre_warning": "Pre-warning",
    "settings_warning_time": "Warning time (sec)",
    "settings_flash_notification": "Flash notification",
    "settings_flash_duration": "Flash duration (sec)",
    "settings_language": "Language",
    "settings_system": "System",
    "settings_startup": "Start on login",
    "settings_save": "Save Settings",
    "settings_reset": "Reset to Defaults",
    "settings_cancel": "Cancel",
    "settings_appearance": "Appearance",
    "settings_preview": "Preview",

    # Settings Categories with Icons
    "category_schedule": "Schedule",
    "category_break_settings": "Break Settings",
    "category_notifications": "Notifications",
    "category_appearance": "Appearance",
    "category_system": "System",

    # Settings Labels (detailed)
    "label_active_hours": "Active Hours",
    "label_from": "From",
    "label_to": "To",
    "label_time_format": "Time Format",
    "label_interval": "Interval (minutes)",
    "label_trigger_minute": "Trigger at minute",
    "label_lock_duration": "Lock duration (seconds)",
    "label_activity_type": "Activity Type",
    "label_position_pref": "Position Preference",
    "label_theme": "Theme",
    "label_language": "Language",
    "label_pre_warning": "Pre-warning",
    "label_warning_time": "Warning time (seconds)",
    "label_flash_notification": "Flash notification",
    "label_flash_duration": "Flash duration (seconds)",
    "label_start_on_login": "Start on login",
    "label_break_offset": "Break Offset Time",
    "label_flash_mode": "Flash Mode",
    "label_exercise_position": "Exercise Position",
    "preview_label": "Preview:",
    "label_time_for_exercise": "Time for exercise",

    # Theme names
    "theme_green": "Fresh Green",
    "theme_blue": "Ocean Blue",
    "theme_purple": "Royal Purple",
    "theme_dark": "Dark Mode",
    "theme_sunset": "Sunset Orange",
    "theme_pink": "Energy Pink",
    "theme_teal": "Calm Teal",
    "theme_indigo": "Deep Indigo",
    "theme_red": "Power Red",
    "theme_forest": "Forest Green",

    # Settings Descriptions/Help Text
    "desc_active_hours": "Hours when breaks are active",
    "desc_interval": "How often breaks occur",
    "desc_trigger_minute": "When in the hour to trigger",
    "desc_lock_duration": "How long the break lasts",
    "desc_activity_type": "Type of activities during breaks",
    "desc_position_pref": "Preferred exercise positions",
    "desc_theme": "Visual theme for the app",
    "desc_pre_warning": "Show warning before break",
    "desc_warning_time": "How long to show warning",
    "desc_flash_notification": "Flash screen as warning",
    "desc_flash_duration": "How long to flash",

    # Tray Menu
    "tray_open_settings": "Settings",
    "tray_daily_progress": "Daily Progress",
    "tray_trigger_now": "Trigger Break Now",
    "tray_pause": "Pause Breaks",
    "tray_resume": "Resume Breaks",
    "tray_help": "Help",
    "tray_about": "About",
    "tray_quit": "Quit",

    # Status Messages
    "next_break": "Next break",
    "next_break_skipped": "Next break: Skipped",
    "status_paused": "Status: Paused",
    "status_active": "Status: Active",
    "paused_for_minutes": "Paused for {minutes} min",

    # Quick Actions Menu
    "menu_quick_actions": "Quick Actions",
    "menu_skip_next": "Skip Next Break",
    "menu_break_in_5": "Break in 5 Minutes",
    "menu_pause_30": "Pause for 30 Minutes",
    "menu_pause_60": "Pause for 1 Hour",
    "menu_pause_120": "Pause for 2 Hours",
    "menu_reset_schedule": "Reset Schedule",

    # Toast Notifications
    "toast_title": "GitFit.dev Break Coming!",
    "toast_message": "Get ready to move in {seconds} seconds!",
    "toast_dismiss": "OK",
    "toast_snooze": "Snooze 5 min",
    "toast_subtitle_reminder": " – Break reminder",
    "toast_subtitle_coming": " – Break coming up!",

    # Stats
    "stats_exercises": "Exercises Completed: {count}",
    "stats_stretches": "Stretches Completed: {count}",
    "stats_coverage": "Muscle Coverage: {covered}/{total} ({percentage:.0f}%)",
    "stats_breaks": "Breaks: {status}",

    # Coverage Status
    "coverage_champion": "[CHAMPION] Excellent full-body coverage!",
    "coverage_great": "[GREAT] Keep up the momentum!",
    "coverage_good": "[GOOD] Target some new muscle groups!",
    "coverage_building": "[BUILDING] You're on the right track!",
    "coverage_start": "Let's get moving! Your body is ready for action!",

    # Exercise Tips
    "tip_skipping_breaks": "[REMINDER] You're skipping breaks - stay consistent for better results!",
    "tip_low_coverage_interval": "[TIP] Low coverage! Consider 15-20 min break intervals (Settings > Time Settings)",
    "tip_low_coverage_variety": "[TIP] Low coverage! Try more varied exercises to work different muscles",
    "tip_increase_frequency": "[TIP] Increase frequency to 20-25 min intervals for better coverage",
    "tip_good_frequency": "[TIP] Good frequency! Focus on exercises for neglected muscle groups",
    "tip_almost_full_coverage": "[TIP] Almost at full coverage! A few more varied exercises will get you there",

    # Body Map Display
    "movement_focus": "Movement Focus:",
    "muscle_groups_worked": "Muscle Groups Worked",
    "body_coverage_map": "Body Coverage Map",
    "muscle_activity": "Muscle Activity",
    "muscle_activity_label": "Muscle Activity",
    "not_worked": "Not worked",
    "light_activity": "Light (1-2x)",
    "medium_activity": "Medium (3-4x)",
    "heavy_activity": "Heavy (5+x)",
    "body_map_no_data": "No exercises completed yet today.\nStart moving to see your progress!",

    # Muscle Groups
    "muscle_arms": "Arms",
    "muscle_core": "Core",
    "muscle_shoulders": "Shoulders",
    "muscle_quads": "Quads",
    "muscle_neck": "Neck",
    "muscle_chest": "Chest",
    "muscle_back": "Back",
    "muscle_upper_back": "Upper Back",
    "muscle_lower_back": "Lower Back",
    "muscle_hamstrings": "Hamstrings",
    "muscle_calves": "Calves",
    "muscle_wrists": "Wrists",
    "muscle_glutes": "Glutes",
    "muscle_hips": "Hips",
    "muscle_ankles": "Ankles",
    "muscle_abs": "Abs",
    "muscle_forearms": "Forearms",
    "muscle_triceps": "Triceps",
    "muscle_biceps": "Biceps",

    # Break Status Messages
    "all_breaks_complete": "All {total} breaks complete! Great job!",
    "breaks_status": "{done} of {total} breaks completed ({remaining} to go)",
    "breaks_behind": "{done} of {total} breaks completed ({behind} behind schedule, {remaining} total remaining)",
    "breaks_with_escapes": "{done} of {shown} breaks completed ({escaped} escaped)",
    "day_complete": "Day complete! {done} of {total} breaks done",
    "day_ended": "Day ended: {done} of {total} breaks ({missed} missed)",
    "work_starts": "Work starts at {time} ({total} breaks planned today)",

    # Break Overlay Messages
    "overlay_time_to_move": "Time to Move!",
    "overlay_stretch_time": "Stretch Time",
    "overlay_exercise_time": "Exercise Time",
    "overlay_break_time": "Break Time",
    "overlay_seconds_left": "seconds left",
    "overlay_press_key": "Press any key for motivation!",
    "overlay_dismiss": "Dismiss",
    "accomplished_today": "Accomplished Today",
    "journey_begins": "Today's Journey Begins Now!",
    "press_esc_msg": "You can press ESC to close this window, but",

    # Activity Terms
    "break": "break",
    "breaks": "breaks",
    "exercise": "exercise",
    "exercises": "exercises",
    "stretch": "stretch",
    "stretches": "stretches",

    # ESC Key Messages
    "esc_completion_1": "you'll achieve peak couch potato status",
    "esc_completion_2": "your muscles will file for unemployment",
    "esc_completion_3": "you'll become one with the furniture",
    "esc_completion_4": "your spine will write you a breakup letter",
    "esc_completion_5": "you'll need a software update to remember how to walk",
    "esc_completion_6": "your body will put itself in airplane mode",
    "esc_completion_7": "you'll unlock the 'human pretzel' achievement",
    "esc_completion_8": "your circulation will take a permanent vacation",
    "esc_completion_9": "you'll become the office ergonomics warning poster",
    "esc_completion_10": "gravity will win the long game",
    "esc_completion_11": "you'll need WD-40 to turn your head",
    "esc_completion_12": "your legs will forget their purpose in life",

    # Keyboard Press Messages
    "keypress_msg_1": "Nice try, but your spine already filed a complaint.",
    "keypress_msg_2": "Nice try, but escape isn't in your exercise routine.",
    "keypress_msg_3": "Nice try, but your muscles voted unanimously for this break.",
    "keypress_msg_4": "Nice try, but the quit button is doing burpees.",
    "keypress_msg_5": "Nice try, but your body needs this more than Netflix needs your attention.",
    "keypress_msg_6": "Nice try, but clicking won't burn calories.",
    "keypress_msg_7": "Nice try, but your posture called - it wants you to stand up.",
    "keypress_msg_8": "Nice try, but this window has commitment issues to closing early.",
    "keypress_msg_9": "Nice try, but your future self is begging you to stretch.",
    "keypress_msg_10": "Nice try, but movement is non-negotiable.",
    "keypress_msg_11": "Nice try, but even your chair needs a break from you.",
    "keypress_msg_12": "Nice try, but the timer runs on determination, not clicks.",
    "keypress_msg_13": "Nice try, but your joints are staging an intervention.",
    "keypress_msg_14": "Nice try, but escape is a myth - exercise is reality.",
    "keypress_msg_15": "Nice try, but your circulatory system demands movement.",
    "keypress_msg_16": "Nice try, but sitting won't complete itself... wait, it will.",
    "keypress_msg_17": "Nice try, but your muscles have entered rebellion mode.",
    "keypress_msg_18": "Nice try, but the close button is on coffee break.",
    "keypress_msg_19": "Nice try, but your vertebrae are begging for mercy.",
    "keypress_msg_20": "Nice try, but this is a no-escape zone.",
    "keypress_msg_21": "Nice try, but your body's warranty requires regular movement.",
    "keypress_msg_22": "Nice try, but harder clicking won't make time go faster.",
    "keypress_msg_23": "Nice try, but your skeleton is disappointed in you.",
    "keypress_msg_24": "Nice try, but movement is the only way out.",
    "keypress_msg_25": "Nice try, but your blood flow has filed a formal protest.",
    "keypress_msg_26": "Nice try, but the universe insists you stretch.",
    "keypress_msg_27": "Nice try, but your muscles forgot what movement feels like.",
    "keypress_msg_28": "Nice try, but this timer has trust issues.",
    "keypress_msg_29": "Nice try, but your back will remember this betrayal.",
    "keypress_msg_30": "Nice try, but exercise is your only escape route.",

    # Errors and Dialogs
    "error_missing_deps": "Missing dependencies for system tray (pystray/Pillow). Please connect to internet and restart, or install manually: pip install pystray Pillow",
    "error_already_running": "{app_name} is already running. Exiting.",
    "error_title": "Error",
    "info_title": "Information",
    "warning_title": "Warning",
    "confirm_title": "Confirm",
    "confirm_reset_settings": "Are you sure you want to reset all settings to defaults?",
    "confirm_reset_data": "Are you sure you want to reset today's exercise data?",
    "settings_saved": "Settings saved successfully!",
    "settings_save_error": "Failed to save settings: {error}",
    "startup_enabled": "GitFit.dev will start automatically on login",
    "startup_disabled": "GitFit.dev will not start automatically on login",
    "startup_error": "Failed to modify startup settings: {error}",
    "reset_dialog_title": "Reset Settings",
    "reset_dialog_message": "Are you sure you want to reset all settings to defaults?",
    "reset_complete_title": "Settings Reset",
    "reset_complete_message": "All settings have been reset to defaults.",
    "check_updates_button": "Check for Updates",
    "validation_invalid_settings": "Invalid settings:",

    # Common Buttons
    "button_save": "Save",
    "button_cancel": "Cancel",
    "button_ok": "OK",
    "button_yes": "Yes",
    "button_no": "No",

    # Activity Types
    "activity_both": "Both",
    "activity_stretch": "Stretching Only",
    "activity_exercise": "Exercise Only",

    # Position Preferences
    "position_all": "All Positions",
    "position_sitting_standing": "Sitting & Standing",
    "position_sitting": "Sitting Only",
    "position_standing": "Standing Only",

    # Time Display
    "time_format_24": "24-hour",
    "time_format_12": "12-hour",

    # Help/About Dialog
    "about_title": "About GitFit.dev",
    "about_version": "Version: {version}",
    "about_description": "A fitness break reminder app for developers and desk workers.",
    "about_copyright": "© 2024 Jozef Jarosciak",
    "about_license": "Licensed under MIT License",
    "github_repo": "GitHub Repository",
    "about_check_version": "Check for Latest Version",
    "about_close": "Close",
    "up_to_date": "You are running the latest version.",
    "version_checking": "Checking for updates...",
    "update_available": "New version {version} is available!",
    "update_current": "You're running the latest version.",
    "update_check_failed": "Failed to check for updates.",

    # Preview Messages
    "preview_title": "Theme Preview",
    "preview_message": "Time to Move!",
    "preview_submessage": "Nice try, but your spine needs this.",
    "preview_close": "Close Preview",

    # Interval Display Hints
    "interval_every_min": "(every {minutes} min)",
    "interval_every_hour": "(every hour)",
    "interval_every_hours": "(every {hours} hours)",
    "interval_every_h_m": "(every {hours}h {minutes}m)",
    "interval_invalid": "(invalid)",

    # Trigger/Break Offset Hints
    "trigger_hint_5min": "(0-4 within each 5-min block)",
    "trigger_hint_10min": "(0-9 within each 10-min block)",
    "trigger_hint_15min": "(0-14 within each 15-min block)",
    "trigger_hint_20min": "(0-19 within each 20-min block)",
    "trigger_hint_25min": "(0-24 within each 25-min block)",
    "trigger_hint_30min": "(0-29 within each 30-min block)",
    "trigger_hint_45min": "(0-44 within each 45-min block)",
    "trigger_hint_generic": "(0-{max} within each {interval}-min block)",
    "trigger_hint_minute_hour": "(minute of the hour: 0-59)",
}

# Fitness-specific translations
FITNESS_TRANSLATIONS = {
    # Headers for overlay display
    "stretch_header": "Stretching Time:",
    "exercise_header": "Exercise Time:",
    "single_activity_header": "Time to Move:",

    # Break titles
    "break_title": "GitFit Break!",
    "time_to_stretch": "Time to Stretch!",
    "movement_time": "Exercise Time!",
    "wellness_break": "Wellness Break!",

    # Common exercise instructions
    "reps_continuous": "continuously",
    "reps_times": "times",
    "hold_seconds": "hold {} seconds",
    "each_side": "each side",
    "each_leg": "each leg",
    "each_arm": "each arm",
    "alternate": "alternate",
    "repeat": "repeat",

    # Position descriptions
    "position_standing": "Stand up for this exercise",
    "position_sitting": "Stay seated for this exercise",
    "position_lying": "Find a clear floor space for this exercise",
}

# Dismiss button texts
DISMISS_BUTTONS = [
    "Boss Alert!",
    "Meeting Mode",
    "Not Now",
    "Busy Bee",
    "In Zone",
    "Skip It",
    "Later, Gator",
    "Nope Rope",
    "All Done!",
    "I'm Good",
    "Exit Stage",
    "Peace Out",
    "Done Deal",
    "Mission Complete",
    "Break Over",
]

# Since exercises and stretches are already in English in fitness_data.py,
# we don't need translations for them. We'll just provide empty dicts
# that the system can check.
EXERCISE_TRANSLATIONS = {}  # English exercises use original descriptions
STRETCH_TRANSLATIONS = {}   # English stretches use original descriptions
MOTIVATION_TRANSLATIONS = {
    "Nice break! Posture reset complete.": "Nice break! Posture reset complete.",
    "Tiny moves, big wins.": "Tiny moves, big wins.",
    "Eyes happy. Neck happy. You got this.": "Eyes happy. Neck happy. You got this.",
    "Back thanks you.": "Back thanks you."
}