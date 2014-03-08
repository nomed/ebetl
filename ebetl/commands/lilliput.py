# -*- coding: utf-8 -*-
# -*- coding: utf-8 *-*
# -*- coding: utf-8 -*-
#!/usr/bin/env python
""" Filconad Command """
import os
import sys
from argparse import ArgumentParser

from paste.deploy import appconfig
from ebetl.config.environment import load_environment
from ebetl import model
from paste.script.command import Command
from ebetl.commands import load_config

from datetime import datetime as dt
from datetime import timedelta as td

from dateutil.relativedelta import relativedelta as rd

from calendar import mdays

def get_map(ret):
    mapdict = {}
    for k in ret:
        pdv = k[0]
        y = k[3]
        m = k[4]
        d = k[5]
        acc_num=k[6]
        rep_num=k[8]
        if pdv not in mapdict.keys():
            mapdict[pdv] = {}
        if y not in mapdict[pdv].keys():
            mapdict[pdv][y]={}            
        if m not in mapdict[pdv][y].keys():
            mapdict[pdv][y][m]={}
        if not d in mapdict[pdv][y][m]:
            mapdict[pdv][y][m][d] = {} 
        if not acc_num in mapdict[pdv][y][m][d]:
            mapdict[pdv][y][m][d][acc_num] = {}
        if not rep_num in mapdict[pdv][y][m][d][acc_num]:
            mapdict[pdv][y][m][d][acc_num][rep_num] = k     
    return mapdict


def get_map_do(ret):
    mapdict = {}
    for k in ret:

        pdv = k[0]
        y = k[1]
        m = k[2]
        d = k[3]
        if pdv not in mapdict.keys():
            mapdict[pdv] = {}
        if y not in mapdict[pdv].keys():
            mapdict[pdv][y]={}            
        if m not in mapdict[pdv][y].keys():
            mapdict[pdv][y][m]={}
        if not d in mapdict[pdv][y][m]:
            mapdict[pdv][y][m][d] = k
               
    return mapdict

            
class Lilliput(Command):

    summary = "Process zucchetti"
    usage = "paster zucchetti [options]"
    group_name = "ebetl.zucchetti"
    parser = Command.standard_parser(verbose=False)
    parser.add_option("-i", "--items",
                      action="store_true", dest="items",
                      help="Export Anag")    
    parser.add_option("-f", "--from",
                  dest="fromd",
                  help="Da Data")
    parser.add_option("-t", "--to",
                  dest="tod",
                  help="A Data")
    parser.add_option("-s", "--sync",
                       dest="sync",metavar='sync',
                      help="Sync lilliput (fiscal) reports")                
    (options, args) = parser.parse_args()



    def command(self):
        config=load_config(self.args)
        from ebetl.lib.views import get_dailytotals,get_dailymenuitems, sync_do, sync_dmi, sync_lilliput
        fromd = dt.strptime(self.options.fromd, "%Y%m%d")
        if self.options.tod:
            tod = dt.strptime(self.options.tod, "%Y%m%d") + td(days=1)
        else:
            tod = fromd + td(days=1)
        if self.options.items:
            #(u'000351', 1, u'351 ARQUATA', 2014, 1, 2, 1, u'PANETTERIA', 17, u'PANETTERIA', 207.73120000000006, 8.308799999999996, 216.03999999999996)
            retly_tmp = get_dailymenuitems(fromd - rd(years=1), tod - rd(years=1))
            retly = []
            for r in retly_tmp:
                row = list(r)
                row[3] = row[3]+1
                retly.append(row)
            maply = get_map(retly)
            ret = get_dailymenuitems(fromd, tod)
            mapcy = get_map(ret)
            results = []
            for k in ret:
                pdv = k[0]
                y = k[3]                
                m = k[4]
                d = k[5]
                acc_num=k[6]
                rep_num=k[8]
                try:
                    ly = maply[pdv][y][m][d][acc_num][rep_num]
                    ly = ly[10:]
                    
                except:
                    ly = ["0","0","0"]
                results.append(list(k)+list(ly)) 
            for k in retly:
                pdv = k[0]
                y = k[3]                
                m = k[4]
                d = k[5]
                acc_num=k[6]
                rep_num=k[8]
                try:
                    mapcy[pdv][y][m][d][acc_num][rep_num]                    
                except:
                    results.append(k[0:10]+["0","0","0"]+k[10:])                 
            #for i in results:
            #    p = [str(j).replace('.',',') for j in i]
            #    print "|".join(p)   
            sync_dmi(results)                                                                                              

        else:    
            # (u'000297', 2013, 1, 8, 396, 14.901287878787729, 5396.611399999985, 504.2985999999985, 5900.909999999941)
            retly_tmp = get_dailytotals(fromd - rd(years=1), tod - rd(years=1))
            retly = []
            for r in retly_tmp:
                row = list(r)
                row[1] = row[1]+1
                retly.append(row)            
            maply = get_map_do(retly)
            ret = get_dailytotals(fromd, tod)
            mapcy = get_map_do(ret)
            
            results = []
            
            for k in ret:
                pdv = k[0]
                y = k[1]
                m = k[2]
                d = k[3]
                
                try:
                    ly = maply[pdv][y][m][d]
                    ly = ly[4:]
                    
                except:
                    ly = ["0","0","0","0","0"]
                results.append(list(k)+list(ly)) 
            for k in retly:
                pdv = k[0]
                y = k[1]
                m = k[2]
                d = k[3]
                try:
                    mapcy[pdv][y][m][d]           
                except:
                    results.append(k[0:4]+["0","0","0","0","0"]+k[4:])                 
            #for i in results:
            #    p = [str(j).replace('.',',') for j in i]
            #    print "|".join(p)
            sync_do(results)
            #print results                          
        if self.options.sync:
            sync_lilliput()




