"""
Generate schedule.json for website v2 pages (roster.html, counter.html).

Reads the same SHOWS data as make_show_schedule.py (Instagram PNG generator)
and outputs a JSON feed in the format expected by the v2 site pages.

Usage: python make_show_schedule_json.py
Output: schedule.json
"""

import json
from datetime import datetime
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# ── Show data (same source as make_show_schedule.py) ──────────────────
SHOWS = [
    ("APRIL", [
        ("18–19", "NTX Fort Worth Card Show",    "Amon G. Carter Jr Exhibits Hall", "Fort Worth, TX"),
        ("24–26", "Texoma Trading Card Expo",     "Choctaw Durant Event Center", "Durant, OK"),
    ]),
    ("MAY", [
        ("2–3",   "NTX Card Show",               "NTX Arena", "Arlington, TX"),
        ("9–10",  "North ATX Card Show",          "Cadence Bank Center", "Austin, TX"),
        ("23–24", "CardsAndMore Pflugerville",    "Courtyard Marriott Pflugerville", "Pflugerville, TX"),
    ]),
    ("JUNE", [
        ("12–14", "Austin Card Show",            "Palmer Event Center", "Austin, TX"),
    ]),
]


def parse_date_range(date_range_str):
    """Parse date range like '18–19' or '12–14' into start and end day."""
    parts = date_range_str.split('–')
    start_day = int(parts[0].strip())
    end_day = int(parts[1].strip())
    return start_day, end_day


def month_num(month_short):
    """Convert month abbreviation to number."""
    months = {
        "APRIL": 4, "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8,
        "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12,
        "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3,
    }
    return months.get(month_short, 1)


def generate_schedule_json():
    """Generate schedule.json from SHOWS data."""
    shows_list = []

    for month_name, month_shows in SHOWS:
        month_short = month_name[:3].upper()
        month_num_val = month_num(month_name)

        for date_range, venue_name, venue_address, city in month_shows:
            start_day, end_day = parse_date_range(date_range)

            show = {
                "month": month_name,
                "monthShort": month_short,
                "dateRange": date_range,
                "startDay": start_day,
                "endDay": end_day,
                "year": 2026,
                "monthNum": month_num_val,
                "name": venue_name,
                "venue": venue_address,
                "city": city,
            }
            shows_list.append(show)

    output = {
        "generated": datetime.now().strftime("%b %d, %Y %I:%M %p"),
        "shows": shows_list,
    }

    return output


if __name__ == "__main__":
    schedule_data = generate_schedule_json()
    output_path = os.path.join(script_dir, "schedule.json")

    with open(output_path, "w") as f:
        json.dump(schedule_data, f, indent=2)

    print(f"✓ Generated {output_path}")
    print(f"  {len(schedule_data['shows'])} shows listed")
