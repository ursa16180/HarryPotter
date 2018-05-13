import re
import orodja
import html

vzorec_opis_zanr = re.compile("""mediumText reviewText">\s+?<span id="freeTextContainer\d+?">(?P<opis>.+?)</span>(\s+?<span id="freeText\d+?" style="display:none">(?P<opis_dolg>.+?)</span>)?""")

vzorec_ime_zanra =re.compile("""<div class="genreHeader">\s+<h1 class="left">\s+(?P<ime_zanra>.*?)\s+?</h1>""")

seznam_vseh_zanrov = []

def shrani_zanre(mapa):
    for zanr in mapa:
        vsebina = orodja.vsebina_datoteke(zanr)
        print(zanr)
        for vzorec1 in re.finditer(vzorec_ime_zanra):
            podatki1 = vzorec1.groupdict()

        for vzorec2 in re.finditer(vzorec_opis_zanr):
            podatki2 = vzorec2.groupdict()
            if podatki2['opis_dolg'] is None: #Opis je takratek
                podatki2['opis'] = podatki2["opis"]
            else:
                podatki2['opis'] = podatki2["opis_dolg"]

    ###CSV za zanr
    podatkiZanr = dict()
    podatkiZanr['ime_zanra'] = html.unescape(podatki1['ime_zanra'])
    podatkiZanr['opis'] = podatki2['opis']#TODO počisti tekst?
    seznam_vseh_zanrov.append(podatkiZanr)
