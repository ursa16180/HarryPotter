import requests
import re
import orodja
from delamo_csv import slovar_url_avtorjev, slovar_url_serij, slovar_url_zanrov
from delamo_csv_serija import urlji_knjig_iz_serij
from delamo_csv_avtor import slovar_url_zanrov_od_avtorjev

vzorec_linka = re.compile(
    """<td width="100%" valign="top">\s*?<a class="bookTitle" itemprop="url" href="(?P<link_knjige>.*?(?P<id>\d+).*?)">\s*?<span itemprop='name'>(?P<naslov>.*?)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>""")


def zajemi_knjige():
    """Iz spletnega seznama "What to read after Harry Potter" zajamemo url-je vseh knjig na sznamu.
    Seznam je trenutno dolg 15 strani."""

    for stran in range(16):
        r = requests.get(
            'https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page={}'.format(stran))
        page_source = r.text
        linki = []  # tu se nabirajo vsi linki do spletnih strani, ki jih moramo prebrati.
        for zadetek in re.finditer(vzorec_linka, page_source):
            # če je v naslovu dvopičje, vprašaj ali slash, pride do napake
            popravljen_naslov = re.sub('[:|/|?*]', '-', zadetek.groupdict()['naslov'])+zadetek.groupdict()['id']
            linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], popravljen_naslov)]
        for link in linki:
            # Vse html datoteke shranimo v mapo knjige
            orodja.shrani_stran(link[0], 'knjige/{}.html'.format(link[1]))


# TODO: Na git ne smeva nalagat stvari ki se same generirajo => v končni verziji ne smeva mape knjige gor loadat i guess??

def zajemi_avtorje():  ###TODO za nekatere strani piše not found (6244,8164) - neka čudna napaka, jst sm še enkrat probala in zdej dela, pa nism nč popravlala
    for avtor in slovar_url_avtorjev.items():
        print(avtor)
        orodja.shrani_stran(avtor[1], 'avtorji/{}.html'.format(avtor[0]))


def zajemi_serije():
    for serija in slovar_url_serij.items():
        print(serija)
        orodja.shrani_stran('https://www.goodreads.com' + serija[1], 'serije/{}.html'.format(serija[0]))


# urlji_knjig_iz_serij = [('/book/show/312080.Magic_or_Not_', 'Magic or Not')]
def zajemi_dodatne_knjige():
    for knjiga in urlji_knjig_iz_serij:
        print(knjiga)
        orodja.shrani_stran('https://www.goodreads.com' + knjiga[0],
                            'dodatne_knjige/{}.html'.format(knjiga[1]))  # tko bova laži vedle kere so ble naknadno


# zajemi_dodatne_knjige()

def zajemi_zanre():
    slovar_vseh_url_zanrov = {**slovar_url_zanrov_od_avtorjev, **slovar_url_zanrov}
    print(slovar_vseh_url_zanrov)
    for zanr in slovar_vseh_url_zanrov.items():
        print(zanr)
        orodja.shrani_stran('https://www.goodreads.com' + zanr[1], 'zanri/{}.html'.format(zanr[0]))
