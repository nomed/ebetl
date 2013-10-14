# -*- coding: utf-8 -*-
import os
from genshi.template import TemplateLoader

def _ensure_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s,'utf-8','replace')
        
movcode_labels =['magazzino','codice_riordino','descrizione', 'iva','grammatura',
                 'udm','costo','qty','costo_totale']



########
path_root = os.path.dirname(
                os.path.join(os.path.dirname(os.path.abspath(__file__))))
path_archive = os.path.join(path_root, 'archive')
path_input = os.path.join(path_archive,'input')

if not os.path.exists(path_input):
    os.makedirs(path_input)
    
path_output = os.path.join(path_archive,'output')

if not os.path.exists(path_output):
    os.makedirs(path_output)

path_genshi= os.path.join(path_archive,'html')

if not os.path.exists(path_genshi):
    os.makedirs(path_genshi)
    
loader_genshi = TemplateLoader([path_genshi],
                        auto_reload=True)
    
######## FATMICRO 
path_famicro_input=os.path.join(path_input,'fatmicro')
path_famicro_output=os.path.join(path_output,'fatmicro')
path_famicro_input_file=os.path.join(path_famicro_input, 'fatmicro')

if not os.path.exists(path_famicro_input):
    os.makedirs(path_famicro_input)

if not os.path.exists(path_famicro_output):
    os.makedirs(path_famicro_output)
