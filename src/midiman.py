#! /usr/bin/python3
import utils
import mido
import time
from modfluid import ModFluid

# mido.set_backend('mido.backends.portmidi')

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
        self.chan_item = self.channel_lst[0]
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

class MidiManager(object):
    """ Midi manager from mido module """
    def __init__(self):
        self.synth = ModFluid()
        self.chan =0
        self.vel = 64
        self.oct =0
        self.transp =0
        self.parent = None
        self._display = None
        self.driver = "alsa"
        self.device = "hw:1"
        self.bank_file = "/home/com/banks/sf2/fluidr3_gm.sf2"
        self._bpm =100
        self._tempo = 60 / self._bpm # time in sec
        self._midout = None
        self._notifying = True


    #-----------------------------------------

    def init(self, driver=None, device=None, bank_file=None):
        """
        init synth 
        from MidiManager object
        """
        self._display = self.parent.display
        if driver is None: driver = self.driver
        if device is None: device = self.device
        if bank_file is None: bank_file = self.bank_file

        self.synth.init(driver, device, bank_file)
        self._display("Zikbox Initialized.")
    #-----------------------------------------
    
    def close(self):
        """ 
        close the synth
        from MidiManager object
        """

        if self.synth:
            self.synth.close()
            self._display("Zikbox Closed.")

    #-----------------------------------------

    def load(self, bank_file=None, chan=1, *args, **kwargs):
        """
        load bank file
        from MidiManager object
        """

        if bank_file is None: bank_file = self.bank_file
        if self.synth:
            self.synth.load(int(chan), str(bank_file))
            self._display(f"load, bankfile: {bank_file}, chan: {chan}")

    #-----------------------------------------

    def unload(self, *args, **kwargs):
        """
        unload bank file
        from MidiManager object
        """
        
        if self.synth:
            self.synth.unload()
            self._display(f"unload ")

    #-----------------------------------------

    def initmod(self, driver=None, device=None, bank_file=None, *args, **kwargs):
        """ 
        Start the engine
        from Midimanager object
        """

        if driver is None: driver = self.driver
        if device is None: device = self.device
        if bank_file is None: bank_file = self.bank_file
        if self.synth is None:
            self.synth = ModFluid()
        if self.synth:
            self.synth.system_stop()
            self.synth.system_start(driver, device, bank_file)
            self._display(f"initmod, driver: {driver}, device: {device}, bankfile: {bank_file}")

    #-----------------------------------------
     
    def stopmod(self, *args, **kwargs):
        """ 
        Stop the engine
        from Midi manager object
        """

        if self.synth:
            self.synth.system_stop()
            self.synth = None
            self._display(f"stopmod ")

    #-----------------------------------------
        
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

    def send_to(self, msg=None, port=4):
        output_names = mido.get_output_names()
        try:
            portname = output_names[port]
            outport = mido.open_output(portname)
            print(f"Outportname: {portname}")
        except KeyError:
            print(f"Mido Output: cannot open port {port}")
            return
        
        if msg:
            outport.send(msg)

    #-----------------------------------------

    def connect_to(self, port=4):
        outport = None
        output_names = mido.get_output_names()
        try:
            portname = output_names[port]
            outport = mido.open_output(portname)
            print(f"Connect to Outport name: {portname}")
        except KeyError:
            print(f"Mido Output: cannot open port {port}")
            return
        
        
        return outport

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
        # print("messagetype: ", msg)
        bank =0
        self.max_val = 127
        fs = self.synth.fs
        if type in ['note_on', 'note_off']:
            m_vel = msg.velocity
            note = msg.note + (12 * self.oct + self.transp)
            note = utils.limit_value(note, 0, self.max_val)
            msg.note = note
            self.chan = msg.channel
            if self.vel != 0:
                # velocity variation
                vel = msg.velocity + self.vel
                vel = utils.limit_value(vel, 0, self.max_val)
                msg.velocity = vel
        if type == "note_on" and m_vel >0:
            fs.noteon(self.chan, msg.note, msg.velocity)
        elif type == "note_on" and m_vel == 0:
            fs.noteoff(self.chan, msg.note)
        elif type == "note_off":
            fs.noteoff(self.chan, msg.note)
            pass
        elif type == "program_change":
            fs.program_change(self.chan, msg.program)
        elif type == "control_change":
            fs.cc(self.chan, msg.control, msg.value)
        elif type == "pitchwheel":
            fs.pitch_bend(self.chan, msg.pitch)
        # notify toplevel application
        self.notify(msg)

    #-----------------------------------------

    def input_callback(self, msg):
        """
        incomming messages callback
        from MidiManager object
        """

        # print(f"In callback, msg type: {msg.type}")
        self.send_message(msg)
        # self.send_to(msg)

    #-----------------------------------------

    def receive_from(self, port=0, callback=None):
        """
        Get incoming messages - nonblocking interface
        with cb_func as callback
        """

        portname = ""
        callback = self.input_callback
        inputnames = mido.get_input_names()
        try:
            portname = inputnames[port]
        except IndexError:
            print("Error: Midi Port {} is not available".format(port))
        
        if portname:
            print("inportname: ",portname)
            inport = mido.open_input(portname)
            # or we can pass the callback function at the opening port:
            # in_port = mido.open_input(port_name, callback=cb_func)
            """
            while 1:
                msg = inport.receive()
                print("voici: ", msg)
            """

            # """
            if callback:
                print("Input callback is active")
                inport.callback = callback
                # no need to connect to out port
                # self._midout = self.connect_to(port=4)
            # """
            # while 1: pass

    #-----------------------------------------

    def notify(self, msg):
        """
        notify midi messages
        from MidiManager object
        """

        if self._notifying:
            self._display(msg)
   
    #-------------------------------------------
 
    def midport(self, *args, **kwargs):
        """
        Midi port function
        from MidiManager object
        """

        in_ports = self.get_in_ports()
        out_ports = self.get_out_ports()
        if not args:
            self._display(f"midport inputs: {in_ports}\noutputs: {out_ports}")
            return

        arg = args[0]
        if arg in kwargs.keys():
            if arg == "in":
                self._display(f"midiport, inputs: {in_ports}")
            elif arg == "out":
                self._display(f"midiport outputs: {out_ports}")
            elif arg == "con":
                self.send_to()
                self._display(f"midiport connect: ... ")
        else:
            self._display(f"midiport {arg}: option not found")


    #-----------------------------------------

    def prog(self, _prog=0, chan=1, *args, **kwargs):
        """
        set program change
        from MidiManager object
        """

        chan = int(chan)
        _prog = int(_prog)
        if self.synth:
            self.synth.program_change(chan, _prog)
            self._chan = chan
            self._display(f"prog: {_prog}, chan: {chan}")

    #------------------------------------------------------------------------------
       
    def bank(self, chan=1, _bank=0, *args, **kwargs):
        """
        change bank
        from MidiManager object
        """

        chan = int(chan)
        _bank = int(_bank)
        if self.synth:
            self.synth.bank_change(chan, _bank)
            self._display(f"bank: {_bank}, chan: {chan}")

    #-----------------------------------------
     
    def noteon(self, key=60, vel=100, chan=1, *args, **kwargs):
        """
        set note on 
        from MidiManager object
        """

        chan = int(chan)
        key = int(key)
        vel = int(vel)

        if self.synth:
            self.synth.note_on(chan, key, vel)
            self._display(f"noteon, key: {key}, vel: {vel}, chan: {chan}")

    #-----------------------------------------

    def noteoff(self, key=60, chan=1, *args, **kwargs):
        """
        set note off
        from MidiManager object
        """

        chan = int(chan)
        key = int(key)

        if self.synth:
            self.synth.note_off(chan, key)
            self._display(f"noteoff, key: {key}, chan: {chan}")

    #-----------------------------------------
    
    def note(self, key=60, vel=100, dur=1, chan=1, *args, **kwargs):
        """
        set note with duration
        from MidiManager object
        """
        print("key: ", repr(key))
        dur = float(dur)
        if self.synth:
            self.noteon(key, vel, chan)
            time.sleep(self._tempo * dur)
            self.noteoff(key, chan)
            self._display(f"note, key: {key}, vel: {vel}, dur: {dur}, chan: {chan}")

    #-----------------------------------------


    def cc(self, ctrl=7, val=100, chan=1, *args, **kwargs):
        """
        set note control change
        from MidiManager object
        """
        
        chan = int(chan)
        ctrl = int(ctrl)
        val = int(val)

        if self.synth:
            self.synth.control_change(chan, ctrl, val)
            self._display(f"cc, ctrl: {ctrl}, val: {val}, chan: {chan}")

    #-----------------------------------------
    
    def panic(self, *args, **kwargs):
       """
       set all notes off controller on al channels
       from MidiManager object
       """
       
       if self.synth:
           self.synth.system_panic()
           self._display("panic ")

    #-----------------------------------------
    
    def reset(self, *args, **kwargs):
        """
        Reset all notes off and programs on al channels
        from MidiManager object
        """

        if self.synth:
            self.synth.system_reset()
            self._display("reset ")

    #------------------------------------------------------------------------------
   
    def bpm(self, _bpm=100, *args, **kwargs):
        """
        set the bpm
        from MidiManager object
        """
        
        _bpm = float(_bpm)
        if self.synth:
            if _bpm >0: # to avoid ZeroDivisionError :-)
                self._tempo = 60 / _bpm
                self._bpm = _bpm
            self._display("bpm, bpm: {_bpm}")

    #-----------------------------------------

    def demo(self, _prog=16, chan=1, *args, **kwargs):
        """
        Test the app
        from MidiManager object
        """
       
        self.prog(_prog=_prog, chan=chan)
        for key in [60, 64, 67]:
            self.note(key=key, chan=chan)
        self.note(key=72,  dur=4, chan=chan)
        self._display(f"demo, prog: {_prog}, chan: {chan}")

    #-----------------------------------------

#========================================

if __name__ == "__main__":
    input("Test...")
