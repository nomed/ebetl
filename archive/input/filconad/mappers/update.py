import urllib
import json 
import csv


url_str='https://docs.google.com/spreadsheet/pub?key=%s&single=true&gid=%s&output=csv'

output='0Ar5Lp6pxOuLJdG1mY3FIWEtkeVo4SkNhR0V2RkRXMUE'

gid = 0

fname = "filconad_big.csv"
jfname = "filconad_big.json"

f = open(fname,'w')

url = url_str%(output,gid)
csv_content = urllib.urlopen(url).read()
f.write(csv_content)
f.close()

header_keys = []
header_vals = []
body_keys = []
body_vals = []
for i in csv.reader(open(fname)):

    if i[0] == 'header':
        header_keys.append("h_%s"%i[4])
        header_vals.append(i[3])
    elif i[0] == 'body':   
        body_keys.append("b_%s"%i[4])
        body_vals.append(i[3])

hdict = dict(header=(header_keys, header_vals),
             body=(body_keys, body_vals))

jsonf = open(jfname,'w')

data = json.dumps(hdict,indent=4)

jsonf.write(data)
jsonf.close()
######################################

gid = 2

fname = "filconad.csv"
jfname = "filconad.json"

f = open(fname,'w')

url = url_str%(output,gid)
csv_content = urllib.urlopen(url).read()
f.write(csv_content)
f.close()

keys = []
vals = []
for key, val, func in csv.reader(open(fname)):

    keys.append(key)
    vals.append((val, func))

hdict = dict(zip(keys, vals))

jsonf = open(jfname,'w')

data = json.dumps(hdict,indent=4)

jsonf.write(data)
jsonf.close()
