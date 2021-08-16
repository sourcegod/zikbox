#python
"""
    FluidSynth module wrapper
    Date: Tue, 17/08/2021
    Author: Coolbrother

"""
import fluidsynth   

class ModFluid(object):
    """ fluidsynth manager """
    def __init__(self):
        self.fs = None
        self.sfid = None

    #-----------------------------------------
    
    def init(self, driver, device, bank_file):
        """
        init Fluidsynth
        from ModFluid object
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
        from ModFluid object
        """
        
        if self.fs:
            self.fs.sfunload(self.sfid, update_midi_preset=0)

    #-----------------------------------------

    
    def system_start(self, driver, device, bank_file):
        """ 
        Start the engine
        from ModFluid object
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
        from ModFluid object
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


