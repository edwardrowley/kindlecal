import os
import requests
from ics import Calendar
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
LOCATION = "Sevenoaks"
FONT_FILE = "Roboto-Bold.ttf"
CALENDAR_URL = os.getenv("CALENDAR_URL")

# 1. Fetch Data
c = Calendar(requests.get(CALENDAR_URL).text)

# 2. Setup Image (600x800)
img = Image.new('L', (600, 800), color=255)
draw = ImageDraw.Draw(img)

# 3. Load Fonts
try:
    date_font = ImageFont.truetype(FONT_FILE, 38)
    event_font = ImageFont.truetype(FONT_FILE, 28)
    weather_font = ImageFont.truetype(FONT_FILE, 24)
except:
    date_font = event_font = weather_font = ImageFont.load_default()

# 4. Filter Events (Today + 3 Days)
now = datetime.now(timezone.utc)
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_time = start_of_today + timedelta(days=3)
events = [e for e in c.events if e.begin.datetime >= start_of_today and e.begin.datetime <= end_time]
events.sort(key=lambda x: x.begin)

# 5. Draw Events
y = 30
current_date = ""

for event in events[:12]:
    day_str = event.begin.strftime("%A, %b %d")
    if day_str != current_date:
        current_date = day_str
        y += 20
        draw.text((30, y), day_str.upper(), fill=0, font=date_font)
        y += 50
        draw.line((30, y-10, 220, y-10), fill=0, width=3)

    time_str = "All Day" if event.all_day else event.begin.strftime("%H:%M")
    display_name = (event.name[:30] + '..') if len(event.name) > 30 else event.name
    draw.text((45, y), f"{time_str}   {display_name}", fill=0, font=event_font)
    y += 48

# 6. Draw 3-Day Weather (Metric/Celsius)
draw.line((30, 680, 570, 680), fill=0, width=2)
try:
    # Fetching Celsius data via wttr.in
    weather = requests.get(f"https://wttr.in/{LOCATION}?format=%l:+%C+%t&m").text
    draw.text((30, 700), f"WEATHER: {weather}", fill=0, font=weather_font)
    draw.text((30, 740), "Sevenoaks Forecast: Next 3 Days", fill=0, font=weather_font)
except:
    draw.text((30, 700), "Weather currently unavailable", fill=0, font=weather_font)

# 7. Save
img.save("calendar.png")
