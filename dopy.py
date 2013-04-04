 # less is less
from display import Display
#from time import time
#import time
from datetime import datetime, timedelta
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
        self.attrs = dict(mark=0, strk=0, bold=0, hide=0, urgent=0, skp=0, rm=0, do=0, proj=0)
        # EC = estimated completion @ due date
        #self.stats = dict(added=0., due=0., spent=0., est=0., ec=0.)
        self.stats = dict(spent=0., est=0., ec=0.)
        self.dates = dict(added=0, due=0)
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
        if a in self.dates.keys(): return self.dates[a]
        else: raise Exception("Bad attr name.")

    def read(self, s):
        if '{' in s:
            s = s.split('{')
            self.desc = s[1].strip()
            s = s[0]
            info = s.split(',')
            for t in info:
                k,v = t.split('|')
                if k in self.attrs.keys(): self.attrs[k] = int(v)
                elif k in self.stats.keys(): self.stats[k] = float(v)
                elif k in self.dates.keys(): 
                    self.dates[k] = datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f")
                else: self.tags[k] = int(v)
        else: # user-entered/unformatted
            self.desc = s.strip()

    def save(self):
        info = ''
        for k in self.attrs.keys():
            info += k + '|' + str(self.attrs[k]) + ','
        for k in self.stats.keys():
            info += k + '|' + str(self.stats[k]) + ','
        for k in self.dates.keys():
            info += k + '|' + str(self.dates[k]) + ','
        for k in self.tags.keys():
            info += k + '|' + str(self.tags[k]) + ','
        return info[:-1] + '{ ' + self.desc






class Dopy:

    def __init__(self):
        self.tasks = []
        self.showtags = []
        self.page = 0
        self.task_added = True # hacky way to move to newest page on task add

    def add(self, desc):
        t = Task(desc)
        # automatically add tag if showtag
        for tag in self.showtags:
            t.tags[tag] = 0
        self.tasks.append(t)
        self.task_added = 1
                
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

    def urgent(self, n):
        self.setAttr(n, 'urgent')

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

    def insert(self, n, m):
        """ Move task n to line m """
        t1 = self.vis(n)
        t2 = self.vis(m)
        self.moveRelative(t1, t2)

    def makeProject(self, n, d):
        """ Mark task n as a project with due date d. """
        # first make sure no other projects that share a tag
        add_proj = True
        t1 = self.vis(n)
        for t2 in self.tasks:
            if t2.get('proj') and self.checkShareTag(t1, t2):
                add_proj = False
                break
        if add_proj:
            self.setAttr(n, 'proj')
            self.setStat(n, 'due', d)

    def markProgress(self, n, h):
        """ Strike out task n and modify estimate to actual time taken. Modify
        all other tasks with shared tags (...even if not a project).
        """
        self.strk(n)
        t1 = self.vis(n)
        err = float(h)/t1.get('est')
        # if shared tag, update t2's time estimate
        for t2 in self.tasks:
            if self.checkShareTag(t1, t2) and not t2.get('proj'):
                # will also update estimate for original task
                t2.stats['est'] = t2.get('est') * err
                
    # REWRITE SPLIT...MAKE SIMPLER
    """  """

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

    def checkShareTag(self, t1, t2):
        """ Return true if t1 and t2 share any tag """
        t1k = t1.tags.keys()
        t2k = t2.tags.keys()
        return any([a == b for a in t1k for b in t2k])

    def moveRelative(self, t1, t2):
        """ Move t1 to before t2 in task list """
        # error handling???
        self.tasks.remove(t1)
        self.tasks.insert(self.tasks.index(t2), t1)

    def updateProjects(self):
        """ Update project tasks (i.e. proj=1):
        - Make sure title task always before component tasks
        - Make sure project time estimate reflects sum of components
        - Add time spent on dead tasks onto project time spent
        - All subcomponents of a project have the same due and add date
        """
        for t1 in self.tasks:
            if t1.get('proj'):
                proj_est = 0
                due = t1.get('due')
                added = t1.get('added')
                subtasks = set()
                # first create set of subcomponents, so we don't have to worry
                # about changing order during iteration
                for t2 in self.tasks:
                    if t2.get('proj') == 0 and self.checkShareTag(t1, t2):
                        subtasks.add(t2)
                # iterate over subcomponent set we just made
                for sub in subtasks:
                    # make sure comes after title task
                    if self.tasks.index(t1) > self.tasks.index(sub):
                        self.moveRelative(t1, sub)
                    # if sub marked for removal, add time spent to project
                    if sub.get('rm'):
                        t1.stats['spent'] += sub.get('est')
                    # make sure subcomponents have the same due and add date
                    sub.dates['due'] = due
                    sub.dates['added'] = added #necessary???
                    # add time estimate to sum of estimates
                    proj_est += sub.get('est')
                t1.stats['est'] = proj_est

    def updateStats(self):
        """ Update some stats for all tasks.
        - Update add and due dates if necessary (i.e. none exists)
        - Update time estimate if necessary (i.e. none made)
        - Recalculate hours until due
        - Recalculate work rate (hours completed / hours since added)
        - Recalculate est. completion @ due date (spent+hours_left*work_rate)
        """
        default_est = 3. #hours

        for t in self.tasks:
            # if no add date, set as added now
            if type(t.get('added')) != type(datetime.now()):
                t.dates['added'] = datetime.now()
            added = t.get('added')

            # if no due date, set as 1 week in the future
            if type(t.get('due')) != type(datetime.now()):
                t.dates['due'] = datetime.now() + timedelta(weeks=1)
            due = t.get('due')

            # if no time estimate set to default of 3 hours
            if type(t.get('est')) != type(datetime.now()):
                t.stats['est'] = default_est
            est = t.get('est')
            
            # caculate a variety of stats...not all are used, but could be!
            spent = t.get('spent') # hours spent
            added_delta = datetime.now() - added
            due_delta = due - datetime.now()
            s_added = abs(added_delta.total_seconds())
            hrs_added = s_added / 3600. # hours since added
            s_due = abs(due_delta.total_seconds())
            hrs_due = s_due / 3600. # hours until due
            work_rate = spent / hrs_added # hours worked per hour
            ec = (spent + work_rate*hrs_due) / est
            t.stats['ec'] = ec
            
            

    # removed old split and (fun) do code - consider re-implementing

    def getPage(self):
        # should always bring focus to page tag is being added on?
        # or only if on page before? (i.e. 'spilled over')
        # could have an 'added' flag, set by add, cleared by this
        # and if set, go to newest page...
        pages = Display.paginate([t for t in self.tasks if not t.get('hide')])
        if(self.task_added):
            self.page = len(pages)-1
        else:
            self.page = max(0, min(len(pages)-1, self.page))
        self.task_added = False
        return pages[self.page]

    def clean(self):
        # CAREFUL with doing this before removing dead tasks...
        # putting here so updateProjects can correctly sum time spent
        # update stats
        self.updateStats()
        # update projects
        self.updateProjects()

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
