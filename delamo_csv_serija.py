from delamo_csv import idji_knjig
import re
import orodja
import copy

vzorec_ime_serije = re.compile("""head>\s*?(<script.*?/script>\s*)*<title>\s*(?P<ime>.*?) (Saga|Series )?by .*?\s*</title>""")
vzorec_knjige_v_seriji = re.compile(
    """class="bookTitle" itemprop="url" href="(?P<kratki_url>.*?(?P<id_knjige>\d+).*?)">\s*?<span itemprop='name'>(?P<naslov>.*?)\((?P<serija>.*?),? #(?P<zaporedna_st>\d+)\)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>""")

seznam_vseh_serij = []
urlji_knjig_iz_serij = []
seznam_serija_knjiga = []
# mapa_serije = orodja.datoteke("serije")
def shrani_serije(mapa):
    for serija in mapa:
        st_knjig = 0
        vsebina = orodja.vsebina_datoteke(serija)

        for vzorec in re.finditer(vzorec_ime_serije, vsebina):
            podatki_serija = vzorec.groupdict()

        for vzorec in re.finditer(vzorec_knjige_v_seriji, vsebina):
            st_knjig += 1
            knjiga = vzorec.groupdict()
            if knjiga['id_knjige'] not in idji_knjig and (knjiga['serija'] == podatki_serija['naslov']):
                naslov = re.sub('[:|/|?]', '-', knjiga['naslov'])
                urlji_knjig_iz_serij.append((knjiga['kratki_url'], naslov))
                seznam_serija_knjiga.append({'id_knjige': knjiga['id_knjige'],
                                             'id_serije': serija.split('.')[0].split('\\')[-1],
                                             'zaporedna_stevilka_serije': knjiga['zaporedna_st'])
                
        # CSV datoteka serija: - naslov se je dodal že prej
        podatki_serija['id'] = serija.split('.')[0].split('\\')[-1]
        podatki_serija['stevilo_knjig'] = st_knjig
        seznam_vseh_serij.append(podatki_serija)

                               
#shrani_serije(mapa_serije)
