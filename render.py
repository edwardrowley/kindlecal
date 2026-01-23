import os
import requests
from ics import Calendar
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta

# 1. Fetch Calendar
url = os.getenv("CALENDAR_URL")
c = Calendar(requests.get(url).text)

# 2. Setup Image (800x600 is standard Kindle resolution)
img = Image.new('L', (800, 600), color=255) # 'L' is grayscale
draw = ImageDraw.Draw(img)

# 3. Simple Drawing Logic
y_cursor = 50
draw.text((50, 20), f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fill=0)
draw.line((50, 45, 750, 45), fill=0)

# Filter for today's events
today = datetime.now().date()
events = [e for e in c.events if e.begin.date() == today]
events.sort(key=lambda x: x.begin)

for event in events[:10]: # Limit to 10 events
    time_str = event.begin.strftime("%H:%M")
    draw.text((50, y_cursor), f"[{time_str}] {event.name}", fill=0)
    y_cursor += 40

# 4. Save
img.save("calendar.png")
