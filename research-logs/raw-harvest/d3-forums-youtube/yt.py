import re, json, sys, time, urllib.request
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
def fetch(url, data=None):
    h={'User-Agent':UA,'Accept-Language':'en-US,en;q=0.9'}
    if data is not None: h['Content-Type']='application/json'; data=json.dumps(data).encode()
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=30).read().decode('utf8','ignore')
def walk(o):
    if isinstance(o, dict):
        for k,v in o.items():
            if k in ('lockupViewModel','videoRenderer','chipViewModel','continuationItemRenderer'): yield k,v
            yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
def vids(d):
    out=[]
    for k,v in walk(d):
        if k=='lockupViewModel' and v.get('contentType','').endswith('VIDEO'):
            md=v['metadata']['lockupMetadataViewModel']
            title=md['title']['content']
            parts=[]
            try:
                for row in md['metadata']['contentMetadataViewModel']['metadataRows']:
                    for p in row.get('metadataParts',[]): parts.append(p.get('text',{}).get('content',''))
            except Exception: pass
            views=next((p for p in parts if 'view' in p), '')
            out.append((v['contentId'], title, views))
        elif k=='videoRenderer':
            out.append((v['videoId'], v['title']['runs'][0]['text'], v.get('viewCountText',{}).get('simpleText','')))
    return out
def channel(handle, pages=2):
    x=fetch(f'https://www.youtube.com/{handle}/videos')
    d=json.loads(re.search(r'var ytInitialData = (\{.*?\});</script>', x, re.S).group(1))
    ver=re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', x).group(1)
    ctx={'client':{'clientName':'WEB','clientVersion':ver,'hl':'en','gl':'US'}}
    tok=None
    for k,v in walk(d):
        if k=='chipViewModel' and v.get('text')=='Popular':
            tok=v['tapCommand']['innertubeCommand']['continuationCommand']['token']
    res=[]
    if not tok: return vids(d)
    for p in range(pages):
        r=json.loads(fetch('https://www.youtube.com/youtubei/v1/browse?prettyPrint=false', {'context':ctx,'continuation':tok}))
        res+=vids(r)
        tok=None
        for k,v in walk(r):
            if k=='continuationItemRenderer':
                try: tok=v['continuationEndpoint']['continuationCommand']['token']
                except Exception: pass
        if not tok: break
        time.sleep(1)
    return res
if __name__=='__main__':
    out=open(sys.argv[1],'a')
    for h in sys.argv[2:]:
        try:
            vs=channel(h)
        except Exception as e:
            print('ERR',h,e); continue
        seen=set()
        for vid,t,vw in vs:
            if vid in seen: continue
            seen.add(vid)
            out.write(f"{h}\t{vw}\t{t}\thttps://www.youtube.com/watch?v={vid}\n")
        print(h, len(seen)); time.sleep(1.5)
