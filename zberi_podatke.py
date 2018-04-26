import requests
import re
import orodja

vzorec_linka = re.compile(r"""<td width="100%" valign="top">\s*?
                          <a class="bookTitle" itemprop="url" href="(?P<link_knjige>.*?)">\s*?
                          <span itemprop='name'>(?P<naslov>.*?)</span>\s*?</a>\s*?<br/>\s*?
                          <span class='by smallText'>by</span>\s*?
                          <span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>\s*?
                          <a class="authorName" itemprop="url" href=".*?"><span itemprop="name">
                          .*?</span></a>""")

vzorec_linka2 = re.compile(r"<td width=\"100%\" valign=\"top\">\s*?<a class=\"bookTitle\" itemprop=\"url\" href=\"(?P<link_knjige>.*?)\">\s*?<span itemprop='name'>(?P<naslov>.*?)</span>\s*?</a>\s*?<br/>\s*?<span class='by smallText'>by</span>\s*?<span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>\s*?<a class=\"authorName\" itemprop=\"url\" href=\".*?\"><span itemprop=\"name\">.*?</span></a>")
# orodja.shrani_stran('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page=1', 'testna.txt', vsili_prenos=False)

# poberemo vse linke do knjig z vseh 10 srani (zaenkrat samo 1.):
for stran in range(1, 2):
    r = requests.get('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page={}'.format(stran))
    page_source = r.text
    linki = []
    for zadetek in re.finditer(vzorec_linka2, page_source):
        # print('ah ja')
        print(zadetek.groupdict())
        linki += [('https://www.goodreads.com' + zadetek.groupdict()['link_knjige'], zadetek.groupdict()['naslov'])]
# če je v naslovu dvopičje, pride do napake
        if ':' in zadetek.groupdict()['naslov']:
            print(zadetek.groupdict()['naslov'])
    #for link in linki:
    #    orodja.shrani_stran(link[0], 'knjige/{}.html'.format(link[1]))

