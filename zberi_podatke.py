import requests
import re
import orodja

vzorec_linka = re.compile(r'<strong\s*?class=\Wuitext\s*?result\W>\s*?(?P<glasov>\d?\d?\d?,?\d?\d?\d)\s*?votes\s*?'
                          r'</strong>\s*?<div\s*?class=\WanswerWrapper\W>\s*?<div\s*?class=\Wjs-tooltip'
                          r'Trigger\s*?tooltipTrigger\W\s*?data-placement=\W\w+?\W\s*?data-resource-id=\W\d+'
                          r'\W\s*?data-resource-type=\WGCA\W>\s*?<a\s*?id="bookCover_\d+?"\s*?class="'
                          r'pollAnswer__bookLink"\s*?href="(?P<url>.*?)"><img\s*?alt=".*?"\s*?title=')
orodja.shrani_stran('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page=1', 'testna.txt', vsili_prenos=False)
##
##for stran in range(1, 15):
##    r = requests.get('https://www.goodreads.com/list/show/559.What_To_Read_After_Harry_Potter?page={}'.format(stran))
##    page_source = r.text
##    linki = []
##    for zadetek in re.finditer(vzorec_linka, stran):
##        linki += [('https://www.goodreads.com' + zadetek.groupdict()['url'], zadetek.groupdict()['glasov'])]
##    print(len(linki))
##    for par in linki:
##        link = par[0]
##        glasov = par[1]
##        orodja.shrani_stran(link, 'podatki/{}-{}-{}.html'.format(leto, zanr, glasov))
