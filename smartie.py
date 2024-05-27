#--------------------------------------
# smartie.py
# Python driver for SureElectronics Smartie LCDs 
#--------------------------------------
import time
import argparse
import serial
import unicodedata

TTY_PATH = '/dev/ttyUSB0'
DELAY = 0.04
SCREEN_WIDTH = 20
SCREEN_LINES = 4

class Smartie(object):
    """Smartie class for interaction with LCD"""
    def __init__(self, path=TTY_PATH):
        self.lcd = serial.Serial(path, 9600)
        # initialise LCD using init sequence
        #self.lcd.write([b'\xFE', b'\x56', b'\x00'])
        self.lcd.write([int.from_bytes(b'\xFE', "big"), int.from_bytes(b'\x56', "big"), int.from_bytes(b'\x00', "big")])
    #-------------------------------------------------------------
    # command - run raw command to LCD
    #-------------------------------------------------------------
    def command(self, cmd):
        """Run raw command to LCD"""
        cmd_str = b''.join([b'\xFE'] + cmd)
        self.lcd.write(cmd_str)
        time.sleep(DELAY)

    #-------------------------------------------------------------
    # backlight_on - Send backlight on command
    #-------------------------------------------------------------
    def backlight_on(self):
        """Send backlight on command"""
        self.command([b'\x42', b'\x00'])

    #-------------------------------------------------------------
    # backlight_off - Send backlight off command
    #-------------------------------------------------------------
    def backlight_off(self):
        """Send backlight off command"""
        self.command([b'\x46'])

    #-------------------------------------------------------------
    # backlight_toggle_on - toggle backlight on/off
    #-------------------------------------------------------------
    def backlight_toggle_on(self, switch):
        """ Toggles backlight on/off """
        if switch is True:
            self.backlight_on()
        else:
            self.backlight_off()

    #-------------------------------------------------------------
    # set_contrast - set LCD contract value
    #-------------------------------------------------------------
    def set_contrast(self, amount):
        """Set LCD contrast"""
        self.command([b'\x50', chr(amount).encode()])

    #-------------------------------------------------------------
    # show_temperature - Show LCD temperature
    #--------------------------------------- ----------------------
    def show_temperature(self, line=1):
        """ show temperature command to the LCD """
        # e.g: smartie.command([b'\x57', b'\x04']) where 04 is line 4
        self.command([b'\x57', chr(line).encode()])

    #-------------------------------------------------------------
    # ClearScreen - Clear all text on LCD
    #-------------------------------------------------------------
    def clear_screen(self):
        """ Clear all text on LCD """
        for line in range(1, SCREEN_LINES+1):
            self.write_line(" ", line)

    #-------------------------------------------------------------
    # write_line - Write message to screen on line specified
    #--------------------------------------- ----------------------
    def write_line(self, data, line=1):
        """Write message to screen on line specified"""
        if line is None or line < 1 or line > 4:
            line = 1

        data = unicodedata.normalize('NFKD', data)
        data = data.encode('ascii', 'ignore')
        data = data.ljust(20)[:20]
        # self.command([b'\x47', b'\x01', chr(line).encode(), data.encode()])
        self.command([b'\x47', b'\x01', chr(line).encode(), data])

    #-------------------------------------------------------------
    # write_line_aligned - Left justified, Right justified or Centered
    #-------------------------------------------------------------
    def write_line_aligned(self, text, line=1, align="c"):
        """Write a line (l)left justified, (r)Right justified or (c)Centered """
        align = align.lower()
        if align == "c":
            text = text.center(SCREEN_WIDTH, " ")
        elif align == "r":
            text = text.rjust(SCREEN_WIDTH, " ")
        else:
            text = text.ljust(SCREEN_WIDTH, " ")
        self.write_line(text, line)

    #-------------------------------------------------------------
    # write_line_flash - Write one line and make it flash for
    #   specified number of times (count) and each flash duration
    #   (tick)
    #-------------------------------------------------------------
    def write_line_flash(self, text, line=1, count=3, tick=0.6):
        """ Write line with flash for count & duration"""
        i = 0
        while i < count:
            self.write_line(text, line)
            time.sleep(tick)
            self.write_line("", line)
            time.sleep(tick)
            i += 1
        self.write_line(text, line)

    #-------------------------------------------------------------
    # write_data_wrapped - send text and wrap to as many lines
    #   as required
    #-------------------------------------------------------------
    def write_data_wrapped(self, text):
        """send text and wrap to as many lines as required"""
        # set first row and truncate text to the max 80 chars
        row = 1
        data = text[:79]
        # chunk text and display on each line as required
        for i in range(0, len(data), 20):
            self.write_line(data[i:i+20], row)
            row += 1

    #-------------------------------------------------------------
    # write_lines - write lines passed as a list
    # ------------------------------------------------------------
    def write_lines(self, textlines):
        """Write lines passed as a list """
        # truncate list to match LCD line count
        texts = textlines[:SCREEN_LINES]
        # loop and display each line
        line = 1
        for linetext in texts:
            self.write_line(linetext, line)
            line += 1

    #-------------------------------------------------------------
    # write_lines_scroll - Write lines passed as list but scroll
    #   if more than max number of LCS lines
    #-------------------------------------------------------------
    def write_lines_scroll(self, textlines, speed=0.5):
        """Write lines passed as a list but scroll as required"""
        # take the lines list, and loop sending a batch at a time to the write_lines function
        numberoflines = len(textlines)
        # check any scrolling needed
        if numberoflines < (SCREEN_LINES+1):
            self.write_lines(textlines)
        else:
            startitem = 0
            # loop until all lines displayed
            while startitem < (numberoflines-(SCREEN_LINES-1)):
                #truncate list to 4 lines using new starting item
                displaytexts = textlines[startitem:startitem+SCREEN_LINES]
                self.write_lines(displaytexts)
                time.sleep(speed)
                startitem += 1

    #-------------------------------------------------------------
    # demo - Run all functions
    #--------------------------------------- ----------------------
    def demo(self):
        """Run a demo of all features for test"""
        self.clear_screen()
        self.backlight_toggle_on(True)
        self.write_line("Left", 1)
        self.write_line_aligned("Right", 2, "r")
        self.write_line_aligned("Center", 3, "c")
        self.write_line_flash("Flash", 4)
        time.sleep(2)
        self.write_data_wrapped("this is a long piece of text that will be wrapped as required!")
        time.sleep(2)
        self.write_lines(['1 As a list', '2', '3', '4'])
        time.sleep(3)
        self.clear_screen()
        self.write_lines_scroll(['1 As a scrolling list', '2', '3', '4', '5', '6', '7', '8'])
        time.sleep(2)
        self.clear_screen()
        self.show_temperature(1)
        time.sleep(2)
        self.clear_screen()
        time.sleep(2)
        self.backlight_toggle_on(False)

#-------------------------------------------------------------
# main function
#--------------------------------------- ----------------------
if __name__ == '__main__':    
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-b', '--backlight')
    PARSER.add_argument('-c', '--contrast', type=int)
    PARSER.add_argument('-l', '--line', type=int)
    PARSER.add_argument('-d', '--demo', default=False, action="store_true")
    PARSER.add_argument('-x', '--clear', default=False, action="store_true")
    PARSER.add_argument('message', nargs='?')
    ARGS = PARSER.parse_args()

    SMARTIE = Smartie()
    
    if ARGS.clear:
        SMARTIE.clear_screen()

    if ARGS.backlight == 'on':
        SMARTIE.backlight_on()
    elif ARGS.backlight == 'off':
        SMARTIE.backlight_off()

    if ARGS.contrast:
        SMARTIE.set_contrast(ARGS.contrast)

    if ARGS.demo:
        SMARTIE.demo()

    if ARGS.message:
        if ARGS.line == None:
            SMARTIE.write_data_wrapped(ARGS.message)
        else:
            SMARTIE.write_line(ARGS.message, ARGS.line)

    
