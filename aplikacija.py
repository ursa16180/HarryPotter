#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
import copy

import hashlib

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)

skrivnost= "To je ultimativni urok za skrivanje skrivnosti. Ne povedati Hagridu. Bljuz43988asjjjdskazzzzz"

def zakodiraj_geslo(geslo):
    hashko=hashlib.md5()
    hashko.update(geslo.encode('utf-8'))
    return hashko.hexdigest()

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    return template('zacetna_stran.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik())


@post('/isci')
def iskanje_get():
    kljucne = request.POST.getall('kljucne_besede')
    parametri = copy.copy(kljucne)
    if request.forms.get('dolzinaInput') is None:
        dolzina = 0
    else:
        dolzina = int(request.forms.get('dolzinaInput'))
        parametri.append(str(dolzina) + '+ pages')
    # print(request.POST.getall('kljucne_besede'))

    zanri = request.POST.getall('zanri')
    parametri += zanri
    jeDelZbirke = request.forms.get('jeDelZbirke')
    parametri_SQL = ()
    # ~~~~~~~~~~~~~~Če so izbrane ključne besede, jih doda
    if kljucne == []:
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr, url_naslovnice FROM knjiga"
    else:
        vmesni_niz = ''
        for kljucna_beseda in kljucne:
            vmesni_niz += """ AND EXISTS (SELECT * FROM knjiga_kljucne_besede WHERE kljucna_beseda = %s AND knjiga_kljucne_besede.id_knjige=knjiga1.id_knjige)"""
            parametri_SQL += (kljucna_beseda,)
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr, url_naslovnice FROM knjiga JOIN (SELECT DISTINCT * FROM knjiga_kljucne_besede knjiga1 WHERE " + vmesni_niz[5:] + ") pomozna_tabela ON knjiga.id=pomozna_tabela.id_knjige"

    # ~~~~~~~~~~~~~~če so izbrani zanri, jih doda
    if zanri != []:
        #print(zanri)
        vmesni_niz = ''
        for zanr in zanri:
            vmesni_niz += """ AND EXISTS (SELECT * FROM zanr_knjige WHERE zanr = %s AND id_knjige=knjiga2.id_knjige)"""
            parametri_SQL += (zanr,)
        niz += " JOIN (SELECT DISTINCT * FROM zanr_knjige knjiga2 WHERE " + vmesni_niz[5:] + ") pomozna_tabela2 ON knjiga.id=pomozna_tabela2.id_knjige"
    else:
        niz += " JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige"

    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    # TODO Ali če se združi že izloči tiste ki niso v serijah?
    # TODO tukaj izbere če želi da je v zbirki ali če mu je vseeno... kaj pa če prou noče da je v zbirki?
    if jeDelZbirke is not None:
        niz += " JOIN del_serije ON knjiga.id=del_serije.id_knjige "
        parametri += ['In series']

    # ~~~~~~~~~~~~~~~Tukaj se doda avtor
    niz += " JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige JOIN avtor ON avtor_knjige.id_avtorja = avtor.id"
    # ~~~~~~~~~~~~~~Tukaj se doda pogoj o dolžini knjige
    niz += " WHERE dolzina>=%s ORDER BY knjiga.id, avtor.id"
    parametri_SQL += (dolzina,)
    cur.execute(niz, parametri_SQL)
    vse_vrstice = cur.fetchall()
    if vse_vrstice == []:
        return template('ni_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri,uporabnik = uporabnik(), parametri=parametri)
    else:
        slovar_slovarjev_knjig = {}
        for vrstica in vse_vrstice:
            id = vrstica[0]
            trenutna_knjiga = slovar_slovarjev_knjig.get(id, {'id': id, 'naslov': None, 'avtorji': set(), 'zanri': set(), 'url_naslovnice':None})
            trenutna_knjiga['naslov'] = vrstica[1]
            trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
            trenutna_knjiga['zanri'].add(vrstica[4])
            trenutna_knjiga['url_naslovnice']=vrstica[5]
            slovar_slovarjev_knjig[id] = trenutna_knjiga
        return template('izpis_knjiznih_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                        knjige=list(slovar_slovarjev_knjig.values()), stran=1, poizvedba=(niz, parametri_SQL), parametri=parametri)


@post('/avtor/:x')
def avtor(x):
    #print(x)
    cur.execute("SELECT id, ime, povprecna_ocena, datum_rojstva, kraj_rojstva FROM avtor WHERE id=%s", (x,))
    avtor = cur.fetchone()
    cur.execute("SELECT zanr FROM avtorjev_zanr WHERE id = %s", (x,))
    zanriAvtorja=cur.fetchall()
    zanriAvtorja = set([x[0] for x in  zanriAvtorja])
    if zanriAvtorja == {None}:
        zanriAvtorja = set()
    cur.execute("""SELECT knjiga.id, knjiga.naslov, zanr_knjige.zanr, serija.id, serija.ime, serija.stevilo_knjig FROM avtor_knjige 
    LEFT JOIN knjiga ON knjiga.id = avtor_knjige.id_knjige 
    LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
    LEFT JOIN del_serije ON knjiga.id = del_serije.id_knjige
    LEFT JOIN serija ON del_serije.id_serije = serija.id
    WHERE id_avtorja =%s""" , (x,))
    vrstice_knjig = cur.fetchall()
    knjige = set()
    serijeAvtorja = {}
    for vrstica in vrstice_knjig:
        id = vrstica[0]
        knjige.add((id, vrstica[1]))
        if vrstica[2] != None:
            zanriAvtorja.add(vrstica[2])
        if vrstica[3] != None:
            serijeAvtorja[vrstica[3]] = (vrstica[4], vrstica[5])
    #print(avtor, zanriAvtorja, knjige)
    return template('avtor.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                    avtor=avtor, knjige=list(knjige), zanriAvtorja=list(zanriAvtorja), serijeAvtorja=serijeAvtorja)


@post('/zanr/:x')
def zanr(x):
    #print(x)
    cur.execute("SELECT ime_zanra, opis FROM zanr WHERE ime_zanra=%s;", (x,))
    zanr = cur.fetchone()
    cur.execute("SELECT id, naslov FROM knjiga JOIN zanr_knjige ON knjiga.id = zanr_knjige.id_knjige WHERE zanr=%s ORDER BY knjiga.povprecna_ocena DESC LIMIT 50;", (x,))
    knjige = cur.fetchall()
    cur.execute("SELECT avtor.id, avtor.ime FROM avtor JOIN avtorjev_zanr ON avtor.id = avtorjev_zanr.id WHERE avtorjev_zanr.zanr=%s;", (x,))
    avtorji = cur.fetchall()
    return template('zanr.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                    zanr=zanr, knjige=knjige, avtorji=avtorji)

@post('/zbirka/:x')
def zbirka(x):
    #print(x)
    cur.execute("""SELECT serija.ime, del_serije.zaporedna_stevilka_serije, knjiga.id, knjiga.naslov, avtor.id, avtor.ime FROM serija
JOIN del_serije ON del_serije.id_serije=serija.id
JOIN knjiga ON del_serije.id_knjige = knjiga.id
JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige
JOIN avtor ON avtor_knjige.id_avtorja =  avtor.id
WHERE serija.id = %s
ORDER BY zaporedna_stevilka_serije;""", (x, ))
    # knjiga ima lahko več avtorjev, več knjig ima iste avtorje
    knjige_ponovitve = cur.fetchall()
    knjige={}
    avtorji = {}
    serija = knjige_ponovitve[0][0]
    for knjiga in knjige_ponovitve:
        knjiga_id = knjiga[2]
        avtor_id = knjiga[4]
        knjige[knjiga_id] = [knjiga_id, knjiga[3], knjiga[1]]
        avtorji[avtor_id] = [avtor_id, knjiga[5]]
    #print(cur.fetchall())
    return template('zbirka.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                    knjige=list(knjige.values()), avtorji=list(avtorji.values()), serija=serija)


@post('/knjiga/:x')
def knjiga(x):
    #print(x)
    cur.execute("""SELECT knjiga.id, isbn, naslov, dolzina, knjiga.povprecna_ocena, stevilo_ocen, leto, knjiga.opis, 
    avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, kljucna_beseda, ime_zanra, knjiga.url_naslovnice FROM knjiga
LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
LEFT JOIN serija ON serija.id=del_serije.id_serije
LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
WHERE knjiga.id =%s;""", (x,))
    vseVrstice = cur.fetchall()
    knjiga = {'id':vseVrstice[0][0],
              'isbn':vseVrstice[0][1],
              'naslov':vseVrstice[0][2],
              'dolzina':vseVrstice[0][3],
              'povprecna_ocena':vseVrstice[0][4],
              'stevilo_ocen':vseVrstice[0][5],
              'leto':vseVrstice[0][6],
              'opis':vseVrstice[0][7],
              'avtor':set(),
              'serija':set(),
              'kljucna_beseda':set(),
              'zanri':set(),
              'url_naslovnice':vseVrstice[0][15]}
    for vrstica in vseVrstice:
        knjiga['avtor'].add((vrstica[8],vrstica[9]))
        knjiga['serija'].add((vrstica[10],vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])
    #print(knjiga)
    return template('knjiga.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                    knjiga=knjiga)

@post('/kazaloAvtorja')
def kazalo_avtorja():
    cur.execute("""SELECT id, ime FROM avtor;""")
    neurejeni_avtorji = cur.fetchall()
    urejeni_avtorji = {}
    for avtor in neurejeni_avtorji:
        priimek = avtor[1].split(' ')[-1]
        crka = priimek[0]
        urejeni_avtorji[crka] = urejeni_avtorji.get(crka, []) + [(priimek, avtor)]
    for avtorji_na_crko in urejeni_avtorji.values():
        avtorji_na_crko.sort()
    avtorji = list(urejeni_avtorji.items())
    avtorji.sort()
    #print(avtorji)
    return template('kazalo_avtorjev.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(), avtorji=avtorji)


@post('/kazaloZanra')
def kazalo_zanra():
    cur.execute("""SELECT ime_zanra FROM zanr;""")
    vsi_zanri_iz_baze = cur.fetchall()
    return template('kazalo_zanrov.html', vseKljucne=vseKljucne, zanri=vsiZanri,uporabnik = uporabnik(), zanri_kazalo=vsi_zanri_iz_baze)


@post('/rezultatiIskanja')
def rezultati_iskanja():
    if request.forms.get('iskaniIzrazKnjige') != '':
        iskani_izraz = request.forms.get('iskaniIzrazKnjige')
        niz = ("""SELECT knjiga.id, knjiga.naslov, avtor.id, avtor.ime, zanr_knjige.zanr, knjiga.url_naslovnice FROM knjiga LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige LEFT JOIN avtor ON avtor_knjige.id_avtorja=avtor.id LEFT JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige WHERE CONCAT_WS('|', knjiga.naslov, knjiga.opis) LIKE %s""", ('%' + iskani_izraz + '%;',))
        cur.execute(niz[0], niz[1])
        vse_vrstice = cur.fetchall()
        if vse_vrstice != []:
            slovar_slovarjev_knjig = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutna_knjiga = slovar_slovarjev_knjig.get(id, {'id': id, 'naslov': None, 'avtorji': set(), 'zanri': set(), 'url_naslovnice':None})
                trenutna_knjiga['naslov'] = vrstica[1]
                trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
                trenutna_knjiga['zanri'].add(vrstica[4])
                trenutna_knjiga['url_naslovnice']=vrstica[5]
                slovar_slovarjev_knjig[id] = trenutna_knjiga
            return template('izpis_knjiznih_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                            knjige=list(slovar_slovarjev_knjig.values()), stran=1, poizvedba=niz, parametri=[])
    elif request.forms.get('iskaniIzrazAvtorji') != None:
        iskani_izraz = request.forms.get('iskaniIzrazAvtorji')
        niz = ("""SELECT avtor.id, avtor.ime, avtorjev_zanr.zanr FROM avtor LEFT JOIN avtorjev_zanr ON avtor.id=avtorjev_zanr.id WHERE avtor.ime LIKE %s""", ('%' + iskani_izraz + '%;',))
        cur.execute(niz[0], niz[1])
        vse_vrstice = cur.fetchall()
        if vse_vrstice != []:
            zadetki_avtorjev = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutni_avtor = zadetki_avtorjev.get(id, {'id': id, 'ime': None, 'zanri': set()})
                trenutni_avtor['ime'] = vrstica[1]
                trenutni_avtor['zanri'].add(vrstica[2])
                zadetki_avtorjev[id] = trenutni_avtor
            return template('izpis_zadetkov_avtorjev.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                            avtorji=list(zadetki_avtorjev.values()), stran=1, poizvedba=niz)
    # če sta obe polji prazni ali če ni zadetkov
    return template('ni_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(), parametri=[iskani_izraz])

@get('/izpis_zadetkov/:x')
def izpis_zadetkov(x):
    [tip, stran, niz] =  x.split('&')
    #print('Tole je cel niz')
    #print(niz)
    niz1, niz2 = niz.split(", ('")
    #print(niz1[2:-1])
    parametri_SQL = ()
    for param in niz2[:-2]. split(','):
        print(param)
        if param != '':
            if " " == param[0]:
                param = param[1:]
            print(param)
            try:
                param = int(param)
                parametri_SQL += (param,)
            except:
                if "'" == param[-1]:
                    param = param[:-1]
                if "'" == param[0]:
                    param = param[1:]
                parametri_SQL += (param,)
    #print(parametri_SQL)
    cur.execute(niz1[2:-1], parametri_SQL)
    vse_vrstice = cur.fetchall()
    if vse_vrstice == []:
        return template('ni_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(), parametri = niz2[:-3])
    else:
        if tip == 'knjiga':
            slovar_slovarjev_knjig = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutna_knjiga = slovar_slovarjev_knjig.get(id,
                                                             {'id': id, 'naslov': None, 'avtorji': set(), 'zanri': set(),
                                                              'url_naslovnice': None})
                trenutna_knjiga['naslov'] = vrstica[1]
                trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
                trenutna_knjiga['zanri'].add(vrstica[4])
                trenutna_knjiga['url_naslovnice'] = vrstica[5]
                slovar_slovarjev_knjig[id] = trenutna_knjiga
            return template('izpis_knjiznih_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(),
                            knjige=list(slovar_slovarjev_knjig.values()), stran=stran, poizvedba=niz, parametri=[])
        elif tip == 'avtor':
            zadetki_avtorjev = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutni_avtor = zadetki_avtorjev.get(id, {'id': id, 'ime': None, 'zanri': set()})
                trenutni_avtor['ime'] = vrstica[1]
                trenutni_avtor['zanri'].add(vrstica[2])
                zadetki_avtorjev[id] = trenutni_avtor
            return template('izpis_zadetkov_avtorjev.html', vseKljucne=vseKljucne, zanri=vsiZanri,uporabnik = uporabnik(),
                            avtorji=list(zadetki_avtorjev.values()), stran=stran, poizvedba=niz)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~UPORABNIKI~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def uporabnik():
    #Preveri če je kdo vpisan
    vzdevek = request.get_cookie('vzdevek', secret=skrivnost)
    if vzdevek is not None: #Preveri če uporabnik obsataja
        cur.execute("SELECT id, vzdevek, dom FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
        vrstica = cur.fetchone()
        if vrstica is not None: #TODO ali možno?
            return vrstica
    else:
        return [0, None, None]


@get("/odjava")
def odjava():
    response.delete_cookie('vzdevek', path='/', domain='localhost')
    redirect('/')

@post("/prijava")
def prijava_uporabnika():
    print("PRIJAVAAAAAA")
    #(vzdevek, dom) = uporabnik()

    vzdevek = request.forms.vzdevek
    geslo =request.forms.geslo
    #print(vzdevek, geslo)
    #zakodiraj_geslo(request.forms.geslo)
    # Preverimo če je bila pravilna prijava
    if vzdevek is not None:
        cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
        if cur.fetchone() is None:
            #TODO TA VZDEVEK NE OBSTAJA
            print('prazno')
            return template("registracija.html", vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(),
                            sporocilo='This username does not yet exist. You may create a new user here.')
    if vzdevek is not None and geslo is not None:
        cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s AND geslo=%s;", (vzdevek, geslo))
        if cur.fetchone() is None:
            #TODO geslo ni pravilno
            return template("zacetna_stran.html", vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik()) #TODO geslo ni pravilno
        else:
            response.set_cookie('vzdevek', vzdevek, path='/', secret= skrivnost)#TODO secret=secret)
            id = uporabnik()[0]
            return template("zacetna_stran.html", vseKljucne=vseKljucne, zanri=vsiZanri,
                            uporabnik=uporabnik())
            #redirect('/profile/' + str(id))

@get('/registracija')
def odpri_registracijo():
    return template('registracija.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik(), sporocilo=None)

@post('/registracija')
def registriraj_uporabnika():
    (id, vzdevek, dom) = uporabnik()

    vzdevek = request.forms.vzdevek
    geslo1 = request.forms.geslo
    geslo2 = request.forms.geslo2
    email= request.forms.email
    dom= request.forms.dom #TODO request.forms.get("dom")
    spol=request.forms.spol #TODO request.forms.get("spol")
    if spol == "Witch":
        spol = "Female"
    else:
        spol = "Male"
    print(vzdevek, geslo1, email, dom, spol)

    cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s;",(vzdevek,))
    if cur.fetchone() is not None:
        return template("registracija.html", vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(), sporocilo='Unfortunately this nickname is taken. Good one though.')
    elif not geslo1 == geslo2:
        return template("registracija.html", vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(), sporocilo='The passwords do not match. Check them again.')
    print(vzdevek, geslo1, email, dom, spol)
    cur.execute("INSERT INTO uporabnik (vzdevek, geslo, email, dom, spol) VALUES(%s,%s,%s,%s,%s);", (vzdevek, geslo1, email, dom, spol))
    #cur.query()
    conn.commit()
    #TODO: odpri neko stran, kjer ti pove da si se registriral in se zdej lahko vpišeš tukaj
    return template('zacetna_stran.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik = uporabnik())

@post('/profile/:x')
def profil(x):
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrane ON knjiga.id= prebrane.id_knjige WHERE prebrane.id_uporabnika=%s;", (uporabnik()[0],))
    prebrane = cur.fetchall()

    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN zelje ON knjiga.id= zelje.id_knjige WHERE zelje.id_uporabnika=%s;", (uporabnik()[0],))
    zelje=cur.fetchall()

    return template('profile.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(), prebrane=prebrane, zelje=zelje)

@get('/spremeni_profil')
def spremeni():
    print(uporabnik()[0])
    cur.execute("SELECT spol FROM uporabnik WHERE id=%s;", (uporabnik()[0],))
    spol = cur.fetchone()[0]
    print(spol)
    if spol == 'Female':
        spol = 'Witch'
    else:
        spol = 'Wizard'
    return template('spremeni_profil.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(), spol=spol, sporocilo=None)

@post('/spremeni_profil')
def spremeni():
    #TODO!!!!!!
    (id, vzdevek, dom) = uporabnik()
    #
    geslo_staro = request.forms.geslo_trenutno
    geslo_novo = request.forms.novo_geslo
    print(geslo_novo == '')
    geslo_novo2 = request.forms.novo_geslo2
    novi_dom = request.forms.dom  # TODO request.forms.get("dom")
    novi_spol = request.forms.spol  # TODO request.forms.get("spol")
    # Preveri, ali lahko sploh karkoli spreminja:
    cur.execute("SELECT geslo FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
    pravo_geslo = cur.fetchone()[0]
    if pravo_geslo != geslo_staro:
        return template("spremeni_profil.html", vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(),
                        sporocilo='The current password you typed is not correct, try again.', spol=novi_spol)
    elif geslo_novo == '':
        geslo_novo = geslo_staro
    elif geslo_novo != geslo_novo2:
        return template("spremeni_profil.html", vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(),
                         sporocilo='The new passwords do not match. Check them again.', spol=novi_spol)
    if novi_spol == "Witch":
        novi_spol = "Female"
    elif novi_spol == "Wizard":
        novi_spol = "Male"
    cur.execute("UPDATE uporabnik SET geslo = %s, dom = %s, spol = %s WHERE id = %s;",
                (geslo_novo, novi_dom, novi_spol, id))
    conn.commit()
    cur.execute(
        "SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrane ON knjiga.id= prebrane.id_knjige WHERE prebrane.id_uporabnika=%s;",
        (uporabnik()[0],))
    prebrane = cur.fetchall()

    cur.execute(
        "SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN zelje ON knjiga.id= zelje.id_knjige WHERE zelje.id_uporabnika=%s;",
        (uporabnik()[0],))
    zelje = cur.fetchall()

    return template('profile.html', vseKljucne=vseKljucne, zanri=vsiZanri, uporabnik=uporabnik(), prebrane=prebrane,
                    zelje=zelje)


######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
# conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# ~~~~~~~~~~~~~~~~~~~~~Pridobi 50 najpogostejših žanrov
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
LIMIT 50;""")

zanri_iz_baze=cur.fetchall()
vsiZanri=[]
for vrstica in zanri_iz_baze:
    vsiZanri.append(vrstica[1])
vsiZanri.sort()

#~~~~~~~~~~~~~~~~~~~~~Pridobi vse skupine ključnih besed
cur.execute("""SELECT skupina, pojem FROM kljucna_beseda JOIN knjiga_kljucne_besede ON pojem=kljucna_beseda
GROUP BY pojem;""")
kljucne_iz_baze = cur.fetchall()
vseKljucne = {}
for vrstica in kljucne_iz_baze:
    skupina = vrstica[0]
    vseKljucne[skupina] = vseKljucne.get(skupina, list()) + [vrstica[1]]

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=True)