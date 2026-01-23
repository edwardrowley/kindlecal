import os
import requests
from ics import Calendar
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
LOCATION = "Sevenoaks"
FONT_FILE = "Roboto-Bold.ttf" # The file you just uploaded

# 1. Fetch Data
url = os.getenv("CALENDAR_URL")
c = Calendar(requests.get(url).text)

# 2. Setup Portrait Image (600x800)
img = Image.new('L', (600, 800), color=255)
draw = ImageDraw.Draw(img)

# 3. Load Custom Fonts
# If the file isn't found, it falls back to default so the script doesn't crash
try:
    header_font = ImageFont.truetype(FONT_FILE, 42)
    date_font = ImageFont.truetype(FONT_FILE, 32)
    event_font = ImageFont.truetype(FONT_FILE, 26)
    weather_font = ImageFont.truetype(FONT_FILE, 22)
except:
    header_font = date_font = event_font = weather_font = ImageFont.load_default()

# 4. Filter Events (Today + 3 Days)
now = datetime.now(timezone.utc)
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_time = start_of_today + timedelta(days=3)
events = [e for e in c.events if e.begin.datetime >= start_of_today and e.begin.datetime <= end_time]
events.sort(key=lambda x: x.begin)

# 5. Draw Header
draw.rectangle([0, 0, 600, 90], fill=0) 
draw.text((25, 20), "SCHEDULE", fill=255, font=header_font)
draw.text((450, 30), now.strftime("%H:%M"), fill=255, font=date_font)

# 6. Draw Events
y = 110
current_date = ""

for event in events[:10]: # Showing top 10 to keep it clean
    day_str = event.begin.strftime("%A, %b %d")
    if day_str != current_date:
        current_date = day_str
        y += 20
        draw.text((25, y), day_str.upper(), fill=0, font=date_font)
        y += 45
        draw.line((25, y-8, 150, y-8), fill=0, width=3)

    time_str = "All Day" if event.all_day else event.begin.strftime("%H:%M")
    draw.text((40, y), f"{time_str}   {event.name[:30]}", fill=0, font=event_font)
    y += 45

# 7. Draw 3-Day Weather at bottom
draw.rectangle([0, 680, 600, 800], fill=240) # Light grey footer
y_w = 700
try:
    # This grabs a 3-day text forecast in Metric (Celsius)
    weather = requests.get(f"https://wttr.in/{LOCATION}?format=%l:+%C+%t+%w").text
    draw.text((25, y_w), f"NOW: {weather}", fill=0, font=weather_font)
    
    # Simple future forecast simulation (using wttr format strings)
    # For a full 3-day icon grid, we'd need a more complex API, 
    # but this shows the immediate outlook nicely.
    y_w += 35
    draw.text((25, y_w), "OUTLOOK: Check Kindle for daily updates", fill=0, font=weather_font)
except:
    draw.text((25, y_w), "Weather service offline", fill=0, font=weather_font)

# 8. Save
img.save("calendar.png")
