import os
import requests
from ics import Calendar
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
LOCATION = "Sevenoaks" # For weather
CALENDAR_URL = os.getenv("CALENDAR_URL")

# 1. Fetch Data
c = Calendar(requests.get(CALENDAR_URL).text)
weather_raw = requests.get(f"https://wttr.in/{LOCATION}?format=%l:+%C+%t\n%d+%C+%h+%H").text

# 2. Setup Portrait Image (600x800)
img = Image.new('L', (600, 800), color=255)
draw = ImageDraw.Draw(img)

# Try to load a default font (Kindles look best with simple sans-serif)
try:
    font_header = ImageFont.load_default(size=40)
    font_date = ImageFont.load_default(size=30)
    font_event = ImageFont.load_default(size=25)
    font_weather = ImageFont.load_default(size=22)
except:
    font_header = font_date = font_event = font_weather = ImageFont.load_default()

# 3. Define the Window (Start of Today + 3 days)
now = datetime.now(timezone.utc)
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_time = start_of_today + timedelta(days=3)

# 4. Filter and Sort
events = [e for e in c.events if e.begin.datetime >= start_of_today and e.begin.datetime <= end_time]
events.sort(key=lambda x: x.begin)

# 5. Draw Header
draw.rectangle([0, 0, 600, 80], fill=0) # Black header bar
draw.text((20, 15), "MY CALENDAR", fill=255, font=font_header)
draw.text((420, 30), now.strftime("%H:%M"), fill=255, font=font_date)

# 6. Draw Events
y_cursor = 100
current_date = None

for event in events[:12]: # Show up to 12 events
    event_date = event.begin.strftime("%A, %b %d")
    
    if event_date != current_date:
        current_date = event_date
        y_cursor += 20
        draw.text((20, y_cursor), event_date.upper(), fill=0, font=font_date)
        y_cursor += 40
        draw.line((20, y_cursor-5, 250, y_cursor-5), fill=0, width=2)

    time_str = event.begin.strftime("%H:%M")
    # Handle All-Day events (they often show as 00:00)
    if event.all_day:
        time_str = "All Day"
        
    draw.text((40, y_cursor), f"{time_str}   {event.name[:35]}", fill=0, font=font_event)
    y_cursor += 45

# 7. Draw 3-Day Weather at the Bottom
draw.line((20, 650, 580, 650), fill=0, width=2)
y_weather = 670

# Fetch weather (Simplified for 3 days)
# We use a simple text-based fetch here for stability
try:
    w_resp = requests.get(f"https://wttr.in/{LOCATION}?format=%a+%C+%t\n").text
    draw.text((20, y_weather), f"Weather in {LOCATION}: {w_resp}", fill=0, font=font_weather)
except:
    draw.text((20, y_weather), "Weather currently unavailable", fill=0, font=font_weather)

# 8. Save
img.save("calendar.png")
