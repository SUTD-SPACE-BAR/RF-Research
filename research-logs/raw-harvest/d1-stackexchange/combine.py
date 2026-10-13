import json,glob,html,re,collections
rows={}
src=collections.defaultdict(list)
for fn in sorted(glob.glob('q_*.json')):
    m=re.match(r'q_(\w+)_(.+)_(votes|hot)_p(\d)\.json',fn)
    site,tag,sort,page=m.groups()
    d=json.load(open(fn))
    for rank,it in enumerate(d.get('items',[])):
        key=(site,it['question_id'])
        r=rows.setdefault(key,dict(site=site,id=it['question_id'],title=html.unescape(it['title']),score=it['score'],views=it['view_count'],tags=it['tags'],link=f"https://{site}.stackexchange.com/q/{it['question_id']}",srcs=[]))
        r['srcs'].append(f"{tag}#{(int(page)-1)*100+rank+1}")
json.dump(list(rows.values()),open('all.json','w'))
print(len(rows))
c=collections.Counter(r['site'] for r in rows.values());print(c)
