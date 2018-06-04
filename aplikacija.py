#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    cur.execute("SELECT id, naslov, dolzina FROM knjiga ORDER BY naslov LIMIT 20")
    kljucne = {'Magija': ['Magic', 'Flying'], 'Bitja': ['Centaur', 'Troll']}
    zanri = {'Childrens', 'Fantasy', 'Young Adult'}
    # TODO: Tole dela, ampak izjemno počasi. Al sm pa samo jst mela v tistem trenutku slab internet :)
    return template('tabela_knjig.html', knjige=cur, vseKljucne=kljucne, zanri=zanri)


@post('/isci')
def iskanje_get():
    dolzina = int(request.forms.get('dolzinaInput'))
    # print(request.POST.getall('kljucne_besede'))
    kljucne = request.POST.getall('kljucne_besede')
    zanri = request.POST.getall('zanri')
    jeDelZbirke = request.forms.get('jeDelZbirke')

    #~~~~~~~~~~~~~~Če so izbrane ključne besede, jih doda
    if kljucne == []:
        niz ="SELECT DISTINCT id, naslov, dolzina FROM knjiga"
    else: # TODO: išči po ključnih besedah - ni lepo ampak mislim da dela
        vmesni_niz=" AND ".join('EXISTS (SELECT * FROM knjiga_kljucne_besede WHERE kljucna_beseda = \'%s\' AND knjiga_kljucne_besede.id_knjige=knjiga1.id_knjige)' %(kljucna_beseda) for kljucna_beseda in kljucne)
        niz = "SELECT DISTINCT id, naslov, dolzina FROM knjiga JOIN (SELECT DISTINCT * FROM knjiga_kljucne_besede knjiga1 WHERE " + vmesni_niz +") pomozna_tabela ON knjiga.id=pomozna_tabela.id_knjige"

    #~~~~~~~~~~~~~~če so izbrani zanri, jih doda
    if zanri !=[]:
        print(zanri)
        vmesni_niz = " AND ".join(
            'EXISTS (SELECT * FROM zanr_knjige WHERE zanr = \'%s\' AND id_knjige=knjiga2.id_knjige)' % (zanr) for zanr in zanri)
        niz += " JOIN (SELECT DISTINCT * FROM zanr_knjige knjiga2 WHERE " + vmesni_niz + ") pomozna_tabela2 ON knjiga.id=pomozna_tabela2.id_knjige"

    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    #TODO Ali če se združi že izloči tiste ki niso v serijah?
    # TODO tukaj izbere če želi da je v zbirki ali če mu je vseeno... kaj pa če prou noče da je v zbirki?
    if jeDelZbirke is not None:
        niz +=" JOIN del_serije ON knjiga.id=del_serije.id_knjige "
        #cur.execute("SELECT id, naslov, dolzina FROM knjiga WHERE dolzina>=%s", [dolzina])

    # ~~~~~~~~~~~~~~Tukaj se doda pogoj o dolžini knjige
    niz +=" WHERE dolzina>=%s" %dolzina

    cur.execute(niz)
    print(niz)
    return template('izpis_knjig.html', dolzina=dolzina, knjige=cur, kljucne=kljucne, zanri=zanri)


# @get('/transakcije/:x/')
# def transakcije(x):
#     cur.execute("SELECT * FROM transakcija WHERE znesek > %s ORDER BY znesek, id", [int(x)])
#     return template('transakcije.html', x=x, transakcije=cur)
#
#
# @get('/dodaj_transakcijo')
# def dodaj_transakcijo():
#     return template('dodaj_transakcijo.html', znesek='', racun='', opis='', napaka=None)
#
#
# @post('/dodaj_transakcijo')
# def dodaj_transakcijo_post():
#     znesek = request.forms.znesek
#     racun = request.forms.racun
#     opis = request.forms.opis
#     try:
#         cur.execute("INSERT INTO transakcija (znesek, racun, opis) VALUES (%s, %s, %s)",
#                     (znesek, racun, opis))
#     except Exception as ex:
#         return template('dodaj_transakcijo.html', znesek=znesek, racun=racun, opis=opis,
#                         napaka='Zgodila se je napaka: %s' % ex)
#     redirect("/")

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
# conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=True)
