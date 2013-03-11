 # less is less
from display import Display
from time import time
import random, re

class Task:
    def __init__(self, desc, load=None):
        # having separate tags/attrs/stats dicts seems a bit inelegant
        # currently their individual purposes are as follows:
        # attrs: boolean line-state variables (underlined, bolded, etc.)
        # tags: (potentially ranked) task tags, to ease display
        # stats: variables related to task (time estimate, due date, etc.)
        self.desc = desc
        self.tags = dict() 
        self.attrs = dict(mark=0, strk=0, bold=0, hide=0, skp=0, rm=0, do=0)
        self.stats = dict(due=0., est=0.)
        if load != None:
            self.read(load)
        
    def __str__(self):
        return self.desc

    def get(self, a):
        """ Return value of attribute a """
        if a == 'desc': return self.desc
        if a == 'tags': return '['+'|'.join([k for k in self.tags.keys()])+']'
        if a in self.attrs.keys(): return self.attrs[a]
        if a in self.stats.keys(): return self.stats[a]
        else: raise Exception("Bad attr name.")

    def read(self, s):
        if ':' in s:
            s = s.split(':')
            self.desc = s[1].strip()
            s = s[0]
            info = s.split(',')
            for t in info:
                k,v = t.split('|')
                if k in self.attrs.keys(): self.attrs[k] = int(v)
                elif k in self.stats.keys(): self.stats[k] = float(v)
                else: self.tags[k] = int(v)
        else: # user-entered/unformatted
            self.desc = s.strip()

    def save(self):
        info = ''
        for k in self.attrs.keys():
            info += k + '|' + str(self.attrs[k]) + ','
        for k in self.stats.keys():
            info += k + '|' + str(self.stats[k]) + ','
        for k in self.tags.keys():
            info += k + '|' + str(self.tags[k]) + ','
        return info[:-1] + ': ' + self.desc






class Dopy:

    def __init__(self):
        self.tasks = []
        self.showtags = []
        self.page = 0

    def add(self, desc): 
        t = Task(desc)
        # automatically add tag if showtag
        for tag in self.showtags:
            t.tags[tag] = 0
        self.tasks.append(t)
                
    def tag(self, n, tag):
        forbid = [',', '|', 'date', 'due', 'est']
        if tag != '' and not any((c in forbid) for c in tag):
            self.vis(n).tags[tag] = 0

    def mark(self, n):
        self.setAttr(n, 'mark')

    def strk(self, n):
        self.setAttr(n, 'strk')
        
    def bold(self, n):
        self.setAttr(n, 'bold')

    def skp(self, n):
        """ Mark task n for splitting """
        self.setAttr(n, 'skp')
        
    def show(self, tag):
        if tag == '': self.showtags = []
        # limit to one tag for now
        else: self.showtags = [tag]

    def rm(self, t=None):
        if t: t.attrs['rm'] = 1
        else: map(self.rm, [t for t in self.tasks if t.get('strk')])

    # REWRITE SPLIT...MAKE SIMPLER

    def setAttr(self, n, a):
        t = self.vis(n)
        if t != None: t.attrs[a] += 1

    def setStat(self, n, a, val):
        t = self.vis(n)
        if t != None: t.stats[a] = val

    def vis(self, n):
        """ Return nth visible task """
        v = [t for t in self.tasks if not t.get('hide')]
        if n < len(v):
            return v[n]
        return None

    def vis_len(self):
        """ Return length of visible task list """
        return len([t for t in self.tasks if not t.get('hide')])

    def do(self):
        ''' Do marked tasks '''
        if True:
            for k in self.getAttrd('mark'):
                k.attrs['do'] = 1
            self.vis(0).attrs['do'] = 1

    def hide(self, t):
        t.attrs['hide'] = 1

    def unhide(self, t):
        t.attrs['hide'] = 0

    # removed old split and (fun) do code - consider re-implementing

    def getPage(self):
        pages = Display.paginate([t for t in self.tasks if not t.get('hide')])
        self.page = max(0, min(len(pages)-1, self.page))
        return pages[self.page]

    def clean(self):
        # remove tasks marked for removal
        map(self.tasks.remove, [t for t in self.tasks if t.get('rm')])

        # split tasks marked for splitting
        #map(self.tasks.split, [t for t in self.tasks if t.get('skp')])

        # rebuild visibile 'sub-list'
        map(self.unhide, self.tasks)
        if self.showtags != []:
            tag = self.showtags[0] # assumes one max showtag
            map(self.hide, [t for t in self.tasks if not tag in t.tags])
        # if no showtags, show only first of each tag set (and untagged)
        else:
            vis_tags = []
            for t in self.tasks:
                tag = t.tags.keys() # assumes one tag
                if tag == []:
                    continue
                if tag not in vis_tags:
                    vis_tags.append(tag)
                else:
                    self.hide(t)

        # mod attributes
        for t in self.tasks:
            for k in t.attrs.keys(): t.attrs[k] %= 2
            
    def save(self, name='todo.txt'):
        with open(name, 'w') as f:
            for i in range(len(self.tasks)):
                f.write(self.tasks[i].save()+'\n')

    def load(self, name='todo.txt'):
        self.tasks = []
        try: open(name)
        except Exception, e: # make todo file if not present
            file = open(name, 'w')
            file.write('')
            file.close()
        with open(name) as f: 
            for line in f:
                self.tasks.append(Task('', load=line))

if __name__ == '__main__':
    d = Dopy()
    print "initialized Dopy object..."
