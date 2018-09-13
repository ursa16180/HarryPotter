import re
import orodja
import html
import copy

vzorec_naslov_url_avtorja_serije = re.compile(
    """metacol" class="last col">\s*?<h1\sid="bookTitle"\sclass="bookTitle"\sitemprop="name">\s*(?P<naslov>.*?)\s*?(<a class="greyText" href="(?P<url_serije>.+?)">(\s|.)*?</a>)?</h1>\s*?<div id="bookAuthors" class="stacked">\s*?<span class='by smallText'>by</span>\s*?<span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja1>.*?(?P<id_avtorja1>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?(\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja2>.*?(?P<id_avtorja2>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?)?(\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja3>.*?(?P<id_avtorja3>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?)?</span>\s*?</div>\s*?<div id="bookMeta""")
vzorec_ocene = re.compile(
    """stars staticStars"(\stitle="really liked it")?>(<span size="12x12" class="staticStar p\d\d?">.*?</span>){5}</span>\s*?<span class="value rating"><span class="average" itemprop="ratingValue">(?P<povprecna_ocena>.*?)</span>""")
vzorec_stevilo_ocen_opis = re.compile(
    """ratingCount" content=".*?">\s*?<span class="votes value-title" title=".*?">\s*(?P<stevilo_ocen>.*?)\s*?</span>\s*?Ratings?\s*?</a><span class="greyText">&nbsp;&middot;&nbsp;</span>\s+?<a class="gr-hyperlink" href="#other_reviews">\s+?<span class="count value-title" title="\d+?">\s+?.+?\s+?</span>\s+?Reviews?\s+?</a>\s+?</div>\s+?<div id="descriptionContainer">\s+?(<div id='choiceBadge'>\s*?<a (class="choiceWinnerBadge20\d\d" )?href="https://www.goodreads.com/choiceawards/best-books-20\d\d">(<img src=".*?" alt=".*?" />)?</a>\s+?</div>\s+?)?<div id="description" class="readable stacked" style="right:0">\s+?<span id="freeTextContainer\d+?">(Alternate Cover Edition can be found <a href=".*?" rel="nofollow">here</a>.)?(<strong>\s+?<i>This is an adaptation. For the editions of the original book, see <a href=".*?" rel="nofollow">here</a></i>\s+?</strong>.<br /><br />)?(.*?[Aa]lternate [Cc]overs? ([Ee]ditions?)?.*?(here</a>\s*and.*?)?here</a>\.?)?(Also see: [Aa]lternate [Cc]overs? ([Ee]ditions? )?for this ISBN \[ACE\] ACE)?(.*?[Aa]lternate [Cc]over [Ee]ditions? (for )?(ASIN \w+?|ISBN \d+ \(.+?\))\.?<.*?>)?(.*?[Aa]lternate [Cc]overs? [Ee]dition.*?\d+?</a>)?(?P<opis1>.+?)</span>(\s+?<span id="freeText\d+?" style="display:none">(Alternate Cover Edition can be found <a href=".*?" rel="nofollow">here</a>.)?(<strong>\s+?<i>This is an adaptation. For the editions of the original book, see <a href=".*?" rel="nofollow">here</a></i>\s+?</strong>.<br /><br />)?(.*?[Aa]lternate [Cc]overs? ([Ee]ditions?)?.*?(here</a>\s*and.*?)?here</a>\.?)?(Also see: [Aa]lternate [Cc]overs? ([Ee]ditions? )?for this ISBN \[ACE\] ACE)?(.*?[Aa]lternate [Cc]over [Ee]ditions? (for )?(ASIN \w+?|ISBN \d+ \(.+?\))\.?<.*?>)?(.*?[Aa]lternate [Cc]overs? [Ee]dition.*?\d+?</a>)?(?P<opis>[\s\S]+?)(</p>)?</span>\s+?<a data-text-id="\d+?" href="#" onclick)?""")
vzorec_stevilo_strani_leto = re.compile(
    """bookFormat">(.*?)</span>,\s*?<span itemprop="numberOfPages">(?P<stevilo_strani>\d\d\d?\d?) pages</span></div>\s*?<div class="row">\s*?Published(\s|.)*?(<nobr class="greyText">\s*?\(first published (?P<leto_izdaje>\d\d\d\d)\)\s*?</nobr>)?\s*?</div>""")
vzorec_ISBN = re.compile("""itemprop='isbn'>(?P<ISBN>(\d{13}|\w{10}))""")
vzorec_zanri = re.compile(
    """stacked">\s*?<div class=" clearFloats bigBox"><div class="h2Container gradientHeaderContainer"><h2 class="brownBackground"><a href="/work/shelves/\d+?">Genres</a></h2></div><div class="bigBoxBody"><div class="bigBoxContent containerWithHeaderContent">\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr1>/genres/.*?)">(?P<zanr1>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr15>.*?)">(?P<zanr15>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr2>/genres/.*?)">(?P<zanr2>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr25>.*?)">(?P<zanr25>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr3>/genres/.*?)">(?P<zanr3>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr35>.*?)">(?P<zanr35>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr4>/genres/.*?)">(?P<zanr4>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr45>.*?)">(?P<zanr45>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr5>/genres/.*?)">(?P<zanr5>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr55>.*?)">(?P<zanr55>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr6>/genres/.*?)">(?P<zanr6>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr65>.*?)">(?P<zanr65>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr7>/genres/.*?)">(?P<zanr7>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr75>.*?)">(?P<zanr75>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr8>/genres/.*?)">(?P<zanr8>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr85>.*?)">(?P<zanr85>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr9>/genres/.*?)">(?P<zanr9>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr95>.*?)">(?P<zanr95>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr10>/genres/.*?)">(?P<zanr10>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr105>.*?)">(?P<zanr105>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr11>/genres/.*?)">(?P<zanr11>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href="(?P<url_zanr115>.*?)">(?P<zanr115>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?<a class="actionLink right bookPageGenreLink__seeMoreLink" href=".*?">See top shelves""")
vzorec_id_knjige = re.compile("""canonical" href="https://www.goodreads.com/book/show/(?P<id_knjige>\d+).*?" />""")
vzorec_serija = re.compile(
    """BoxRowTitle">Series</div>\s+<div class="infoBoxRowItem">\s+<a href="(?P<url_serije1>/series/(?P<id_serije1>\d+)-[^"]*?)">.*?#?(?P<zaporedna_stevilka_serije1>\d\d?)?</a>(, <a href="(?P<url_serije2>/series/(?P<id_serije2>\d+?)-[^"]*?)">.*?#?(?P<zaporedna_stevilka_serije2>\d\d?)?</a>)?(, <a href="(?P<url_serije3>/series/(?P<id_serije3>\d+?)-[^"]*?)">.*?#?(?P<zaporedna_stevilka_serije3>\d\d?)?</a>)?(\s*,\s*<a href="/work/\d+?-[^"]*?/series">more</a>)?\s*</div>""")
vzorec_jezik = re.compile("""inLanguage'>(?P<jezik>.+?)</div>""")

vzorec_naslovnica = re.compile(
    """<div class="bookCoverPrimary">\s+?(<a rel="nofollow" itemprop="image" href=".+?"><img id="coverImage" alt=".+?" src="(?P<url_naslovnice>.+?))?(<div class="noCoverMediumContainer">\s+?<img title=".+?" id=".+?" src="(?P<url_prazne>.+?))?\.jpg""")

seznam_vseh_knjig = []
seznam_tujih_knjig = []
seznam_avtor_knjiga = []
seznam_zanr_knjiga = []
slovar_url_avtorjev = dict()
seznam_serija_knjiga = []
slovar_url_serij = dict()
idji_knjig = set()
slovar_url_zanrov = dict()
dodaj_ze_znanim_serijam = []

def shrani_knjige(mapa, prvic='True'):
    for knjiga in mapa:
        vsebina = orodja.vsebina_datoteke(knjiga)
        print(knjiga)
        podatki1 = {'naslov': 'Untitled', 'id_avtorja1': None, 'url_avtorja1': None,
                    'id_avtorja2': None, 'url_avtorja2': None,
                    'id_avtorja3': None, 'url_avtorja3': None}
        podatki2 = {'povprecna_ocena': None}
        podatki3 = {'opis': None, 'stevilo_ocen': '0'}
        podatki4 = {'leto_izdaje': None, 'stevilo_strani': None}
        podatki5 = {'ISBN': None}
        podatki6 = {'zanr1': None}
        podatki7 = {'id_knjige': None}
        podatki8 = {'url_serije1': None, 'url_serije2': None, 'url_serije3': None,
                    'id_serije1': None, 'id_serije2': None, 'id_serije3': None,
                    'zaporedna_stevilka_serije1': None, 'zaporedna_stevilka_serije2': None,
                    'zaporedna_stevilka_serije3': None}
        podatki9 = {'jezik': 'English'}
        podatki10 = {'url_naslovnice': None, 'url_prazne': None}

        for vzorec1 in re.finditer(vzorec_naslov_url_avtorja_serije, vsebina):
            podatki1 = vzorec1.groupdict()
        for vzorec2 in re.finditer(vzorec_ocene, vsebina):
            podatki2 = vzorec2.groupdict()
        for vzorec3 in re.finditer(vzorec_stevilo_ocen_opis, vsebina):
            podatki3 = vzorec3.groupdict()
            if podatki3['opis'] is None:
                podatki3['opis'] = html.unescape(orodja.pocisti_niz(podatki3['opis1']))
            else:
                podatki3['opis'] = html.unescape(orodja.pocisti_niz(podatki3['opis']))
        for vzorec4 in re.finditer(vzorec_stevilo_strani_leto, vsebina):
            podatki4 = vzorec4.groupdict()
        for vzorec5 in re.finditer(vzorec_ISBN, vsebina):
            podatki5 = vzorec5.groupdict()
        for vzorec6 in re.finditer(vzorec_zanri, vsebina):
            podatki6 = vzorec6.groupdict()
        for vzorec7 in re.finditer(vzorec_id_knjige, vsebina):
            podatki7 = vzorec7.groupdict()
        for vzorec8 in re.finditer(vzorec_serija, vsebina):
            podatki8 = vzorec8.groupdict()
        for vzorec9 in re.finditer(vzorec_jezik, vsebina):
            podatki9 = vzorec9.groupdict()
        for vzorec10 in re.finditer(vzorec_naslovnica, vsebina):
            podatki10 = vzorec10.groupdict()

        if podatki9['jezik'] == 'English':  # Če knjiga ni angleška, se ne sme dodati na noben csv
            ###CSV za tabelo KNJIGA
            podatkiKnjiga = dict()
            podatkiKnjiga['naslov'] = html.unescape(podatki1['naslov'])
            podatkiKnjiga['stevilo_ocen'] = int(
                re.sub('[,]', '', podatki3['stevilo_ocen']))  ###to spremeni niz glasov v integer brez vejc
            podatkiKnjiga['vsota_ocen'] = podatki2['povprecna_ocena'] * podatki_knjiga['stevilo_ocen']
            podatkiKnjiga['opis'] = podatki3['opis']
            podatkiKnjiga['dolzina'] = podatki4['stevilo_strani']
            podatkiKnjiga['leto'] = podatki4['leto_izdaje']
            podatkiKnjiga['ISBN'] = podatki5['ISBN']
            podatkiKnjiga['id'] = podatki7['id_knjige']
            if podatki10['url_naslovnice'] is not None:
                podatkiKnjiga['url_naslovnice'] = podatki10['url_naslovnice']+'.jpg'
            else:
                podatkiKnjiga['url_naslovnice'] = podatki10['url_prazne']+'.jpg'
            idji_knjig.add(podatki7['id_knjige'])
            seznam_vseh_knjig.append(podatkiKnjiga)

            ###CSV za tabelo AVTORKNJIGE
            podatkiAvtor1 = dict()
            podatkiAvtor2 = dict()
            podatkiAvtor3 = dict()
            podatkiAvtor1['id_knjige'] = podatki7['id_knjige']
            podatkiAvtor1['id_avtorja'] = podatki1['id_avtorja1']
            podatkiAvtor2['id_knjige'] = podatki7['id_knjige']
            podatkiAvtor2['id_avtorja'] = podatki1['id_avtorja2']
            podatkiAvtor3['id_knjige'] = podatki7['id_knjige']
            podatkiAvtor3['id_avtorja'] = podatki1['id_avtorja3']

            if podatkiAvtor2['id_avtorja'] is not None:
                seznam_avtor_knjiga.extend([podatkiAvtor1, podatkiAvtor2])
                slovar_url_avtorjev[podatki1['id_avtorja1']] = podatki1['url_avtorja1']
                slovar_url_avtorjev[podatki1['id_avtorja2']] = podatki1['url_avtorja2']
                if podatkiAvtor3['id_avtorja'] is not None:
                    seznam_avtor_knjiga.append(podatkiAvtor3)
                    slovar_url_avtorjev[podatki1['id_avtorja3']] = podatki1['url_avtorja3']
            else:
                seznam_avtor_knjiga.append(podatkiAvtor1)
                slovar_url_avtorjev[podatki1['id_avtorja1']] = podatki1['url_avtorja1']

            ###CSV za tabelo ZANRKNJIGE
            podatkiZanr = dict()
            podatkiZanr['id_knjige'] = podatki7['id_knjige']
            i = 1
            zanri_te_knjige = []
            while podatki6['zanr{0}'.format(str(i))] is not None:
                podatkiZanr['zanr'] = html.unescape(podatki6['zanr{0}'.format(str(i))])
                slovar_url_zanrov[html.unescape(podatki6['zanr{0}'.format(str(i))])] = podatki6[
                    'url_zanr{0}'.format(str(i))]
                if podatkiZanr not in zanri_te_knjige:
                    zanri_te_knjige.append(podatkiZanr.copy())
                if podatki6['zanr{0}5'.format(str(i))] is not None:
                    podatkiZanr['zanr'] = html.unescape(podatki6['zanr{0}5'.format(str(i))])
                    slovar_url_zanrov[html.unescape(podatki6['zanr{0}5'.format(str(i))])] = podatki6[
                        'url_zanr{0}5'.format(str(i))]
                    if podatkiZanr not in zanri_te_knjige:
                        zanri_te_knjige.append(podatkiZanr.copy())
                i += 1
            for x in zanri_te_knjige:
                seznam_zanr_knjiga.append(x)

            ###CSV za tabelo DelSerije
            podatkiSerije = dict()
            podatkiSerije['id_knjige'] = podatki7['id_knjige']
            i = 1
            while i < 4 and podatki8['id_serije{0}'.format(str(i))] is not None:
                if prvic:
                    slovar_url_serij[podatki8['id_serije{0}'.format(str(i))]] = podatki8['url_serije{0}'.format(str(i))]
                podatkiSerije['id_serije'] = copy.copy(podatki8['id_serije{0}'.format(str(i))])
                podatkiSerije['zaporedna_stevilka_serije'] = copy.copy(
                    podatki8['zaporedna_stevilka_serije{0}'.format(str(i))])
                if prvic:
                    seznam_serija_knjiga.append(podatkiSerije.copy())
                else:
                    dodaj_ze_znanim_serijam.append(podatkiSerije.copy())
                i += 1

        else:
            seznam_tujih_knjig.append(podatki7['id_knjige'])

# mapa = orodja.datoteke("knjige")
# shrani_knjige(mapa)
#
# mapa_dodatne_knjige = orodja.datoteke("dodatne_knjige")
# shrani_knjige(mapa_dodatne_knjige, prvic=False)
# orodja.zapisi_tabelo(seznam_vseh_knjig,
#                      ['id', 'ISBN', 'naslov', 'dolzina', 'povprecna_ocena', 'stevilo_ocen', 'leto', 'opis'],
#                      'podatki/knjiga.csv')

# orodja.zapisi_tabelo(seznam_zanr_knjiga, ['id_knjige', 'zanr'], 'podatki/zanr_knjige.csv')
