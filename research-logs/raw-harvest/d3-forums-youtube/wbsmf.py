import re, html, json, sys, time, urllib.request, gzip
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'gzip'}),timeout=60).read()
    try: r=gzip.decompress(r)
    except Exception: pass
    return r.decode('utf8','ignore')
seen={}
out=sys.argv[1]
for spec in sys.argv[2:]:
    url,ts=spec.split('@') if '@' in spec else (spec,'')
    try:
        a=json.loads(get(f'https://archive.org/wayback/available?url={urllib.parse.quote(url)}&timestamp={ts}'))
        snap=a['archived_snapshots'].get('closest')
        if not snap: print('none',spec); continue
        su=snap['url'].replace('/https://','id_/https://',1).replace('/http://','id_/http://',1)
        x=get(su)
    except Exception as e:
        print('ERR',spec,e); continue
    rows=re.findall(r'<span id="msg_\d+"><a href="([^"]+)">(.*?)</a></span>.*?(\d+)\s+Replies\s*<br\s*/?>\s*(\d+)\s+Views', x, re.S)
    n=0
    for u,t,r,v in rows:
        u=re.sub(r'^https?://web\.archive\.org/web/\d+[a-z_]*/','',u)
        key=u.split('?')[0]
        if key not in seen: seen[key]=(int(r),int(v),html.unescape(t).strip(),key,snap['timestamp'][:8]); n+=1
    print(spec, snap['timestamp'], len(rows), n); time.sleep(2)
with open(out,'a') as f:
    for v in seen.values(): f.write('\t'.join(map(str,v))+'\n')
