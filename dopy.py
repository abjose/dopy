 # less is less
from display import Display
import random, re

class Task:
    def __init__(self, desc, load=None):
        self.desc = desc
        self.tags = dict() 
        self.attrs = dict(mark=0, strk=0, bold=0, hide=0, skp=0, rm=0, do=0)
        if load != None:
            self.read(load)
        
    def __str__(self):
        return self.desc

    def get(self, a):
        """ Return value of attribute a """
        if a == 'desc': return self.desc
        if a == 'tags': return '['+'|'.join([k for k in self.tags.keys()])+']'
        if a in self.attrs.keys(): return self.attrs[a]
        else: raise Exception("Bad attr name.")

    def read(self, s):
        #frmt = ('[01]/'*len(self.tags.keys()))[:-1] + '[^:]*: *' # use {m}?
        #m = re.match(frmt, s)
        #if m != None: # preformatted
        if ':' in s:
            s = s.split(':')
            self.desc = s[1].strip()
            s = s[0]
            info = s.split(',')
            for t in info:
                k,v = t.split('|')
                if k in self.attrs.keys(): self.attrs[k] = int(v)
                else: self.tags[k] = int(v)
        else: # user-entered/unformatted
            self.desc = s.strip()

    def save(self):
        info = ''
        for k in self.attrs.keys(): # can assume ordered if get this way?
            info += k + '|' + str(self.attrs[k]) + ','
        for k in self.tags.keys():
            info += k + '|' + str(self.tags[k]) + ','
        return info[:-1] + ': ' + self.desc

class Dopy:

    def __init__(self):
        self.tasks = []
        self.showtags = []
        self.page = 0

    def add(self, desc): 
        if self.showtags == []:
            self.tasks.append(Task(desc))
        else:
            t = Task(desc)
            for tag in showtags:
                self.tag(0, tag, t)
                

    def tag(self, n, tag, taskobj=None):
        if 0 <= n < self.vis_len() and tag != '' and ',' not in tag and '|' not in tag: # should regex...
            t = self.vis(n)
            if taskobj != None: t = taskobj
            if tag not in t.tags.keys():
                t.tags[tag] = self.updateTag(tag)

    def mark(self, n):
        self.setAttr(n, 'mark')

    def strk(self, n):
        self.setAttr(n, 'strk')
        
    def bold(self, n):
        self.setAttr(n, 'bold')
        
    def show(self, tag):
        if tag == '': self.showtags = []
        else: self.showtags.append(tag)
        self.clean()

    def skp(self, n):
        self.setAttr(n, 'skp')

    def rm(self, n):
        if n == -1:
            for t in [t for t in self.tasks if t.get('strk')]:
                t.attrs['rm'] = 1
                self.clean()

    def split(self, n):
        print Display.CLEARSCRN + 'Enter 2+ sequential subtasks. CR to append.'
        t = self.vis(n)
        tag = None
        descs = []        
        if len(t.tags.keys()) > 1:
            print "Which task to add to?"
            print t.tags.keys()
            while tag == None:
                inp = raw_input()
                if inp in t.tags.keys() or inp == '':
                    tag = inp
                else:
                    print 'Tag must be one of:\n', t.tags.keys()
        elif len(t.tags.keys()) == 1: tag = t.tags.keys()[0]
        inp = None
        while inp != '' or len(descs) < 2:
            print 'New task:'
            inp = raw_input()
            if inp == '' and len(descs) < 2:
                print 'Including old task. Need >=1 more task'
                if t.desc not in descs: descs.append(t.desc)
            elif inp != '':
                descs.append(inp)
        for i,d in enumerate(descs):
            nt = Task(d)
            if tag != None and tag != '':
                pos = t.tags[tag]+i
                self.updateTag(tag, pos, insert=True)
                nt.tags[tag] = pos
            self.tasks.append(nt)
        self.tasks.remove(t)

    def setAttr(self, n, a, complement=False):
        """ If complement, sets everything but the tasks indicated """
        # ignore complement for number n, for now
        if n >= self.vis_len() or n < 0: return
        if not type(n) == int:# or not n.isdigit():
            for t in self.getTagged(n, complement): t.attrs[a] += 1
        else: self.vis(n).attrs[a] += 1
        self.clean()

    def getTagged(self, tag, complement=False):
        if complement:
            return [t for t in self.tasks if tag not in t.tags.keys()]
        return [t for t in self.tasks if tag in t.tags.keys()]

    def getAttrd(self, attr, complement=False):
        if complement:
            return [t for t in self.tasks if attr in t.attrs.keys() and not t.attrs[attr]]
        return [t for t in self.tasks if attr in t.attrs.keys() and t.attrs[attr]]


    def updateTag(self, tag, pos=None, insert=False):
        """ Given added/removed tag, gives rank (if added) or updates ranks
        (if removed - i.e. pos != None) """
        tags = self.getTagged(tag)
        if tags == []:
            return 0 # 0 works whether inserting, removing, appending?
        ranks = [t.tags[tag] for t in tags]
        if pos == None: return max(ranks) + 1
        if insert:
            for t in tags:
                if t.tags[tag] >= pos: t.tags[tag] += 1
        elif not pos in ranks: # only change if nothing else at same rank
            for t in tags:
                if t.tags[tag] > pos: t.tags[tag] -= 1

    def vis(self, n):
        """ Return nth visible task """
        ct = 0
        for i in range(len(self.tasks)):
            if self.tasks[i].attrs['hide'] == 0:
                if ct == n: return self.tasks[i]
                ct += 1
        return None

    def vis_len(self):
        ct = 0
        for t in self.tasks:
            if t.get('hide') == 0: ct += 1
        return ct

    def do(self):
        ''' Do marked tasks '''
        if True:#self.getAttrd('do') == []:
            for k in self.getAttrd('mark'):
                k.attrs['do'] = 1
            self.vis(0).attrs['do'] = 1

    """
    def do(self, tag=None):
        ''' Do marked tasks or tasks in tag, if specified. '''
        inp = None
        tasks = [self.tasks[0]]+[t for t in self.tasks[1:] if t.get('mark')]
        if tag != None: tasks = self.getTagged(tag)
        tasks.reverse()
        with open('words.txt') as f:
            while inp != 'stop' and tasks != []:
                self.save()
                w = []
                f.seek(0)
                for line in f:
                    w.append(random.choice(line.split(',')).strip())
                pre = (w[0]+' '+ w[1]+'!').upper()+' '+w[2].title()+' '+w[3]+':'
                print Display.CLEARSCRN + str(pre)
                print Display.GREEN + str(tasks[0]) + Display.NRML
                inp = raw_input("(add|split|done)")
                if inp == 'add':
                    read = raw_input("What task to add?: ")
                    self.add(read)
                elif inp == 'skip': 
                    self.split(tasks.pop(0))
                elif inp == 'done': 
                    tasks.pop(0).attrs['strk'] = 1
                    self.clean()
            self.clean()
            print Display.CLEARSCRN+'QUEST COMPLETE!'

    def split(self, t):
        print Display.CLEARSCRN + "SINNER! SPLIT TASK INTO SEQUENTIAL SUBTASKS!"
        tag = None
        descs = []
        if len(t.tags.keys()) > 1:
            print "SCRUM! WHICH TAG WILL YOU ADD TO?:"
            print t.tags.keys()
            while tag == None:
                inp = raw_input()
                if inp in t.tags.keys():
                    tag = inp
                else:
                    print 'YOU FAIL! TAG MUST BE ONE OF:', t.tags.keys()
        elif len(t.tags.keys()) == 1: tag = t.tags.keys()[0]
        inp = None
        print 'ENTER SILENCE TO CEASE ATONEMENT.'
        postfx = '!:'
        while inp != '' or len(descs) < 2:
            print 'ATONE' + postfx
            inp = raw_input()
            if inp == '' and len(descs) < 2:
                print 'THOU MUST ATONE YET!'
            elif inp != '':
                descs.append(inp)
            postfx = ' AGAIN!:'
        for i,d in enumerate(descs):
            nt = Task(d)
            if tag != None:
                pos = t.tags[tag]+i
                self.updateTag(tag, pos, insert=True)
                nt.tags[tag] = pos
            self.tasks.append(nt)
        self.tasks.remove(t)
    """

    def getPage(self):
        pages = Display.paginate([t for t in self.tasks if t.get('hide') == 0])
        self.page = max(0, min(len(pages)-1, self.page))
        return pages[self.page]

    def clean(self):
        for t in self.tasks:
            if t.get('rm') == 1: 
                self.tasks.remove(t)
                for tag in t.tags.keys():
                    self.updateTag(tag, t.tags[tag])

        for t in self.tasks:
            if t.get('skp'):
                self.split(t)

            if self.showtags != []:
                t.attrs['hide'] = 1
                for tg in t.tags:
                    if tg in self.showtags: t.attrs['hide'] = 0
            else:
                if 0 in t.tags.values() or t.tags.keys() == []: 
                    t.attrs['hide'] = 0
                else: 
                    t.attrs['hide'] = 1
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
    d.do()
