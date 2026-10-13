import json, re, sys, time
sys.path.insert(0,'.')
from yt import fetch
def walk(o, key):
    if isinstance(o, dict):
        for k,v in o.items():
            if k==key: yield v
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o: yield from walk(v, key)
x=fetch('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
ver=re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', x).group(1)
ctx={'client':{'clientName':'WEB','clientVersion':ver,'hl':'en','gl':'US'}}
out=open('yt_comments.txt','a')
for vid in sys.argv[1:]:
    try:
        d=json.loads(fetch('https://www.youtube.com/youtubei/v1/next?prettyPrint=false',{'context':ctx,'videoId':vid}))
        title=next(walk(d,'videoPrimaryInfoRenderer'))['title']['runs'][0]['text']
        tok=None
        for isr in walk(d,'itemSectionRenderer'):
            if isr.get('sectionIdentifier')=='comment-item-section':
                for c in isr.get('contents',[]):
                    if 'continuationItemRenderer' in c:
                        tok=c['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
        coms=[]
        for page in range(2):
            if not tok: break
            r=json.loads(fetch('https://www.youtube.com/youtubei/v1/next?prettyPrint=false',{'context':ctx,'continuation':tok}))
            for p in walk(r,'commentEntityPayload'):
                t=p['properties']['content']['content']; likes=p.get('toolbar',{}).get('likeCountNotliked','')
                coms.append((likes,t.replace('\n',' ')))
            tok=None
            for cir in walk(r,'continuationItemRenderer'):
                try: tok=cir['continuationEndpoint']['continuationCommand']['token']
                except Exception:
                    try: tok=cir['button']['buttonRenderer']['command']['continuationCommand']['token']
                    except Exception: pass
            time.sleep(1)
        out.write(f"\n=== {title} | https://www.youtube.com/watch?v={vid} | {len(coms)} comments fetched\n")
        for l,t in coms: out.write(f"- [{l}] {t[:240]}\n")
        print(vid, title[:60], len(coms))
    except Exception as e:
        print('ERR', vid, e)
    time.sleep(1.5)
