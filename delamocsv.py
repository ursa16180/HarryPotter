import re
import orodja

vzorec_avtorja = re.compile(r'metacol" class="last col">\s*?<h1\sid="bookTitle"\sclass="bookTitle"\sitemprop'
                            r'="name">\s*(?P<naslov>.*?)\s*?(?:<a(\s|.)*?</a>)?</h1>\s*?<div id="bookAuthors"'
                            r'\sclass="stacked">\s*?<span class=\Wby smallText\W>by</span>\s*?<span itemprop='
                            r'\Wauthor\W itemscope=\W\W itemtype=\Whttp://schema.org/Person\W>\s*?<a class="'
                            r'authorName" itemprop="url" href=".*?"><span itemprop="name">(?P<avtor>.*?)</span>'
                            r'</a>( <span class=.*?</span>)?(,\s*?<a class="authorName" itemprop="url" href=".*?">'
                            r'<span itemprop="name">(?P<avtor2>.*?)</span></a>( <span class=.*?</span>)?)?\s*?'
                            r'</span>\s*?</div>\s*?<div id="bookMeta"')

# preveri alico v čudežni deželi

vzorec_ocene = re.compile(r'<span class="stars staticStars">(<span size="12x12" class="staticStar '
                          r'p\d\d?"></span>){5}</span>\s*?<span class="value rating"><span class="average" itemprop='
                          r'"ratingValue">(?P<povprecna_ocena>.*?)</span></span>\s*?<span class="greyText">&nbsp;'
                          r'&middot;&nbsp;</span>')

vzorec_stevilo_strani = re.compile(r'<span class="value-title" title="(?P<stevilo_ocen>\d+?)" itemprop="ratingCount">'
                                   r'.*?Ratings</span>\s*?</a><span class="greyText">&nbsp;&middot;&nbsp;</span>'
                                   r'\s*?<a class="actionLinkLite" href="#other_reviews">(\s|.)*?<div class="row">'
                                   r'(<span itemprop="bookFormatType">.*?</span>)?(, )?(<span itemprop="numberOfPages">'
                                   r'(?P<stevilo_strani>\d\d\d?\d?) pages</span>)?</div>\s*?'
                                   r'<div class="row">\s*?Published')

#preveri!!!!
vzorec_ISBN = re.compile(r'<div class="clearFloats">\s*?<div class="infoBoxRowTitle">Original Title</div>'
                         r'\s*?<div class="infoBoxRowItem">.*?</div>\s*?</div>\s*?<div class="clearFloats">'
                         r'\s*?<div class="infoBoxRowTitle">ISBN</div>\s*?<div class="infoBoxRowItem">.*?'
                         r'<span class="greyText">(ISBN13: <span itemprop='isbn'>(?P<ISBN>.*?)</span>)</span>\s.*?</div>'
                         )

knjige = orodja.datoteke('podatki\\knjige')
i = 0
# i nam bo nekako indeksiral knjige, saj bi sicer lahko na koncu kakšen rezultat prepisali,
# če je knjiga slučajno dobila nagrado v več kategorijah

seznam_vseh_knjig = []

for knjiga in knjige:
    #print(knjiga + str(i))
    glasovi1 = knjiga.split('-')[-1][:-5]
    glasovi = glasovi1.replace('_', '')
    vmes = knjiga.split('\\')[2].split('-')[:-1]
    leto = vmes[0]
    if len(vmes) == 2:
        zanr = vmes[1]
    else:
        zanr = vmes[1] + ' ' + vmes[2]
    print(vmes, zanr, glasovi, leto)

    vsebina = orodja.vsebina_datoteke(knjiga)

    #  sedaj imamo shranjen žanr, leto in število glasov, ostale podatke dobimo na strani o knjigi
    for vzorec1 in re.finditer(vzorec_avtorja, vsebina):
        #print('pršu v zanko')
        podatki1 = vzorec1.groupdict()
        #print('končal prvo iteracijo')
    #print('prvega sm')
    for vzorec2 in re.finditer(vzorec_ocene, vsebina):
        podatki2 = vzorec2.groupdict()
    #print('druzga sm')
    for vzorec3 in re.finditer(vzorec_stevilo_strani, vsebina):
        podatki3 = vzorec3.groupdict()

    print('zbral od knjige ' + str(i))

    podatki = podatki1

    podatki['povprečna ocena'] = podatki2['povprecna_ocena']
    podatki['št. ocen'] = podatki3['stevilo_ocen']
    podatki['št. strani'] = podatki3['stevilo_strani']
    podatki['leto'] = leto
    podatki['žanr'] = zanr
    podatki['št. glasov'] = glasovi
    podatki['id'] = i
    seznam_vseh_knjig += [podatki]

    print('en narjen ' + str(i))
    i += 1

orodja.zapisi_tabelo(seznam_vseh_knjig, ['id', 'avtor', 'naslov', 'št. strani', 'povprečna ocena',
                                         'št. ocen' , 'leto', 'žanr', 'št. glasov', 'avtor2'
                                        ], 'podatki/tabela_knjige.csv')


