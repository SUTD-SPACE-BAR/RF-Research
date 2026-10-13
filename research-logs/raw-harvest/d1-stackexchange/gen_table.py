import json,os,re,sys
KB="/Users/marcusquek/Documents/RF Physics/kb"
dmap={d[:2]:d for d in os.listdir(KB) if re.match(r'\d\d-',d)}
k=json.load(open('keep_sorted.json'))
cls={}
for line in open(sys.argv[1] if len(sys.argv)>1 else 'cls.txt'):
    line=line.rstrip('\n')
    if not line.strip(): continue
    p=line.split('|',4)
    cls[int(p[0])]=p
def expand(pg):
    if not pg: return ''
    m=re.match(r'(\d\d)/([^#]+)(#.*)?$',pg)
    if not m: return pg
    nn,slug,sec=m.groups()
    path=f"kb/{dmap.get(nn,nn)}/{slug}.md"
    exists=os.path.exists(os.path.join(KB,dmap.get(nn,nn),slug+'.md'))
    return path+(sec or '')+('' if exists else ' (NOT FOUND)')
rows=[]
for i,r in enumerate(k,1):
    c=cls.get(i,[str(i),'','TBD','',''])
    t=r['title'].replace('|','/')
    tag=r['srcs'][0].split('#')[0]
    rows.append(dict(n=i,title=t,url=r['link'],src=f"{r['site'][:3]}/{tag}",vv=f"{r['score']}/{r['views']}",dom=c[1],st=c[2],page=expand(c[3]),note=c[4].replace('|','/'),score=r['score'],views=r['views']))
json.dump(rows,open('merged.json','w'))
out=["| # | question | URL | site/tag | votes/views | domain | status | KB page | note |","|---|---|---|---|---|---|---|---|---|"]
for x in rows:
    out.append(f"| {x['n']} | {x['title']} | {x['url']} | {x['src']} | {x['vv']} | {x['dom']} | {x['st']} | {x['page']} | {x['note']} |")
open('table.md','w').write("\n".join(out)+"\n")
nf=[x for x in rows if 'NOT FOUND' in x['page']]
print(len(rows),'rows; not-found page refs:',len(nf))
for x in nf[:20]: print(x['n'],x['page'])
