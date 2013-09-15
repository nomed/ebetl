# -*- coding: utf-8 -*-

def strip_non_ascii(string):
    """
    Returns the string without non ASCII characters
    """
    stripped = []
    if string:
        for c in string:
            if 0 < ord(c) < 127:
                stripped.append(c)
            else:
                stripped.append(' ')
    ret=''.join(stripped)
    return ret

def get_discount_from_string(dstr):
    """
    Split a discount string of the form "d1+d2+..dn" and return a multiplier for
    final price
    
    DSTR="4+4"
    MULT=0.9216
    PRICE: 2.78
    FINAL_PRICE: 2.562
    
    >>> dstr="4+4"
    >>> get_discount_from_string(dstr)
    0.9216
    >>> x=get_discount_from_string(dstr)
    >>> price=2.78
    >>> final_price=price*x
    >>> final_price
    2.562048
    >>> dstr="4+4"
    >>> x=get_discount_from_string(dstr)
    >>> x
    0.9216
    >>> price=2.78
    >>> price
    2.78
    >>> final_price=price*x
    >>> final_price
    2.562048
    
    
    
    """
    # list of discount integer values
    if dstr:
        dvals = dstr.split('+')
    
        # find the value to multiply for unit price
        mult = 1
        for d in dvals:
            d = d.strip().replace(',','.')
            if d:
                mult = (1 - float(d)/100)*mult
    else:
        mult = 1
    return mult

   

