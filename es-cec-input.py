#!/usr/bin/env python

# Name: es-cec-input.py
# Version: 1.3
# Description: cec remote control for emulation station in retropie
# Author: dillbyrne
# Homepage: https://github.com/dillbyrne/es-cec-input
# Licence: GPL3


# It depends on python-uinput package which contains
# the library and the udev rules at
# /etc/udev/rules.d/40-uinput.rules
#
# cec-utils also needs to be installed
#
# to run the code as a non root user
# sudo addgroup uinput
# sudo adduser pi uinput
#
# to start on boot, add to user crontab. crontab -e
# @reboot hohup ./home/pi/RetroPie/scripts/es-cec-input.py


import subprocess
import uinput
import sys
import re


# map ES supported keys to python-uinput keys
def get_keymap():

    keymap = {'left': uinput.KEY_LEFT, 'right': uinput.KEY_RIGHT,
            'up': uinput.KEY_UP, 'down': uinput.KEY_DOWN,
            'enter': uinput.KEY_ENTER, 'kp_enter': uinput.KEY_KPENTER,
            'tab': uinput.KEY_TAB, 'insert': uinput.KEY_INSERT,
            'del': uinput.KEY_DELETE, 'end': uinput.KEY_END,
            'home': uinput.KEY_HOME, 'rshift': uinput.KEY_RIGHTSHIFT,
            'shift': uinput.KEY_LEFTSHIFT, 'rctrl': uinput.KEY_RIGHTCTRL,
            'ctrl': uinput.KEY_LEFTCTRL, 'ralt': uinput.KEY_RIGHTALT,
            'alt': uinput.KEY_LEFTALT, 'space': uinput.KEY_SPACE,
            'escape': uinput.KEY_ESC, 'kp_minus': uinput.KEY_KPMINUS,
            'kp_plus': uinput.KEY_KPPLUS, 'f1': uinput.KEY_F1,
            'f2': uinput.KEY_F2, 'f3': uinput.KEY_F3,
            'f4': uinput.KEY_F4, 'f5': uinput.KEY_F5, 
            'f6': uinput.KEY_F6, 'f7': uinput.KEY_F7,
            'f8': uinput.KEY_F8, 'f9': uinput.KEY_F9, 
            'f10': uinput.KEY_F10, 'f11': uinput.KEY_F11,
            'f12': uinput.KEY_F12, 'num1': uinput.KEY_1, 
            'num2': uinput.KEY_2, 'num3': uinput.KEY_3, 
            'num4': uinput.KEY_4, 'num5': uinput.KEY_5, 
            'num6': uinput.KEY_6, 'num7': uinput.KEY_7,
            'num8': uinput.KEY_8, 'num9': uinput.KEY_9,
            'num0': uinput.KEY_0, 'pageup': uinput.KEY_PAGEUP, 
            'pagedown': uinput.KEY_PAGEDOWN, 'keypad1': uinput.KEY_KP1,
            'keypad2': uinput.KEY_KP2, 'keypad3': uinput.KEY_KP3, 
            'keypad4': uinput.KEY_KP4, 'keypad5': uinput.KEY_KP5,
            'keypad6': uinput.KEY_KP6, 'keypad7': uinput.KEY_KP7, 
            'keypad8': uinput.KEY_KP8, 'keypad9': uinput.KEY_KP9, 
            'keypad0': uinput.KEY_KP0, 'period': uinput.KEY_DOT, 
            'capslock': uinput.KEY_CAPSLOCK,'numlock': uinput.KEY_NUMLOCK,
            'backspace': uinput.KEY_BACKSPACE, 'pause': uinput.KEY_PAUSE,
            'scrolllock': uinput.KEY_SCROLLLOCK, 'backquote': uinput.KEY_GRAVE,
            'comma': uinput.KEY_COMMA, 'minus': uinput.KEY_MINUS,
            'slash': uinput.KEY_SLASH, 'semicolon': uinput.KEY_SEMICOLON,
            'equals': uinput.KEY_EQUAL,'backslash': uinput.KEY_BACKSLASH, 
            'kp_period': uinput.KEY_KPDOT, 'kp_equals': uinput.KEY_KPEQUAL,
            'a': uinput.KEY_A, 'b': uinput.KEY_B, 'c': uinput.KEY_C, 
            'd': uinput.KEY_D, 'e': uinput.KEY_E, 'f': uinput.KEY_F, 
            'g': uinput.KEY_G, 'h': uinput.KEY_H, 'i': uinput.KEY_I, 
            'j': uinput.KEY_J, 'k': uinput.KEY_K, 'l': uinput.KEY_L, 
            'm': uinput.KEY_M, 'n': uinput.KEY_N, 'o': uinput.KEY_O,
            'p': uinput.KEY_P, 'q': uinput.KEY_Q, 'r': uinput.KEY_R, 
            's': uinput.KEY_S, 't': uinput.KEY_T, 'u': uinput.KEY_U, 
            'v': uinput.KEY_V, 'w': uinput.KEY_W, 'x': uinput.KEY_X, 
            'y': uinput.KEY_Y, 'z': uinput.KEY_Z }

    return keymap

# create a dictionary of the buttons we need
# mapped to the physical key list.
# we then use this dictionary when the remote is pressed
# to generate the correct keypress
def generate_es_key_dict(keylist):
    
    es_key_dict = {}
    # A Button
    es_key_dict[('select', 'red')] = keylist[0]
    # B Button
    es_key_dict[('exit', 'green')] = keylist[1]
    # Start
    es_key_dict['Fast forward', 'blue'] = keylist[2]
    # Select
    es_key_dict[('rewind', 'yellow')] = keylist[3]
    # Left on DPAD
    es_key_dict[('left',)] = keylist[4]
    # Right on DPAD 
    es_key_dict[('right',)] = keylist[5]
    # Up on DPAD 
    es_key_dict[('up',)] = keylist[6]
    # Down on DPAD 
    es_key_dict[('down',)] = keylist[7] 
    
    return es_key_dict

# list of keys we actually need
# this will be stored in memory and will comprise of
# a,b,x,y,start,select,left,right,up,down
# keyboard corresponding values the user has chosen
# in the retroarch.cfg file
def generate_keylist():
    keylist = []
    key_bindings = get_key_bindings('/opt/retropie/configs/all/retroarch.cfg')
    keymap = get_keymap()
    errors = []
        
    for binding in key_bindings:
        
        try:
            keylist.append(keymap[binding])
        except KeyError as e:
            errors.append(e)
                
    if (len(errors) > 0):        
        print 'The %s keys in your retroarch.cfg are unsupported by this script\n' % ', '.join(map(str, errors))
        print 'Supported keys are:\n'
        print get_keymap().keys()
        sys.exit()

    return keylist

# read key mappings from retroarch.cfg file
# uses a regex to pull out the correct input values
def get_key_bindings(ra_cfg):

    keys = []
    
    #The below regex will only pull out the values that we care about - a,b,start,select,up,down,left,and right
    pattern = re.compile('^input_player1_([ab]|start|select|up|down|left|right).*$', re.MULTILINE)
    buffer = open(ra_cfg).read()
    
    for match in pattern.finditer(buffer):
        value = match.group(0)
        keys.append(match.group(0).split('=')[1][2:-1])

    return keys




def register_device(keylist):

    return uinput.Device(keylist)

def press_keys(line,device,key_dict):
    
    # check for key released as pressed was displaying duplicate
    # presses on the remote control used for development

    if "released" in line: 
        
        for es_tuple_key in key_dict.iterkeys():
            if any(es_key in line for es_key in es_tuple_key):
                device.emit_click(key_dict[es_tuple_key])
                break


def main():

    keylist = generate_keylist()
    es_key_dict = generate_es_key_dict(keylist)
    device = register_device(keylist)
    
    #use cec-client to track pressed buttons on remote
    p = subprocess.Popen('cec-client', stdout=subprocess.PIPE, bufsize=1)
    lines = iter(p.stdout.readline, b'')

    while True:

        # only run apply key presses when emulation station is running, not in emulators or kodi
        # kodi has its own built in support already

        running_processes = subprocess.check_output(['ps', '-A'])
        
        if running_processes.find('kodi.bin') == -1 and running_processes.find('retroarch') == -1:

            press_keys(lines.next(), device, es_key_dict)
        else:
            # prevent lines from building up in buffer when not in ES
            # as the commands would be applied when control returns to ES
            lines.next()


if __name__ == "__main__":
    main()
