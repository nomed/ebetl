#!/usr/bin/env python
""" 
"""
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl.model import *
from paste.script.command import Command
from ebetl.lib import views
from ebetl.lib.views import get_latest_cogs as gcogs

def load_config(args):
    if len(args) == 0:
        # Assume the .ini file is ./development.ini
        config_file = 'development.ini'
        if not os.path.isfile(config_file):
            raise BadCommand('%sError: CONFIG_FILE not found at: .%s%s\n'
                             'Please specify a CONFIG_FILE' % \
                             (self.parser.get_usage(), os.path.sep,
                              config_file))
    else:
        config_file = args[0]
    config_name = 'config:%s' % config_file
    here_dir = os.getcwd()
    conf = appconfig(config_name, relative_to=here_dir)
    load_environment(conf.global_conf, conf.local_conf)
    return conf



    
class Updatecosts(Command):
    summary = "Processa i file cli00 e genera i files OFFERTE.TXT"
    usage = "--NO USAGE--"
    group_name = "ebetl"
    parser = Command.standard_parser(verbose=False)                                       
    parser.add_option("-r", "--run",
                      action="store_true", dest="run_variazioni",
                      help="doc/TODO_cli00.txt")                
                 
    (options, args) = parser.parse_args()
    
    def command(self):
        config=load_config(self.args)
        ics = DBSession.query(Aggiornaic).filter(Aggiornaic.status==1).all()
        for i in ics:
            doc = i.inventario
            invs = DBSession.query(Inventarirconta).filter(Inventarirconta.numeroinventario==doc.numeroinventario).all()
            for ic in invs:
                ic.costo, ic.datacosto = gcogs(ic.numeroprodotto, doc.numeromagazzino ,date=doc.datainventario)
                if not ic.costo2  or ic.costo2 == 0:
                    ic.costo2 = ic.costo
                if ic.prodotto:
                    print "%s %s %s %s"%(ic.prodotto.codiceprodotto,ic.prodotto.prodotto, ic.datacosto, ic.costo, ic.costo2)
            DBSession.add(ic)       
        transaction.commit()
