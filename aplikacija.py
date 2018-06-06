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
    # TODO: Tole dela, ampak izjemno počasi. Al sm pa samo jst mela v tistem trenutku slab internet :)
    return template('tabela_knjig.html', knjige=cur, vseKljucne=vseKljucne, zanri=vsiZanri)


@post('/isci')
def iskanje_get():
    dolzina = int(request.forms.get('dolzinaInput'))
    # print(request.POST.getall('kljucne_besede'))
    kljucne = request.POST.getall('kljucne_besede')
    zanri = request.POST.getall('zanri')
    jeDelZbirke = request.forms.get('jeDelZbirke')

    # ~~~~~~~~~~~~~~Če so izbrane ključne besede, jih doda
    if kljucne == []:
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.ime, zanr FROM knjiga"
    else:  # TODO: išči po ključnih besedah - ni lepo ampak mislim da dela
        vmesni_niz = " AND ".join(
            'EXISTS (SELECT * FROM knjiga_kljucne_besede WHERE kljucna_beseda = \'%s\' AND knjiga_kljucne_besede.id_knjige=knjiga1.id_knjige)' % (
                kljucna_beseda) for kljucna_beseda in kljucne)
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.ime, zanr FROM knjiga JOIN (SELECT DISTINCT * FROM knjiga_kljucne_besede knjiga1 WHERE " + vmesni_niz + ") pomozna_tabela ON knjiga.id=pomozna_tabela.id_knjige"

    # ~~~~~~~~~~~~~~če so izbrani zanri, jih doda
    if zanri != []:
        print(zanri)
        vmesni_niz = " AND ".join(
            'EXISTS (SELECT * FROM zanr_knjige WHERE zanr = \'%s\' AND id_knjige=knjiga2.id_knjige)' % (zanr) for zanr
            in zanri)
        niz += " JOIN (SELECT DISTINCT * FROM zanr_knjige knjiga2 WHERE " + vmesni_niz + ") pomozna_tabela2 ON knjiga.id=pomozna_tabela2.id_knjige"
    else:
        niz += " JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige"

    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    # TODO Ali če se združi že izloči tiste ki niso v serijah?
    # TODO tukaj izbere če želi da je v zbirki ali če mu je vseeno... kaj pa če prou noče da je v zbirki?
    if jeDelZbirke is not None:
        niz += " JOIN del_serije ON knjiga.id=del_serije.id_knjige "
        # cur.execute("SELECT id, naslov, dolzina FROM knjiga WHERE dolzina>=%s", [dolzina])

    # ~~~~~~~~~~~~~~~Tukaj se doda avtor
    niz += " JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige JOIN avtor ON avtor_knjige.id_avtorja = avtor.id"
    # ~~~~~~~~~~~~~~Tukaj se doda pogoj o dolžini knjige
    niz += " WHERE dolzina>=%s ORDER BY knjiga.id, avtor.ime" % dolzina

    cur.execute(niz)
    vse_vrstice = cur.fetchall()
    idiji_knjig = set()
    seznam_slovarjev_knjig = []
    for vrstica in vse_vrstice:  # TODO to dela prepočasi!
        # print(vrstica)
        idiji_knjig.add(vrstica[0])
    for id in list(idiji_knjig):
        slovar = {'id': id, 'naslov': None, 'avtorji': set(), 'zanri': set()}
        for vrstica in vse_vrstice:
            if vrstica[0] == id:
                slovar['naslov'] = vrstica[1]
                slovar['avtorji'].add(vrstica[2])
                slovar['zanri'].add(vrstica[3])
        slovar['avtorji'] = list(slovar['avtorji']) #TODO ali množica ni kul?
        slovar['zanri'] = list(slovar['zanri'])
        seznam_slovarjev_knjig.append(slovar)

    return template('izpis_knjiznih_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    knjige=seznam_slovarjev_knjig)  # , dolzina=dolzina, kljucne=kljucne, zanri=zanri)


@post('/avtor/:x')
def avtor(x):
    print(x)
    cur.execute("SELECT * FROM avtor WHERE ime='%s'"%x)
    return template('avtor.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    avtor=cur.fetchone())

@post('/zanr/:x')
def zanr(x):
    print(x)
    cur.execute("SELECT * FROM zanr WHERE ime_zanra='%s'"%x)
    return template('zanr.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    zanr=cur.fetchone())

@post('/knjiga/:x')
def knjiga(x):
    print(x)
    cur.execute("SELECT * FROM knjiga WHERE naslov='%s'"%x)
    return template('knjiga.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    knjiga=cur.fetchone())




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

#~~~~~~~~~~~~~~~~~~~~~Pridobi 50 najpogostejših žanrov
cur.execute("""SELECT sum(stevilo) AS stevilo_skupaj, ime_zanra FROM (
 SELECT count(*) AS stevilo, ime_zanra FROM zanr AS zanr1
 JOIN zanr_knjige ON zanr1.ime_zanra=zanr_knjige.zanr
 GROUP BY ime_zanra
 UNION ALL
 SELECT count(*) AS stevilo, ime_zanra FROM zanr AS zanr2
 JOIN avtorjev_zanr ON zanr2.ime_zanra=avtorjev_zanr.zanr
 GROUP BY ime_zanra
) AS tabela
GROUP BY ime_zanra
ORDER BY stevilo_skupaj DESC
LIMIT 50""")

klucni2=cur.fetchall()
vsiZanri=[]
for vrstica in klucni2:
    vsiZanri.append(vrstica[1])
vsiZanri.sort()
vseKljucne = {'Magija': ['Magic', 'Flying'], 'Bitja': ['Centaur', 'Troll']}
#vsiZanri = {'Childrens', 'Fantasy', 'Young Adult'}

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=True)

