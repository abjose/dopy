import cmd
import time
from dopy import Dopy

class Interface(cmd.Cmd):    
    def cmdloop(self, intro=None):
        cmd.Cmd.prompt = '> '
        return cmd.Cmd.cmdloop(self, intro)
    
    def preloop(self):
        print chr(27) + "[2J"
        self.d = Dopy()
        self.d.load()
        self.d.clean()
        # do something to make sure tag ranks are continuous starting at 0?
        print self.d.getPage()
    
    def postloop(self):
        pass#print

    def emptyline(self):
        pass
    
    def default(self, line):
        self.do_tsk(line)
    
    def precmd(self, line):
        print chr(27) + "[2J"
        #self.d.load()
        return cmd.Cmd.precmd(self, line)
    
    def postcmd(self, stop, line):
        self.d.clean()
        self.d.save()
        print self.d.getPage()
        return cmd.Cmd.postcmd(self, stop, line)

    def do_EOF(self, line):
        "Exit"
        return True

    def do_tsk(self, line):
        """ Add a task. Default cmd, i.e. can just type and press enter """
        self.d.add(line.replace(':',' -'))
    
    def do_tag(self, line):
        """ 'tg [n...] [t...]' tags tasks n... with tags t... """
        n, t = self.strip_index(line)
        for k in n:
            for l in t:
                self.d.tag(k, l)

    def do_rm(self, line):
        """ Removes all stricken tasks permanently """
        self.d.rm()
        #n, t = self.strip_index(line)
        #for k in n:
        #    self.d.rm(k)

    def do_showtag(self, line):
        """ Takes tag: show members of that tag; no args, show all """
        n, t = self.strip_index(line)
        for k in t:
            self.d.show(k)

    def do_mk(self, line):
        """  'mk n1 n2 ...' marks n1, n2, ... to be done next 'quest' """
        n, t = self.strip_index(line)
        for k in n:
            self.d.mark(k)

    def do_stk(self, line):
        """ 'stk n1 n2 ...' strikes out n1, n2, ... """
        n, t = self.strip_index(line)
        for k in n:
            self.d.strk(k)

    def do_urgent(self, line):
        """ 'urg n1 n2 ...' marks n1, n2 ... as urgent """
        n, t = self.strip_index(line)
        for k in n:
            self.d.urgent(k)

    def do_due(self, line):
        """ 'due n HHMM month/day/year' sets n's due date to that spec'd """
        n = int(line.split()[0])-1
        fmt = '%H%M %m/%d/%y'
        date = time.mktime(time.strptime(' '.join(line.split()[1:]), fmt))
        print date
        self.d.setStat(n, 'due', date)

    def do_est(self, line):
        """ 'est n hours' sets est of n to be hours """
        # forces focus to one element for now...
        n = int(line.split()[0])-1
        self.d.setStat(n, 'est', float(line.split()[1]))

    #def do_splt(self, line):
    #    ''' Split a task into 2+. '''
    #    n, t = self.strip_index(line)
    #    for i in n:
    #        self.d.split(i) 

    #def do_reset(self, line):
    #    for t in self.d.tasks:
    #        t.attrs['do'] = 0

    def do_hlt(self, line):
        """ 'hlt n1 n2 ...' highlights (underlines) tasks n1, n2, ... """
        n, t = self.strip_index(line)
        for k in n:
            self.d.bold(k)
        
    def do_n(self, line):
        """ Go to the next page, if more than one page to show """
        self.d.page += 1

    def do_p(self, line):
        """ Go to the previous page, if more than one page to show """
        self.d.page -= 1

    def do_doit(self, line):
        """ Start a 'quest' of marked tasks """
        n, t = self.strip_index(line)
        if t != ['']: # hmm...
            for k in t:
                self.d.do(t)
        else: self.d.do()

    def strip_index(self, line):
        if line == '': return [-1], [line]
        args = line.split()
        n = [int(k)-1 for k in args if k.isdigit()]
        t = [k.replace(':',' -') for k in args if not k.isdigit()]
        return sorted(n, reverse=True), t

if __name__ == '__main__':
    # start cli
    Interface().cmdloop()
