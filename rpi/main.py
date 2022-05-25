import board
import digitalio
from RPLCD.i2c import CharLCD
import time
import websocket
import json
import os

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, cols=16, rows=2) #nastavit nastavení připojení k LCD 

kava = (0b01000, 0b00100, 0b01000, 0b11110, 0b10011, 0b10011, 0b10011, 0b11110) #vytvoření emotikony

SERVER_IP = os.getenv('SERVER_IP')

lcd.create_char(0, kava) #uložit emotikonu do paměti lcd
#lcd.write_string("\x00")

#nastavení pinu pro tranzistor
kaves_ok = digitalio.DigitalInOut(board.D4) 
kaves_ok.direction = digitalio.Direction.OUTPUT

amountOfHate = 0 #základní hodnota hatů
threshold = 3  #kolik káv pro to, aby se káva uvařila

framebuffer = [
        '',
        '',
        ]

def write_to_lcd(lcd, framebuffer, num_cols): #funkce pro psaní dlouhého textu
    lcd.home()
    for row in framebuffer:
        lcd.write_string(row.ljust(num_cols)[:num_cols])
        lcd.write_string('\r\n')

def loop_string(string, lcd, framebuffer): #funkce pro ježdění textu
    padding = ' ' * 16
    s = padding + string + padding
    for i in range(len(s) - 16 + 1):
        framebuffer[0] = s[i:i+16]
        write_to_lcd(lcd, framebuffer, 16)
        time.sleep(0) #rychlost 


def progress_bar(percentage):
    global lcd
    global threshold
    lcd.cursor_pos = (1, 0) 
    msg = ""
    for i in range(round(percentage / threshold * 16)):
        msg += "\00"

    lcd.write_string(msg)
    lcd.cursor_pos = (0,0)

def show_tweet(twt):
    global amountOfHate
    global threshold
    global kaves_ok
    global framebuffer
    #print("Received hate tweet, current hate is: " + amountOfHate)
    #write_to_lcd(framebuffer, 16)
    loop_string(''.join(twt.splitlines()), lcd, framebuffer)
    amountOfHate += 1
    
    if (amountOfHate == threshold):
        print("makin' da coffee")
        amountOfHate = 0
        kaves_ok.value = True
        time.sleep(0.5)
        kaves_ok.value = False
        progress_bar(amountOfHate)
        lcd.write_string("   Delam kavu")
        time.sleep(10)
        lcd.clear()
        lcd.write_string("Vitej, cekam na prvni tweet")
        

    else:
        progress_bar(amountOfHate)

    

def on_message(ws, message):
    print("got message")
    _json = json.loads(message)
    #tweet = _json[0]["body"]
    tweet = "test"
    show_tweet(tweet)

def on_open(ws):
    global isConnected
    isConnected = True
    global amountOfHate
    amountOfHate = 0
    print("Connected to server")
    lcd.write_string("Connected to    server")
    time.sleep(2)
    lcd.clear()
    lcd.write_string("Vitej, cekam na prvni tweet")

def animation():
    lcd.clear()
    lcd.cursor = (0,0)
    msg = ""
    for i in range(16):
        msg += "\00"
        lcd.cursor = (0,0)
        lcd.clear() 
        lcd.write_string(msg)
        time.sleep(0.35)

    lcd.clear()
    lcd.write_string("Na, dej si kaves")
    kaves_ok.value = True
    time.sleep(0.5)
    kaves_ok.value = False

lcd.clear()

wsapp = websocket.WebSocketApp("ws://" + SERVER_IP + ":8080/", on_message=on_message, on_open=on_open, keep_running=True)
wsapp.run_forever()

