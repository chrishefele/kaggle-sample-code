def reTag(atag):  
    # renames tags that are not all upper-case chars
    # f = lambda c: c if c.isupper() else 'ORD'+str(ord(c))
    def f(c): 
        if c.isupper():
            return c
        else:
            return 'ORD'+str(ord(c))
    return ''.join( map(f, [c for c in atag]) )

