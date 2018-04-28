import requests
import re
import orodja

vzorec_linka = re.compile("""<td width="100%" valign="top">\s*?<a class="bookTitle" itemprop="url" href="(?P<link_knjige>.*?)">\s*?<span itemprop='name'>(?P<naslov>.*?)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>""")

#vzorec_linka2 = re.compile(r"<td width=\"100%\" valign=\"top\">\s*?<a class=\"bookTitle\" itemprop=\"url\" href=\"(?P<link_knjige>.*?)\">\s*?<span itemprop='name'>(?P<naslov>.*?)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>\s*?<span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>\s*?<a class=\"authorName\" itemprop=\"url\" href=\".*?\"><span itemprop=\"name\">.*?</span></a>")
#orodja.shrani_stran('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page=1', 'testna.txt', vsili_prenos=False)

# poberemo vse linke do knjig z vseh 10 strani (zaenkrat samo 1.):
for stran in range(1, 2):
    r = requests.get('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page={}'.format(stran))
    page_source = r.text
    linki = []
    for zadetek in re.finditer(vzorec_linka, page_source):
        print('ah ja')
# če je v naslovu dvopičje, pride do napake, 
        if ':' in zadetek.groupdict()['naslov']:
            popravljen_naslov = zadetek.groupdict()['naslov']
            linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], popravljen_naslov.replace(':','-'))]
#če je v naslovu slash pride do napake
        elif '/' in zadetek.groupdict()['naslov']:
            popravljen_naslov = zadetek.groupdict()['naslov']
            ###TODO če ima obe napaki, se nama bo naslov dvakrat vnesel v seznam
            linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], popravljen_naslov.replace('/','-'))] ###pazit morva da če ima serija 2 imeni jih ločiva
        else:
            linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], zadetek.groupdict()['naslov'])]
    for link in linki:
        print(link)
        #orodja.shrani_stran('https://www.goodreads.com' + link[0],'knjige/{}.html'.format(link[1])) ###link že vsebuje www.goodreads...
        orodja.shrani_stran(link[0], 'knjige/{}.html'.format(link[1]))

print(len(linki))
