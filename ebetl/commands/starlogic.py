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
from ebetl.model import *
from ebetl.commands import load_config
from tg import config

    
class Starlogic(Command):
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
    parser.add_option("-a", "--a",
                  action="store_true", dest="all",
                  help="")  
                                 
    (options, args) = parser.parse_args()
    
    def command(self):
        config=load_config(self.args)
        if self.options.export:
            f = open(config.get('starlogic.out'),'w')
            fs = open(config.get('starlogic.sincro'))
            sincro = 0
            for i in  fs.readlines():
                sincro = i.strip()
                sincro = int(sincro)
            fs.close()
            ps = DBSession.query(Eanprodotti)
            if not self.options.all:
                ps = ps.filter(Eanprodotti.sincrofield>sincro)
            ps = ps.order_by(Eanprodotti.sincrofield).all()

            for p in ps:
                codart = p.prodotto.eans[0].ean
                desc = p.prodotto.prodotto.encode('ascii', 'ignore')
                prezzo = p.prodotto.prezzo            
                sincro = p.sincrofield
                print >> f, "%s;%s;%s;%s;%s"%(codart, p.ean, desc, prezzo,0)
                
                if len(p.aliases)>0:
                    for alias in p.aliases:
                        print >> f, "%s;%s;%s;%s;%s"%(codart, alias.alias, desc, prezzo,1)
            f.close()
            f = open(config.get('starlogic.sincro'),'w')
            print >>  f, sincro		        
            f.close()
            
        
             
        
	    
