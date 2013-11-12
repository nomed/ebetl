#!/usr/bin/env python
""" Print all the usernames to the console. """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl import model
from ebetl.lib.etl.mistral import MistralObj, Db2Mistral, set_account_from_rep2
from paste.script.command import Command

from ebetl.commands import load_config


    
class Mistral(Command):
    summary = "Export to financial"
    usage = "--NO USAGE--"
    group_name = "ebetl.export"
    parser = Command.standard_parser(verbose=False)
    #parser.add_option("-r", "--run",
    #                  action="store_true", dest="run",
    #                  help="")
    #parser.add_option("-p", "--pc",
    #              action="store_true", dest="pc",
    #              help="")
    parser.add_option("-x", "--x",
                  action="store_true", dest="export",
                  help="")  
                                 
    (options, args) = parser.parse_args()
    
    def command(self):
        config=load_config(self.args)
        if self.options.export:
            mistralobj=Db2Mistral(config)
            mistralobj.write_out2()            
            mistralobj.write_out()
            #set_account_from_rep2()
        #if self.options.pc:
        #    #mistralobj=Db2Mistral(config)
        #    set_account_from_rep2()            
        #if self.options.run:
        #    mistralobj=MistralObj(config, pc=self.options.pc)
        #    mistralobj.write_out()
        #    print 'done'
        
             
        
	    
