import re, sys, time, urllib.request, html
feeds = ['category/radio-hacks'] + ['tag/'+t for t in ['lora','sdr','radar','antenna','antennas','rtl-sdr','nanovna','phased-array','software-defined-radio','ham-radio','meshtastic','vna','spectrum-analyzer','tinysa','lorawan','gps','rf']]
seen = {}
for fd in feeds:
    for p in range(1, 9 if fd.startswith('category') else 4):
        url = f'https://hackaday.com/{fd}/feed/?paged={p}'
        try:
            x = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read().decode('utf8','ignore')
        except Exception as e:
            print('ERR', url, e, file=sys.stderr); break
        items = re.findall(r'<item>(.*?)</item>', x, re.S)
        if not items: break
        for it in items:
            t = html.unescape(re.search(r'<title>(.*?)</title>', it, re.S).group(1))
            l = re.search(r'<link>(.*?)</link>', it).group(1)
            c = re.search(r'<slash:comments>(\d+)', it); c = int(c.group(1)) if c else 0
            d = re.search(r'<pubDate>(.*?)</pubDate>', it).group(1)[5:16]
            seen.setdefault(l, (c, d, fd, t, l))
        time.sleep(1)
with open('hackaday.tsv','w') as f:
    for v in sorted(seen.values(), reverse=True): f.write('\t'.join(map(str,v))+'\n')
print(len(seen))
