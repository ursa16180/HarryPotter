from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
from operator import itemgetter

import hashlib

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)

skrivnost = "To je ultimativni urok za skrivanje skrivnosti. Ne povedati Hagridu. Bljuz43988asjjjdskazzzzz"


def zakodiraj_geslo(geslo):
    hashko = hashlib.md5()
    hashko.update(geslo.encode('utf-8'))
    return hashko.hexdigest()


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    return template('zacetna_stran.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik())


@post('/book/:x')
def knjiga(x):
    cur.execute(  # SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis,
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
        avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, pojem, ime_zanra, 
        knjiga.url_naslovnice FROM knjiga
        LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
        LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
        LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
        LEFT JOIN serija ON serija.id=del_serije.id_serije
        LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
        LEFT JOIN kljucna_beseda ON knjiga_kljucna_beseda.id_knjige = kljucna_beseda.id 
        LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
        LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
        WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()

    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    if trenutni_uporabnik[1] is None:
        prebrano = False
        zelja = False
    else:
        cur.execute("SELECT id_knjige FROM prebrana_knjiga WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        prebrano = len(cur.fetchall()) > 0
        cur.execute("SELECT id_knjige FROM wishlist WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        zelja = len(cur.fetchall()) > 0

        if not prebrano:
            request.forms.get('')

    # ~~~~~~~~~~~~~~~~~~ OCENE ~~~~~~~~~~~~~~~~~~~~~~~~~

    if prebrano:
        cur.execute("SELECT ocena FROM prebrana_knjiga WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        stara_ocena = cur.fetchone()
        stara_ocena = stara_ocena[0]
        nova_ocena = request.forms.get('ocena')
        if stara_ocena is not None:
            # knjigo je uporabnik že ocenil, preverimo, ali je oceno spremenil:
            if nova_ocena is None:
                nova_ocena = stara_ocena
            elif stara_ocena != int(nova_ocena):
                cur.execute("UPDATE prebrana_knjiga SET ocena = %s WHERE id_knjige = %s AND id_uporabnika = %s;",
                            (nova_ocena, knjiga['id'], trenutni_uporabnik[0]))
                nova_vsota_ocen = knjiga['vsota_ocen'] + int(nova_ocena) - stara_ocena
                cur.execute("UPDATE knjiga SET vsota_ocen = %s WHERE id = %s;",
                            (nova_vsota_ocen, knjiga['id']))
                conn.commit()
            ocena_uporabnika = int(nova_ocena)
        else:
            if nova_ocena is not None:
                nova_ocena = int(nova_ocena)
                # uporabnik je knjigo na novo ocenil
                cur.execute("UPDATE prebrana_knjiga SET ocena = %s WHERE id_knjige = %s AND id_uporabnika = %s;",
                           (nova_ocena, knjiga['id'], trenutni_uporabnik[0]))
                cur.execute("UPDATE knjiga SET vsota_ocen = %s, stevilo_ocen = %s WHERE id = %s;",
                            (knjiga['vsota_ocen'] + nova_ocena, knjiga['stevilo_ocen'] + 1, knjiga['id']))
                conn.commit()
                ocena_uporabnika = nova_ocena
            else:
                ocena_uporabnika = None
    else:
        # uporabnik knjige še ni prebral, ali nihče ni vpisan
        ocena_uporabnika = None
    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=ocena_uporabnika, prebrano=prebrano, zelja=zelja)


@get('/author/:x')
def avtor(x):
    cur.execute("SELECT id, ime, povprecna_ocena, datum_rojstva, kraj_rojstva FROM avtor WHERE id=%s", (x,))
    avtor = cur.fetchone()
    cur.execute("SELECT id_zanra FROM avtorjev_zanr WHERE id_avtorja = %s", (x,))
    zanri_avtorja = cur.fetchall()
    zanri_avtorja = set([x[0] for x in zanri_avtorja])
    if zanri_avtorja == {None}:
        zanri_avtorja = set()
    cur.execute("""SELECT knjiga.id, knjiga.naslov, zanr_knjige.id_zanra, serija.id, serija.ime, serija.stevilo_knjig 
    FROM avtor_knjige 
    LEFT JOIN knjiga ON knjiga.id = avtor_knjige.id_knjige 
    LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
    LEFT JOIN del_serije ON knjiga.id = del_serije.id_knjige
    LEFT JOIN serija ON del_serije.id_serije = serija.id
    WHERE id_avtorja =%s""", (x,))
    vrstice_knjig = cur.fetchall()
    knjige = set()
    serije_avtorja = {}
    for vrstica in vrstice_knjig:
        id = vrstica[0]
        knjige.add((id, vrstica[1]))
        if vrstica[2] is not None:
            zanri_avtorja.add(vrstica[2])
        if vrstica[3] is not None:
            serije_avtorja[vrstica[3]] = (vrstica[4], vrstica[5])
    return template('avtor.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    avtor=avtor, knjige=list(knjige), zanriAvtorja=list(zanri_avtorja), serijeAvtorja=serije_avtorja)


@get('/genre/:x')
def zanr(x):
    cur.execute("SELECT ime_zanra, opis FROM zanr WHERE ime_zanra=%s;", (x,))
    zanr = cur.fetchone()
    cur.execute("SELECT id, naslov, knjiga.vsota_ocen, knjiga.stevilo_ocen FROM knjiga JOIN zanr_knjige "
                "ON knjiga.id = zanr_knjige.id_knjige WHERE id_zanra=%s ", (x,))
    knjige = cur.fetchall()
    for knjiga in knjige:
        if knjiga[3] == 0:
            knjiga[2] = 0
        else:
            knjiga[2] = knjiga[2]/knjiga[3]

    cur.execute("SELECT avtor.id, avtor.ime FROM avtor JOIN avtorjev_zanr ON avtor.id = avtorjev_zanr.id_avtorja "
                "WHERE avtorjev_zanr.zanr=%s ORDER BY avtor.povprecna_ocena DESC LIMIT 50;", (x,))
    avtorji = cur.fetchall()
    return template('zanr.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    zanr=zanr, knjige=sorted(knjige, key=itemgetter(2), reverse=True)[:50], avtorji=avtorji)


@get('/series/:x')
@post('/series/:x')
def zbirka(x):
    cur.execute("""SELECT serija.ime, del_serije.zaporedna_stevilka_serije, knjiga.id, knjiga.naslov, avtor.id, avtor.ime, knjiga.url_naslovnice FROM serija
        JOIN del_serije ON del_serije.id_serije=serija.id
        JOIN knjiga ON del_serije.id_knjige = knjiga.id
        JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige
        JOIN avtor ON avtor_knjige.id_avtorja =  avtor.id
        WHERE serija.id = %s
        ORDER BY zaporedna_stevilka_serije;""", (x, ))
    # knjiga ima lahko več avtorjev, več knjig ima iste avtorje
    knjige_ponovitve = cur.fetchall()
    knjige = {}
    avtorji = {}
    serija = knjige_ponovitve[0][0]
    for knjiga in knjige_ponovitve:
        knjiga_id = knjiga[2]
        avtor_id = knjiga[4]
        knjige[knjiga_id] = [knjiga_id, knjiga[3], knjiga[1], knjiga[6]]
        avtorji[avtor_id] = [avtor_id, knjiga[5]]
    return template('zbirka.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    knjige=list(knjige.values()), avtorji=list(avtorji.values()), serija=serija)


@post('/all_authors')
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
    return template('kazalo_avtorjev.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), avtorji=avtorji)


@post('/all_genres')
def kazalo_zanra():
    cur.execute("""SELECT ime_zanra FROM zanr;""")
    vsi_zanri_iz_baze = cur.fetchall()
    return template('kazalo_zanrov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), zanri_kazalo=vsi_zanri_iz_baze)


@post('/search/')
@post('/search/<dolzina>/<kljucne>/<zanri>/<je_del_zbirke>/<stran:int>')
def iskanje_get(dolzina=200, kljucne='[]', zanri='[]', je_del_zbirke='Either way', stran=0):
    stran = int(stran)
    dolzina = int(dolzina)
    kljucne_v_delu = []
    if kljucne != '[]':
        for kljucna_string in kljucne[1:-1].split(', '):
            kljucne_v_delu.append(kljucna_string[1:-1])
        kljucne = kljucne_v_delu
    else:
        kljucne = []
    if zanri != '[]':
        zanri_v_delu = []
        for zanr_string in zanri[1:-1].split(', '):
            zanri_v_delu.append(zanr_string[1:-1])
        zanri = zanri_v_delu
    else:
        zanri = []
    na_stran = 10
    offset = stran * na_stran

    dobljena_dolzina = request.forms.get('dolzinaInput')
    if dobljena_dolzina is not None:
        dolzina = dobljena_dolzina
    dobljene_kljucne = request.POST.getall('kljucne_besede')
    if dobljene_kljucne != []:
        kljucne = dobljene_kljucne
    dobljeni_zanri = request.POST.getall('zanri')
    if dobljeni_zanri != []:
        zanri = dobljeni_zanri
    dobljene_zbirke = request.forms.get('zbirka')
    if dobljene_zbirke is not None:
        je_del_zbirke = dobljene_zbirke
    parametri_sql = ()
    parametri = []
    # ~~~~~~~~~~~~~~~Tukaj se doda avtor
    niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, url_naslovnice, " \
          "vsota_ocen, stevilo_ocen FROM knjiga " \
          "JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige " \
          "JOIN avtor ON avtor_knjige.id_avtorja = avtor.id"
    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    if je_del_zbirke == 'Yes':
        niz += " WHERE knjiga.id IN (SELECT id_knjige FROM del_serije) AND"
        parametri += ['Part of series']
    elif je_del_zbirke == 'No':
        parametri += ['Not part of series']
        niz += " WHERE knjiga.id NOT IN (SELECT id_knjige FROM del_serije) AND"
    else:
        niz += " WHERE"
    # ~~~~~~~~~~~~~ Tukaj se doda pogoj o dolžini knjige
    niz += " dolzina>=%s"
    parametri_sql += (dolzina,)
    parametri.append(str(dolzina) + ' pages')
    # ~~~~~~~~~~~~~~ Če so izbrane ključne besede, jih doda
    if kljucne != []:
        vmesni_niz = ''
        for kljucna_beseda in kljucne:
            vmesni_niz += """ AND (knjiga.id, %s) IN (
                SELECT id_knjige, id_kljucne_besede FROM knjiga_kljucne_besede)"""
            parametri_sql += (kljucna_beseda,)
            cur.execute('SELECT pojem FROM kljucna_beseda WHERE id = %s', (kljucna_beseda,))
            parametri += cur.fetchone()
        niz += vmesni_niz
    # ~~~~~~~~~~~~~~ če so izbrani zanri, jih doda
    if zanri != []:
        vmesni_niz = ''
        for zanr in zanri:
            vmesni_niz += """ AND (knjiga.id, %s) IN (
                SELECT id_knjige, id_zanra FROM zanr_knjige)"""
            cur.execute('SELECT ime_zanra FROM zanr WHERE id = %s', (zanr,))
            parametri += cur.fetchone()
            parametri_sql += (zanr,)
        niz += vmesni_niz
    niz += " ORDER BY knjiga.id, avtor.id"
    cur.execute(niz, parametri_sql)
    vse_vrstice = cur.fetchall()
    if vse_vrstice == []:
        return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                        uporabnik=uporabnik(), parametri=parametri)
    else:
        #knjiga.id, naslov, avtor.id, avtor.ime, url_naslovnice, vsota_ocen, stevilo_ocen
        slovar_slovarjev_knjig = {}
        for vrstica in vse_vrstice:
            id = vrstica[0]
            trenutna_knjiga = slovar_slovarjev_knjig.get(id, {'id': id, 'naslov': None, 'avtorji': set(),
                                                              'zanri': set(), 'url_naslovnice': None})
            trenutna_knjiga['naslov'] = vrstica[1]
            trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
            trenutna_knjiga['url_naslovnice'] = vrstica[4]
            if vrstica[6] != 0:
                trenutna_knjiga['povprecna_ocena'] = vrstica[5] / vrstica[6]
            else:
                trenutna_knjiga['povprecna_ocena'] = 0
            slovar_slovarjev_knjig[id] = trenutna_knjiga
        for id_knjige in slovar_slovarjev_knjig.keys():
            cur.execute("SELECT id, ime_zanra FROM zanr "
                        "JOIN zanr_knjige ON id_zanra=id "
                        "WHERE id_knjige=%s", (id_knjige,))
            zanri_knjige = cur.fetchall()
            slovar_slovarjev_knjig[id_knjige]['zanri'] = zanri_knjige
        vse_knjige = sorted(list(slovar_slovarjev_knjig.values()), key=itemgetter('povprecna_ocena'), reverse=True)
        stevilo_knjig = len(vse_knjige)
        st_strani = stevilo_knjig // 10 + 1
        if stevilo_knjig % 10 == 0:
            st_strani -= 1
        return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        knjige=vse_knjige[offset: offset + na_stran], stran=stran, iskane_dolzine=dolzina,
                        iskane_kljucne=kljucne, iskani_zanri=zanri, iskano_zbirka=je_del_zbirke, parametri=parametri,
                        ima_naslednjo=stran+1 < st_strani, ima_prejsnjo=stran != 0, st_strani=st_strani,
                        st_zadetkov=stevilo_knjig, veliki_mali='veliki')

def poisci_kombinacije(besede):
    if besede == []:
        return []
    prva_beseda = besede[0]
    if len(besede) == 1:
        return [prva_beseda, prva_beseda[0].upper() + prva_beseda[1:]]
    kombinacije = []
    for kombinacija in poisci_kombinacije(besede[1:]):
        kombinacije += [prva_beseda + ' ' + kombinacija]
        kombinacije += [prva_beseda[0].upper() + prva_beseda[1:] + ' ' + kombinacija]
    return kombinacije

@get('/search_results_books/<iskani_izraz>/')
@post('/search_results_books/')
@post('/search_results_books/<iskani_izraz>/<stran>')
def rezultati_iskanja_knjiga(iskani_izraz="You haven't searched for any keyword.", stran=0):
    stran = int(stran)
    na_stran = 10
    offset = stran * na_stran
    dobljen_izraz = request.forms.get('iskaniIzrazKnjige')
    if dobljen_izraz is not None:
        iskani_izraz = dobljen_izraz
    if iskani_izraz != '':
        nizi = [('% ' + iskani_izraz + ' %',), ('% ' + iskani_izraz[0].upper() + iskani_izraz[1:] + ' %',),
                ('% ' + iskani_izraz + 's %',), ('% ' + iskani_izraz[0].upper() + iskani_izraz[1:] + 's %',)]
        besede = iskani_izraz.split(' ')
        if len(besede) > 1:
            vse_moznosti = poisci_kombinacije(besede)
            for izraz in vse_moznosti:
                nizi += [('% ' + izraz + ' %',)]

        vse_vrstice = []
        for niz in nizi:
            cur.execute("SELECT knjiga.id, knjiga.naslov, avtor.id, avtor.ime, knjiga.url_naslovnice, "
                        "knjiga.stevilo_ocen, knjiga.vsota_ocen FROM knjiga LEFT JOIN avtor_knjige "
                        "ON knjiga.id=avtor_knjige.id_knjige LEFT JOIN avtor ON avtor_knjige.id_avtorja=avtor.id "
                        "WHERE knjiga.opis LIKE %s;", niz)
            nove_vrstice1 = cur.fetchall()
            vse_vrstice += nove_vrstice1
        cur.execute("SELECT knjiga.id, knjiga.naslov, avtor.id, avtor.ime, knjiga.url_naslovnice, "
                    "knjiga.stevilo_ocen, knjiga.vsota_ocen FROM knjiga LEFT JOIN avtor_knjige "
                    "ON knjiga.id=avtor_knjige.id_knjige LEFT JOIN avtor ON avtor_knjige.id_avtorja=avtor.id "
                    "WHERE knjiga.naslov LIKE %s;",
                    ('%' + iskani_izraz[0].upper() + iskani_izraz[1:] + '%',))
        nove_vrstice2 = cur.fetchall()
        vse_vrstice += nove_vrstice2
        if vse_vrstice != []:
            slovar_slovarjev_knjig = {}
            for vrstica in vse_vrstice:
                id_knjige = vrstica[0]
                trenutna_knjiga = slovar_slovarjev_knjig.get(id_knjige, {'id': id_knjige, 'naslov': None,
                                                                         'avtorji': set(), 'zanri': set(),
                                                                         'url_naslovnice': None})
                trenutna_knjiga['naslov'] = vrstica[1]
                trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
                trenutna_knjiga['url_naslovnice'] = vrstica[4]
                trenutna_knjiga['stevilo_ocen'] = vrstica[5]
                if vrstica[5] != 0:
                    trenutna_knjiga['povprecna_ocena'] = vrstica[6]/vrstica[5]
                else:
                    trenutna_knjiga['povprecna_ocena'] = 0
                slovar_slovarjev_knjig[id_knjige] = trenutna_knjiga
            for id_knjige in slovar_slovarjev_knjig.keys():
                cur.execute("SELECT id, ime_zanra FROM zanr "
                            "JOIN zanr_knjige ON id_zanra=id "
                            "WHERE id_knjige=%s", (id_knjige,))
                zanri_knjige = cur.fetchall()
                slovar_slovarjev_knjig[id_knjige]['zanri'] = zanri_knjige
            vse_knjige =sorted(list(slovar_slovarjev_knjig.values()), key=itemgetter('povprecna_ocena'), reverse=True)
            st_zadetkov = len(vse_knjige)
            st_strani = st_zadetkov//10 + 1
            if st_zadetkov % 10 == 0:
                st_strani -= 1
            return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), knjige=vse_knjige[offset: offset + na_stran],
                            stran=stran, parametri=[iskani_izraz], iskani_izraz_knjiga=iskani_izraz, st_zadetkov=st_zadetkov,
                            st_strani=st_strani, ima_naslednjo=stran+1 < st_strani, ima_prejsnjo=stran != 0,
                            veliki_mali='mali')
    return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), parametri=[iskani_izraz])


@post('/search_results_authors/')
@post('/search_results_authors/<iskani_izraz>/<stran>')
def rezultati_iskanja_avtor(iskani_izraz="You haven't searched for any author.", stran=0):
    stran = int(stran)
    na_stran = 10
    offset = na_stran * stran

    dobljeni_izraz = request.forms.get('iskaniIzrazAvtorji')
    if dobljeni_izraz is not None:
        iskani_izraz = dobljeni_izraz
    if iskani_izraz != '':
        iskani_izraz = iskani_izraz.title()
        nizi = [("""SELECT avtor.id, avtor.ime, zanr.ime_zanra, avtor.povprecna_ocena, zanr.id FROM avtor 
        LEFT JOIN avtorjev_zanr ON avtor.id=avtorjev_zanr.id_avtorja 
        LEFT JOIN zanr ON zanr.id = avtorjev_zanr.id_zanra
        WHERE avtor.ime LIKE %s """, ('%' + iskani_izraz + '%', ))]
        vse_vrstice = []
        for niz in nizi:
            cur.execute(niz[0], niz[1])
            vse_vrstice += cur.fetchall()
        if vse_vrstice != []:
            zadetki_avtorjev = {}
            for vrstica in vse_vrstice:
                id_avtorja = vrstica[0]
                trenutni_avtor = zadetki_avtorjev.get(id_avtorja, {'id': id_avtorja, 'ime': None, 'zanri': set()})
                trenutni_avtor['ime'] = vrstica[1]
                trenutni_avtor['zanri'].add(vrstica[2])
                trenutni_avtor['povprecna_ocena']  = vrstica[3]
                zadetki_avtorjev[id_avtorja] = trenutni_avtor
            vsi_avtorji = sorted(list(zadetki_avtorjev.values()), key=itemgetter('povprecna_ocena'))
            st_zadetkov = len(vsi_avtorji)
            st_strani = st_zadetkov// 10 + 1
            if st_zadetkov%10 == 0:
                st_strani -= 1
            return template('izpis_zadetkov_avtorjev.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), avtorji=vsi_avtorji[offset:offset + na_stran], stran=stran,
                            iskani_izraz_avtor=iskani_izraz, st_zadetkov=st_zadetkov,
                            st_strani=st_strani, ima_naslednjo=stran + 1 < st_strani, ima_prejsnjo=stran != 0)
    # če je polje prazno ali če ni zadetkov
    return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), parametri=[iskani_izraz])



@post('/add_wishlist/:x')
def dodaj_zeljo(x):
    cur.execute(  # SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis,
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
        avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, pojem, ime_zanra, 
        knjiga.url_naslovnice FROM knjiga
        LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
        LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
        LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
        LEFT JOIN serija ON serija.id=del_serije.id_serije
        LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
        LEFT JOIN kljucna_beseda ON knjiga_kljucne_besede.id_kljucne_besede = kljucna_beseda.id
        LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
        LEFT JOIN zanr ON zanr_knjige.id_zanra = zanr.id
        WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()

    cur.execute("""SELECT * FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s;""", (trenutni_uporabnik[0], x))
    zelja = len(cur.fetchall()) > 0
    if zelja:
        return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                        knjiga=knjiga, ocena=None, prebrano=False, zelja=True)
    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~


    cur.execute("""INSERT INTO wishlist (id_uporabnika, id_knjige) VALUES (%s,%s)""", (trenutni_uporabnik[0], x))
    conn.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=False, zelja=True)


@post('/remove_wishlist/:x')
def odstrani_zeljo(x):
    cur.execute(
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
        avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, pojem, ime_zanra, 
        knjiga.url_naslovnice FROM knjiga
        LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
        LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
        LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
        LEFT JOIN serija ON serija.id=del_serije.id_serije
        LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
        LEFT JOIN kljucna_beseda ON knjiga_kljucne_besede.id_kljucne_besede = kljucna_beseda.id
        LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
        LEFT JOIN zanr ON zanr_knjige.id_zanra = zanr.id
        WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()
    cur.execute("""SELECT * FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s;""", (trenutni_uporabnik[0], x))
    zelja = len(cur.fetchall()) > 0
    if not zelja:
        return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                        knjiga=knjiga, ocena=None, prebrano=False, zelja=False)
    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""DELETE FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s""", (trenutni_uporabnik[0], x))
    conn.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=False, zelja=False)


@post('/read/:x')
def prebral(x):
    cur.execute(
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
        avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, pojem, ime_zanra, 
        knjiga.url_naslovnice FROM knjiga
        LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
        LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
        LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
        LEFT JOIN serija ON serija.id=del_serije.id_serije
        LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
        LEFT JOIN kljucna_beseda ON knjiga_kljucne_besede.id_kljucne_besede = kljucna_beseda.id
        LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
        LEFT JOIN zanr ON zanr_knjige.id_zanra = zanr.id
        WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()
    cur.execute("""SELECT * FROM prebrana_knjiga WHERE id_uporabnika = %s AND id_knjige = %s;""", (trenutni_uporabnik[0], x))
    prebrano = len(cur.fetchall()) > 0
    if prebrano:
        return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                        knjiga=knjiga, ocena=None, prebrano=True, zelja=False)
    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""DELETE FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s;
    INSERT INTO prebrana_knjiga (id_uporabnika, id_knjige, ocena) VALUES (%s, %s, %s)""", (trenutni_uporabnik[0], x, trenutni_uporabnik[0], x, None))

    conn.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=True, zelja=False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~UPORABNIKI~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def uporabnik():
    # Preveri če je kdo vpisan
    vzdevek = request.get_cookie('vzdevek', secret=skrivnost)
    if vzdevek is not None:  # Preveri če uporabnik obsataja
        cur.execute("SELECT id, vzdevek, dom FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
        vrstica = cur.fetchone()
        if vrstica is not None:  # TODO ali možno?
            return vrstica
    else:
        return [0, None, None]


@get("/sign_out")
def odjava():
    response.delete_cookie('vzdevek', path='/', domain='localhost')
    redirect('/')


@post("/sign_in")
def prijava_uporabnika():
    vzdevek = request.forms.vzdevek
    geslo = zakodiraj_geslo(request.forms.geslo)
    # Preverimo če je bila pravilna prijava
    if vzdevek is not None:
        cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
        if cur.fetchone() is None:
            return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                            sporocilo='This username does not yet exist. You may create a new user here.',
                            email='', username='', house='Gryffindor', sex='Witch')
    if vzdevek is not None and geslo is not None:
        cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s AND geslo=%s;", (vzdevek, geslo))
        if cur.fetchone() is None:
            return template("prijava.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                            sporocilo='Password you have entered is not correct. Try again.')
        else:
            response.set_cookie('vzdevek', vzdevek, path='/', secret=skrivnost)
            # id = uporabnik()[0]
            # TODO: ko tukaj kličeva naslednjo stran, cookie še ni nastavljen in je prva stran še nepobarvana, zato
            # je trenutno narejen uporabnik na roke.
            cur.execute("SELECT id, vzdevek, dom FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
            vrstica = cur.fetchone()
            return template("zacetna_stran.html", vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=vrstica)
            # redirect('/profile/' + str(id))


@get('/sign_up')
def odpri_registracijo():
    return template('registracija.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(), sporocilo=None,
                    email='', username='', house='Gryffindor', sex='Witch')


@post('/sign_up')
def registriraj_uporabnika():
    vzdevek = request.forms.vzdevek
    geslo1 = request.forms.geslo
    geslo2 = request.forms.geslo2
    email = request.forms.email
    dom = request.forms.dom  # TODO request.forms.get("dom")
    spol = request.forms.spol  # TODO request.forms.get("spol")
    if spol == "Witch":
        spol = "Female"
    else:
        spol = "Male"

    cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
    nov_vzdevek = cur.fetchone() is None
    cur.execute("SELECT email FROM uporabnik WHERE email=%s;", (email,))
    nov_mail = cur.fetchone() is None
    if not nov_vzdevek:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='Unfortunately this nickname is taken. Good one though.',
                        email=email, username='', house=dom, sex=spol)
    if not nov_mail:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='Unfortunately someone has already used this email to sign up to our library.',
                        username=vzdevek, house=dom, sex=spol, email='')
    elif not geslo1 == geslo2:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The passwords do not match. Check them again.',
                        email=email, username=vzdevek, house=dom, sex=spol)
    geslo_kodirano = zakodiraj_geslo(geslo1)
    cur.execute("INSERT INTO uporabnik (vzdevek, geslo, email, dom, spol) VALUES(%s,%s,%s,%s,%s);",
                (vzdevek, geslo_kodirano, email, dom, spol))
    conn.commit()
    return template('prijava.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    sporocilo='Great, you are now member of our community. You can sign in here.')

@get('/profile/:x')
@post('/profile/:x')
def profil(x):
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrana_knjiga "
                "ON knjiga.id= prebrana_knjiga.id_knjige WHERE prebrana_knjiga.id_uporabnika=%s;", (uporabnik()[0],))
    prebrane = cur.fetchall()

    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN wishlist ON knjiga.id= wishlist.id_knjige "
                "WHERE wishlist.id_uporabnika=%s;", (uporabnik()[0],))
    zelje = cur.fetchall()

    return template('profile.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    prebrane=prebrane, zelje=zelje)


@get('/change_profile')
def spremeni():
    cur.execute("SELECT spol FROM uporabnik WHERE id=%s;", (uporabnik()[0],))
    spol = cur.fetchone()[0]
    if spol == 'Female':
        spol = 'Witch'
    else:
        spol = 'Wizard'
    return template('spremeni_profil.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    spol=spol, sporocilo=None)


@post('/change_profile')
def spremeni():
    (id, vzdevek, dom) = uporabnik()

    geslo_staro = zakodiraj_geslo(request.forms.geslo_trenutno)
    geslo_novo = request.forms.novo_geslo
    geslo_novo2 = request.forms.novo_geslo2
    novi_dom = request.forms.dom  # TODO request.forms.get("dom")
    novi_spol = request.forms.spol  # TODO request.forms.get("spol")
    # Preveri, ali lahko sploh karkoli spreminja:
    cur.execute("SELECT geslo FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
    pravo_geslo = cur.fetchone()[0]
    if pravo_geslo != geslo_staro:
        return template("spremeni_profil.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The current password you typed is not correct, try again.', spol=novi_spol)
    elif geslo_novo == '':
        geslo_novo = geslo_staro
    elif geslo_novo != geslo_novo2:
        return template("spremeni_profil.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The new passwords do not match. Check them again.', spol=novi_spol)
    else:
        geslo_novo = zakodiraj_geslo(geslo_novo)
    if novi_spol == "Witch":
        novi_spol = "Female"
    elif novi_spol == "Wizard":
        novi_spol = "Male"
    cur.execute("UPDATE uporabnik SET geslo = %s, dom = %s, spol = %s WHERE id = %s;",
                (geslo_novo, novi_dom, novi_spol, id))
    conn.commit()
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrana_knjiga "
                "ON knjiga.id= prebrana_knjiga.id_knjige WHERE prebrana_knjiga.id_uporabnika=%s;",
                (uporabnik()[0],))
    prebrane = cur.fetchall()
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN wishlist "
                "ON knjiga.id= wishlist.id_knjige WHERE wishlist.id_uporabnika=%s;",
                (uporabnik()[0],))
    zelje = cur.fetchall()

    return template('profile.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(), prebrane=prebrane,
                    zelje=zelje)


@error(404)
def error404(error):
    return template('404.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik())

######################################################################
# Glavni program


# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
# conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# ~~~~~~~~~~~~~~~~~~~~~Pridobi 50 najpogostejših žanrov
cur.execute("""SELECT sum(stevilo) AS stevilo_skupaj, ime_zanra, id FROM (
 SELECT count(*) AS stevilo, ime_zanra, id FROM zanr AS zanr1
 JOIN zanr_knjige ON zanr1.id=zanr_knjige.id_zanra
 GROUP BY ime_zanra, id UNION ALL
 SELECT count(*) AS stevilo, ime_zanra, id FROM zanr AS zanr2
 JOIN avtorjev_zanr ON zanr2.id=avtorjev_zanr.id_zanra
 GROUP BY ime_zanra, id
) AS tabela
GROUP BY ime_zanra, id
ORDER BY stevilo_skupaj DESC
LIMIT 50;""")

zanri_iz_baze = cur.fetchall()
vsi_zanri = []
for vrstica in zanri_iz_baze:
    vsi_zanri.append((vrstica[1], vrstica[2]))
vsi_zanri.sort()

# ~~~~~~~~~~~~~~~~~~~~~Pridobi vse skupine ključnih besed
cur.execute("""SELECT skupina, pojem, id FROM kljucna_beseda JOIN knjiga_kljucne_besede ON id=id_kljucne_besede
GROUP BY id;""")
kljucne_iz_baze = cur.fetchall()
vse_kljucne = {}
for vrstica in kljucne_iz_baze:
    skupina = vrstica[0]
    vse_kljucne[skupina] = vse_kljucne.get(skupina, list()) + [(vrstica[1], vrstica[2])]

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=True)

