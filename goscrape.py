import re
import requests
from bs4 import BeautifulSoup
import calendar
from datetime import datetime
import json

month_list = list(calendar.month_name)[1:]
month_string = "|".join(month_list)
month_regexp = f"({month_string})"
date_pattern = re.compile(rf"^{month_regexp} (\d{{1,2}})", re.IGNORECASE)

def extract_date(year, event):
    match = date_pattern.match(event)
    if match:
        month_name = match.group(1)
        day = int(match.group(2))
        month_number = datetime.strptime(month_name, "%B").month
        return datetime(year, month_number, day)
    else:
        return None
    
def fetch_page(year):
    # Wikipedia page URL
    url = f"https://en.wikipedia.org/wiki/{year}"

    # Fetch the page content
    response = requests.get(url)
    html = response.text  # Extract raw HTML

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Print the title of the page
    print(soup.title.text)
    content_id = soup.find("div", id="bodyContent")
    # print(content_id)

    uls = content_id.find_all("ul")
    lis = []
    for ul in uls:
        lis.append(ul.find_all("li"))

    events = [item for sublist in lis for item in sublist]
    
    parsed_events = {extract_date(year, event.get_text()) : event.get_text()  for event in events}
    return parsed_events

def custom_date(obj):
    if isinstance(obj, datetime.datetime):
        return obj.time("%d %m %Y")
    raise TypeError(f'Cannot serialize object of {type(obj)}')

def dump_json(eventdict):
    outdict = {}
    for eventdate, eventtext in eventdict.items():
        if (eventdate):
            outdict[eventdate.strftime("%d %m %Y")] = eventtext
    json_output = json.dumps(outdict,  indent = 4, ensure_ascii=False)
    return json_output

if __name__ == "__main__":
    year = 1523
    event_dict = fetch_page(year)
    jsonstring = dump_json(event_dict)
    with open(f"year{year}.json", "w", encoding="utf-8") as f:
        f.write(jsonstring)