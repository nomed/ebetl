#!/usr/bin/env python
""" Load Config in commands """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl import model
from ebetl.lib.etl.filconad import FilconadObj
from paste.script.command import Command

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
