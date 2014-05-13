# -*- coding: utf-8 -*-
#!/usr/bin/env python
""" Filconad Command """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl.model import *
from paste.script.command import Command
from ebetl.commands import load_config


    
class Mailman(Command):
    summary = "Process email addresses"
    usage = "paster mailman [options]"
    group_name = "ebetl.mailman"
    parser = Command.standard_parser(verbose=False)  
     
    parser.add_option("-x", "--export",
                       dest="export",metavar='PATH',
                      help="Export to file")
    (options, args) = parser.parse_args()
    
    def command(self):
        config=load_config(self.args)
                        
        if self.options.export:
            cfs = DBSession.query(Clientifid).filter(Clientifid.email!=' ').all()
            output = []
            for c in cfs:
			output.append('"%s %s" <%s>'%(c.nome, c.cognome, c.email))
			f = open(self.options.export, 'w')
			for o in output:
				print >> f, o.encode('utf-8')
			f.close()
	    

