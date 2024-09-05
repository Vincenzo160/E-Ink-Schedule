# E-Ink Schedule
Display your schedule on a e-ink display using a Raspberry Pi Pico WH with Micropython
Note: This project includes the display driver for the Waveshare Pico e-Paper 2.9 (B) display provided by Waveshare

## Hardware used
- Rasberry Pi Pico WH
- [Waveshare Pico e-Paper 2.9 (B)](https://www.waveshare.com/wiki/Pico-ePaper-2.9-B)

## Capabilities
- Display up to 7 tasks at a time
- Display the current date
- Display the schedule for tomorrow or today depending on the time of day

## How to install
For a more simple guide follow the one on [gorzog.com/e-ink-schedule](https://gorzog.com/e-ink-schedule) [TBD]
### Using MicroPico VS Code extension
1. Install the [MicroPico extension](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) on VS Code
2. Flash Micropython on the Rasberry Pi Pico [(Official guide)](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
3. Open a Micropython project
4. Connect the Rasberry Pi Pico to your computer
5. If you don't see the filesystem of your Rasberry Pi Pico on the explorer tab use the "Toggle Pico-W-FS" button on the VSC bottom status bar
6. Transfer [main.py](https://github.com/Vincenzo160/E-Ink-Schedule/blob/main/src/main.py) to the Rasberry Pi Pico
7. Install needed dependecies (datetime) using the MicroPico Tab (You may need to connect to a Wi-Fi Network)
8. Open main.py on the filesystem of the Rasberry Pi Pico and modify the config on the top of the file
   **System config:**
   `scdate`: Time after which to show the schedule for the next day 
   `fastBoot`: Use a less verbose init process (Faster)
   `utcOffset`: UTC offset in hours (ex. 2 = UTC+2)
   `refreshTime`: How many seconds to wait before updating information
   **Network config:**
   `ssid`: The SSID of your Wi-Fi network [REQUIRED]
   `password`: The password of your Wi-Fi network [REQUIRED]
   `ntptime.host`: NTP Server to use for time retrieval
   `scheduleServer`: URL for the schedule.json hosted on a web server, you can find an example for formatting [here](https://github.com/Vincenzo160/E-Ink-Schedule/blob/main/example/schedule.json), for more info see [schedule format](https://github.com/Vincenzo160/E-Ink-Schedule/blob/main/README.md#Schedule+Format)
   **Strings:**
   These can be used for localization, try to use the same character count otherwise change manualy the offsets
   **Display driver config:**
   Display pins mapping, don't change if using socket

## Schedule Format
The Rasberry Pi Pico will retrieve your schedule from a web server, the screen can display up to 7 subjects if more are defined "..." will be displayed instead, if the day dosen't contain any subject a "free" screen will be displayed.
Example Schedule:
```
{
  "weekly_schedule": {
    "0": [
      {
        "time": "08",
        "subject": "Hello World!"
      }
    ],
    "1": [
      ...
    ],
    "2": [
      ...
    ],
    "3": [
      ...
    ],
    "4": [
      ...
    ],
    "5": [
      {
        "displayMode": "free"
      }
    ],
    "6": [
      ...
    ]
  }
}
```

For a full example see [example/schedule.json](https://github.com/Vincenzo160/E-Ink-Schedule/blob/main/example/schedule.json)