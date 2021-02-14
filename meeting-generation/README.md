# Meeting Generation

This script is intended to batch creation of Zoom meetings.

## Usage

**Input**: CSV of one column: `Email`  
**Output**: CSV of two columns: `Email`,`Link`  
**Options**: See `--help`
+ `-t, --topic TEXT`: Name (Topic) of meeting (with the @ symbol replaced by the participant email)
+ `-c, --cohost`: Add each email as a co-host for their meeting
+ `-w, --when INTEGER`: Date/time of meeting, as a [UNIX timestamp](https://www.epochconverter.com/) (in seconds)
+ `-d, --duration INTEGER`: Duration of meeting, in minutes (ex. 60, 90, 120)
+ `-b, --browser [chrome|firefox]`: Which Selenium WebDriver to use

## Example

```
python meeting-generation.py emails.csv links.csv -t "[CS 162] Demo Exam: @" -c -w 1604016000 -d 90
```

## Notes/Recommendations

+ May want to turn off the meeting enter/exit sound notification in Zoom Settings ("Sound notification when someone joins or leaves")
+ May want to turn off the associated email notifications in Zoom Settings ("When a cloud recording is available").
+ When using the `--cohost` option, you may want to turn off the Zoom email notifications that go to hosts ("When an alternative host is set or removed from a meeting").
+ When using the `--duration` option, make sure the quantity is selectable in Zoom's dropdown.

## Known Issues

+ Some users see the message "you have a meeting that is currently in progress"; it is safe to click "end other meeting" and join anyway.
+ Some users do not have Zoom Education accounts provisioned (usually concurrent enrollment students); we usually handle these cases separately.
+ Zoom's web client sometimes doesn't allow someone to join a meeting (seen in FA20, might have been fixed).
