import re
import orodja

vzorec_naslov_url_avtorja_serije = re.compile("""metacol" class="last col">\s*?<h1\sid="bookTitle"\sclass="bookTitle"\sitemprop="name">\s*(?P<naslov>.*?)\s*?(<a class="greyText" href="(?P<url_serije>.+?)">(\s|.)*?</a>)?</h1>\s*?<div id="bookAuthors" class="stacked">\s*?<span class='by smallText'>by</span>\s*?<span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja1>.*?(?P<id_avtorja1>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?(\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja2>.*?(?P<id_avtorja2>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?)?(\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja3>.*?(?P<id_avtorja3>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?)?</span>\s*?</div>\s*?<div id="bookMeta""")
vzorec_id_knjige = re.compile("""canonical" href="https://www.goodreads.com/book/show/(?P<id_knjige>\d+).*?" />""")
vzorec_ocene = re.compile("""stars staticStars"(\stitle="really liked it")?>(<span size="12x12" class="staticStar p\d\d?">.*?</span>){5}</span>\s*?<span class="value rating"><span class="average" itemprop="ratingValue">(?P<povprecna_ocena>.*?)</span>""")
vzorec_stevilo_ocen_opis = re.compile("""#other_reviews">\s*?<meta itemprop="ratingCount" content=".*?">\s*?<span class="votes value-title" title=".*?">\s*(?P<stevilo_ocen>.*?)\s*?</span>\s*?Ratings\s*?</a><span class="greyText">&nbsp;&middot;&nbsp;</span>\s+?<a class="gr-hyperlink" href="#other_reviews">\s+?<span class="count value-title" title="\d+?">\s+?.+?\s+?</span>\s+?Reviews\s+?</a>\s+?</div>\s+?<div id="descriptionContainer">\s+?<div id="description" class="readable stacked" style="right:0">\s+?<span id="freeTextContainer\d+?">(?P<opis1>.+?)</span>(\s+?<span id="freeText\d+?" style="display:none">(Alternate Cover Edition can be found <a href=".*?" rel="nofollow">here</a>.)?(<strong>\s+?<i>This is an adaptation. For the editions of the original book, see <a href=".*?" rel="nofollow">here</a></i>\s+?</strong>.<br /><br />)?(?P<opis>.+?)(</p>)?</span>\s+?<a data-text-id="\d+?" href="#" onclick)?""")
vzorec_stevilo_strani_leto = re.compile("""bookFormat">(.*?)</span>,\s*?<span itemprop="numberOfPages">(?P<stevilo_strani>\d\d\d?\d?) pages</span></div>\s*?<div class="row">\s*?Published(\s|.)*?(<nobr class="greyText">\s*?\(first published (?P<leto_izdaje>\d\d\d\d)\)\s*?</nobr>)?\s*?</div>""")
vzorec_zanri = re.compile("""stacked">\s*?<div class=" clearFloats bigBox"><div class="h2Container gradientHeaderContainer"><h2 class="brownBackground"><a href="/work/shelves/\d+?">Genres</a></h2></div><div class="bigBoxBody"><div class="bigBoxContent containerWithHeaderContent">\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr1>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr15>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr2>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr25>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr3>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr35>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr4>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr45>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr5>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr55>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr6>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr65>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr7>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr75>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr8>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr85>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr9>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr95>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr10>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr105>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr11>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr115>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?<a class="actionLink right bookPageGenreLink__seeMoreLink" href=".*?">See top shelves""")
# TODO? zajem opisov žanrov
vzorec_ISBN_serija = re.compile("""itemprop='isbn'>(?P<ISBN>(\w{10}|\d{13}))(</span>\)</span>)?\s*?</div>(\s*?</div>\s*?<div class="clearFloats">\s*?<div class="infoBoxRowTitle">Edition Language</div>\s*?<div class="infoBoxRowItem" itemprop='inLanguage'>.+</div>)?(\s*?</div>\s*?<div class="clearFloats">\s*?<div class="infoBoxRowTitle">URL</div>\s*?<div class="infoBoxRowItem">\s*?<a .*?>.*?</a>\s*?</div>)?(\s*?</div>\s*<div class="clearFloats">\s+<div class="infoBoxRowTitle">Series</div>\s+<div class="infoBoxRowItem">\s+<a href="(?P<url_serije1>/series/(?P<id_serije1>\d+)-[^"]*?)">.*?#?(?P<zaporedna_stevilka_serije1>\d\d?)?</a>)?(, <a href="(?P<url_serije2>/series/(?P<id_serije2>\d+?)-[^"]*?)">.*?#?(?P<zaporedna_stevilka_serije2>\d\d?)?</a>)?(, <a href="(?P<url_serije3>/series/(?P<id_serije3>\d+?)-[^"]*?)">.*?#?(?P<zaporedna_stevilka_serije3>\d\d?)?</a>)?(\s*,\s*<a href="/work/\d+?-[^"]*?/series">more</a>)?\s*?</div>""")

seznam_vseh_knjig = []
seznam_avtor_knjiga=[]
seznam_zanr_knjiga = []
slovar_url_avtorjev = dict()
seznam_serija_knjiga = []
slovar_url_serij = dict()
idji_knjig = set()

# mapa = orodja.datoteke("knjige/test")
def shrani_knjige(mapa, prvic='True'):
    for knjiga in mapa:
        vsebina = orodja.vsebina_datoteke(knjiga)
        print(knjiga)
        for vzorec1 in re.finditer(vzorec_naslov_url_avtorja_serije, vsebina):
            podatki1 = vzorec1.groupdict()
        for vzorec2 in re.finditer(vzorec_ocene, vsebina):
            podatki2 = vzorec2.groupdict()
        for vzorec3 in re.finditer(vzorec_stevilo_ocen_opis, vsebina):
            podatki3 = vzorec3.groupdict()
            if podatki3['opis'] is None:
                podatki3['opis'] = orodja.pocisti_niz(podatki3['opis1'])
            else:
                podatki3['opis'] = orodja.pocisti_niz(podatki3['opis'])
        for vzorec4 in re.finditer(vzorec_stevilo_strani_leto, vsebina):
            podatki4 = vzorec4.groupdict()
        for vzorec5 in re.finditer(vzorec_ISBN_serija, vsebina):
            podatki5 = vzorec5.groupdict()
        for vzorec6 in re.finditer(vzorec_zanri, vsebina):
            podatki6 = vzorec6.groupdict()
        for vzorec7 in re.finditer(vzorec_id_knjige, vsebina):
            podatki7 = vzorec7.groupdict()

        ###CSV za tabelo KNJIGA
        podatkiKnjiga = dict()
        podatkiKnjiga['naslov']=podatki1['naslov']
        podatkiKnjiga['povprecna_ocena'] = podatki2['povprecna_ocena']
        podatkiKnjiga['stevilo_ocen'] = int(re.sub('[,]','',podatki3['stevilo_ocen']))###to spremeni niz glasov v integer brez vejc
        podatkiKnjiga['opis'] = podatki3['opis']
        podatkiKnjiga['dolzina'] = podatki4['stevilo_strani']
        podatkiKnjiga['leto'] = podatki4['leto_izdaje']
        podatkiKnjiga['ISBN'] = podatki5['ISBN']
        podatkiKnjiga['id_knjige'] = podatki7['id_knjige']
        idji_knjig.add(podatkiKnjiga['id_knjige'])
        seznam_vseh_knjig.append(podatkiKnjiga)

        ###CSV za tabelo AVTORKNJIGE
        podatkiAvtor1 = dict()
        podatkiAvtor2 = dict()
        podatkiAvtor3 = dict()
        podatkiAvtor1['ISBN'] = podatki5['ISBN']
        podatkiAvtor1['id'] = podatki1['id_avtorja1']
        podatkiAvtor2['ISBN'] = podatki5['ISBN']
        podatkiAvtor2['id'] = podatki1['id_avtorja2']
        podatkiAvtor3['ISBN'] = podatki5['ISBN']
        podatkiAvtor3['id'] = podatki1['id_avtorja3']

        if podatkiAvtor2['id'] is not None:
            seznam_avtor_knjiga.extend([podatkiAvtor1, podatkiAvtor2])
            if prvic:
                slovar_url_avtorjev[podatki1['id_avtorja1']]= podatki1['url_avtorja1']
                slovar_url_avtorjev[podatki1['id_avtorja2']] = podatki1['url_avtorja2']
            if podatkiAvtor3['id'] is not None:
                seznam_avtor_knjiga.append(podatkiAvtor3)
                if prvic:
                    slovar_url_avtorjev[podatki1['id_avtorja3']] = podatki1['url_avtorja3']
        else:
            seznam_avtor_knjiga.append(podatkiAvtor1)
            if prvic:
                slovar_url_avtorjev[podatki1['id_avtorja1']] = podatki1['url_avtorja1']

        ###CSV za tabelo ZANRKNJIGE
        podatkiZanr = dict()
        podatkiZanr['ISBN']= podatki5['ISBN']
        i = 1
        while podatki6['zanr{0}'.format(str(i))] is not None:
            podatkiZanr['zanr'] =   podatki6['zanr{0}'.format(str(i))]
            seznam_zanr_knjiga.append(podatkiZanr.copy())
            if podatki6['zanr{0}5'.format(str(i))] is not None: ###NINA kaj ta if dela - včasih maš pr enih napisan žanr in njegov podžanr v isti vrstici, in zajamem dva v istem zadetku (pol sta poimenovana npr. 2 in 25)
                podatkiZanr['zanr'] = podatki6['zanr{0}5'.format(str(i))]
                seznam_zanr_knjiga.append(podatkiZanr)
            i += 1

        ###CSV za tabelo DelSerije
        podatkiSerije = dict()
        podatkiSerije['ISBN'] = podatki5["ISBN"]
        i = 1
        while i<4 and podatki5['id_serije{0}'.format(str(i))] is not None: ###TODO če je vrstni red obraten ne dela - čak, zakaj je to TODO, če dela?
            if prvic:
                slovar_url_serij[podatki5['id_serije{0}'.format(str(i))]] = podatki5['url_serije{0}'.format(str(i))]
            podatkiSerije['id_serije'] = podatki5['id_serije{0}'.format(str(i))]
            podatkiSerije['zaporedna_stevilka_serije'] = podatki5['zaporedna_stevilka_serije{0}'.format(str(i))]
            seznam_serija_knjiga.append(podatkiSerije)
            i += 1
# shrani_knjige(mapa)

