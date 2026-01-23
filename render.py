import os
import requests
from ics import Calendar
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta

# 1. Fetch Calendar
url = os.getenv("CALENDAR_URL")
c = Calendar(requests.get(url).text)

# 2. Setup Image (600x800 for Portrait)
# Changed from (800, 600) to (600, 800)
img = Image.new('L', (600, 800), color=255) 
draw = ImageDraw.Draw(img)

# 3. Define the Window (Today + next 3 days)
start_time = datetime.now()
end_time = start_time + timedelta(days=3)

# 4. Filter and Sort Events
events = [e for e in c.events if e.begin.datetime >= start_time and e.begin.datetime <= end_time]
events.sort(key=lambda x: x.begin)

# 5. Drawing Logic (Adjusted X-coordinates for 600px width)
y_cursor = 60
draw.text((30, 20), f"Kindle Calendar | Updated: {start_time.strftime('%H:%M')}", fill=0)
draw.line((30, 45, 570, 45), fill=0) # Shortened line for 600px width

current_date = None

for event in events[:18]: # Can fit more events in portrait!
    event_date = event.begin.strftime("%A, %b %d")
    
    # If it's a new day, print a header
    if event_date != current_date:
        current_date = event_date
        y_cursor += 15
        draw.text((30, y_cursor), event_date.upper(), fill=0)
        y_cursor += 25
        draw.line((30, y_cursor-5, 180, y_cursor-5), fill=0)

    # Print the event (adjusted indent)
    time_str = event.begin.strftime("%H:%M")
    draw.text((45, y_cursor), f"{time_str} - {event.name}", fill=0)
    y_cursor += 35

# 6. Save
img.save("calendar.png")
