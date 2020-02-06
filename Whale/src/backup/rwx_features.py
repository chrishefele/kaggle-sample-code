import os
import stat
import sys

def isOwnerExecutable(filepath):
    st = os.stat(filepath)
    return bool(st.st_mode & stat.S_IXUSR)

fname = sys.argv[1]
if isOwnerExecutable(fname):
    print fname, 'is owner executable'
else:
    print fname, 'is NOT owner executable'

