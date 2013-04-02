import math
import os
#from dopy import Task # for testing

class Display:

    # https://en.wikipedia.org/wiki/ANSI_escape_code
    # terminal/cursor  modification
    CLEARSCRN = '\x1b[H\x1b[2J'
    # background colors
    BGCYAN = '\033[106m'
    BGMAGENTA = '\033[105m'
    BGBLUE = '\033[104m'
    BGYELLOW = '\033[103m'
    BGREEN = '\033[102m'
    BGRED = '\033[101m'
    BGBLACK = '\033[100m'
    # foreground colors    
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLACK = '\033[90m'
    # effects
    STRIKE = '\033[9m'
    BOLD = '\033[1m'
    NEGATIVE = '\033[7m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m' #doesn't seem to be supported
    URGENT = RED+BOLD
    # other
    NRML = '\033[0m'

    @staticmethod
    def getTerminalSize():
        rows,columns = os.popen('stty size','r').read().split()
        return int(rows), int(columns)

    @staticmethod
    def paginate(tasks):
        """ Convert list of tasks objects to list of string 'pages' for display.
        Pages and columns should be sized based on the terminal size.
        """
        # include vector of weights describing what 'portion' of remaining
        # spaces large strings get? (i.e. 'greediness')

        # list of (name, weight) tuples
        if len(tasks) == 0: return ['Nothing to show.']

        # set do
        do = False
        for k in tasks: 
            if k.get('do'): do = True
        names = [('tags', 1), ('desc', 1)]
        
        lists = [[str(i) for i in range(1, len(tasks)+1)]] # insert IDs
        lists.extend([[t.get(names[j][0]) for t in tasks] 
                      for j in range(len(names))])

        widths = [max([len(k) for k in lists[j]]) for j in range(len(lists))]

        r,c = Display.getTerminalSize()
        max_avg = c / len(widths)

        small = [w for w in widths if w < max_avg]
        large = [w for w in widths if w >= max_avg]
        max_w = c - (sum(small) + len(small))
        if large != []: max_w /= len(large)
        rows = Display.getRows(lists, 
                               [min(max_w, w) for w in small+large],
                               tasks, do)
        r -= 1
        pages = ['\n'.join(rows[r*a:r*(a+1)]) for a in range(len(rows)/r + 1)]
        return pages
    
    @staticmethod
    def getRows(l, w, tasks, do):
        """ Returns a list of rows to print to the display. 
        l: list of unformatted columns
        w: list of widths for each column
        tasks: task list, for sake of applying 'effects' """
        cols = range(len(l))
        out = []
        for r in range(len(l[0])):
            row = [Display.block(l[c][r], w[c]) for c in cols]
            h = max([len(k) for k in row])
            # lazy - delete height-handling stuff in block and change here
            row = [Display.block(l[c][r], w[c], h) for c in cols]
            for i in range(h):
                t = tasks[r]
                fx = ''
                if t.get('mark') or r == 0: fx += Display.NEGATIVE
                if t.get('strk'): fx += Display.STRIKE
                if t.get('bold'): fx += Display.UNDERLINE
                if t.get('urgent'): fx += Display.URGENT
                elif do and not t.get('do'): fx += Display.BLACK
                elif r%2==0: fx += Display.MAGENTA#YELLOW
                else: fx += Display.BLUE#GREEN
                out.append(fx+' '.join([row[c][i] for c in cols])+Display.NRML)
        return out       

    @staticmethod
    def block(s, w, h=-1):
        """ Make string s into array of substrings <= w chars long """
        s = s.split()
        t = []
        for word in s:
            while len(word) > w:
                t.append(word[:w-1]+'-')
                word = word[w-1:]
            t.append(word)

        out = []
        while h > 0 or (t != [] and h < 0):
            h -= 1
            sub = ''
            while t != [] and len(sub)+len(t[0]) <= w:
                sub += t.pop(0) + ' '
            #sub = ('{:\'<'+str(w)+'}').format(sub[:-1])
            sub = ('{:<'+str(w)+'}').format(sub[:-1])
            out.append(sub)
        return out

if __name__ == '__main__':
    s = 'why hello there fine gentleman, how are you doing today?'
    #print '\n'.join(Display.block(s, 20))
