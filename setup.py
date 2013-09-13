# -*- coding: utf-8 -*-
#quickstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       None
#
#

#This is just a work-around for a Python2.7 issue causing
#interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=['WebTest >= 1.2.3',
               'nose',
               'coverage',
               'wsgiref',
               ]
install_requires=[
    "TurboGears2 >= 2.2.0",
    "Genshi",
    "zope.sqlalchemy >= 0.4",
    "repoze.tm2 >= 1.0a5",
    "sqlalchemy",
    "sqlalchemy-migrate",
    "repoze.who",
    "repoze.who-friendlyform >= 1.0.4",
    "tgext.admin >= 0.5.1",
    "repoze.who.plugins.sa",
    "tw2.forms",
    ]

setup(
    name='ebetl',
    version='0.2.11',
    description='',
    author='',
    author_email='',
    #url='',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'ebetl': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'ebetl': [
            ('**.py', 'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = ebetl.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    
    [paste.paster_command]
    #fatmicro = ebetl.commands.fatmicro:Fatmicro
    #ftpacquire = ebetl.commands.ftpacquire:Ftpacquire
    #zipextract = ebetl.commands.zipextract:Zipextract
    #benettontv = ebetl.commands.benettontv:Benettontv
    #cli00 = ebetl.commands.cli00:Cli00
    #cli00new = ebetl.commands.cli00new:Cli00new
    #mergealfiean = ebetl.commands.mergealfiean:Mergealfiean
    #getalfiultimocosto = ebetl.commands.getalfiultimocosto:Getalfiultimocosto
    #bz00varp = ebetl.commands.bz00varp:Bz00varp
    #cleanupcsv = ebetl.commands.cleanupcsv:Cleanupcsv
    #cleanupean = ebetl.commands.cleanupean:Cleanupean
    #winvarp = ebetl.commands.winvarp:Winvarp  
    #upgradefilter = ebetl.commands.upgradefilter:Upgradefilter  
    #getindprezzo = ebetl.commands.getindprezzo:Getindprezzo
    #seeds = ebetl.commands.seeds:Seeds 
    #seedsfid = ebetl.commands.seedsfid:Seedsfid 
    #profis = ebetl.commands.profis:Profis
    #sisa = ebetl.commands.sisa:Sisa
    #mistral = ebetl.commands.mistral:Mistral
    #fidelity= ebetl.commands.fidelity:Fidelity
    #acq_anag= ebetl.commands.acq_anagra00f:AcqAnagra00f
    #acq_listfor = ebetl.commands.acq_mgart00f:AcqMgart00f
    #gilda = ebetl.commands.gilda:Gilda
    #parmalat = ebetl.commands.listini.parmalat:Parmalat
    #vismara = ebetl.commands.listini.vismara:Vismara 
    #big = ebetl.commands.listini.big:Big           
    #updateconti = ebetl.commands.updateconti:Updateconti
    #acqmonciotti = ebetl.commands.acqmonciotti:Acqmonciotti
    #cei = ebetl.commands.cei:Cei    
    filconad = ebetl.commands.filconad:Filconad  
    #syncdb = ebetl.commands.syncdb:Syncdb  
    #exportclifor = ebetl.commands.exportclifor:Exportclifor   
    #cleanupcar = ebetl.commands.cleanupcar:Cleanupcar
    #getgrammatura = ebetl.commands.getgrammatura:Getgrammatura
    #mycommand = ebetl.commands.mycommand:Mycommand
    #bigupdate = ebetl.commands.listini.bigupdate:Bigupdate
    #clientifid = ebetl.commands.clientifid:Clientifid
    #testcmd = ebetl.commands.testcmd:Testcmd  
    """,
    dependency_links=[
        "http://tg.gy/220"
        ],
    zip_safe=False
)


