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
    BGGREEN = '\033[102m'
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
    URGENT = RED
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

        if len(tasks) == 0: return ['Nothing to show.']

        # set do
        do = False
        for k in tasks: 
            if k.get('do'): do = True
        # list of (name, weight) tuples
        names = [('tags', 1), ('desc', 1)]
        
        lists = [[str(i) for i in range(1, len(tasks)+1)]] # insert IDs
        lists.extend([[t.get(names[j][0]) for t in tasks] 
                      for j in range(len(names))])

        widths = [max([len(k) for k in lists[j]]) for j in range(len(lists))]

        r,c = Display.getTerminalSize()
        r -= 1 # to hack in a title line later
        max_avg = c / len(widths)

        small = [w for w in widths if w < max_avg]
        large = [w for w in widths if w >= max_avg]
        max_w = c - (sum(small) + len(small))
        if large != []: max_w /= len(large)
        final_w = [min(max_w, w) for w in small+large]
        rows = Display.getRows(lists, final_w, tasks, do)
        r -= 1
        # also need the -1 after len(rows) to get pages to update properly...
        # so hacky.
        pages = ['\n'.join(rows[r*a:r*(a+1)]) for a in range((len(rows)-1)/r+1)]

        # Add a title line in the grossest possible way
        title = Display.GREEN + Display.BOLD + Display.UNDERLINE
        # add in number over task numbers...not actually task attribute
        title += ('{:<'+str(final_w[0])+'}').format('#') + ' '
        # add in capitalized titles for task attributes
        for i, title_w in enumerate(final_w[1:]):
            title += ('{:<'+str(title_w+1)+'}').format(names[i][0].upper())
        # now add to all pages, adding in pagenumbers as you go
        for i in range(len(pages)):
            pagestring = str(i+1) + '/' + str(len(pages))
            pagedtitle = title[:-(len(pagestring)+1)] + pagestring
            pages[i] = pagedtitle + '\n' + pages[i]
        # wait...what happens if there's only space for a title page?
        # thankfully can't make terminal that small on my computer...hmm.
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
                fx = Display.NRML
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
