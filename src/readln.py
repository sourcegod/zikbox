#! /usr/bin/python3
"""
    readline wrapper for input
    Date: Thu, 26/08/2021
    Author: Coolbrother
"""
import os
from os.path import expanduser
import readline

_HISTORY_TEMPFILE = '/tmp/completer.hist'
_HISTORY_FILENAME = expanduser('~/.synth_history')
_complete_dic = {
        'list': ['files', 'directories'],
        'print': ['byname', 'bysize'],
        'stop': [],
        }

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
# readline.parse_and_bind('set editing-mode vi')

def list_folder(path):
    """
    Lists folder contents
    """
    if path.startswith(os.path.sep):
        # absolute path
        basedir = os.path.dirname(path)
        contents = os.listdir(basedir)
        # add back the parent
        contents = [os.path.join(basedir, d) for d in contents]
    else:
        # relative path
        contents = os.listdir(os.curdir)
    return contents

#------------------------------------------------------------------------------

def get_history_items():
    return [ readline.get_history_item(i)
             for i in range(1, readline.get_current_history_length() + 1)
             ]

#------------------------------------------------------------------------------


class BufferCompleter(object):
    def __init__(self, options):
        self.options = options
        self.current_candidates = []
        return

    #------------------------------------------------------------------------------

    def _complete(self, text, state):
        """ manage completer functions """
        # print("text: ",text)
        origline = readline.get_line_buffer()
        words = origline.split()
        print("voici: ",words)
        if '/' in words:
            text = '/'

        # if text and text.startswith(os.path.sep):
            return self.path_completer(text, state)

        return self.line_completer(text, state)

    #------------------------------------------------------------------------------

    def path_completer(self, text, state):
        """
        Our custom completer function
        """
        # print("voici: ",text)
        
        line = readline.get_line_buffer().split()

        # replace ~ with the user's home dir. See https://docs.python.org/2/library/os.path.html
        if '~' in text:
            text = os.path.expanduser('~')

        # autocomplete directories with having a trailing slash
        if os.path.isdir(text):
            text += '/'

        return [x for x in glob.glob(text + '*')][state]

        """
        options = [x for x in list_folder(text) if x.startswith(text)]
        return options[state]
        """
    #------------------------------------------------------------------------------

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            if not words:
                self.current_candidates = sorted(self.options.keys())
            else:
                try:
                    if begin == 0:
                        # first word
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        candidates = self.options[first]

                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.current_candidates = [ w for w in candidates
                                                    if w.startswith(being_completed) ]
                    else:
                        # matching empty string so use all candidates
                        self.current_candidates = candidates

                except (KeyError, IndexError) as err:
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        return response

    #------------------------------------------------------------------------------

#========================================

class HistoryCompleter(object):
    def __init__(self):
        self.matches = []
        return

    #------------------------------------------------------------------------------

    def complete(self, text, state):
        response = None
        if state == 0:
            history_values = get_history_items()
            # logging.debug('history: %s', history_values)
            if text:
                self.matches = sorted(h
                                      for h in history_values
                                      if h and h.startswith(text))
            else:
                self.matches = []
            # logging.debug('matches: %s', self.matches)
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        # logging.debug('complete(%s, %s) => %s',
        #              repr(text), state, repr(response))
        return response

    #------------------------------------------------------------------------------

#========================================

def read_historyfile(filename=""):
    if not filename:
        filename = _HISTORY_FILENAME
    if os.path.exists(filename):
        readline.read_history_file(filename)
        # print('Max history file length:', readline.get_history_length())
        # print('Startup history:', get_history_items())

#------------------------------------------------------------------------------

def write_historyfile(filename=""):
    # print('Final history:', get_history_items())
    if not filename:
        filename = _HISTORY_FILENAME
    readline.write_history_file(filename)

#------------------------------------------------------------------------------


def get_input(stg=""):
    return input(stg)

#------------------------------------------------------------------------------

def set_completer(dic={}):
    if not dic:
        dic = _complete_dic
    func = BufferCompleter(dic).complete
    readline.set_completer(func)

#------------------------------------------------------------------------------


def main():
    filename = _HISTORY_TEMPFILE
    # Register our completer function
    set_completer(None)
    # readline.set_completer(HistoryCompleter().complete)
    read_historyfile(filename)
    try:
        while True:
            line = get_input(">> ")
            if line == "stop":
                break
            
            if line:
                print(f"Adding {line} to the history")

    finally:
        print('Final history:', get_history_items())
        write_historyfile(filename)

#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#------------------------------------------------------------------------------
