import requests
import re
import orodja
#from delamocsv import slovar_url_avtorjev

vzorec_linka = re.compile("""<td width="100%" valign="top">\s*?<a class="bookTitle" itemprop="url" href="(?P<link_knjige>.*?)">\s*?<span itemprop='name'>(?P<naslov>.*?)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>""")

# poberemo vse linke do knjig z vseh 10 strani (zaenkrat samo 1.):
def zajemiKnjige():
    for stran in range(1, 2):
        print('tuki sm')
        r = requests.get('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page={}'.format(stran))
        page_source = r.text
        linki = []
        for zadetek in re.finditer(vzorec_linka, page_source):
            # če je v naslovu dvopičje, pride do napake,
            print('ah ja')
            if ':' in zadetek.groupdict()['naslov']:
                print(1)
                popravljen_naslov = zadetek.groupdict()['naslov']
                linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], popravljen_naslov.replace(':','-'))]
            #če je v naslovu slash pride do napake
            elif '/' in zadetek.groupdict()['naslov']:
                print(2)
                popravljen_naslov = zadetek.groupdict()['naslov']
                ###TODO če ima obe napaki, se nama bo naslov dvakrat vnesel v seznam
                linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], popravljen_naslov.replace('/','-'))] ###pazit morva da če ima serija 2 imeni jih ločiva
            else:
                print(3)
                linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], zadetek.groupdict()['naslov'])]
        for link in linki:
            print(link)
            #orodja.shrani_stran('https://www.goodreads.com' + link[0],'knjige/{}.html'.format(link[1])) ###link že vsebuje www.goodreads...
            orodja.shrani_stran(link[0], 'knjige/{}.html'.format(link[1]))

#zajemiKnjige()

#print(len(linki))
def zajemiAvtorje(): ###TODO za nekatere strani piše not found (6244,8164)
    for avtor in slovar_url_avtorjev.items():
        print(avtor)
        # orodja.shrani_stran('https://www.goodreads.com' + link[0],'knjige/{}.html'.format(link[1])) ###link že vsebuje www.goodreads...
        orodja.shrani_stran(avtor[1], 'avtorji/{}.html'.format(avtor[0]))

#zajemiAvtorje()
