import re
import orodja
import html

vzorec_id = re.compile("""avtorji.(?P<id>\d+)\.html""")
vzorec_povprecna_ocena = re.compile(
    """class="average" itemprop='ratingValue'>(?P<povprecna_ocena_avtorja>\d\.\d?\d?)""")
vzorec_zanri = re.compile(
    """<div class="dataItem">\s*<a href="(?P<url_zanr1>/genres.*?)">(?P<zanr1>.*?)</a>(, <a href="(?P<url_zanr2>/genres.*?)">(?P<zanr2>.*?)</a>)?(, <a href="(?P<url_zanr3>/genres.*?)">(?P<zanr3>.*?)</a>)?(, <a href="(?P<url_zanr4>/genres.*?)">(?P<zanr4>.*?)</a>)?(, <a href="(?P<url_zanr5>/genres.*?)">(?P<zanr5>.*?)</a>)?\s*?</div>""")
vzorec_ime_kraj_datum_rojstva = re.compile(
    """h1 class="authorName">\s*<span itemprop="name">(?P<ime>.*)<.span>\s*</h1>\s*(<h3 class="right goodreadsAuthor">Goodreads Author</h3>\s*)?(</div>\s*<br class="clear"/>\s*)?(<div class="dataTitle">Born<\/div>\s*(in )?(?P<kraj_rojstva>.*)\s*<)?((div class="dataItem" itemprop='birthDate'>\s*(?P<mesec>\w+) (?P<dan>\d{2}), (?P<leto>\d{4}))?)?""")

seznam_vseh_avtorjevih_zanrov = []
seznam_vseh_avtorjev = []
slovar_url_zanrov_od_avtorjev = dict()
#mnozica_vseh_zanrov = set()

mesci = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
         'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}


def uredi_datum(mesec, dan, leto):
    popravljen_mesec = mesci[mesec]
    popravljen_datum = leto + popravljen_mesec + dan
    return (popravljen_datum)


# mapa  = orodja.datoteke("avtorji/test")
def shrani_avtorje(mapa):
    print("shranjujem avtorje")
    for avtor in mapa:
        vsebina = orodja.vsebina_datoteke(avtor)
        print(avtor)
        for vzorec1 in re.finditer(vzorec_ime_kraj_datum_rojstva, vsebina):
            podatki1 = vzorec1.groupdict()
            # print(podatki1)
        for vzorec2 in re.finditer(vzorec_povprecna_ocena, vsebina):
            podatki2 = vzorec2.groupdict()
            # print(podatki2)
        for vzorec3 in re.finditer(vzorec_zanri, vsebina):
            podatki3 = vzorec3.groupdict()
            # print(podatki3)
        for vzorec4 in re.finditer(vzorec_id, avtor):
            podatki4 = vzorec4.groupdict()
            # print(podatki4)

        ###CSV za tabelo AVTOR
        podatkiAvtor = dict()
        podatkiAvtor['ime'] = podatki1['ime']
        podatkiAvtor['id'] = podatki4['id']
        podatkiAvtor['kraj_rojstva'] = podatki1['kraj_rojstva']
        podatkiAvtor['povprecna_ocena'] = podatki2['povprecna_ocena_avtorja']
        if podatki1['leto'] is not None:
            podatkiAvtor['datum_rojstva'] = uredi_datum(podatki1['mesec'], podatki1['dan'], podatki1['leto'])
        seznam_vseh_avtorjev.append(podatkiAvtor)

        ###CSV za tabelo AvtorZanri
        i = 1
        while i <= 5 and podatki3['zanr{0}'.format(str(i))] is not None:
            slovar_url_zanrov_od_avtorjev[html.unescape(podatki3['zanr{}'.format(str(i))])] = podatki3['url_zanr{0}'.format(str(i))]
            #mnozica_vseh_zanrov.add(html.unescape(podatki3['zanr{}'.format(str(i))]))
            seznam_vseh_avtorjevih_zanrov.append({'id': podatki4['id'], 'zanr': html.unescape(
                podatki3['zanr{0}'.format(str(i))])})  ###html.unescape premeni &amp v & in podobno
            i += 1

        #
        # if podatki3['zanr1'] is not None:
        #     mnozica_vseh_zanrov.add(html.unescape(podatki3['zanr1']))
        #     seznam_vseh_avtorjevih_zanrov.append({'id': podatki4['id'], 'zanr': html.unescape(
        #         podatki3['zanr1'])})  ###html.unescape premeni &amp v & in podobno
        #     if podatki3['zanr2'] is not None:
        #         mnozica_vseh_zanrov.add(html.unescape(podatki3['zanr2']))
        #         seznam_vseh_avtorjevih_zanrov.append({'id': podatki4['id'], 'zanr': html.unescape(podatki3['zanr2'])})
        #         if podatki3['zanr3'] is not None:
        #             mnozica_vseh_zanrov.add(html.unescape(podatki3['zanr3']))
        #             seznam_vseh_avtorjevih_zanrov.append(
        #                 {'id': podatki4['id'], 'zanr': html.unescape(podatki3['zanr3'])})
        #             if podatki3['zanr4'] is not None:
        #                 mnozica_vseh_zanrov.add(html.unescape(podatki3['zanr4']))
        #                 seznam_vseh_avtorjevih_zanrov.append(
        #                     {'id': podatki4['id'], 'zanr': html.unescape(podatki3['zanr4'])})
        #                 if podatki3['zanr5'] is not None:
        #                     mnozica_vseh_zanrov.add(html.unescape(podatki3['zanr5']))
        #                     seznam_vseh_avtorjevih_zanrov.append(
        #                         {'id': podatki4['id'], 'zanr': html.unescape(podatki3['zanr5'])})
