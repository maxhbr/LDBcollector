""" Tiny utility to split up a dist_git_commit string. """

def run(string):
    namespace, rest = string.split('/', 1)
    name, gitref = rest.split('#', 1)
    return dict(namespace=namespace, name=name, gitref=gitref)
