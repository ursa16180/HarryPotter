import re
import orodja

vzorec_knjige_v_seriji = re.compile("""class="bookTitle" itemprop="url" href="(?P<kratki_url>.*?)">\s*?<span itemprop='name'>.*?\(.*?, #\d+\)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>""")

serije = orodja.datoteke("serije")


for serija in serije:
    vsebina = orodja.vsebina_datoteke(serija)
    print(serija)
    for vzorec1 in re.finditer(vzorec_knjige_v_seriji, vsebina):
        knjiga = vzorec1.groupdict()
        if knjiga['id_knjige'] in
