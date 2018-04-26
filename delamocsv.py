import re
import orodja

vzorec_naslov_url_avtorja = re.compile("""Authors" class="stacked">\s+?<span class='by smallText'>by</span>\s+?<span itemprop='author' itemscope='' itemtype='http://schema\.org/Person'>\s(<div class=("|')authorName__container("|')>\s?)?<a class="authorName" itemprop="url" href="(?P<url_avtorja1>.+?)"><span itemprop="name">\D+?</span></a>(\s<span class="greyText">\(Goodreads Author\)</span>)?(\s*?<span class="authorName greyText smallText role">.+?</span>)?(,(\s*?</div>\s*?<div class=("|')authorName__container("|')>)?\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja2>.+?)"><span itemprop="name">\D+?</span></a>(\s<span class="greyText">\(Goodreads Author\)</span>)?(\s?<span class="authorName greyText smallText role">.+?</span>)?)?((\s?</div>\s?<div class=("|')authorName__container("|')>)?\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja3>.+?)"><span itemprop="name">\D+?</span></a>(\s<span class="greyText">\(Goodreads Author\)</span>)? (<span class="authorName greyText smallText role">.+?</span>)?)?(\s*?</div>)?\s*?</span>\s+?</div>\s+?<div id="bookMeta""")

vzorec_ocene = re.compile("""stars staticStars"(\stitle="really liked it")?>(<span size="12x12" class="staticStar p\d\d?">.*?</span>){5}</span>\s*?<span class="value rating"><span class="average" itemprop="ratingValue">(?P<povprecna_ocena>.*?)</span></span>\s*?<span class="greyText">&nbsp;&middot;&nbsp;</span>""")

vzorec_stevilo_ocen = re.compile("""#other_reviews\">\s*?<meta itemprop=\"ratingCount\" content=\".*?\">\s*?<span class=\"votes value-title\" title=\".*?\">\s*?(?P<stevilo_ocen>.*?)\s*?</span>\s*?Ratings\s*?</a><span class=\"greyText\">&nbsp;&middot;&nbsp;</span>""")

vzorec_stevilo_strani_leto = re.compile("""bookFormat">(.*?)</span>,\s*?<span itemprop="numberOfPages">(?P<stevilo_strani>\d\d\d?\d?) pages</span></div>\s*?<div class="row">\s*?Published(\s|.)*?(<nobr class="greyText">\s*?\(first published (?P<leto_izdaje>\d\d\d\d)\)\s*?</nobr>)?\s*?</div>\s*?<div class="buttons">\s*?<a id="bookDataBoxShow" class="left inter""")

vzorec_ISBN = re.compile("""<div class="clearFloats">\s*?<div class="infoBoxRowTitle">ISBN</div>\s*?<div class="infoBoxRowItem">\s*?\d+?\s*?<span class="greyText">\(ISBN13: <span itemprop='isbn'>(?P<ISBN>\d+?)</span>\)</span>\s.*?</div>""")

#vzorec_opis

#vzorec_url_serije

#vzorec_url_avtorja



knjige = orodja.datoteke("knjige") #/test")
i = 0
# i nam bo nekako indeksiral knjige, saj bi sicer lahko na koncu kakšen rezultat prepisali,
# če je knjiga slučajno dobila nagrado v več kategorijah

seznam_vseh_knjig = []
for knjiga in knjige:
    vsebina = orodja.vsebina_datoteke(knjiga)
    print(knjiga)
    for vzorec1 in re.finditer(vzorec_avtorja, vsebina):
        podatki1 = vzorec1.groupdict()
        #print(podatki1)
    print('prvega sm')
    for vzorec2 in re.finditer(vzorec_ocene, vsebina):
        podatki2 = vzorec2.groupdict()
        #print(podatki2)
    print('druzga sm')
    for vzorec3 in re.finditer(vzorec_stevilo_strani_leto, vsebina):
        #print('najdu vzorec3')
        podatki3 = vzorec3.groupdict()
    print('tretji je')
    for vzorec4 in re.finditer(vzorec_ISBN, vsebina):
        podatki4 = vzorec4.groupdict()
        print(podatki4)
    
#
#     print('zbral od knjige ' + str(i))
#
#     podatki = podatki1
#
#     podatki['povprečna ocena'] = podatki2['povprecna_ocena']
#     podatki['št. ocen'] = podatki3['stevilo_ocen']
#     podatki['št. strani'] = podatki3['stevilo_strani']
#     podatki['leto'] = leto
#     podatki['žanr'] = zanr
#     podatki['št. glasov'] = glasovi
#     podatki['id'] = i
#     seznam_vseh_knjig += [podatki]
#
#     print('en narjen ' + str(i))
#     i += 1

#orodja.zapisi_tabelo(seznam_vseh_knjig, ['id', 'avtor', 'naslov', 'št. strani', 'povprečna ocena',
#                                         'št. ocen' , 'leto', 'žanr', 'št. glasov', 'avtor2'
#                                        ], 'podatki/tabela_knjige.csv')





