import json, sys, time, urllib.request, urllib.parse
base, outname = sys.argv[1], sys.argv[2]
queries = sys.argv[3:]
seen = {}
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0', 'Accept':'application/json'})
    for i in range(3):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            time.sleep(3+5*i); err=e
    print('ERR', url, err, file=sys.stderr); return {}
for q in queries:
    for order in ['order:views', '']:
        d = get(f"{base}/search.json?q={urllib.parse.quote(q+' '+order)}")
        for t in d.get('topics', []):
            tid = t['id']
            if tid not in seen:
                seen[tid] = dict(id=tid, title=t['title'], posts=t.get('posts_count'), slug=t['slug'], q=q, created=t.get('created_at','')[:10])
        time.sleep(2.5)
with open(outname,'w') as f:
    for t in seen.values():
        f.write(f"{t['id']}\t{t['posts']}\t{t['created']}\t{t['q']}\t{t['title']}\t{base}/t/{t['slug']}/{t['id']}\n")
print(len(seen))
