import json, subprocess, sys, time
queries = sys.argv[2:]; out = sys.argv[1]
seen = {}
Q = '''query($q:String!){ search(query:$q, type:DISCUSSION, first:50){ nodes{ ... on Discussion { title url comments{totalCount} upvoteCount createdAt repository{nameWithOwner} } } } }'''
for q in queries:
    r = subprocess.run(['gh','api','graphql','-f',f'query={Q}','-f',f'q={q}'],capture_output=True,text=True)
    try:
        nodes = json.loads(r.stdout)['data']['search']['nodes']
    except Exception as e:
        print('ERR', q, r.stderr[:200], file=sys.stderr); continue
    for n in nodes:
        if n and n['url'] not in seen:
            seen[n['url']] = (n['comments']['totalCount'], n['upvoteCount'], n['createdAt'][:10], q, n['title'].replace('\t',' '), n['url'])
    time.sleep(1)
with open(out,'w') as f:
    for v in seen.values(): f.write('\t'.join(map(str,v))+'\n')
print(len(seen))
