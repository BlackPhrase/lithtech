#!/usr/bin/python3
"""
    2018 (c) Rene 'Katana Steel' Kjellerup, distributed under the terms of
    the GNU General Public Licenses version 3 or later for details see:
    http://www.gnu.org/licenses/gpl.html
"""
from sys import argv
from os.path import exists

str_table = []
text = []
defs = []


def parseRC(rcFile):
    ret_incl = []
    with open(rcFile, 'r', encoding='utf-8') as f:
        cur_lst = None
        str_id = None
        txt = None
        for l in f.readlines():
            if l.lower().startswith(u'#include'):
                n = l.split('"')
                ret_incl.append(n[1].replace(u'\\', u'/'))
            if u'stringtable' in l.lower():
                cur_lst = str_table
            if u'end' in l.lower():
                cur_lst = None
            if l.startswith(u' ') and cur_lst is not None:
                n = l.strip(u'\n').split(u'"')
                if str_id is None:
                    str_id = n[0].strip()
                if len(n) is 1:
                    continue
                txt = u'"'.join(n[1:-1])
                cur_lst.append((str_id, txt))
                str_id = None
                txt = None
    return ret_incl


def parseH(hFile):
    try:
        with open(hFile, u'r') as h:
            for l in h.readlines():
                defs.append(l.strip(u'\n'))
    except Exception:
        pass


def getIncludes(base, paths, includes):
    ret_incl = []
    # fetching includes and dropping them directly into the generated file
    for i in includes[:]:
        inc = u''
        for p in paths:
            if exists(u'/'.join([base, p, i])):
                inc = u'/'.join([base, p, i])
                break
            if exists(u'/'.join([p, i])):
                inc = u'/'.join([p, i])
                break
        if exists(u'/'.join([base, i])):
            inc = u'/'.join([base, i])
        if len(inc) < 1:
            print(u'not found: {0}'.format(i))
            continue
        if u'.h' in i.lower():
            print(u'including: {0}'.format(inc))
            parseH(inc)
        if u'.rc' in i.lower():
            print(u'including: {0}'.format(inc))
            ret_incl.extend(parseRC(inc))
    return ret_incl


main_rc = u''
paths = [u'.']
for p in argv:
    if p.lower().endswith(u'rc'):
        main_rc = p
        continue
    paths.append(p)

base = u'/'.join(main_rc.split('/')[:-1])

includes = parseRC(main_rc)
while len(includes) > 0:
    includes = getIncludes(base, paths, includes[:])


with open(main_rc.split(u'/')[-1] + u'.cpp', 'w', encoding='utf-8') as o:
    o.write(u'''/*
  my template c++ file which implements the internal resource
  lookup and storage
*/

#include "dynres.h"
#include <string>
#include <cinttypes>
#include <utility>
#include <algorithm>
#include <vector>
''')
    for i in defs:
        o.write(u'{0}'.format(i)+'\n')
    o.write('''

std::vector<std::pair<uint32_t,const char*>> str_tab {
''')
    for x in str_table:
        o.write(u'    std::make_pair({0},"{1}"),\n'.format(x[0], x[1]))
    o.write(u'''    std::make_pair(0,"generated by LithTech Resource compiler\\n\\n" \\
    "2018 (c) Rene 'Katana Steel' Kjellerup, distributed under the terms" \\
    " of\\nthe GNU General Public Licenses version 3 or later for details" \\
    " see:\\nhttp://www.gnu.org/licenses/gpl.html\\n")
};

extern "C" {
  const char* LoadString(uint32_t id)
  {
    auto res = std::find_if(str_tab.begin(),
                            str_tab.end(),
                            [id](std::pair<uint32_t, const char*> x){
                                return (x.first == id);
                            });
    if(res != str_tab.end())
        return res->second;
    else
        return nullptr;
  }
}

void setup_cursors() { }

void setup_string_tables() {
    bool c = false;
    for(auto&& p : str_tab)
        c = (LoadString(p.first) == p.second);
}
''')
