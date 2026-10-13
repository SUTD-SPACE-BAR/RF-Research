import re, sys, html, urllib.request, time
pats = sys.argv[1:]
rows = [l.rstrip('\n').split('\t') for l in open('hackaday.tsv')]
out = open('hd_comments.txt','a')
for p in pats:
    r = next((r for r in rows if p.lower() in r[3].lower()), None)
    if not r: print('nomatch', p); continue
    x = urllib.request.urlopen(urllib.request.Request(r[4], headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read().decode('utf8','ignore')
    cs = re.findall(r'class="comment-content">(.*?)</div>', x, re.S)
    out.write(f"\n=== {r[3]} | {r[4]} | {r[0]} comments\n")
    for c in cs:
        t = html.unescape(re.sub(r'<[^>]+>',' ',c)); t = re.sub(r'\s+',' ',t).strip()
        if '?' in t or len(t) > 120:
            out.write('- ' + t[:260] + '\n')
    time.sleep(1)
