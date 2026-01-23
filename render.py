import os
import requests
import icalendar
import recurring_ical_events
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
LOCATION = "Sevenoaks"
FONT_FILE = "Roboto-Bold.ttf"
CALENDAR_URL = os.getenv("CALENDAR_URL")

# 1. Fetch and "Unfold" Recurring Events
raw_data = requests.get(CALENDAR_URL).text
ical_data = icalendar.Calendar.from_ical(raw_data)

# 2. Define the 3-day Window
now = datetime.now(timezone.utc)
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_time = start_of_today + timedelta(days=3)

# 3. Get all occurrences (including the recurring ones!)
events = recurring_ical_events.of(ical_data).between(start_of_today, end_time)
events.sort(key=lambda x: x.get('DTSTART').dt if hasattr(x.get('DTSTART').dt, 'hour') else datetime.combine(x.get('DTSTART').dt, datetime.min.time()).replace(tzinfo=timezone.utc))

# 4. Setup Image (600x800)
img = Image.new('L', (600, 800), color=255)
draw = ImageDraw.Draw(img)

try:
    date_font = ImageFont.truetype(FONT_FILE, 38)
    event_font = ImageFont.truetype(FONT_FILE, 28)
    weather_font = ImageFont.truetype(FONT_FILE, 24)
except:
    date_font = event_font = weather_font = ImageFont.load_default()

# 5. Draw Events
y = 40
current_date = ""

for event in events[:12]:
    start = event.get('DTSTART').dt
    
    # Handle Date vs Datetime (All day events vs timed)
    if not isinstance(start, datetime):
        start = datetime.combine(start, datetime.min.time()).replace(tzinfo=timezone.utc)
    elif start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    day_str = start.strftime("%A, %b %d")
    if day_str != current_date:
        current_date = day_str
        y += 30
        draw.text((30, y), day_str.upper(), fill=0, font=date_font)
        y += 50
        draw.line((30, y-10, 220, y-10), fill=0, width=3)

    # Time formatting
    is_all_day = not hasattr(event.get('DTSTART').dt, 'hour')
    time_str = "All Day" if is_all_day else start.strftime("%H:%M")
    
    summary = str(event.get('SUMMARY'))
    display_name = (summary[:30] + '..') if len(summary) > 30 else summary
    
    draw.text((45, y), f"{time_str}   {display_name}", fill=0, font=event_font)
    y += 50

# 6. Draw Weather Footer
draw.line((30, 680, 570, 680), fill=0, width=2)
try:
    w_data = requests.get(f"https://wttr.in/{LOCATION}?format=%C+%t+%m&m").text
    draw.text((30, 700), f"Sevenoaks: {w_data}", fill=0, font=weather_font)
except:
    draw.text((30, 700), "Weather error", fill=0, font=weather_font)

img.save("calendar.png")
