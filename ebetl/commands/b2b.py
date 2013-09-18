# -*- coding: utf-8 -*-
#!/usr/bin/env python
""" Filconad Command """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl import model
from ebetl.lib.etl.b2b import B2bObj
from paste.script.command import Command
from ebetl.commands import load_config


    
class B2b(Command):
    summary = "Process dbretail"
    usage = "paster filconad [options]"
    group_name = "ebetl.b2b"
    parser = Command.standard_parser(verbose=False)  
    parser.add_option("-w", "--write",
                      action="store_true", dest="write",
                      help="Write files content to fact_b2b")  
    parser.add_option("-x", "--export",
                      action="store_true", dest="export",
                      help="Export to dbretail")
    (options, args) = parser.parse_args()
    
    def command(self):
        config=load_config(self.args)
        b2bobj=B2bObj(config)                  
        if self.options.write:
            b2bobj.write_out()
        if self.options.export:
            b2bobj.export()            
             
        
	    
