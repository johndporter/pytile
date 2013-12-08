#!/usr/bin/python
# sweep.py
#
# Copyright (C) 2013 
# Author: John Porter <jdp@user-desktop>
# Created: 08 Dec 2013
#
"""
Find largest empty rectangle in space full of rectangles
(currently assumes non intersecting rectangles....)

"""
from operator import attrgetter

class Edge:
    def __init__(self, y0,y1,x,start):
        self.y0,self.y1,self.x,self.start = y0,y1,x,start
        self.i = -1
        
    def __repr__(self):
        return 'E(%d,%d,%s,%d,%s,%d)' % (self.x,self.y0,None,self.y1,self.start,self.i)

class Rect:
    def __init__(self, x0,y0,x1,y1):
        self.x0,self.y0,self.x1,self.y1 = x0,y0,x1,y1

    def w(self):
        return self.x1-self.x0
    
    def h(self):
        return self.y1-self.y0

    def area(self):
        return self.w()*self.h()
        
    def __repr__(self):
        return '(%d,%d,%d,%d)' % (self.x0,self.y0,self.x1,self.y1)
        
class Line(Rect):
    def __init__(self, y0, y1, x):
        self.y0,self.y1,self.x0 = y0,y1,x
        self.x1 = -1
        

        
        
class Sweeper:
    """Sweep a line across the plane looking for empty rectangles"""

    def __init__(self, x0,y0, x1,y1):
        self.xmin,self.xmax = x0,x1
        self.ymin,self.ymax = y0,y1
        self.rects = []
        self.edges = []
        self.res = []

    def add_rect(self, rect):
        self.rects.append(rect)
        self.edges.extend([Edge(rect.y0,rect.y1,rect.x0,True),
                           Edge(rect.y0,rect.y1,rect.x1,False)])
        
    def sort_edges(self):
        # sort edges by right
        self.edges.sort(key=attrgetter('x'))
        for i,e in enumerate(self.edges): e.i = i
        # sort rectangles by top
        self.rects.sort(key=attrgetter('y0'))

    def next_rect(self, overlaps_x, greater_than_y):
        """Find first rect in y which overlaps x and stops a line down from
        greater_than_y"""
        
        for rect in self.rects:
            if (rect.x0 >= overlaps_x and rect.x1 <= overlaps_x and
                rect.y0 >= greater_than_y):
                return rect
            

    def line_above(self, edge, line):
        """Got to the end of a rectangle

        Create the new line which includes this edge ie
        is drawn down from the edge until it hits the next rect.

        The only time when the line is drawn upwards is when the
        rectangle just finishing is flush with ymin.

        """
        #print 'line above', edge, line
        if edge.y0 == line.y1:
            # the top part of the line is just extended
            y0 = line.y0
            # find the rectangle terminating the new line
            # ie rect.x0 <= edge.x and rect.x1 >= edge.x
            # and the first rect for which rect.y0 >= edge.y1
            nrect = self.next_rect(edge.x, edge.y1)
            if not nrect: y1 = self.ymax
            else: y1 = nrect.y0
            nline = Line(y0,y1,edge.x)
            #print 'nline',nline
            return nline
        elif edge.y0 == self.ymin and edge.y1 == line.y0:
            #print '---------------------'
            # rectangle was flush with top edge
            # so return new line up to the top
            nline = Line(self.ymin,line.y1,edge.x)
            return nline

    def get_next_edge(self, edge=None):
        """Next edge in x direction from edge"""
        if edge is None:
            return self.edges[0]
        else:
            #print 'get_next',edge
            if edge.i >= (len(self.edges)-1):
                return None
            else:
                return self.edges[edge.i+1]

    def get_next_line_edge(self, edge, line):
        """Find the next edge intersected by line"""
        while True:
            edge = self.get_next_edge(edge)
            if not edge:
                return
            else:
                if (line.y0 <= edge.y1) and (line.y1 >= edge.y0):
                    return edge
                

    def split_line(self, edge, line):
        #print 'split_line',edge,line
        if line.y0 < edge.y0:
            # start new sweep line
            # splits previous sweep line
            line0 = Line(line.y0,edge.y0, line.x0)
        else:
            line0 = None
        if line.y1 > edge.y1:
            # split bottom part of line
            line2 = Line(edge.y1,line.y1, line.x0)
        else:
            line2 = None
        line.x1 = edge.x
        #print 'split',line0,line,line2
        return line0,line2

    def sweep_lines(self):
        self.res = []
        line = Line(self.ymin,self.ymax,self.xmin)
        self.sweep(None, line)
        
    def sweep(self, edge, line):
        print 'sweep',edge,line
        while True:
            pedge = edge
            edge = self.get_next_line_edge(edge, line)
            print 'next edge', pedge,edge
            if not edge: break
            if edge.start:
                line0,line2 = self.split_line(edge, line)
                print 'push',line
                self.res.append(line)
                if line0:
                    self.sweep(edge, line0)
                if line2:
                    self.sweep(edge, line2)
                # this line is finished
                return
            else:
                # edge end
                #self.sweep(edge, line)
                nline = self.line_above(edge, line)
                print 'nline',line,nline
                if nline:
                    self.sweep(edge, nline)
        #
        line.x1 = self.xmax
        print 'push',line
        self.res.append(line)

    def get_max(self):
        ras = sorted([(r.area(),r) for r in self.res])
        return ras[-1][1]

def main():
    import matplotlib.pyplot as plt
    import matplotlib.collections

    sw = Sweeper(0,0,1000,1000)
    sw.add_rect(Rect(100,0, 400,200))
    sw.add_rect(Rect(100,240,320,400))
    sw.add_rect(Rect(700,700,800,800))
    sw.sort_edges()
    
    ax = plt.gca()
    for l in sw.rects:
        rect = matplotlib.patches.Rectangle( (l.x0,l.y0), width=l.w(), height=l.h(),
                                             alpha=0.5,
                                             color='green')
        ax.add_patch(rect)
    for e in sw.edges:
        print e
    #
    print 'sweep'
    sw.sweep_lines()
    print 'results'

    for l in sw.res:
        c = plt.plot([l.x0,l.x1],[l.y0,l.y1],alpha=0.5)[0].get_color()
        rect = matplotlib.patches.Rectangle( (l.x0,l.y0), width=l.w(), height=l.h(),
                                             alpha=0.2,
                                             color=c)
        ax.add_patch(rect)

    l = sw.get_max()
    print l
    rect = matplotlib.patches.Rectangle( (l.x0,l.y0), width=l.w(), height=l.h(),
                                         alpha=0.5,
                                         color='red')
    ax.add_patch(rect)
    
    #plt.plot([0,1000],[0,1000])
    plt.show()


if __name__ == "__main__":
    main()
