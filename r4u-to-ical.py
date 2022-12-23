#!/usr/bin/env python3
from typing import Dict
from xml.dom.minidom import parseString
from icalendar import Calendar, Event, vCalAddress, vText, vDatetime, vDate
from datetime import datetime, date, timezone, timedelta

def main() -> int:
    events = list()
    cal = Calendar()
    cal.add('prodid', '//Fracs calendar adapter//frac.dev')
    cal.add('version', '2.0')
    try:
        html = open("running4you.html","r").read()
    except Exception as e:
        print("Cound not open file ./running4you.html because:\n\n", e)
        raise
    html = html[html.find('<table '):]
    html = html[:html.find("</table>")+10]
    contents = parseString(html)
    table = contents.childNodes.item(0).childNodes[3] # tbody
    for row in table.childNodes:
        if row.nodeName == 'tr':
            row = getRowCells(row)
            ev = genEvent(row)
            if ev :
                events.append(ev)
                cal.add_component(ev)
    print(events)
    f = open('training.ics', 'wb')
    f.write(cal.to_ical())
    f.close()
    print("Results in training.ics")
    return 0


def getRowCells(row) -> list[str]:
    """
    Extract the <td> sub elements from a row, their contents in a list.
    Elements will be:
    0: date
    1: day of week
    2: type
    3: description
    4: target HR
    5: warmup
    6: cooldown
    7: total distance
    8: note
    """
    rv = list()
    for c in row.childNodes:
        if c.nodeName == 'td' and c.hasChildNodes():
            rv.append(c.childNodes[0].data.strip())
    return rv


def genEvent(row: list[str]) -> Event|None :
    """
    gets input from getRowCells, returns  an calendar event
    """
    rv = Event()
    mytz = datetime.now(timezone.utc).astimezone().tzinfo
    timestamp = vDatetime(datetime.now()).to_ical()
    if row[2] == 'RIPOSO' :
        return None
    evdate = [int(x) for x in row[0].split("/")]
    evdate.reverse()
    evdate[0] = evdate[0] + 2000
    rv['dtstart'] = vDatetime(
        datetime(evdate[0], evdate[1], evdate[2]).replace(tzinfo=mytz)
        ).to_ical()
    rv['dtend'] = vDatetime(
        datetime(evdate[0], evdate[1], evdate[2]).replace(tzinfo=mytz)
            + timedelta(days=1)
        ).to_ical()
    description = row[2] + ": "
    if row[5] != "0":
        description = description + f"risc: {row[5]}, "
    description = description + row[3]
    if row[6] != "0":
        description = description + f", def: {row[6]}"
    rv['summary'] = description
    if len(row) > 8:
        rv['description'] = row[8]
    rv['organizer'] = vCalAddress('MAILTO:me@example.com')
    rv['uid'] = f'training-{row[2]}-{row[0]}@example.com'
    rv['dtstamp'] = timestamp
    rv['last-modified'] = timestamp
    rv['created'] = timestamp
#    rv['status'] = 'confirmed'
    return rv

main()