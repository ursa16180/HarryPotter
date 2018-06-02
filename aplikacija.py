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
    # TODO: Tole dela, ampak izjemno počasi. Al sm pa samo jst mela v tistem trenutku slab internet :)
    return template('tabela_knjig.html', knjige=cur, vseKljucne=kljucne)


@post('/isci')
def iskanje_get():
    dolzina = int(request.forms.get('dolzinaInput'))
    # print(request.POST.getall('kljucne_besede'))
    kljucne = request.POST.getall('kljucne_besede')
    jeDelZbirke = request.forms.get('jeDelZbirke')
    # TODO: išči po ključnih besedah
    if jeDelZbirke is None:  # TODO tukaj izbere če želi da je v zbirki ali če mu je vseeno... kaj pa če prou noče da je v zbirki?
        cur.execute("SELECT id, naslov, dolzina FROM knjiga WHERE dolzina>=%s", [dolzina])
    else:
        cur.execute(
            "SELECT id, naslov, dolzina FROM knjiga JOIN del_serije ON knjiga.id=del_serije.id_knjige WHERE dolzina>=%s",
            [dolzina])

    return template('izpis_knjig.html', dolzina=dolzina, knjige=cur, kljucne=kljucne)


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
