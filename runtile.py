#!/usr/bin/python
# tst.py
#
# Copyright (C) 2013 
# Author: John Porter <jdp@user-desktop>
# Created: 24 Nov 2013
#
"""
tst.py
['__class__', '__cmp__', '__copy__', '__deepcopy__', '__delattr__', '__dict__', '__doc__', '__format__', '__gdoc__', '__getattribute__', '__gobject_init__', '__grefcount__', '__gtype__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'activate', 'activate_transient', 'chain', 'close', 'connect', 'connect_after', 'connect_object', 'connect_object_after', 'disconnect', 'disconnect_by_func', 'emit', 'emit_stop_by_name', 'freeze_notify', 'get_actions', 'get_application', 'get_class_group', 'get_client_window_geometry', 'get_data', 'get_geometry', 'get_group_leader', 'get_icon', 'get_icon_is_fallback', 'get_icon_name', 'get_mini_icon', 'get_name', 'get_pid', 'get_properties', 'get_property', 'get_screen', 'get_session_id', 'get_session_id_utf8', 'get_sort_order', 'get_state', 'get_transient', 'get_window_type', 'get_workspace', 'get_xid', 'handler_block', 'handler_block_by_func', 'handler_disconnect', 'handler_is_connected', 'handler_unblock', 'handler_unblock_by_func', 'has_icon_name', 'has_name', 'is_above', 'is_active', 'is_below', 'is_fullscreen', 'is_in_viewport', 'is_maximized', 'is_maximized_horizontally', 'is_maximized_vertically', 'is_minimized', 'is_most_recently_activated', 'is_on_workspace', 'is_pinned', 'is_shaded', 'is_skip_pager', 'is_skip_tasklist', 'is_sticky', 'is_visible_on_workspace', 'keyboard_move', 'keyboard_size', 'make_above', 'make_below', 'maximize', 'maximize_horizontally', 'maximize_vertically', 'minimize', 'move_to_workspace', 'needs_attention', 'notify', 'or_transient_needs_attention', 'pin', 'props', 'set_data', 'set_fullscreen', 'set_geometry', 'set_icon_geometry', 'set_properties', 'set_property', 'set_skip_pager', 'set_skip_tasklist', 'set_sort_order', 'set_window_type', 'shade', 'stick', 'stop_emission', 'thaw_notify', 'transient_is_most_recently_activated', 'unmake_above', 'unmake_below', 'unmaximize', 'unmaximize_horizontally', 'unmaximize_vertically', 'unminimize', 'unpin', 'unshade', 'unstick', 'weak_ref']
"""
import time
import os
import wnck
import gtk
import globalhotkeys
import psutil
import prettytable
import subprocess as sp

globalhotkeys.init()
hotkeys = globalhotkeys.GlobalHotkey()
mask = (wnck.WINDOW_CHANGE_X|
        wnck.WINDOW_CHANGE_Y|
        wnck.WINDOW_CHANGE_HEIGHT|
        wnck.WINDOW_CHANGE_WIDTH)

#use the left top corner of the client window as gravity point
gravity = wnck.WINDOW_GRAVITY_STATIC

def test_key(*args):
    print 'HELLO', args
    
def shrun(cmd_str):
    proc = sp.Popen([cmd_str], shell=True,
                    stdin=None, stdout=None, stderr=None, close_fds=True)
import os
import sys

def run(cmd_str):
    """Spawn a completely detached subprocess (i.e., a daemon).
    """
    # fork the first time (to make a non-session-leader child process)
    try:
        pid = os.fork()
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))
    if pid != 0:
        # parent (calling) process is all done
        os.waitpid(pid, 0)
        print 'waited for pid', pid
        return

    # detach from controlling terminal (to make child a session-leader)
    os.setsid()
    try:
        pid = os.fork()
    except OSError, e:
        raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))
        raise Exception, "%s [%d]" % (e.strerror, e.errno)
    if pid != 0:
        # child process is all done
        os._exit(0)

    # grandchild process now non-session-leader, detached from parent
    # grandchild process must now close all open files
    try:
        maxfd = os.sysconf("SC_OPEN_MAX")
    except (AttributeError, ValueError):
        maxfd = 1024

    for fd in range(maxfd):
        try:
           os.close(fd)
        except OSError: # ERROR, fd wasn't open to begin with (ignored)
           pass

    # redirect stdin, stdout and stderr to /dev/null
    os.open(os.devnull, os.O_RDWR)  # standard input (0)
    os.dup2(0, 1)
    os.dup2(0, 2)

    # and finally let's execute the executable for the daemon!
    try:
        os.execvp(cmd_str, [cmd_str])
    except Exception, e:
      # oops, we're cut off from the world, let's just give up
      os._exit(255)

class unknown_proc:
    name = 'unknown'
      
class WindowManager (object):
    def __init__(self):
        self.screen = wnck.screen_get_default()
        self.screen.force_update()
        self.get_size()
        self.bind_keys()
        ws = self.screen.get_active_workspace()
        active = self.screen.get_active_window()
        self.windows= [w for w in self.screen.get_windows()
                       if (w.is_visible_on_workspace(ws) and
                           w.is_in_viewport(ws))
                       ]
        self.choose_window()
        #self.info(active, ws)
        self.screen.connect("window-opened", self.window_opened)
        self.screen.connect("window-closed", self.window_closed)
        self.screen.connect("active-workspace-changed", self.active_workspace_changed)
        self.screen.connect("active-window-changed", self.active_window_changed)
        self.screen.connect("viewports-changed", self.viewports_changed)

        self.orgs = {}
        self.actives = {}

    def window_opened(self,*args):
        print 'open', args
        self.re_arrange_terminals()
        
    def window_closed(self,*args):
        print 'close', args
        self.re_arrange_terminals()

    def active_workspace_changed(self,*args):
        print 'awsc', args
        
    def active_window_changed(self,*args):
        print 'awc', args
        
    def viewports_changed(self,*args):
        print 'vpc', args

    def get_active_window(self):
        w = self.screen.get_active_window()
        pid = w.get_application().get_pid()
        print 'get active', w.get_xid(), pid
        if pid:
            p = psutil.Process(pid)
        else:
            p = unknown_proc
        w.proc = p
        return w

    def get_view(self):
        ws = self.screen.get_active_workspace()
        return ws.get_viewport_x(),ws.get_viewport_y()

    def get_actives(self):
        vp = self.get_view()
        actives = self.actives.setdefault(vp,[])
        return actives
    
    def get_org(self):
        vp = self.get_view()
        return self.orgs.get(vp,'')
    
    def set_org(self, org):
        vp = self.get_view()
        self.orgs[vp] = org

    def get_visible_windows(self):
        ws = self.screen.get_active_workspace()
        actives = self.get_actives()
        wlist = []
        for w in self.screen.get_windows():
            if (w.is_visible_on_workspace(ws) and
                w.is_in_viewport(ws)):
                pid = w.get_application().get_pid()
                print w.get_name(),'%x' % w.get_xid(),pid
                if pid:
                    p = psutil.Process(pid)
                else:
                    p = unknown_proc
                w.proc = p
                wlist.append(w)

        rwlist = []
        for a in actives:
            if a in wlist:
                rwlist.append(a)
                wlist.remove(a)
        rwlist.extend(wlist)
        
        return rwlist
    
    def choose_window(self):
        ws = self.screen.get_active_workspace()
        for w in self.windows:
            p = psutil.Process(w.get_application().get_pid())
            print w.get_name(),w.get_geometry(),
            print w.get_application().get_name(),
            #print w.get_application().get_icon_name(),
            print w.is_in_viewport(ws),
            print p.name
            print

    def show_info(self):
        ws = self.screen.get_active_workspace()
        print 'ws',ws.get_number(), ws.get_viewport_x()
        wlist = self.get_visible_windows()
        pt = prettytable.PrettyTable(['name','app'])
        for w in wlist:
            pt.add_row([w.get_name(), w.proc.name])
        print pt
            
    def info(self, w):
        return '%s:%s' % (w.get_name(),w.proc.name)
        #xx,yy,ww,hh =  w.get_geometry () # (734, 25, 1130, 1016)
        #w.set_geometry(gravity, mask x, y, w, h)
        #w.move_to_workspace(ws)
        #w.activate()
        #w.maximize_vertically()
        #w.unmaximize_vertically()

        # above all others
        #w.make_above()
        #w.unmake_above()

        # stick/unstick 
        #w.stick()
        #w.unstick()

    def get_size(self):
        h = self.screen.get_height()
        w = self.screen.get_width()

    def isterm(self, w):
        return w.proc.name in ['urxvt','mrxvt','rxvt','xterm']
    
    def isemacs(self, w):
        return w.proc.name in ['emacs']

    def get_space(self):
        w = self.screen.get_width()
        h = self.screen.get_height()
        wlist = self.get_visible_windows()
        named = dict([(ww.get_name(),ww) for ww in wlist])
        try:
            # this worked for old gnome...
            # TODO - use named
            bp = [ww for ww in wlist if 'Bottom Expanded' in ww.get_name()][0]
            tp = [ww for ww in wlist if 'Top Expanded' in ww.get_name()][0]
            bx,by,bw,bh = bp.get_geometry()
            tx,ty,tw,th = tp.get_geometry()
            h = h - (th+bh)
            x = 0
            y = th
        except IndexError:
            # this works on mint - maybe works everywhere ?
            dt = named.get('Desktop')
            if dt:
                x,y,w,h = dt.get_geometry()
            else:
                raise ValueError, "Can't get geometry..."
        return x,y,w,h
        
    
    def move_viewport(self,d):
        ws = self.screen.get_active_workspace()
        w = self.screen.get_width()
        x = ws.get_viewport_x()
        y = ws.get_viewport_y()
        #w = ws.get_width()
        x += d*w
        print ws.get_layout_row()
        self.screen.move_viewport(x,y)

    def restart(self):
        os.system("(sleep 1 ; python tst.py)&")
        exit()
        
    def test_key(self, key, *args):
        k = key.split(">")[-1]
        if k == 'x': gtk.main_quit()
        elif k == 'Left': self.next_sides('l') 
        elif k == 'Right': self.next_sides('r')
        elif k == 'Up': self.next_sides('t')
        elif k == 'Down': self.next_sides('b')
        elif k == 'f': self.focus_active()
        elif k == 'c': self.restart()
        elif k == 'i': self.show_info()
        elif k == 'l': self.move_viewport(+1)
        elif k == 'k': self.move_viewport(-1)
        elif k == 't': self.add_terminal()
        elif k == 'space': self.arrange_terminals()
        elif k == 'p': self.pack_terminals()
        elif k == 'g': self.grid_terminals()
        elif k in '0123456789':
            self.goto_terminal(int(k))
        else: print key

    def focus_active(self):
        active = self.get_active_window()
        if not self.isterm(active):
            print 'not a terminal - ignoring'
            return
        actives = self.get_actives()
        if active in actives:
            actives.remove(active)
        actives.insert(0,active)
        
        self.re_arrange_terminals()
        wlist = self.get_visible_terms()
        
        #if wlist: wlist[0].activate(int(time.time()))
        active.activate(int(time.time()))
        
    def re_arrange_terminals(self):
        org = self.get_org()
        if org == 'a':
            self.arrange_terminals()
        elif org == 'g':
            self.grid_terminals()
        elif org == 'p':
            self.pack_terminals()
        else:
            pass

    def get_target_cols(self, w):
        return int(w/522)
    
    def grid_terminals(self):
        self.set_org('g')
        wlist = self.get_visible_terms()
        if not len(wlist): return
        x,y,w,h = self.get_space()
        target_cols = self.get_target_cols()
        cols = min(target_cols,max(1,len(wlist)))
        rows = (len(wlist)+(cols-1))/cols
        i = 0
        colw = w/cols
        rowh = h/rows
        for col in range(cols):
            for row in range(rows):
                if i >= len(wlist): return
                w = wlist[i]
                w.set_geometry(gravity, mask, x+col*colw,y+row*rowh,colw,rowh)
                i += 1
        
    def pack_terminals(self):
        """Arrange so with one terminal big.
        
        Smash all the others into a small space.
        """
        self.set_org('p')
        wlist = self.get_visible_terms()
        if not len(wlist): return
        print 'wins',len(wlist)
        x,y,w,h = self.get_space()
        minw = 200
        maxw = w-minw
        i = 0
        col = 0
        if i >= len(wlist): return
        wlist[i].set_geometry(gravity, mask, x,y,maxw,h)
        i += 1
        if i >= len(wlist): return
        rowh = h/(len(wlist)-1)
        colw = minw
        for row in range(0,len(wlist)-1):
            print 'row',row,i
            wlist[i].set_geometry(gravity, mask, x+maxw,y+row*rowh,minw,rowh)
            i += 1

    def get_layout(self):
        wlist = self.get_visible_terms()
        for ww in wlist:
            ww.x,ww.y,ww.w,ww.h = ww.get_geometry()
        return wlist
    
    def next_sides(self,dir='r'):
        active = self.get_active_window()
        wlist = self.get_layout()
        
        if not wlist: return
        actives = [w for w in wlist if w.get_xid()==active.get_xid()]
        
        if not actives: return
        active = actives[0]
        
        def midy(w):
            return (w.y+w.h/2)
        def midx(w):
            return (w.x+w.w/2)
        if dir in 'rl': mid = midy
        else: mid = midx
        if dir == 'r':
            wins = sorted([(w.x,abs(mid(active)-mid(w)),w) for w in wlist if w.x > active.x])
        elif dir == 'l':
            wins = sorted([(w.x,-abs(mid(active)-mid(w)),w) for w in wlist if w.x < active.x],
                          reverse=True)
        elif dir == 't':
            wins = sorted([(w.y,-abs(mid(active)-mid(w)),w) for w in wlist if w.y < active.y],
                          reverse=True)
        elif dir == 'b':
            wins = sorted([(w.y,abs(mid(active)-mid(w)),w) for w in wlist if w.y > active.y],
                          reverse=False)
        if wins:
            w = wins[0][-1]
            w.activate(int(time.time()))

        
    def arrange_terminals(self):
        """Arrange into one big and maybe another bit and then smaller.."""
        self.set_org('a')
        wlist = self.get_visible_terms()
        if not len(wlist): return
        x,y,w,h = self.get_space()
        target_cols = self.get_target_cols(w)
        cols = max(target_cols,min(target_cols,len(wlist)))
        colw = w/cols
        i = 0
        col = 0
        rows0 = 1
        row = 0
        rowh = h/rows0
        if i >= len(wlist): return
        for r in range(rows0):
            wlist[i].set_geometry(gravity, mask, x+col*colw,y+row*rowh,colw,rowh)
        #
        
        i+=1
        if i >= len(wlist): return
        col = 1
        cols_left = target_cols-1
        if cols_left == 1:
            rows1 = max(1,min(12,len(wlist)-rows0))
        else:
            rows1 = max(1,min(2,len(wlist)-cols_left-rows0))
        row = 0
        rowh = h/rows1
        for r in range(rows1):
            wlist[i].set_geometry(gravity, mask, x+col*colw,y+row*rowh,colw,rowh)
            i+=1
            if i >= len(wlist): return
            row += 1
        #
        if target_cols <= 3: return
        col = 2
        rows2 = max(1,min(12,len(wlist)-rows1-rows0))
        row = 0
        rowh = h/rows2
        for r in range(rows2):
            wlist[i].set_geometry(gravity, mask, x+col*colw,y+row*rowh,colw,rowh)
            i+=1
            if i >= len(wlist): return
            row += 1
            
        print rows1

    def get_visible_terms(self):
        wlist = self.get_visible_windows()
        wlist = [w for w in wlist if self.isterm(w) or self.isemacs(w)]
        return wlist
    
    def goto_terminal(self, n):
        wlist = self.get_visible_terms()

        if n < len(wlist):
            w = wlist[n]
            print 'goto', self.info(w)
            w.activate(int(time.time()))
        else:
            print 'nup',n
        
    def add_terminal(self):
        run("urxvt")
        
    def bind_keys(self):
        keys = ([str(i) for i in range(10)] +
                [v for v in "bcdfghijklopqrtuvxyz,./><=+-"] +
                ["Up","Down","Left","Right","space"])
        for k in keys:
            if not hotkeys.bind("<Mod4>%s" % k, self.test_key):
                print "FAIL: key taken"


    
def main():
    if not hotkeys.bind("<Mod4>R", test_key):
        print "FAIL: key taken"
    wm = WindowManager()
    gtk.main()
    print 'Finished'
    
if __name__ == "__main__":
    main()
    


