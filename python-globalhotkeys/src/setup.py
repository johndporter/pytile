from distutils.core import setup, Extension
import commands

def pkgconfig(*packages, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    cmd = "pkg-config --libs --cflags %s" % ' '.join(packages)
    output = commands.getoutput(cmd)
    for token in output.split():
        t = flag_map.get(token[:2])
        if t:
            kw.setdefault(t, []).append(token[2:])
    return kw



setup(name = "globalhotkeys",
      version = "1.0",
      ext_modules = [
          Extension("globalhotkeys", 
                    ["globalhotkeys.c", "eggaccelerators.c", "keybinder.c"], 
                    **pkgconfig("glib-2.0","gtk+-2.0")) ])

