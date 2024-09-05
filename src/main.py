from machine import Pin, SPI
import network
import requests
from time import sleep
import time
import json
import ntptime
import time
import framebuf
import utime

ver = "1.8"

# System config
scdate = 09 # When to show the schedule for the next day
fastBoot = True # Skip verbose boot
utcOffset = 2 # UTC + offset in hours (ex. 2 = UTC+2)
refreshTime = 3600 # Refresh time in seconds

# Network config
ssid = 'YOUR_SSID'
password = 'YOUR_PASSWORD'
ntptime.host = "1.europe.pool.ntp.org" # NTP server
scheduleServer = "https://YOUR_WEB_SERVER/schedule.json"

# Strings
str_today = "Today"
str_tomorrow = "Tomorrow"
str_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Display driver config
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

SCK_PIN         = 10
DIN_PIN         = 11
RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

# Pin definitions
led = Pin("LED", Pin.OUT)


led.value(0)
class EPD_2in9_B_V4_Portrait:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else :
            self.width = (EPD_WIDTH // 8) * 8 + 8
        self.height = EPD_HEIGHT
        
        self.spi = SPI(1,baudrate=4000_000,sck=Pin(SCK_PIN),mosi=Pin(DIN_PIN))
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        
        self.buffer_balck = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_balck, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)


    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        while(self.digital_read(self.busy_pin) == 1): 
            self.delay_ms(10) 
        self.delay_ms(20)
        
    def TurnOnDisplay(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Base(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF4)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Fast(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()
        
    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0x1C)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()


    def init(self):
        # EPD hardware init start
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   

        self.send_command(0x01) #Driver output control      
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)
        self.send_data(0x00)

        self.send_command(0x11) #data entry mode       
        self.send_data(0x03)

        self.send_command(0x44) #set Ram-X address start/end position   
        self.send_data(0x00)
        self.send_data(self.width//8-1)   

        self.send_command(0x45) #set Ram-Y address start/end position          
        self.send_data(0x00)
        self.send_data(0x00) 
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)

        self.send_command(0x3C) #BorderWavefrom
        self.send_data(0x05)	

        self.send_command(0x21) #  Display update control
        self.send_data(0x00)		
        self.send_data(0x80)	

        self.send_command(0x18) #Read built-in temperature sensor
        self.send_data(0x80)	

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(0x00)
        self.send_command(0x4F)   # set RAM y address count to 0X199    
        self.send_data(0x00)    
        self.send_data(0x00)
        self.ReadBusy()
        
        return 0
    
    def init_Fast(self):
        # EPD hardware init start
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   	

        self.send_command(0x18) #Read built-in temperature sensor
        self.send_data(0x80)

        self.send_command(0x22) # Load temperature value
        self.send_data(0xB1)		
        self.send_command(0x20)	
        self.ReadBusy()   

        self.send_command(0x1A) # Write to temperature register
        self.send_data(0x5a)		# 90		
        self.send_data(0x00)	
                    
        self.send_command(0x22) # Load temperature value
        self.send_data(0x91)		
        self.send_command(0x20)	
        self.ReadBusy()  

        self.send_command(0x01) #Driver output control      
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)
        self.send_data(0x00)

        self.send_command(0x11) #data entry mode       
        self.send_data(0x03)

        self.send_command(0x44) #set Ram-X address start/end position   
        self.send_data(0x00)
        self.send_data(self.width//8-1)   

        self.send_command(0x45) #set Ram-Y address start/end position          
        self.send_data(0x00)
        self.send_data(0x00) 
        self.send_data((self.height-1)%256)    
        self.send_data((self.height-1)//256)	

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(0x00)
        self.send_command(0x4F)   # set RAM y address count to 0X199    
        self.send_data(0x00)    
        self.send_data(0x00)
        self.ReadBusy()	
        
        return 0
    
    def display(self): # ryimage: red or yellow image
        self.send_command(0x24)
        self.send_data1(self.buffer_balck)

        self.send_command(0x26)
        self.send_data1(self.buffer_red)

        self.TurnOnDisplay()

    def display_Fast(self): # ryimage: red or yellow image
        self.send_command(0x24)
        self.send_data1(self.buffer_balck)

        self.send_command(0x26)
        self.send_data1(self.buffer_red)

        self.TurnOnDisplay_Fast()

    def Clear(self):
        self.send_command(0x24)
        self.send_data1([0xFF] * self.height * int(self.width / 8))
        
        self.send_command(0x26)
        self.send_data1([0x00] * self.height * int(self.width / 8))
                                
        self.TurnOnDisplay()

    def display_Partial(self, Image, Xstart, Ystart, Xend, Yend):
        if((Xstart % 8 + Xend % 8 == 8 & Xstart % 8 > Xend % 8) | Xstart % 8 + Xend % 8 == 0 | (Xend - Xstart)%8 == 0):
            Xstart = Xstart // 8
            Xend = Xend // 8
        else:
            Xstart = Xstart // 8 
            if Xend % 8 == 0:
                Xend = Xend // 8
            else:
                Xend = Xend // 8 + 1
                
        if(self.width % 8 == 0):
            Width = self.width // 8
        else:
            Width = self.width // 8 +1
        Height = self.height

        Xend -= 1
        Yend -= 1
	
        self.send_command(0x44)       # set RAM x address start/end, in page 35
        self.send_data(Xstart & 0xff)    # RAM x address start at 00h
        self.send_data(Xend & 0xff)    # RAM x address end at 0fh(15+1)*8->128 
        self.send_command(0x45)       # set RAM y address start/end, in page 35
        self.send_data(Ystart & 0xff)    # RAM y address start at 0127h
        self.send_data((Ystart>>8) & 0x01)    # RAM y address start at 0127h
        self.send_data(Yend & 0xff)    # RAM y address end at 00h
        self.send_data((Yend>>8) & 0x01)   

        self.send_command(0x4E)   # set RAM x address count to 0
        self.send_data(Xstart & 0xff)
        self.send_command(0x4F)   # set RAM y address count to 0X127    
        self.send_data(Ystart & 0xff)
        self.send_data((Ystart>>8) & 0x01)

        self.send_command(0x24)   #Write Black and White image to RAM
        for j in range(Height):
            for i in range(Width):
                if((j > Ystart-1) & (j < (Yend + 1)) & (i > Xstart-1) & (i < (Xend + 1))):
                    self.send_data(Image[i + j * Width])
        self.TurnOnDisplay_Partial()

    def sleep(self):
        self.send_command(0x10) 
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit()


def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        led.value(0)
        sleep(2)
        led.value(1)
    ip = wlan.ifconfig()[0]
    led.value(1)
    return ip

def get_subjects(day):
    subjects = []
    day_schedule = data["weekly_schedule"].get(str(day), [])
    for entry in day_schedule:
        if "subject" in entry and "time" in entry:
            subjects.append((entry["time"], entry["subject"]))
    return subjects

def get_formatted_date(date_tuple):
    months = str_months
    day = date_tuple[2]
    month = months[date_tuple[1] - 1]
    year = date_tuple[0] % 100 
    return "{:02d} {} {:02d}".format(day, month, year)

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=60)
        return True
    except OSError as e:
        print("No internet connection:", e)
        throwError("NTW ERR", "No connection or timeout")
        return False

def drawSchedule(subjects, isToday, formattedDate, hour):
    epd = EPD_2in9_B_V4_Portrait()
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)
    if isToday:
        epd.imagered.text(str_today, 45, 10, 0xff)
    else: 
        if str_tomorrow == "Tomorrow":
            epd.imagered.text(str_tomorrow, 30, 10, 0xff)
        else:
            epd.imagered.text(str_tomorrow, 40, 10, 0xff)
    epd.imageblack.hline(30, 20, 64, 0x00)
    print("Draw schedule: " + str(subjects))
    if len(subjects) == 0:
        print("Free as the wind")
        epd.imagered.text("Free as the wind", 0, 133, 0xff)

    else:
        print("Using " + str(len(subjects)) + " layout")
        clock = 0
        while clock < len(subjects):
            isPrev = False
            print("Subject: " + subjects[clock][1])
            if clock == 7:
                print("^...")
                epd.imageblack.text("...", 0, 40  + clock * 30, 0x00)
            if clock < 7:
                epd.imageblack.hline(0, 50 + 8 + clock * 30, 128, 0x00)
                input_string = subjects[clock][1]
                if len(input_string) > 15:
                    first_part = input_string[:15] + '-'
                    second_part = input_string[15:]
                    epd.imageblack.text(first_part, 0, 40  + clock * 30, 0x00)
                    epd.imageblack.text(second_part, 0, 40 + 10 + clock * 30, 0x00)
                    isPrev = True
                else:
                    if isPrev:
                        epd.imageblack.text(subjects[clock][1], 0, 40 + 40 + clock * 30, 0x00)
                    else:
                        epd.imageblack.text(subjects[clock][1], 0, 40 + clock * 30, 0x00)
            else:
                clock += len(subjects)
            clock += 1
            
    epd.imagered.hline(0, 260, 128, 0xff)
    epd.imagered.vline(90, 260, 36, 0xff)
    if hour < 10:
        hour = "0" + str(hour)
    else:
        hour = str(hour)
    epd.imagered.text(hour, 103, 275, 0xff)
    epd.imagered.text(formattedDate, 5, 275, 0xff)

    epd.display()
    epd.sleep()
    print("Sleeping")
        

def throwError(Error, CustomError=None):
    epd = EPD_2in9_B_V4_Portrait()
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)
    print("Displaying error")
    epd.TurnOnDisplay_Fast()
    epd.imagered.text("ERROR", 40, 10, 0xff)
    epd.imagered.hline(30, 20, 64, 0xff)
    epd.imagered.hline(0, 260, 128, 0xff)
    epd.imagered.vline(90, 260, 36, 0xff)
    epd.imagered.text(":(", 103, 275, 0xff)
    epd.imagered.text(Error, 5, 275, 0xff)


    ErrorDesc = "An error has occurred, please restart the microcontroller. - C'e' stato un errore, riavviare il microcontrollore."

    if ErrorDesc:
        def split_text(text, length):
            parts = [text[i:i+length] for i in range(0, len(text), length)]
            for i in range(len(parts) - 1):
                if not parts[i].endswith(' '):
                    parts[i] += '-'
            return parts

        lines = split_text(ErrorDesc, 15)
        for i, line in enumerate(lines):
            epd.imagered.text(line, 0, 103 + i * 10, 0xff)

    epd.imagered.hline(0, 100, 128, 0xff)
    epd.imagered.hline(0, 185, 128, 0xff)
    if CustomError: # MAX 31 characters
        input_string = CustomError
        if len(input_string) > 15:
            first_part = input_string[:15] + '-'
            second_part = input_string[15:]
            epd.imagered.text(first_part, 0, 190, 0xff)
            epd.imagered.text(second_part, 0, 200, 0xff)
            epd.imagered.hline(0, 215, 228, 0xff)
        else:
            epd.imagered.text(CustomError, 0, 190, 0xff)
            epd.imagered.hline(0, 205, 228, 0xff)



    epd.imagered.text("/!\\", 50, 80, 0xff)
    # epd.imagered.text("/!\\", 50, 220, 0xff)
    epd.display()
    epd.sleep()
    print("Sleeping")

if __name__ == '__main__':
    print("Init display")
    epd = EPD_2in9_B_V4_Portrait()
    epd.reset()
    if fastBoot==False:
        epd.Clear()
        
    led.value(1)
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)
    epd.imageblack.text("v" + ver, 5, 10, 0x00)
    print("Init display done")

    # CONNECTION
    print("Connecting to " + ssid)
    epd.imageblack.text(ssid, 0, 143, 0x00)
    if fastBoot==False:
        epd.imageblack.text("Connecting to:", 5, 133, 0x00)
        print("Fastboot disabled")
    else:
        epd.imageblack.text("Connecting and", 0, 123, 0x00)
        epd.imageblack.text("retriving, SSID:", 0, 133, 0x00)
        epd.imagered.text("Fastboot", 30, 50, 0xff)
        epd.imageblack.text("Please wait..", 0, 163, 0x00)
    epd.display()
    led.value(0)
    ip = None
    while ip == None:
        ip = connect()
        if ip:
            led.value(1)
            print("Connected as " + ip)
            if fastBoot==False:
                epd.imageblack.text("Connected!", 0, 163, 0x00)
                epd.imageblack.text("Waiting for", 0, 183, 0x00)
                epd.imageblack.text("Schedule...", 0, 193, 0x00)
                epd.display()

            try:
                ntptime.settime()
            except OSError as e:
                print("Connection failed:", e)
                throwError("WiFi -2", "Init connection failed, no NTP")

        else:
            print("Failed to connect, retrying...")
            sleep(5)
        

    print("Waiting for schedule")
    print("")
    print("")


    while True:
        if not is_connected():
            connect()
            print("Waiting for internet connection...")
            time.sleep(10)
            continue

        today = time.localtime(time.time() + (+utcOffset * 3600))
        today_day_of_week = today[6]
        print("h:"+str(today[3])+" m:"+str(today[4])+" s:"+str(today[5]))

        tomorrow = time.localtime(time.time() + (+utcOffset * 3600 + 86400))
        tomorrow_day_of_week = tomorrow[6]
        print("Today: " + str(today_day_of_week) + " Tomorrow: " + str(tomorrow_day_of_week))

        try:
            headers = {
                'User-Agent': 'Pico-cosimello/' + ver,
            }

            response = requests.get(scheduleServer, headers=headers)
            try:
                data = json.loads(response.text)
            except ValueError as e:
                print("JSON decoding failed:", e)
                throwError("JSON DF", "JSON decoding failed")
        except OSError as e:
            print("Request failed:", e)
            throwError("HTTP ERR", "HTTP request failed")

        subjects_today = get_subjects(today_day_of_week)
        subjects_tomorrow = get_subjects(tomorrow_day_of_week)

        formatted_today = get_formatted_date(today)
        print(today)
        current_hour = today[3]
        if 0 <= current_hour < scdate:
            print("Print schedule for today")
            drawSchedule(subjects_today, True, formatted_today, today[3])
        else:
            print("Print schedule for tomorrow")
            drawSchedule(subjects_tomorrow, False, formatted_today, today[3])

        time.sleep(refreshTime)
    
