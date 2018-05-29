import orodja

seznam_besed = ['Headmaster', 'School', 'Student', 'Castle', 'Boarding school', 'Beast', 'Goblin', 'Centaur',
                'Giant',
                'Phoenix', 'Witch', 'Wizard', 'Dragon', 'Boggart', 'Vampire', 'Monster', 'Elf', 'Dwarf', 'Demigod',
                'Alien',
                'Werewolf', 'Unicorn', ' Rat ', ' Rats ', ' Owl', 'Sphinx', 'Troll', 'Hobbit', 'Fairy', 'Human',
                'Angel', 'Demon',
                'God',
                'mystical creatures ', 'Prince', 'Princess', 'Queen', 'Prisoner', 'Orphan', 'Muggle', 'Witch',
                'Wizard',
                'Dark Lord', 'Apprentice', 'Friend', 'Enemy', 'Magic', 'Witchcraft', 'Wizardry', 'Charms',
                'Transfiguration', 'Curse',
                'Jinx', 'Divination', 'Dark arts', 'Patronus', 'Invisibility', 'Immortal', 'Alchemy', 'Animagus',
                'Spell', 'Sorcery',
                'ability to fly', 'Powers', 'Time travel', 'Magician', 'Miracles', 'Transform', 'Enchantment', 'Force',
                'Friendship',
                'Power', 'Bravery', 'Courage', 'Loyalty', 'Honesty', 'Dark side', 'Wisdom ', 'Evil', 'Love', 'Elitism',
                'Pure Blood',
                'Choice', 'Friendship', 'Imagination', 'eternal life', 'Family', 'Goblet', 'Potion', 'Wand',
                'Flying broom', 'Train',
                'Socks', 'Mirror', 'Letter', 'Sword', 'Chess', 'Scar', 'Pig tail', 'Chocolate', 'Parchment',
                'Maze',
                'Voldemort', 'Hermione Granger', 'Harry Potter', 'Ron Weasley', 'Nicholas Flamel', 'marauders ', 'Duel',
                'Invisible',
                'Apocalypse', 'Journey', 'Invasion ', 'Fighting', 'test', 'Nightmare', 'Mankind', 'Secret', 'Legend',
                'Myth',
                'Destiny', 'Fate', 'Mysterious', 'Consequences', 'Danger ', 'Dangerous', 'Future', 'Revenge', 'Hate',
                'Tom Riddle',
                'Leacky cauldron', 'Orphanage', 'Outsider', 'Mission', 'Quest', 'Calling', 'Save the world',
                'Destroy the base',
                'Find', ' King', ' Hat '] + ['warlock', 'ghost', 'faries', 'academy', 'adevture', 'adventure',
                                             'intelligence', 'symbol',
                                             'voyage', 'pirate', 'enemy', 'eternal', 'eternity', 'life', 'time',
                                             'world', 'Black', 'save', 'lost', 'adventure', 'learn', 'dead', 'death',
                                             'life', 'live',
                                             'father', 'mother', 'parent', 'help', 'home', 'fantasy', 'battle', 'child',
                                             ' war', 'different', 'truth', 'lies',
                                             'inherit', 'special', 'dream', 'survival', 'survive', 'hope', 'trouble',
                                             'travel', 'peculiar', 'dark', 'chosen one',
                                             'army', ' teen', 'ancient', 'London', 'sacrifice', 'escape', 'rescue']

seznam_vseh_knjig_kljucnih_besed = []
dodane_knjige = set()
mankajoce = []

frekvenca = dict()
for pojem in seznam_besed:
    frekvenca[pojem.lower()] = 0


def poisci_kljucne_besede(seznam_vseh_knjig):
    for knjiga in seznam_vseh_knjig:
        opis = knjiga['opis'].lower()
        naslov = knjiga['naslov'].lower()
        for beseda in seznam_besed:
            if beseda.lower() in opis + naslov:
                kljucna_beseda = dict()
                kljucna_beseda['id_knjige'] = knjiga['id']
                kljucna_beseda['kljucna_beseda'] = beseda
                seznam_vseh_knjig_kljucnih_besed.append(kljucna_beseda)
                dodane_knjige.add(knjiga['id'])
                frekvenca[beseda.lower()] += 1
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
