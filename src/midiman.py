#! /usr/bin/python3
import utils
import fluidsynth
import mido
import time

class MidiFluid(object):
    """ fluidsynth manager """
    def __init__(self):
        self.fs = None
        self.sfid = None

    #-----------------------------------------
    
    def init(self, driver, device, bank_file):
        """
        init Fluidsynth
        from MidiFluid object
        """

        self.fs = fluidsynth.Synth(gain=0.5)
        self.fs.start(driver=driver, device=device)
        self.sfid = self.fs.sfload(bank_file, update_midi_preset=0)
        # chan, sfid, bank, preset
        # bank select 128 for percussion
        self.fs.program_select(0, self.sfid, 0, 0)
        # self.fs.bank_select(0, 128)

    #-----------------------------------------
    
    def close(self):
        """ close fluidsynth """
        self.fs.sfunload(self.sfid, update_midi_preset=0)
        self.fs.delete()
        time.sleep(0.5)

    #-----------------------------------------

    def load(self, chan, bank_file, *args, **kwargs):
        """
        load bank file
        from MidiMFluid object
        """

        if self.fs:
            self.sfid = self.fs.sfload(bank_file, update_midi_preset=0)
            # chan, sfid, bank, preset
            # bank select 128 for percussion
            self.fs.program_select(chan, self.sfid, 0, 0)

    #-----------------------------------------

    def unload(self, *args, **kwargs):
        """
        unload bank file
        from MidiFluid object
        """
        
        if self.fs:
            self.fs.sfunload(self.sfid, update_midi_preset=0)

    #-----------------------------------------

    
    def system_start(self, driver, device, bank_file):
        """ 
        Start the engine
        from MidiFluid object
        """

        self.init(driver, device, bank_file)


    #-----------------------------------------
     
    def system_stop(self):
        """ 
        Start the engine
        from FluidSynth manager
        """

        self.fs.delete()
        self.fs = None

    #-----------------------------------------

    def system_panic(self):
       """
       set all notes off controller on al channels
       from FluidSynth object
       """

       control = 123 # all notes off
       if self.fs:
           for chan in range(16):
                self.fs.cc(chan, control, 0)

    #-----------------------------------------
    
    def system_reset(self):
        """
        Reset all notes and programs on all channels
        from FluidSynth object
        """
        
        if self.fs:
            self.fs.system_reset()

    #------------------------------------------------------------------------------
    
    def program_change(self, chan, program):
        """
        set program change
        from FluidSynth  object
        """

        if self.fs:
            self.fs.program_change(chan, program)

    #-----------------------------------------
    
    def bank_change(self, chan, bank):
        """
        change bank
        from FluidSynth object
        """
       
        if self.fs:
            self.fs.bank_select(chan, bank)

    #-----------------------------------------
    
    def note_on(self, chan, key, vel):
       """
       set note on 
       from FluidSynth object
       """

       if self.fs:
            self.fs.noteon(chan, key, vel)

    #-----------------------------------------

    def note_off(self, chan, key):
       """
       set note off
       from FluidSynth object
       """

       if self.fs:
            self.fs.noteoff(chan, key)

    #-----------------------------------------

    def control_change(self, chan, ctrl, val):
       """
       set control change
       from FluidSynth object
       """

       if self.fs:
            self.fs.cc(chan, ctrl, val)

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
        self.driver = "alsa"
        self.device = "hw:1"
        self.bank_file = "/home/com/banks/sf2/fluidr3_gm.sf2"
        self._bpm =100
        self._tempo = 60 / self._bpm # time in sec



    #-----------------------------------------

    def init(self, driver=None, device=None, bank_file=None):
        """
        init synth 
        from MidiManager object
        """
        if driver is None: driver = self.driver
        if device is None: device = self.device
        if bank_file is None: bank_file = self.bank_file

        self.synth.init(driver, device, bank_file)

    #-----------------------------------------
    
    def close(self):
        """ 
        close the synth
        from MidiManager object
        """

        if self.synth:
            self.synth.close()

    #-----------------------------------------

    def load(self, bank_file=None, chan=1, *args, **kwargs):
        """
        load bank file
        from MidiManager object
        """

        if bank_file is None: bank_file = self.bank_file
        if self.synth:
            self.synth.load(int(chan), str(bank_file))

    #-----------------------------------------

    def unload(self, *args, **kwargs):
        """
        unload bank file
        from MidiManager object
        """
        
        if self.synth:
            self.synth.unload()

    #-----------------------------------------

    def startsys(self, driver=None, device=None, bank_file=None, *args, **kwargs):
        """ 
        Start the engine
        from Midimanager object
        """

        if driver is None: driver = self.driver
        if device is None: device = self.device
        if bank_file is None: bank_file = self.bank_file
        if self.synth is None:
            self.synth = MidiFluid()
        if self.synth:
            self.synth.system_start(driver, device, bank_file)

    #-----------------------------------------
     
    def stopsys(self, *args, **kwargs):
        """ 
        Stop the engine
        from Midi manager object
        """

        if self.synth:
            self.synth.system_stop()
            self.synth = None

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
        print(f"prog: {_prog}, chan: {chan}")

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

    #-----------------------------------------
    
    def panic(self, *args, **kwargs):
       """
       set all notes off controller on al channels
       from MidiManager object
       """
       
       if self.synth:
           self.synth.system_panic()

    #-----------------------------------------
    
    def reset(self, *args, **kwargs):
        """
        Reset all notes off and programs on al channels
        from MidiManager object
        """

        if self.synth:
            self.synth.system_reset()

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

    #-----------------------------------------

#========================================

if __name__ == "__main__":
    input("Test...")
