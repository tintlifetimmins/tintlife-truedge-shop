# Generates mini.html from index.html (same markup/CSS/JS), swapping only Tintlife TruEdge Mini product data.
import re
s=open('index.html').read(); old=open('/tmp/mini_old.html').read() if False else None
def R(a,b,n=1):
    global s; assert s.count(a)>=1,a[:60]; s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# head
s=re.sub(r'<script>if\(/\[\?&\]size=mini.*?</script>','',s,1)
s=re.sub(r'<title>.*?</title>','<title>Tintlife TruEdge Mini | Pocket squeegee &amp; hard card sharpener, from $19.99 CAD</title>',s,1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Tintlife TruEdge Mini is the pocket-size Tintlife TruEdge, using the same Stanley blade. Eco $19.99, Premium $29.99 CAD.">',s,1)
s=re.sub(r'<meta property="og:.*?\n<script type="application/ld\+json">.*?</script>\n','',s,1,flags=re.S)
R('<link rel="canonical" href="https://shop.tintlife.ca/">','<link rel="canonical" href="https://shop.tintlife.ca/mini.html">')
R('<a href="index.html" class=on>Shop</a><a href="mini.html">','<a href="index.html">Shop</a><a href="mini.html" class=on>')
R('<a href="index.html" aria-current="true">Full-size</a><a href="mini.html" aria-current="false">','<a href="index.html" aria-current="false">Full-size</a><a href="mini.html" aria-current="true">')
# product panel
R('<p class="tlp-kicker">Squeegee &amp; hard card sharpener</p>','<p class="tlp-kicker">Pocket squeegee &amp; hard card sharpener</p>')
R('<h1 class="tlp-h">Tintlife TruEdge</h1>','<h1 class="tlp-h">Tintlife TruEdge Mini</h1>')
s=re.sub(r'<p class="hdesc">.*?</p>','<p class="hdesc">The pocket-size Tintlife TruEdge. Uses the same Stanley blade as the full-size Tintlife TruEdge.</p>',s,1)
s=re.sub(r'(<div class="tlp-price" id="tlp-price">)\$29\.99',r'\g<1>$19.99',s,1)
s=re.sub(r'<button type="button" role="radio" data-p="29.99" data-n="Eco">.*?</button>','<button type="button" role="radio" data-p="19.99" data-n="Eco"><b>Eco — $19.99</b><span>Carbon Fibre $24.99</span></button>',s,1)
s=re.sub(r'<button type="button" role="radio" data-p="39.99" data-n="Premium">.*?</button>','<button type="button" role="radio" data-p="29.99" data-n="Premium"><b>Premium — $29.99</b><span>Carbon Fibre $34.99</span></button>',s,1)
R('Engraving text (one line, on the plain side wall)','Engraving text (one line, on the blank side)')
R('Engraving is recessed into the part, same colour as the body (single-colour print). Preview is approximate.','Engraving goes on the blank side.')
R('Every Tintlife TruEdge is serial numbered (TE-0001, TE-0002 …). Made in Timmins, Ontario.','Made in Timmins, Ontario.')
R("var IMG='renders_v1.22/',V='_v1.22';","var IMG='renders_mini_v1.5/',V='_v1.5';")
R(',["Carbon Fibre (black only) (Nylon)","#1F2125","pa_cf",1]]',']')
R('["Carbon Fibre (black only) (PETG-CF)"','["Carbon Fibre (black only)"')
R('renders_v1.22/truedge_pla_basic_black_v1.22.webp" alt="Tintlife TruEdge squeegee','renders_mini_v1.5/truedge_pla_basic_black_v1.5.webp" alt="Tintlife TruEdge Mini squeegee')
import json
c=json.load(open('/workspace/truedge-mini/work/r15/bl/c_black.json'))
s=re.sub(r'var Q=\[\[.*?\]\];','var Q='+json.dumps([c['tl'],c['tr'],c['br'],c['bl']])+';',s,count=1)  # Mini blank-side text rect (54 x 13.5 mm) from blank.py
R('inv(basis([[0,0],[1000,0],[1000,135],[0,135]]))','inv(basis([[0,0],[540,0],[540,135],[0,135]]))')
R('<text id="tlp-ovt" x="500"','<text id="tlp-ovt" x="270"')
R('fs=w>1000?80*1000/w:80','fs=w>540?80*540/w:80')
R("var b=this,o=window.TE();","var b=this,o=window.TE();o.product='mini';")
R("% on the Tintlife TruEdge)","% on the Tintlife TruEdge Mini)")
R("% off the Tintlife TruEdge.","% off the Tintlife TruEdge Mini.")
R("discount on the base Tintlife TruEdge line only","discount on the base Tintlife TruEdge Mini line only")
s=re.sub(r'<section class="sec"><h2>New: Tintlife TruEdge Mini</h2>.*?</main>',open('mini_sections.html').read().strip()+'</main>',s,1,flags=re.S)
open('mini.html','w').write(s)
