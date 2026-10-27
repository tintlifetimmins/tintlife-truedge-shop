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
s=re.sub(r'  <div class="tax"><label for="prov">.*?\n  <div class="tax"><label for="tlp-code">.*?\n','',s,1)
s=re.sub(r'<a class="tlp-btn" href="#" id="buy">.*?</a>\n.*?\n.*?</p>\n',
 '<!-- MINI CHECKOUT PLACEHOLDER: no Square checkout for the Tintlife TruEdge Mini yet (Worker prices full-size only). -->\n  <a class="tlp-btn" href="#" id="buy" aria-disabled="true" style="opacity:.55;cursor:not-allowed;box-shadow:none">Checkout coming soon</a>\n  <p class="tlp-note" style="color:#ffcc33">Online checkout for the Tintlife TruEdge Mini is not open yet. <a href="contact.html">Contact us</a> to order.</p>\n',s,1,flags=re.S)
R("var IMG='renders_v1.22/',V='_v1.22';","var IMG='renders_mini_v1.5/',V='_v1.5';")
R(',["Carbon Fibre (black only) (Nylon)","#1F2125","pa_cf",1]]',']')
R('["Carbon Fibre (black only) (PETG-CF)"','["Carbon Fibre (black only)"')
R('renders_v1.22/truedge_pla_basic_black_v1.22.webp" alt="Tintlife TruEdge squeegee','renders_mini_v1.5/truedge_pla_basic_black_v1.5.webp" alt="Tintlife TruEdge Mini squeegee')
R("function ov(){var t=et.value.trim();if(!E()||!t){","function ov(){var t=et.value.trim();if(1){") # engraving overlay is calibrated to the full-size render; off for Mini
s=re.sub(r'\nvar RT=.*?\n</script></div>',"\nvar MINI_CHECKOUT_URL=null; // PLACEHOLDER\ndocument.getElementById('buy').onclick=function(e){e.preventDefault();if(!MINI_CHECKOUT_URL)alert('Online checkout for the Tintlife TruEdge Mini is coming soon. Please contact us to order.')};\n</script></div>",s,1,flags=re.S)
s=re.sub(r'<section class="sec"><h2>New: Tintlife TruEdge Mini</h2>.*?</main>',open('mini_sections.html').read().strip()+'</main>',s,1,flags=re.S)
open('mini.html','w').write(s)
