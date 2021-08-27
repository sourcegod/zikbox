#python
"""
    File: utils.py
    Author: Coolbrother
    Date: Thu, 12/08/2021
"""
_DEBUG =1

def debugMsg(title="", msg="", _type="Info"):
    if _DEBUG:
        if title: 
            msg = f"{_type}: {msg}"
        else:
            msg = f"{_type}: {title}\n{msg}"
        
        print(msg)

#-------------------------------------------

def is_number(stg):
    """ Returns True is string is a number. """
    try:
        float(stg)
        return True
    except ValueError:
        return False

#-------------------------------------------

def limit_value(val, min_val=0, max_val=127):
    """ limit value """
    
    if val < min_val: return min_val
    elif val > max_val: return max_val
    
    return val

#-------------------------------------------

def is_int(val):
    # return val % 1 == 0
    return float(val).is_integer()

#-------------------------------------------


