#!/usr/bin/env python
""" Print all the usernames to the console. """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl.model import *
from paste.script.command import Command
from genshi.template import TemplateLoader

from slugify import slugify

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




class Export(Command):
    summary = "Genera export di prodotti in html"
    usage = "--NO USAGE--"
    group_name = "ebetl"
    parser = Command.standard_parser(verbose=False)
    parser.add_option("-r", "--run",
                      action="store_true", dest="run",
                      help="Export Anag")
    (options, args) = parser.parse_args()

    def command(self):
        config=load_config(self.args)
        path_genshi=  config.get('exportanag.path_genshi')
        opath=  config.get('exportanag.path_out')
        print path_genshi
        loader_genshi = TemplateLoader([path_genshi],
                        auto_reload=True)
        if self.options.run:
            reparti = DBSession.query(Reparti).all()
            rep_dict = {}
            prods = {}
            for r in reparti:
                rep = slugify(r.reparto)
                values = []
                print "========", rep
                prodotti = DBSession.query(Prodotti).filter_by(numeroreparto=r.numeroreparto).order_by(Prodotti.descrizioneestesa).all()
                for p in prodotti:
                    desc = p.descrizioneestesa
                    if not desc:
                        desc = p.prodotto
                    values.append([p.eans[0].codicebilancia, desc])
                    print "%4s %s"%(p.eans[0].codicebilancia,desc )
                tmpl = loader_genshi.load('index.html')
                print "STREAM"
                stream = tmpl.generate(r=r, values=values)
                print "RENDER"
                s = stream.render('html', doctype='xhtml', encoding='utf-8')
                output_html = open(os.path.join(opath,rep+'.html'), 'w')
                print "WRITE"
                output_html.write(s)
                print "written %s"%(os.path.join(opath,rep+'.html'))



