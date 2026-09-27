import re,pickle,sys
def load(fn):
    blocks={};cur=None
    for l in open(fn).read().split('\n'):
        m=re.match(r'^(\d+) (P|TBL|sectPr)',l)
        if m: cur=int(m.group(1)); blocks[cur]=l[len(m.group(1))+1:]
        elif cur is not None: blocks[cur]+='\n'+l
    return blocks
