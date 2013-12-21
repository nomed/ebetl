# -*- coding: utf-8 -*-
#!/usr/bin/env python
""" Filconad Command """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl import model
from ebetl.lib.etl.zucchetti import ZucchettiObj
from paste.script.command import Command
from ebetl.commands import load_config



class Zucchetti(Command):
    summary = "Process zucchetti"
    usage = "paster zucchetti [options]"
    group_name = "ebetl.zucchetti"
    parser = Command.standard_parser(verbose=False)
    parser.add_option("-s", "--s",
                      action="store_true", dest="store",
                      help="Store files in input_b2b")
    parser.add_option("-w", "--write",
                      action="store_true", dest="write",
                      help="Write files content to fact_b2b")
    parser.add_option("-e", "--etl",
                  dest="etl",
                  help="Tipo Tracciato")
    (options, args) = parser.parse_args()

    def command(self):
        config=load_config(self.args)
        self.options.etl = 'zucchetti'
        zucchettiobj=ZucchettiObj(config,self.options.etl)
        if self.options.store:
            zucchettiobj.store_files()
        if self.options.write:
            zucchettiobj.write_out()




