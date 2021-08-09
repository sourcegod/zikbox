#python
import fluidsynth
import mido
import time

def limit_value(val, min_val=0, max_val=127):
    """ limit value """
    
    if val < min_val: val = min_val
    elif val > max_val: val = max_val
    
    return val

#-------------------------------------------

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

        self.driver = driver
        # device = "hw:1"
        self.device = device
        self.bank_file = bank_file
        self.fs = fluidsynth.Synth(gain=0.5)
        self.fs.start(driver=self.driver, device=self.device)
        self.sfid = self.fs.sfload(self.bank_file, update_midi_preset=0)
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
        self.device = "hw:2"
        self.bank_file = "/home/com/banks/sf2/fluidr3_gm.sf2"


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
    
    def load(self, chan=0, bank_file=None):
        """
        load bank file
        from MidiManager object
        """

        chan = int(chan)
        if chan > 0: chan -= 1
        if bank_file is None: bank_file = self.bank_file
        self.synth.sfid = self.synth.fs.sfload(self.bank_file, update_midi_preset=0)
        # chan, sfid, bank, preset
        # bank select 128 for percussion
        self.synth.fs.program_select(chan, self.synth.sfid, 0, 0)

    #-----------------------------------------

    def unload(self):
        """
        unload bank file
        from MidiManager object
        """

        self.synth.fs.sfunload(self.synth.sfid, update_midi_preset=0)

    #-----------------------------------------


    def close(self):
        self.synth.close()

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
            note = limit_value(note, 0, self.max_val)
            msg.note = note
            self.chan = msg.channel
            if self.vel != 0:
                # velocity variation
                vel = msg.velocity + self.vel
                vel = limit_value(vel, 0, self.max_val)
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

    def program_change(self, chan, program):
        """
        set program change
        from MidiManager object
        """

        chan = int(chan)
        if chan > 0: chan -= 1
        if self.synth:
            self.synth.fs.program_change(int(chan), int(program))
            # input callback function
            self.chan = chan

    #-----------------------------------------

    def bank_change(self, chan, bank):
        """
        change bank
        from MidiManager object
        """
        chan = int(chan)
        if chan > 0: chan -= 1
       
        if self.synth:
            self.synth.fs.bank_select(int(chan), int(bank))

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
   
    def noteon(self, chan, note, vel):
       """
       set note on 
       from MidiManager object
       """

       chan = int(chan)
       if chan > 0: chan -= 1
       if self.synth:
            self.synth.fs.noteon(int(chan), int(note), int(vel))

    #-----------------------------------------

    def noteoff(self, chan, note):
       """
       set note off
       from MidiManager object
       """

       chan = int(chan)
       if chan > 0: chan -= 1
       if self.synth:
            self.synth.fs.noteoff(int(chan), int(note))

    #-----------------------------------------

    def cc(self, chan, ctl, val):
       """
       set note control change
       from MidiManager object
       """

       chan = int(chan)
       if chan > 0: chan -= 1
       if self.synth:
            self.synth.fs.cc(int(chan), int(ctl), int(val))

    #-----------------------------------------


#========================================

