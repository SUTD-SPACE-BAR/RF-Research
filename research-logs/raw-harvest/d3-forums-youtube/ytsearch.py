import sys, json, re, time, urllib.parse
sys.path.insert(0,'.')
from yt import fetch, vids
out=open(sys.argv[1],'a')
for q in sys.argv[2:]:
    try:
        x=fetch('https://www.youtube.com/results?search_query='+urllib.parse.quote(q))
        d=json.loads(re.search(r'var ytInitialData = (\{.*?\});</script>', x, re.S).group(1))
    except Exception as e:
        print('ERR',q,e); continue
    # channel names
    chans={}
    s=json.dumps(d)
    n=0
    def walk(o):
        if isinstance(o, dict):
            if 'videoRenderer' in o: yield o['videoRenderer']
            for v in o.values(): yield from walk(v)
        elif isinstance(o, list):
            for v in o: yield from walk(v)
    for v in walk(d):
        t=v['title']['runs'][0]['text']; vw=v.get('viewCountText',{}).get('simpleText','')
        ch=v.get('ownerText',{}).get('runs',[{}])[0].get('text','')
        out.write(f"search:{q}\t{vw}\t{t}\thttps://www.youtube.com/watch?v={v['videoId']}\t{ch}\n"); n+=1
    print(q,n); time.sleep(1.5)
