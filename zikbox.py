#! /usr/bin/python3
"""
    File: zikbox.py
    Groove box expander synth midi with fluidsynth
    From groovit_01.py
    See changelog file.
    Date: vendredi, 19/08/16
    Author:
    Coolbrother

"""

import time
import fluidsynth
import mido
import curses
import os

# print("module path: ", os.path.abspath(fluidsynth.__file__))

# global variables
_driver = "alsa"
_device = "hw:2"
_bank_file = "/home/com/banks/sf2/fluidr3_gm.sf2"

id_octave =101
id_transpose =103
id_velocity =105
id_channel =111
id_bank = 113
id_preset = 115
id_patch = 117


_gm_patch_lst = [
            'Acoustic Grand Piano',
            'Bright Acoustic Piano',
            'Electric Grand Piano',
            'Honky-Tonk Piano',
            'Electric Piano 1',
            'Electric Piano 2',
            'Harpsichord',
            'Clavinet',
            'Celesta',
            'Glockenspiel',
            'Music Box',
            'Vibraphone',
            'Marimba',
            'Xylophone',
            'Tubular Bells',
            'Dulcimer',
            'Drawbar Organ',
            'Percussive Organ',
            'Rock Organ',
            'Church Organ',
            'Reed Organ',
            'Accordion',
            'Harmonica',
            'Tango Accordion',
            'Nylon String Guitar',
            'Steel String Guitar',
            'Electric Jazz Guitar',
            'Electric Clean Guitar',
            'Electric Muted Guitar',
            'Overdriven Guitar',
            'Distortion Guitar',
            'Guitar Harmonics',
            'Acoustic Bass',
            'Electric Bass (finger)', 
            'Electric Bass (pick)',
            'Fretless Bass',
            'Slap Bass 1',
            'Slap Bass 2',
            'Synth Bass 1',
            'Synth Bass 2',
            'Violin',
            'Viola',
            'Cello',
            'Contrabass',
            'Tremolo Strings',
            'Pizzicato Strings',
            'Orchestral Harp',
            'Timpani',
            'String Ensemble 1',
            'String Ensemble 2',
            'SynthStrings 1',
            'SynthStrings 2',
            'Choir Aahs',
            'Voice Oohs',
            'Synth Voice',
            'Orchestra Hit',
            'Trumpet',
            'Trombone',
            'Tuba',
            'Muted Trumpet',
            'French Horn',
            'Brass Section',
            'SynthBrass 1',
            'SynthBrass 2',
            'Soprano Sax',
            'Alto Sax',
            'Tenor Sax',
            'Baritone Sax',
            'Oboe',
            'English Horn',
            'Bassoon',
            'Clarinet',
            'Piccolo',
            'Flute',
            'Recorder',
            'Pan Flute',
            'Blown Bottle',
            'Shakuachi',
            'Whistle',
            'Ocarina',
            'Lead 1 (square)',
            'Lead 2 (sawtooth)',
            'Lead 3 (calliope)',
            'Lead 4 (chiff)',
            'Lead 5 (charang)',
            'Lead 6 (voice)',
            'Lead 7 (fifths)',
            'Lead 8 (bass+lead)', 
            'Pad 1 (new age)',
            'Pad 2 (warm)',
            'Pad 3 (polysynth)',
            'Pad 4 (choir)',
            'Pad 5 (bowed)',
            'Pad 6 (metallic)',
            'Pad 7 (halo)',
            'Pad 8 (sweep)',
            'FX 1 (rain)',
            'FX 2 (soundtrack)',
            'FX 3 (crystal)',
            'FX 4 (atmosphere) 108 Koto',
            'FX 5 (brightness)',
            'FX 6 (goblins)',
            'FX 7 (echoes)',
            'FX 8 (sci-fi)',
            'Sitar',
            'Banjo',
            'Shamisen',
            'Koto',
            'Kalimba',
            'Bagpipe',
            'Fiddle',
            'Shanai',
            'Tinkle Bell',
            'Agogo',
            'Steel Drums',
            'Woodblock',
            'Taiko Drum',
            'Melodic Tom',
            'Synth Drum',
            'Reverse Cymbal',
            'Guitar Fret Noise',
            'Breath Noise',
            'Seashore',
            'Bird Tweet',
            'Telephone Ring',
            'Helicopter',
            'Applause',
            'Gunshot'
            ]

_gm2_drumkit = list(range(128))
_gm2_drumkit[0] = "Standard Kit 1"
_gm2_drumkit[1] = "Standard Kit 2"
_gm2_drumkit[8] = "Room Kit"
_gm2_drumkit[16] = "Power Kit"
_gm2_drumkit[24] = "Electronic Kit"
_gm2_drumkit[25] = "TR-808 Kit"
_gm2_drumkit[32] = "Jazz Kit"
_gm2_drumkit[40] = "Brush Kit"
_gm2_drumkit[48] = "Orchestra Kit"
_gm2_drumkit[56] = "Sound Fx Kit"

help = """
       Menu : Octave    Channel    Patch
        Use Key Left/Right to change menu, Key Up/Down to change menu item,
        Ctrl+F Filter On,
        Shift+F Filter Off,
        Escape to quit.
        """

#-------------------------------------------
DEBUG =1

def debug(msg="", title="", bell=True):
    if DEBUG:
        if msg:
            print("{}: {}".format(title, msg))
        if bell:
            curses.beep()
    
#------------------------------------------------------------------------------

def limit_value(val, min_val=0, max_val=127):
    """ limit value """
    
    if val < min_val: val = min_val
    elif val > max_val: val = max_val
    
    return val

#-------------------------------------------

def beep():
    """ make a beep """
    curses.beep()
#-------------------------------------------

class CChannel(object):
    """ Channel parameters """
    def __init__(self):
        self.chan =0
        self.patch =0
        self.bank =0
        self.msb_preset =0
        self.lsb_preset =0

    #-------------------------------------------

#========================================

class MidiFluid(object):
    """ fluidsynth manager """
    def __init__(self):
        self.fs = None
        self.sfid = None

    #-----------------------------------------
    
    def init(self, filename):
        """
        init Fluidsynth
        from MidiFluid object
        """

        driver = _driver
        # device = "hw:1"
        device = _device
        self.fs = fluidsynth.Synth(gain=0.5)
        self.fs.start(driver=driver, device=device)
        self.sfid = self.fs.sfload(filename, update_midi_preset=0)
        # chan, sfid, bank, preset
        # bank select 128 for percussion
        self.fs.program_select(0, self.sfid, 0, 0)
        # self.fs.bank_select(0, 128)

    #-----------------------------------------

    def close(self):
        """ close fluidsynth """
        self.fs.sfunload(self.sfid, update_midi_preset=0)
        self.fs.delete()

    #-----------------------------------------

    def play_notes(self):
        """
        test for fluidsynth
        from MidiFluid object
        """

        self.fs.noteon(0, 60, 100)
        time.sleep(1.0)
        self.fs.noteon(0, 67, 100)
        time.sleep(1.0)
        self.fs.noteon(0, 76, 100)

        time.sleep(1.0)

        self.fs.noteoff(0, 60)
        self.fs.noteoff(0, 67)
        self.fs.noteoff(0, 76)

        time.sleep(1.0)

    #-----------------------------------------

#========================================

class MidiManager(object):
    """ Midi manager from mido module """
    def __init__(self):
        self.synth = MidiFluid()
        self.chan =0
        self.vel = 64
        self.oct =0
        self.transp =0
        self.parent = None

    #-----------------------------------------

    def init(self, filename):
        """
        init synth 
        from MidiManager object
        """

        self.synth.init(filename)

    #-----------------------------------------

    def close(self):
        self.synth.close()

    def print_ports(self):
        """
        print input and output ports through mido driver
        from MidiManager object
        """

        print("In ports:")
        print(mido.get_input_names())
        print("Out ports:")
        print(mido.get_output_names())

    #-----------------------------------------
    def get_in_ports(self):
        return mido.get_input_names()

    #-----------------------------------------

    def get_out_ports(self):
        return mido.get_output_names()

    #-----------------------------------------

    def send_to(self, msg, port=0):
        output_names = mido.get_output_names()
        port_name = output_names[port]
        out_port = mido.open_output(port_name)
        out_port.send(msg)

    #-----------------------------------------

    def get_message_blocking(self, port=0):
        # Get incoming messages - blocking interface
        input_names = mido.get_input_names()
        port_name = input_names[port]
        in_port = mido.open_input(port_name)
        for msg in in_port: 
            print("\a") 
            print(msg)

    #-----------------------------------------

    def send_message(self, msg):
        """
        send message to fluidsynth
        from MidiManager object
        """
        
        # print("Message in:", msg)
        type = msg.type
        bank =0
        self.max_val = 127
        fs = self.synth.fs
        if type in ['note_on', 'note_off']:
            note = msg.note + (12 * self.oct + self.transp)
            note = limit_value(note, 0, self.max_val)
            msg.note = note
            chan = msg.channel
            if self.vel != 0:
                # velocity variation
                vel = msg.velocity + self.vel
                vel = limit_value(vel, 0, self.max_val)
                msg.velocity = vel
        if type == "note_on":
            fs.noteon(self.chan, msg.note, msg.velocity)
        elif type == "note_off":
            fs.noteoff(self.chan, msg.note)
        elif type == "program_change":
            fs.program_change(self.chan, msg.program)
        elif type == "control_change":
            fs.cc(self.chan, msg.control, msg.value)
        elif type == "pitchwheel":
            fs.pitch_bend(self.chan, msg.pitch)
        # notify toplevel application
        if self.parent:
            self.parent.notify(msg)

    #-----------------------------------------

    def input_callback(self, msg):
        """
        incomming messages callback
        from MidiManager object
        """

        self.send_message(msg)

    #-----------------------------------------

    def receive_from(self, port=0, callback=None):
        """
        Get incoming messages - nonblocking interface
        with cb_func as callback
        """

        portname = ""
        inputnames = mido.get_input_names()
        try:
            portname = inputnames[port]
        except IndexError:
            print("Error: Midi Port {} is not available".format(port))
        
        if portname:
            inport = mido.open_input(portname)
            # or we can pass the callback function at the opening port:
            # in_port = mido.open_input(port_name, callback=cb_func)
            if callback:
                inport.callback = callback

        """
        input_names = mido.get_input_names()
        port_name = input_names[port]
        in_port = mido.open_input(port_name)
        # or we can pass the callback function at the opening port:
        # in_port = mido.open_input(port_name, callback=cb_func)
        if callback:
            in_port.callback = callback
        """

    #-----------------------------------------

    def program_change(self, chan, program):
       """
       set program change
       from MidiManager object
       """

       if self.synth:
           self.synth.fs.program_change(chan, program)
           # input callback function
           self.chan = chan

    #-----------------------------------------

    def bank_change(self, chan, bank):
        """
        change bank
        from MidiManager object
        """
        
        if self.synth:
            self.synth.fs.bank_select(chan, bank)

    #-----------------------------------------
        
    def panic(self):
       """
       set all notes off controller on al channels
       from MidiManager object
       """

       control = 123 # all notes off
       if self.synth:
           for chan in range(16):
            self.synth.fs.cc(chan, control, 0)

    #-----------------------------------------

#========================================

class MenuItem(object):
    """ menuitem manager """
    def __init__(self):
        self.id =0
        self.title = ""
        self.action = None

    #-----------------------------------------
    
    def action_change(self, *args, **kwargs):
        """
        change action event 
        from MenuItem object
        """

        action = None
        
        if self.action:
            action = self.action(self, *args, **kwargs)
    
        return action
    #-----------------------------------------

#========================================

class MenuBase(list):
    """ Generic Menu base manager """
    def __init__(self, title="", index=0, lst=[]):
        list.__init__([])
        self.title = title
        self.index = index
        self[:] = lst

    #-----------------------------------------
    
    def items(self):
        """
        returns items list
        from MenuBase object
        """

        return self

    #-----------------------------------------

    def set_items(self, items):
        """
        set items list
        from MenuBase object
        """
        # Todo: best implementation

        self[:]  = items

    #-----------------------------------------

    def cur(self):
        """
        returns current item
        from MenuBase object
        """

        res = None
        try:
            res = self[self.index]
        except IndexError:
            pass
        
        return res

    #-----------------------------------------
    
    def evt_change(self, step=0, adding=0):
        """
        change current item in the list
        returns menuitem object
        from MenuBase object
        """
        
        res = None        
        changing =0
        val =0
        if not self:
            return (step, res)
        
        max_val = len(self) -1
        if adding == 0: # no adding step
            if step == -1:
                step = max_val
        else: # adding value
            val = self.index + step
            changing =1
        if changing:
            step = limit_value(val, 0, max_val)
        if self.index != step:
            self.index = step
            res = self[self.index]
        else: # no change for menu num
            beep()
   
        # debug("voici res {}".format(res))
        return (step, res)

    #-----------------------------------------

#========================================

class Menu(MenuBase):
    """ Generic Menu object """
    def __init__(self):
        MenuBase.__init__(self)
        self.index =0

    #-----------------------------------------
    
    def append(self, id=0, title="", action=None):
        """
        append menuitem in the list
        from Menu object
        """

        menuitem = MenuItem()
        menuitem.id = id
        menuitem.title = title
        menuitem.action = action
        super(Menu, self).append(menuitem)

        return menuitem

    #-----------------------------------------

#========================================

class TopMenu(object):
    """ container for menu object """
    def __init__(self):
        self.title = ""
        self.menu = None

    #-----------------------------------------

#========================================

class MenuBar(MenuBase):
    """ Menu Barre manager inherited from Menu object """
    def __init__(self):
        super().__init__()

    #-----------------------------------------
    
    def append_menu(self, title="", menu=None):
        """
        append topmenu object to the menu bar
        returns the topmenu object
        from MenuBar object
        """

        topmenu = TopMenu()
        topmenu.title = title
        topmenu.menu = menu
        # adding to the parent of Menu
        super(MenuBase, self).append(topmenu)

        return topmenu

    #-----------------------------------------

#========================================

class MenuManager(object):
    """ Menu Manager object """
    def __init__(self):
        self.menubar = None
        self.cur_menu = None
        self.cur_menuitem = None
        self._evt_click = None

    #-----------------------------------------

    def evt_change(self, step=0, adding=0):
        """
        change current item in the list
        returns topmenu object
        from Menu object
        """
        
        res = None        
        changing =0
        val =0
        if not self:
            return
        
        max_val = len(self) -1
        if adding == 0: # no adding step
            if step == -1:
                step = max_val
        else: # adding value
            val = self.index + step
            changing =1
        if changing:
            step = limit_value(val, 0, max_val)
        if self.index != step:
            self.index = step
        else: # no change for menu num
            pass
        try:
            res = self[self.index]
        except IndexError:
            pass
    
        return res

    #-----------------------------------------

    def set_menubar(self, menubar):
        """
        set the Menu Barre
        from MenuManager object
        """

        if menubar:
            self.menubar = menubar
            self.cur_topmenu = self.menubar.cur()
            self.cur_menu = self.cur_topmenu.menu
            self.cur_menuitem = self.cur_menu.cur()

    #-----------------------------------------

    def get_topmenu(self):
        """
        return current topmenu 
        from MenuManager object
        """
        
        return self.cur_topmenu

    #-----------------------------------------

    def topmenu_select(self, step=0, adding=0):
        """
        select menu in the menubar
        returns current topmenu selected
        from MenuManager object
        """

        topmenu_num =0
        if self.menubar:
            (topmenu_num, topmenu_item) = self.menubar.evt_change(step, adding)
            if topmenu_item is not None:
                self.cur_topmenu = topmenu_item
                self.cur_menu = self.cur_topmenu.menu
                self.cur_menuitem = self.cur_menu.cur()

        return (topmenu_num, self.cur_topmenu)

    #-----------------------------------------

    def get_menu(self):
        """
        return menu name and item
        from MenuManager object
        """
        
        return self.cur_menu

    #-----------------------------------------

    def get_menuitem(self):
        """
        return menuitem name and item
        from MenuManager object
        """
        
        return self.cur_menuitem
        
    #-----------------------------------------

    def menuitem_select(self, step=0, adding=0):
        """
        select menuitem
        returns current menuitem selected
        from MenuManager object
        """

        menuitem_num =0
        if self.cur_menu:
            (menuitem_num, menuitem_item) = self.cur_menu.evt_change(step, adding)
            if menuitem_item is not None:
                self.cur_menuitem =  menuitem_item

        return (menuitem_num, self.cur_menuitem)

    #-----------------------------------------

    def action_select(self, step=0, adding=0):
        """
        select menuitem
        returns current menuitem selected
        from MenuManager object
        """

        action = None

        if self.cur_menuitem:
            action = self.cur_menuitem.action_change(step, adding)

        return action

    #-----------------------------------------

    def set_evt_click(self, evt_click):
        """
        set click event
        from MenuManager object
        """

        self._evt_click = evt_click

    #-----------------------------------------

    def evt_click(self, *args, **kwargs):
        """
        call click event
        from MenuManager object
        """

        if self._evt_click:
            self._evt_click(self.cur_menuitem, *args, **kwargs)

    #-----------------------------------------

#========================================

class CData(MenuBase):
    """ Item manager """
    def __init__(self, title="", index=0, lst=[]):
        MenuBase.__init__(self, title, index, lst)
        self.title = title

    #-----------------------------------------

#========================================

class MidiParams(object):
    """ Midi Params manager """
    def __init__(self):
        self.octave_num =4
        self.octave_lst = list(range(-4, 8))
        self.oct_item = None
        self.transpose_num =12 # beging at 0 in the list
        self.transpose_lst = list(range(-12, 13))
        self.trans_item = None
        self.vel_num =64 # begining at medium
        self.vel_lst = list(range(128))
        self.vel_item = None
        self.channel_num =0 # for channel 1
        self.channel_lst = [] # containing channel object
        self.chan_item = None
        self.patch_num =0
        self.patch_item = None
        self.volume =0
        self.bank_lst = ["0 (MSB)", "32 (LSB)"]
        self.bank_num =0
        self.bank_item = None
        self.preset_lst = list(range(128))
        self.preset_item = None
        self.msb_preset_num =0
        self.lsb_preset_num =0
        self.bank_select_num =0 # result of: (msb_preset_num + lsb_preset_num*128)
        self.bank_select_lst = [0, 128] # bank select allowed
        self.bank_select_item = None
        self.preset_modified =0
        self.new_patch_lst = list(range(128)) # empty patch
        self.filename = "/home/com/banks/sf2/fluidr3_gm.sf2"
        # self.filename = "/home/banks/sf2/drum_loops.sf2"
        self.data_dic = {}
        self.curdata = None

    #-----------------------------------------

    def init(self):
        """
        init midi params 
        from MidiParams object
        """

        self.set_channels()
        # construct data dictionnary
        # CData takes 3 arguments to init:
        # title, index, lst
        self.oct_data = CData("Octave", self.octave_num, 
                self.octave_lst)
        self.data_dic[id_octave] = self.oct_data
        self.trans_data = CData("Transpose", self.transpose_num,
                self.transpose_lst)
        self.data_dic[id_transpose] = self.trans_data
        self.vel_data = CData("Velocity", self.vel_num, 
                self.vel_lst)
        self.data_dic[id_velocity] = self.vel_data
        
        self.curdata = self.oct_data



    #-----------------------------------------

    def set_data(self, id):
        """
        set current data object
        from MidiParams object
        """

        try:
            self.curdata = self.data_dic[id]
        except KeyError:
            pass

        return self.curdata
    
    #-----------------------------------------

    def get_channel(self):
        """
        returns channel object
        from MidiParams object
        """
        
        res = None
        try:
            res = self.channel_lst[self.channel_num]
        except IndexError:
            pass

        return res

    #-----------------------------------------
    
    def set_channels(self):
        """
        set channel object list
        from MidiParams object
        """
        
        self.channel_lst = []
        for i in range(16):
            ch = CChannel()
            ch.chan = i
            self.channel_lst.append(ch)

    #-------------------------------------------

    def event_change(self, ev_num, ev_lst, step=0, adding=0):
        """
        generic change event
        from MidiParams object
        """

        changing =0
        val =0
        ev_item = None
        if not ev_lst:
            return (ev_num, ev_item)

        max_val = len(ev_lst) -1
        if adding == 0:
            if step == -1:
                step = max_val
        else: # adding value
            val = ev_num + step
            changing =1
        if changing:
            step = limit_value(val, 0, max_val)
        if ev_num != step:
            ev_num = step
            ev_item = ev_lst[ev_num]
        else: # no change for menu num
            beep()
        
        return (ev_num, ev_item)

    #-------------------------------------------

    def channel_change(self, chan_num, step=0, adding=0):
        """
        changing channel object in list
        from MidiParams
        """

        changing =0
        val =0
        chan_item = None
        if not self.channel_lst:
            return (chan_num, chan_item)
        
        max_val = len(self.channel_lst) -1
        if adding == 0:
            if step == -1:
                step = max_val
        else: # adding value
            val = chan_num + step
            changing =1
        if changing:
            step = limit_value(val, 0, max_val)
        if chan_num != step:
            chan_num = step
            chan_item = self.channel_lst[chan_num]
        else: # no change for chan num
            beep()
            
        
        return (chan_num, chan_item)
    
    #-------------------------------------------

#========================================

class MainApp(object):
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho() # don't repeat key hit at the screen
        # curses.cbreak()
        # curses.raw() # for no interrupt mode like suspend, quit
        curses.start_color()
        curses.use_default_colors()
        self.ypos =0; self.xpos =0
        self.height, self.width = self.stdscr.getmaxyx()
        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)
        self.win.refresh()
        self.win.keypad(1) # allow to catch code of arrow keys and functions keys
        # self.win.nodelay(1)

        self.octave_num =4
        self.octave_lst = range(-4, 8)
        self.transpose_num =12 # beging at 0 in the list
        self.transpose_lst = range(-12, 13)
        self.vel_num =1 # begining at medium
        self.vel_lst = [0, 64, 127]
        self.nbnote =12 # notes per octave
        self.channel_num =0 # for channel 1
        self.channel_lst = [] # containing channel object
        self.patch_num =0
        self.volume =0
        self.bank_lst = ["0 (MSB)", "32 (LSB)"]
        self.bank_num =0
        self.preset_lst = range(128)
        self.msb_preset_num =0
        self.lsb_preset_num =0
        self.bank_select_num =0 # result of: (msb_preset_num + lsb_preset_num*128)
        self.bank_select_lst = [0, 128] # bank select allowed
        self.preset_modified =0
        self.new_patch_lst = range(128) # empty patch
        self.filename = _bank_file
        # self.filename = "/home/banks/sf2/drum_loops.sf2"

        self.channelmenu_names = [
                    'Channel',
                    'Bank', 
                    'Preset',
                    'Patch',
                    ]
        self.menu_num =0
        self.menuitem =0
        self.channelmenu_lst = [
                    self.onchannel,
                    self.onbank, 
                    self.onpreset,
                    self.onpatch,
                    ]

        self.curmenu = self.channelmenu_lst[self.menu_num]
        self.midi_man = None
        self.midiparams = None
        self.notifying =0
        self.menuman = MenuManager()

        # global menu
        # id, title, action
        id =0
        global_menu = Menu()
        global_menu.append(id_octave, "Octave", self.onoctave)
        global_menu.append(id_transpose, "Transpose", self.ontranspose)
        global_menu.append(id_velocity, "Velocity", self.onvelocity)
        
        # midi menu
        midi_menu = Menu()
        midi_menu.append(id_channel, "Channel", self.onchannel)
        midi_menu.append(id_bank, "Bank", self.onbank)
        midi_menu.append(id_preset, "Preset", self.onpreset)
        midi_menu.append(id_patch, "Patch", self.onpatch)
        
        self.menuman.set_evt_click(self.onclick)
        # Menu Bar
        # title, menu
        menubar = MenuBar()
        menubar.append_menu("Global Menu", global_menu)
        menubar.append_menu("Midi Menu", midi_menu)
        self.menuman.set_menubar(menubar)


    #-------------------------------------------
    
    def display(self, msg=""):
        self.win.clrtoeol()
        self.win.refresh()
        # self.win.addstr(3, 0, "                                                           ")
        self.win.addstr(3, 0, str(msg))
        self.win.move(3, 0)
        self.win.refresh()

    #-------------------------------------------

    def display_status(self, msg=""):
        self.win.clrtobot()
        self.win.move(22, 0) # bottom of screen
        self.win.addstr(22, 0, str(msg))
        self.win.move(22, 0) # bottom of screen

    #-------------------------------------------

    def display_menu(self):
        self.win.addstr(0, 0, str(help))
        self.win.move(0, 0)
        self.win.refresh()

    #-------------------------------------------

    def beep(self):
        curses.beep()

    #-------------------------------------------

    def notify(self, msg):
        """
        receive notification
        """

        if self.notifying:
            self.display(msg)

    #-------------------------------------------

    def switch_notifier(self):
        """
        active or not notification
        """

        self.notifying = not self.notifying
        if self.notifying:
            msg = "Notification enabled"
        else:
            msg = "Notification disabled"
        self.display(msg)

    #-------------------------------------------

    def print_ports(self):
        """
        print midi driver ports
        from MainApp object
        """
        inports = self.midi_man.get_in_ports()
        outports = self.midi_man.get_out_ports()
        msg = "Input ports: {} \nOutports: {}".format(inports, outports)
        self.display(msg)

    #-------------------------------------------

    def set_channels(self):
        """
        set channel list
        """
        
        self.channel_lst = []
        for i in range(16):
            ch = CChannel()
            ch.chan = i
            self.channel_lst.append(ch)

    #-------------------------------------------

    def get_menu_num(self):
        """ 
        returns menu number
        """
        
        return self.menu_num

    #-------------------------------------------

    def select_channelmenu(self, step=0, adding=0):
        """
        select menu by index
        """
        
        self.menu_num = self.event_change(self.menu_num, self.channelmenu_names, 
                step, adding)
        menu_name = self.channelmenu_names[self.menu_num]
        bank_name = self.bank_lst[self.bank_num]
        if self.bank_num == 0:
            preset_num = self.msb_preset_num
        else:
            preset_num = self.lsb_preset_num
        patch_name = _gm_patch_lst[self.patch_num]
        self.curmenu = self.channelmenu_lst[self.menu_num]
        if menu_name == "Channel":
            msg = "Menu {}: {}".format(menu_name, self.channel_num+1)
        elif menu_name == "Bank":
            msg = "Menu {}: {}".format(menu_name, bank_name)
        elif menu_name == "Preset":
            msg = "Menu {}: {}".format(menu_name, preset_num)
        elif menu_name == "Patch":
            msg = "Menu {}: {} - {}".format(menu_name, self.patch_num, patch_name)
        else:
            msg = "Menu {}".format(menu_name)
        self.display(msg)


    #-------------------------------------------

    def event_change(self, ev_num, ev_lst, step=0, adding=0):
        """
        generic change event
        from MainApp object
        """

        changing =0
        val =0
        max_val = len(ev_lst) -1
        if adding == 0:
            if step == -1:
                step = max_val
        else: # adding value
            val = ev_num + step
            changing =1
        if changing:
            step = limit_value(val, 0, max_val)
        if ev_num != step:
            ev_num = step
        else: # no change for menu num
            self.beep()
        
        return (ev_num, ev_lst[ev_num])

    #-------------------------------------------

    def channel_change(self, chan_num, step=0, adding=0):
        """
        changing channel object list
        """

        changing =0
        val =0
        max_val = len(self.channel_lst) -1
        if adding == 0:
            if step == -1:
                step = max_val
        else: # adding value
            val = chan_num + step
            changing =1
        if changing:
            step = limit_value(val, 0, max_val)
        if chan_num != step:
            chan_num = step
        else: # no change for chan num
            self.beep()
        
        return (chan_num, self.channel_lst[chan_num])
    
    #-------------------------------------------

    def onevent(self, step=0, adding=0):
        """
        Generic Event manager 
        from MainApp object
        """

        msg = "On Event"
        self.display(msg)
        self.beep()
        
    #-------------------------------------------

    def onclick(self, evt, *args, **kwargs):
        """
        click event handler
        from MainApp object
        """
        msg = ""
        
        params = self.midiparams
        if evt:
            if evt.id == id_octave:
                item = params.octave_lst[params.octave_num]
                msg = "{}: {}".format(evt.title, item)
            if evt.id == id_transpose:
                item = params.transpose_lst[params.transpose_num]
                msg = "{}: {}".format(evt.title, item)
            elif evt.id == id_patch:
                item = _gm_patch_lst[params.patch_num]
                msg = "{}: {}".format(evt.title, item)
            else:
                item =0
                msg = "{}: {}".format(evt.title, item)

            self.display(msg)
            self.beep()

    #-------------------------------------------

    def onoctave(self, evt, step=0, adding=0):
        """
        select octave menu by index
        from MainApp object
        """
        
        params = self.midiparams
        oct_data = params.oct_data
        # (params.octave_num, oct_item) = params.event_change(params.octave_num, params.octave_lst, step, adding)
        (oct_num, oct_item) = oct_data.evt_change(step, adding)
        if oct_item is not None:
            # params.oct_item = oct_item
            self.midi_man.oct = oct_item
        else:
            # oct_item = params.oct_item
            oct_item = oct_data.cur()
        
        msg = "Octave : {}".format(oct_item)
        self.display(msg)
        
    #-------------------------------------------

    def ontranspose(self, evt, step=0, adding=0):
        """
        select transpose menu by index
        """
        
        params = self.midiparams
        trans_data = params.trans_data
        (trans_num, trans_item) = trans_data.evt_change(step, adding)
        if trans_item is not None:
            self.midi_man.transp = trans_item
        else:
            trans_item = trans_data.cur()
        msg = "Transpose : {}".format(trans_item)
        self.display(msg)
        
    #-------------------------------------------

    def onvelocity(self, evt, step=0, adding=0):
        """
        select velocity menu by index
        """
        
        params = self.midiparams
        (params.vel_num, vel_item) = params.event_change(params.vel_num, params.vel_lst, step, adding)
        if vel_item is not None:
            params.vel_item = vel_item
            self.midi_man.vel = vel_item
        else:
            vel_item = params.vel_item
        msg = "Vel : {}".format(vel_item)
        self.display(msg)
        
    #-------------------------------------------

    def onchannel(self, evt, step=0, adding=0):
        """
        select channel menu by index
        """
        
        params = self.midiparams
        (params.channel_num,  chan_item) = params.channel_change(params.channel_num, step, adding)
        if chan_item is not None:
            params.chan_item = chan_item
            channel_obj = params.chan_item
            chan_num = channel_obj.chan
            patch_num = channel_obj.patch
            params.channel_num = chan_num
            params.patch_num = patch_num
            self.midi_man.chan = chan_num
            self.midi_man.program_change(chan_num, patch_num)
        else:
            self.beep()
        msg = "Channel : {}".format(params.channel_num+1)
        self.display(msg)

    #-------------------------------------------
    
    def onbank(self, evt, step=0, adding=0):
        """
        change bank type
        from MainApp object
        """

        params = self.midiparams
        channel_obj = params.chan_item
        chan_num = channel_obj.chan
        bank_num = channel_obj.bank
        (bank_num, bank_item) = params.event_change(bank_num, params.bank_lst, step, adding)
        if bank_item is not None:
            channel_obj.bank = bank_num
            params.bank_num = bank_num
            params.bank_item = bank_item
        else:
            bank_item = params.bank_item
            self.beep()
        
        msg = "{}".format(bank_item)
        self.display(msg)

    #-------------------------------------------

    def onpreset(self, evt, step=0, adding=0):
        """
        change bank preset
        """

        preset_item = None

        params = self.midiparams
        channel_obj = params.channel_lst[params.channel_num]
        chan_num = channel_obj.chan
        bank_num = channel_obj.bank
        msb_num = channel_obj.msb_preset
        lsb_num = channel_obj.lsb_preset
        if bank_num == 0: # msb type
            preset_num = msb_num
            (preset_num, preset_item) = params.event_change(preset_num, params.preset_lst, step, adding)
            if preset_item is not None:
                params.preset_item = preset_item
                channel_obj.msb_preset = preset_num
                params.msb_preset_num = preset_num
        elif bank_num == 1: # lsb type
            preset_num = lsb_num
            (preset_num, preset_item) = params.event_change(preset_num, params.preset_lst, step, adding)
            if preset_item is not None:
                params.preset_item = preset_item
                channel_obj.msb_preset = preset_num
                params.msb_preset_num = preset_num
                channel_obj.lsb_preset = preset_num
                params.lsb_preset_num = preset_num
        if preset_item is None:
            self.beep()

        params.preset_modified =1
        params.bank_select_num = (params.msb_preset_num + (params.lsb_preset_num * 128))
        msg = "{}".format(params.preset_item)
        self.display(msg)

    #-------------------------------------------

    def onpatch(self, evt, step=0, adding=0):
        """
        select patch menu by index
        """
        
        params = self.midiparams
        channel_obj = params.chan_item
        chan_num = channel_obj.chan
        patch_num = channel_obj.patch
        if params.bank_select_num == 0: # GM patch
            patch_lst = _gm_patch_lst
        elif params.bank_select_num == 128: # GM2 drumkit set
            patch_lst = _gm2_drumkit
        else: # no bank select
            patch_lst = params.new_patch_lst
        (patch_num, patch_item) = params.event_change(patch_num, patch_lst, step, adding)
        if patch_item is not None:
            params.patch_item = patch_item
            channel_obj.patch = patch_num
            params.patch_num = patch_num
            if params.preset_modified and\
                params.bank_select_num in params.bank_select_lst:
                # change bank number before sending patch
                self.midi_man.bank_change(chan_num, self.bank_select_num)
                params.preset_modified =0
        else: # no patch_item
            self.beep()
        
        self.midi_man.program_change(chan_num, patch_num)
        msg = "{} - {}".format(patch_num, params.patch_item)
        self.display(msg)

    #-------------------------------------------

    def close_win(self):
        curses.nocbreak()
        self.win.keypad(0)
        curses.echo()

    #-------------------------------------------

    def test(self):
        chan=9; note=60; vel=127
        print("select_num: {}".format(self.bank_select_num))
        # print("len _gm_patch_lst: ", len(_gm_patch_lst))
        # self.synth.play_notes()
        # self.midi_man.print_ports()
        # self.print_ports()
        # self.midi_man.receive_from(port=1, callback=self.midi_man.input_callback)
        self.beep()
            
    #------------------------------------------------------------------------------

    def init_app(self):
        """
        init application
        from MainApp object
        """

        # self.set_channels()
        self.midiparams = MidiParams()
        self.midiparams.init()
        self.midi_man = MidiManager()
        self.midi_man.parent = self
        self.midi_man.init(self.filename)
        self.midi_man.receive_from(port=1, callback=self.midi_man.input_callback)

    #------------------------------------------------------------------------------
        
    def close_app(self):
        """
        close application
        from MainApp object
        """

        self.midi_man.close()

    #------------------------------------------------------------------------------

    def key_handler(self):
        msg = "Grovit Synth..."
        self.display(msg)
        curses.beep() # to test the nodelay function
        while 1:
            key = self.win.getch()
            if key >= 32 and key < 128:
                key = chr(key)
            if key == 'Q':
                self.close_app()
                self.close_win()
                self.beep()
                break
            elif key == 9: # Tab key
                (topmenu_num, topmenu) = self.menuman.topmenu_select(step=1, adding=1)

                msg = topmenu.title
                self.display(msg)
            elif key == 27: # Escape for key
                key = self.win.getch()
                if key == 9: # Alt+Tab
                    (topmenu_num, topmenu) = self.menuman.topmenu_select(step=-1, adding=1)
                    msg = topmenu.title
                    self.display(msg)
                elif key == 27: # Alt+Escape
                    self.beep()
            elif  key == ' ': # space
                self.switch_notifier()
            elif key == 10: # Enter key
                # click event
                self.menuman.evt_click()
            elif key == 20: # ctrl+T
                msg = "Test"
                self.display(msg)
                self.test()
            elif key == curses.KEY_LEFT:
                (menuitem_num, cur_menuitem) = self.menuman.menuitem_select(step=-1, adding=1)
                msg = cur_menuitem.title
                self.display(msg)
            elif key == curses.KEY_RIGHT:
                (menuitem_num, cur_menuitem) = self.menuman.menuitem_select(step=1, adding=1)
                msg = cur_menuitem.title
                self.display(msg)
            elif key == curses.KEY_UP:
                action = self.menuman.action_select(step=-1, adding=1)
            elif key == curses.KEY_DOWN:
                action = self.menuman.action_select(step=1, adding=1)
            elif key == '.' or key == curses.KEY_DC: # dot, delete key
                self.midi_man.panic()
                self.display("Panic")
            elif key == curses.KEY_HOME:
                # go to top of menuitem list
                self.menuman.menuitem_select(step=0, adding=0)
            elif key == curses.KEY_END:
                # go to end menuitem
                self.menuman.menuitem_select(step=-1, adding=0)
            elif key == curses.KEY_PPAGE:
                self.curmenu(step=-25, adding=1)
            elif key == curses.KEY_NPAGE:
                self.curmenu(step=25, adding=1)
    
    #-------------------------------------------
    
    def main(self):
        self.init_app()
        self.key_handler()

    #-------------------------------------------

#========================================

if __name__ == "__main__":
    app = MainApp()
    app.main()

#------------------------------------------------------------------------------
