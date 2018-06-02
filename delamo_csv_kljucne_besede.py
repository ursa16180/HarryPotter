import orodja

def naredi_slovar_kljucnih_besed():
    datoteka = open('podatki/kljucna_beseda.csv', 'r')
    slovar_kljucnih = dict()
    for vrstica in datoteka:
        (pojem, skupina) = vrstica.split(';')
        slovar_kljucnih[' {0}'.format(pojem.lower())]=pojem
    datoteka.close()
    return slovar_kljucnih

seznam_vseh_knjig_kljucnih_besed = []
dodane_knjige = set()
mankajoce = []

frekvenca = dict()
for pojem in naredi_slovar_kljucnih_besed().values():
    frekvenca[pojem] = 0


def poisci_kljucne_besede(seznam_vseh_knjig):
    for knjiga in seznam_vseh_knjig:
        if knjiga['opis'] is not None:
            opis = knjiga['opis'].lower()
            naslov = knjiga['naslov'].lower()
            slovar_kljucnih = naredi_slovar_kljucnih_besed()
            for beseda in slovar_kljucnih.keys():
                if beseda in opis + naslov:
                    kljucna_beseda = dict()
                    kljucna_beseda['id_knjige'] = knjiga['id']
                    kljucna_beseda['kljucna_beseda'] = slovar_kljucnih[beseda]
                    seznam_vseh_knjig_kljucnih_besed.append(kljucna_beseda)
                    dodane_knjige.add(knjiga['id'])
                    frekvenca[slovar_kljucnih[beseda]] += 1
            if knjiga['id'] not in dodane_knjige:  # Naredi csv knjig, ki niso imele nobene kljucne besede
                mankajoce.append(knjiga)
    orodja.zapisi_tabelo(mankajoce,
                         ['id', 'ISBN', 'naslov', 'dolzina', 'povprecna_ocena', 'stevilo_ocen', 'leto', 'opis'],
                         'podatki/mankajoce.csv')

    print(len(dodane_knjige), len(seznam_vseh_knjig_kljucnih_besed))
    print(sorted(frekvenca, key=frekvenca.get, reverse=True))  # Vrne seznam od najpogostejše do neobstojece
    # prestej_besede('podatki/mankajoce.csv')


def naredi_seznam_kljucnih_besed():
    datoteka = open('kljucni.csv', 'r')
    seznam_kljucnih = []
    for vrstica in datoteka:
        (pojem, skupina) = vrstica.split(';')
        seznam_kljucnih.append(pojem)
    datoteka.close()
    return seznam_kljucnih


def prestej_besede(ime_datoteke):
    datoteka = open(ime_datoteke, "r", encoding="utf8")
    slovar_besed = dict()
    for beseda in datoteka.read().split():
        if beseda not in slovar_besed:
            slovar_besed[beseda] = 1
        else:
            slovar_besed[beseda] += 1
    print(sorted(slovar_besed, key=slovar_besed.get, reverse=True))
