"""
SCIL Item Pool — 100 strukturierte Items fuer wissenschaftlich fundierte Erhebung.

Jedes Item misst eine spezifische SCIL-Frequenz der Wirkungskompetenz (Aussenwirkung).
SCIL misst NICHT Persoenlichkeit, sondern wie eine Person auf andere wirkt.

Stamm: "Andere sagen ueber mich, dass ich..."
Alle 100 Items vervollstaendigen diesen Satz aus der Fremdwahrnehmungsperspektive.

Verteilung: 25 Items pro Cluster (Sensus, Corpus, Intellektus, Lingua)
Pro Frequenz: 5-7 Items (25 Items / 4 Frequenzen ≈ 6.25)

Scoring: 0-4 Skala (0=schwache Auspraegung, 4=ausgepragte Staerke)
Bewertungsstufen: a) 3.5-4.0, b) 2.5-3.5, c) 1.5-2.5, d) 0.5-1.5, e) 0.0-0.5

IRT-Parameter (initial neutral, werden nach Datensammlung kalibriert):
  - difficulty: 0.5 = mittlere Schwierigkeit
  - discrimination: 1.0 = mittlere Trennschaerfe

Autor: SCIL Performance Strategie (c) Andreas Bornhaeusser
Framework: S.C.I.L. = Sensus, Corpus, Intellektus, Lingua

Original Items: 100 Items aus CSV (test_id=1, pages 1-100)
"""

from __future__ import annotations

from typing import TypedDict


class SCILItem(TypedDict):
    id: str
    area: str
    frequency: str
    text_de: str
    scoring_guidance: str
    reverse_scored: bool
    difficulty: float
    discrimination: float


# ---------------------------------------------------------------------------
# SCIL ITEM POOL — 100 Original Items from CSV
# ---------------------------------------------------------------------------
# Mapping: page_id → area/frequency based on SCIL framework definitions
#
# SENSUS (25 items): innere_praesenz(6), innere_ueberzeugung(7), prozessfokussierung(6), emotionalitaet(6)
#   - innere_praesenz: pages 1, 16, 24, 47, 51, 78
#   - innere_ueberzeugung: pages 6, 33, 41, 61, 89, 93, 94
#   - prozessfokussierung: pages 17, 40, 46, 56, 69, 81
#   - emotionalitaet: pages 11, 28, 32, 48, 52, 77
#
# CORPUS (25 items): erscheinungsbild(6), mimik(5), gestik(7), raeumliche_praesenz(7)
#   - erscheinungsbild: pages 2, 12, 18, 37, 55, 57
#   - mimik: pages 31, 34, 58, 62, 70
#   - gestik: pages 5, 27, 42, 66, 86, 90, 98
#   - raeumliche_praesenz: pages 15, 21, 45, 73, 74, 82, 85
#
# INTELLEKTUS (25 items): sachlichkeit(6), analytik(6), struktur(7), zielorientierung(6)
#   - sachlichkeit: pages 3, 14, 25, 49, 83, 99
#   - analytik: pages 9, 53, 59, 63, 71, 79
#   - struktur: pages 7, 19, 30, 38, 75, 87, 91
#   - zielorientierung: pages 22, 35, 43, 67, 95, 97
#
# LINGUA (25 items): stimme(6), artikulation(6), beredsamkeit(7), bildhaftigkeit(6)
#   - stimme: pages 10, 44, 50, 64, 76, 88
#   - artikulation: pages 13, 20, 39, 68, 72, 80
#   - beredsamkeit: pages 8, 26, 36, 60, 84, 92, 96
#   - bildhaftigkeit: pages 4, 23, 29, 54, 65, 100
# ---------------------------------------------------------------------------

SCIL_ITEM_POOL: list[SCILItem] = [
    # =====================================================================
    # SENSUS (S01-S25) — Innere Haltung, Empathie, Beziehungsgestaltung
    # =====================================================================

    # --- Innere Praesenz (S01-S06) --- pages: 1, 16, 24, 47, 51, 78
    {
        "id": "S01",  # page 1
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "... gut zuhöre und auf sie eingehe.",
        "scoring_guidance": "Hoch (3-4): Wird als aufmerksamer Zuhoerer beschrieben, greift Gesagtes auf, zeigt echtes Interesse. Mittel (1.5-2.5): Hoert zu, aber nicht immer mit voller Aufmerksamkeit. Niedrig (0-1): Wirkt abwesend, unterbricht haeufig, geht nicht auf andere ein.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S02",  # page 16
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "... Stimmungen sehr gut erfasse.",
        "scoring_guidance": "Hoch (3-4): Spuert Stimmungen sofort, reagiert sensibel auf emotionale Atmosphaere. Mittel (1.5-2.5): Nimmt Stimmungen wahr, aber nicht immer zeitnah. Niedrig (0-1): Uebersieht Stimmungen, wirkt unsensibel fuer Atmosphaere.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S03",  # page 24
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "... mich gut in andere einfühle.",
        "scoring_guidance": "Hoch (3-4): Zeigt starke Empathie, versteht Perspektiven anderer intuitiv. Mittel (1.5-2.5): Kann sich einfuehlen, braucht aber manchmal Zeit. Niedrig (0-1): Wirkt distanziert, versteht emotionale Lagen anderer selten.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S04",  # page 47
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "... stets den richtigen Ton (meines vis-á-Vis) treffe.",
        "scoring_guidance": "Hoch (3-4): Passt Kommunikation perfekt an das Gegenueber an, trifft immer den passenden Ton. Mittel (1.5-2.5): Trifft meist den richtigen Ton, gelegentlich Fehleinschaetzungen. Niedrig (0-1): Wirkt oft unangemessen oder verfehlt den Ton.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S05",  # page 51
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "... die körpersprachlichen Signale anderer gut wahrnehme.",
        "scoring_guidance": "Hoch (3-4): Liest Koerpersprache anderer praezise, reagiert darauf angemessen. Mittel (1.5-2.5): Nimmt offensichtliche Signale wahr, uebersieht subtilere. Niedrig (0-1): Achtet kaum auf Koerpersprache anderer.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S06",  # page 78
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "... auf nonverbale Signale anderer sofort eingehe.",
        "scoring_guidance": "Hoch (3-4): Reagiert unmittelbar und passend auf nonverbale Hinweise. Mittel (1.5-2.5): Reagiert auf nonverbale Signale, aber verzoegert. Niedrig (0-1): Ignoriert oder uebersieht nonverbale Kommunikation.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Innere Ueberzeugung (S07-S13) --- pages: 6, 33, 41, 61, 89, 93, 94
    {
        "id": "S07",  # page 6
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... über eine gute Intuition verfüge.",
        "scoring_guidance": "Hoch (3-4): Wird als Person mit starker Intuition wahrgenommen, Bauchgefuehl ist zuverlaessig. Mittel (1.5-2.5): Hat manchmal gute Eingebungen, nicht immer konsistent. Niedrig (0-1): Wirkt eher kopfgesteuert, Intuition spielt kaum Rolle.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S08",  # page 33
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... authentisch und offen auf sie wirke.",
        "scoring_guidance": "Hoch (3-4): Wird als sehr echt und transparent wahrgenommen, keine Fassade. Mittel (1.5-2.5): Grundsaetzlich authentisch, manchmal etwas zurueckhaltend. Niedrig (0-1): Wirkt aufgesetzt oder verschlossen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S09",  # page 41
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... eine positive Ausstrahlung habe.",
        "scoring_guidance": "Hoch (3-4): Strahlt Positivitaet aus, hebt die Stimmung durch blosse Anwesenheit. Mittel (1.5-2.5): Wirkt meist positiv, aber nicht immer strahlend. Niedrig (0-1): Ausstrahlung wirkt neutral oder negativ.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S10",  # page 61
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... eine positive Einstellung vermittle.",
        "scoring_guidance": "Hoch (3-4): Vermittelt durchgehend optimistische, konstruktive Haltung. Mittel (1.5-2.5): Grundsaetzlich positiv, aber nicht immer ueberzeugend. Niedrig (0-1): Wirkt skeptisch, pessimistisch oder gleichgueltig.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S11",  # page 89
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... ein gewinnendes Wesen habe.",
        "scoring_guidance": "Hoch (3-4): Wird sofort als sympathisch und einnehmend wahrgenommen. Mittel (1.5-2.5): Wirkt angenehm, aber nicht besonders gewinnend. Niedrig (0-1): Wirkt distanziert oder unnahbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S12",  # page 93
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... einen gesunden Optimismus verbreite.",
        "scoring_guidance": "Hoch (3-4): Verbreitet realistischen, ansteckenden Optimismus. Mittel (1.5-2.5): Zeigt gelegentlich optimistische Haltung. Niedrig (0-1): Wirkt pessimistisch oder unrealistisch.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S13",  # page 94
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "... selbstbewusst auftrete.",
        "scoring_guidance": "Hoch (3-4): Tritt sicher und selbstbewusst auf, ohne arrogant zu wirken. Mittel (1.5-2.5): Grundsaetzlich selbstsicher, gelegentlich unsicher. Niedrig (0-1): Wirkt unsicher, zoegerlich oder ueberheblich.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Prozessfokussierung (S14-S19) --- pages: 17, 40, 46, 56, 69, 81
    {
        "id": "S14",  # page 17
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "... eine Atmosphäre der Beteiligung schaffe.",
        "scoring_guidance": "Hoch (3-4): Schafft Raeume, in denen alle sich einbringen koennen und wollen. Mittel (1.5-2.5): Bemuehung um Beteiligung erkennbar, nicht immer erfolgreich. Niedrig (0-1): Atmosphaere wirkt exklusiv oder unbeteiligend.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S15",  # page 40
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "... ihre unterschiedlichen Sinne erreiche.",
        "scoring_guidance": "Hoch (3-4): Spricht verschiedene Sinne und Wahrnehmungskanaele gezielt an. Mittel (1.5-2.5): Erreicht manchmal mehrere Sinne, nicht systematisch. Niedrig (0-1): Kommuniziert eindimensional, nur auf einer Ebene.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S16",  # page 46
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "... konzentriert bei der Sache bleibe.",
        "scoring_guidance": "Hoch (3-4): Bleibt fokussiert und praesent, laesst sich nicht ablenken. Mittel (1.5-2.5): Meist konzentriert, gelegentlich abschweifend. Niedrig (0-1): Wirkt unkonzentriert oder leicht ablenkbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S17",  # page 56
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "... die Atmosphäre gekonnt beeinflusse.",
        "scoring_guidance": "Hoch (3-4): Gestaltet Stimmung im Raum bewusst und wirkungsvoll. Mittel (1.5-2.5): Hat manchmal Einfluss auf Atmosphaere, nicht immer gezielt. Niedrig (0-1): Atmosphaere wird nicht aktiv gestaltet.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S18",  # page 69
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": '... eher die Wirkung eines \u201eBauchmenschen\u201d habe.',
        "scoring_guidance": "Hoch (3-4): Wird als intuitiv und gefuehlsgeleitet wahrgenommen. Mittel (1.5-2.5): Balance zwischen Bauch und Kopf. Niedrig (0-1): Wirkt sehr rational und kopfgesteuert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S19",  # page 81
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "... eher prozessorientiert agiere.",
        "scoring_guidance": "Hoch (3-4): Achtet auf den Weg, nicht nur das Ziel, begleitet Prozesse aufmerksam. Mittel (1.5-2.5): Prozessbewusstsein vorhanden, nicht immer im Fokus. Niedrig (0-1): Nur ergebnisorientiert, Prozess wird vernachlaessigt.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Emotionalitaet (S20-S25) --- pages: 11, 28, 32, 48, 52, 77
    {
        "id": "S20",  # page 11
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "... eine gute Stimmung verbreite.",
        "scoring_guidance": "Hoch (3-4): Hebt die Stimmung, bringt gute Laune in Gruppen. Mittel (1.5-2.5): Traegt manchmal zu guter Stimmung bei. Niedrig (0-1): Stimmung wird nicht positiv beeinflusst oder gedaempft.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S21",  # page 28
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "... anderen Menschen ein Wohlgefühl vermittle.",
        "scoring_guidance": "Hoch (3-4): Andere fuehlen sich wohl und entspannt in ihrer Gegenwart. Mittel (1.5-2.5): Vermittelt manchmal Wohlgefuehl, nicht durchgehend. Niedrig (0-1): Andere fuehlen sich unwohl oder angespannt.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S22",  # page 32
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "... schnell Sympathie gewinne und Vertrauen schaffe.",
        "scoring_guidance": "Hoch (3-4): Baut sofort Vertrauen auf, wird schnell sympathisch gefunden. Mittel (1.5-2.5): Gewinnt Sympathie, braucht aber etwas Zeit. Niedrig (0-1): Vertrauensaufbau dauert lange oder gelingt selten.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S23",  # page 48
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "... als grundsätzlich wohlwollende Person wahrgenommen werde.",
        "scoring_guidance": "Hoch (3-4): Wird als gutmeinend und wohlwollend erlebt. Mittel (1.5-2.5): Grundsaetzlich wohlwollend, manchmal neutral. Niedrig (0-1): Wirkt gleichgueltig oder ablehnend.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S24",  # page 52
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "... liebevoll mit mir und anderen umgehe.",
        "scoring_guidance": "Hoch (3-4): Zeigt echte Zuneigung und Wertschaetzung im Umgang. Mittel (1.5-2.5): Grundsaetzlich freundlich, aber nicht besonders herzlich. Niedrig (0-1): Umgang wirkt kuehl oder distanziert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S25",  # page 77
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "... andere Menschen offensichtlich aufrichtig wertschätze.",
        "scoring_guidance": "Hoch (3-4): Zeigt echte, spuerbare Wertschaetzung fuer andere. Mittel (1.5-2.5): Wertschaetzung vorhanden, nicht immer sichtbar. Niedrig (0-1): Wertschaetzung fehlt oder wirkt unecht.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # =====================================================================
    # CORPUS (C01-C25) — Koerperliche Praesenz, Erscheinung, Ausstrahlung
    # =====================================================================

    # --- Erscheinungsbild (C01-C06) --- pages: 2, 12, 18, 37, 55, 57
    {
        "id": "C01",  # page 2
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "... stets angemessen gekleidet bin.",
        "scoring_guidance": "Hoch (3-4): Kleidung ist immer passend zum Anlass, gepflegt und stimmig. Mittel (1.5-2.5): Meist angemessen gekleidet, gelegentlich unpassend. Niedrig (0-1): Kleidung oft unpassend oder nachlässig.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "C02",  # page 12
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "... u.a. auch durch meine äußere Erscheinung gewinne.",
        "scoring_guidance": "Hoch (3-4): Aeussere Erscheinung traegt deutlich zum positiven Eindruck bei. Mittel (1.5-2.5): Erscheinung ist angemessen, aber kein besonderer Pluspunkt. Niedrig (0-1): Erscheinung macht keinen positiven Eindruck.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C03",  # page 18
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "... mich selbst als ganze Erscheinung gut in Szene zu setzen weiß.",
        "scoring_guidance": "Hoch (3-4): Praesentation der eigenen Person ist durchdacht und wirkungsvoll. Mittel (1.5-2.5): Setzt sich manchmal gut in Szene, nicht konsistent. Niedrig (0-1): Selbstpraesentation ist unbeholfen oder uneffektiv.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C04",  # page 37
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "... mich in jedem Umfeld angemessen zu bewegen weiß.",
        "scoring_guidance": "Hoch (3-4): Passt sich mühelos verschiedenen sozialen Kontexten an. Mittel (1.5-2.5): Meist angemessenes Verhalten, gelegentlich unsicher. Niedrig (0-1): Wirkt in manchen Umfeldern fehl am Platz.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C05",  # page 55
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "... sichtbaren Wert auf mein Äußeres lege.",
        "scoring_guidance": "Hoch (3-4): Pflegt Aeusseres bewusst und sichtbar, wirkt gepflegt. Mittel (1.5-2.5): Achtet auf Aeusseres, aber nicht auffaellig. Niedrig (0-1): Aeusseres scheint unwichtig, wenig Pflege erkennbar.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "C06",  # page 57
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "... meine eigene Stimmung deutlich zeige.",
        "scoring_guidance": "Hoch (3-4): Stimmung ist klar ablesbar, authentischer Ausdruck. Mittel (1.5-2.5): Zeigt Stimmung manchmal, nicht immer deutlich. Niedrig (0-1): Stimmung bleibt verborgen oder ist nicht erkennbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Mimik (C07-C11) --- pages: 31, 34, 58, 62, 70
    {
        "id": "C07",  # page 31
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "... ein gewisses schauspielerisches Talent habe.",
        "scoring_guidance": "Hoch (3-4): Kann Emotionen und Rollen ueberzeugend darstellen. Mittel (1.5-2.5): Hat manchmal darstellerische Momente, nicht konsistent. Niedrig (0-1): Wirkt steif oder unnatuerlich bei Darstellung.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C08",  # page 34
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "... geschickt mit meiner Mimik spiele.",
        "scoring_guidance": "Hoch (3-4): Setzt Gesichtsausdruck gezielt und wirkungsvoll ein. Mittel (1.5-2.5): Mimik ist vorhanden, aber nicht bewusst gesteuert. Niedrig (0-1): Mimik ist starr oder unauthentisch.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C09",  # page 58
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "... meinen Körper als Medium begreife und nutze.",
        "scoring_guidance": "Hoch (3-4): Nutzt Koerper bewusst als Kommunikationswerkzeug. Mittel (1.5-2.5): Setzt Koerper manchmal ein, nicht immer bewusst. Niedrig (0-1): Koerper wird kaum als Ausdrucksmittel genutzt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C10",  # page 62
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "... meine Inhalte im wahrsten Sinne des Wortes verkörpere.",
        "scoring_guidance": "Hoch (3-4): Koerperlicher Ausdruck stimmt perfekt mit Inhalt ueberein. Mittel (1.5-2.5): Verkoerperung manchmal vorhanden, nicht durchgaengig. Niedrig (0-1): Koerper und Inhalt passen nicht zusammen.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C11",  # page 70
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "... meine Mimik und Gestik bewusst einsetze.",
        "scoring_guidance": "Hoch (3-4): Nutzt Mimik und Gestik gezielt und wirkungsvoll. Mittel (1.5-2.5): Einsatz manchmal bewusst, oft unbewusst. Niedrig (0-1): Kaum bewusster Einsatz von Mimik und Gestik.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Gestik (C12-C18) --- pages: 5, 27, 42, 66, 86, 90, 98
    {
        "id": "C12",  # page 5
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... eine authentische Gestik und Mimik habe.",
        "scoring_guidance": "Hoch (3-4): Koerpersprache wirkt echt und stimmig zur Person. Mittel (1.5-2.5): Meist authentisch, gelegentlich aufgesetzt. Niedrig (0-1): Gestik wirkt gekuenstelt oder unstimmig.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C13",  # page 27
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... mit meiner Gestik das Gesprochene gekonnt unterstreiche.",
        "scoring_guidance": "Hoch (3-4): Gestik unterstuetzt und verstaerkt das Gesagte wirkungsvoll. Mittel (1.5-2.5): Gestik vorhanden, aber nicht immer passend. Niedrig (0-1): Gestik fehlt oder lenkt ab.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C14",  # page 42
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... über eine ausgeprägte und stimmige Körpersprache verfüge.",
        "scoring_guidance": "Hoch (3-4): Koerpersprache ist ausdrucksstark und passt zur Botschaft. Mittel (1.5-2.5): Koerpersprache vorhanden, nicht besonders ausgepraegt. Niedrig (0-1): Koerpersprache ist schwach oder inkonsistent.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C15",  # page 66
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... auch nonverbal überzeugend bin.",
        "scoring_guidance": "Hoch (3-4): Ueberzeugt auch ohne Worte durch Koerpersprache. Mittel (1.5-2.5): Nonverbal erkennbar, aber nicht durchgehend ueberzeugend. Niedrig (0-1): Nonverbale Kommunikation ist schwach oder widerspruechlich.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C16",  # page 86
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... meine Körpersprache offensichtlich gut kontrolliere.",
        "scoring_guidance": "Hoch (3-4): Hat volle Kontrolle ueber Koerpersprache, setzt sie gezielt ein. Mittel (1.5-2.5): Teilweise kontrolliert, manchmal unbewusste Signale. Niedrig (0-1): Koerpersprache scheint unkontrolliert.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C17",  # page 90
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... durch meine Körpersprache Souveränität ausstrahle.",
        "scoring_guidance": "Hoch (3-4): Koerpersprache vermittelt Sicherheit und Kompetenz. Mittel (1.5-2.5): Wirkt meist souveraen, gelegentlich unsicher. Niedrig (0-1): Koerpersprache verraet Unsicherheit.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C18",  # page 98
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "... körpersprachlich sehr schnell auf andere reagiere.",
        "scoring_guidance": "Hoch (3-4): Reagiert koerperlich unmittelbar und passend auf andere. Mittel (1.5-2.5): Reagiert koerperlich, aber verzoegert. Niedrig (0-1): Kaum koerperliche Reaktion auf andere.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Raeumliche Praesenz (C19-C25) --- pages: 15, 21, 45, 73, 74, 82, 85
    {
        "id": "C19",  # page 15
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... körperlich sehr präsent bin.",
        "scoring_guidance": "Hoch (3-4): Physische Praesenz ist deutlich spuerbar, nimmt Raum ein. Mittel (1.5-2.5): Praesenz vorhanden, aber nicht dominant. Niedrig (0-1): Wirkt koerperlich unauffaellig oder zurueckgezogen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C20",  # page 21
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... stets den zur Verfügung stehenden Raum ausfülle.",
        "scoring_guidance": "Hoch (3-4): Nutzt den verfuegbaren Raum selbstbewusst und angemessen. Mittel (1.5-2.5): Nutzt Raum teilweise, manchmal zurueckhaltend. Niedrig (0-1): Nutzt kaum Raum, wirkt eingeschuchtert.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C21",  # page 45
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... wahrgenommen werde, sobald ich einen Raum betrete.",
        "scoring_guidance": "Hoch (3-4): Wird sofort bemerkt, zieht Aufmerksamkeit auf sich. Mittel (1.5-2.5): Wird nach einiger Zeit wahrgenommen. Niedrig (0-1): Geht in der Menge unter, bleibt unbemerkt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C22",  # page 73
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... meine Stimmung auf andere übertrage.",
        "scoring_guidance": "Hoch (3-4): Eigene Stimmung beeinflusst andere spuerbar, ansteckende Praesenz. Mittel (1.5-2.5): Stimmung wird manchmal uebertragen. Niedrig (0-1): Stimmung bleibt privat, beeinflusst andere kaum.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C23",  # page 74
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... eine Person bin, die im Raum wahrgenommen wird.",
        "scoring_guidance": "Hoch (3-4): Praesenz ist deutlich, wird als wichtige Person im Raum erlebt. Mittel (1.5-2.5): Wird wahrgenommen, aber nicht herausragend. Niedrig (0-1): Bleibt unauffaellig, wird kaum beachtet.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C24",  # page 82
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... Raum nehme.",
        "scoring_guidance": "Hoch (3-4): Nimmt selbstbewusst Raum ein, ohne aufdringlich zu wirken. Mittel (1.5-2.5): Nimmt angemessen Raum, aber nicht dominant. Niedrig (0-1): Nimmt wenig Raum ein, wirkt zurueckhaltend.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C25",  # page 85
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "... warmherzig wirke.",
        "scoring_guidance": "Hoch (3-4): Strahlt Waerme und Herzlichkeit aus, einladende Praesenz. Mittel (1.5-2.5): Grundsaetzlich warm, aber nicht immer spuerbar. Niedrig (0-1): Wirkt kuehl oder distanziert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # =====================================================================
    # INTELLEKTUS (I01-I25) — Geistige Struktur, Logik, Zielorientierung
    # =====================================================================

    # --- Sachlichkeit (I01-I06) --- pages: 3, 14, 25, 49, 83, 99
    {
        "id": "I01",  # page 3
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "... eher rational auf sie wirke.",
        "scoring_guidance": "Hoch (3-4): Wird als sehr vernunftgesteuert und sachlich wahrgenommen. Mittel (1.5-2.5): Balance zwischen rational und emotional. Niedrig (0-1): Wirkt eher emotional als rational.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I02",  # page 14
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "... offensichtlich eher mit dem Kopf als mit dem Bauch entscheide.",
        "scoring_guidance": "Hoch (3-4): Entscheidungen wirken durchdacht und analytisch. Mittel (1.5-2.5): Mischung aus Kopf- und Bauchentscheidungen. Niedrig (0-1): Wirkt impulsiv oder gefuehlsgesteuert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I03",  # page 25
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "... als ein von der Vernunft geleiteter Mensch erscheine.",
        "scoring_guidance": "Hoch (3-4): Wird als sehr vernuenftig und logisch wahrgenommen. Mittel (1.5-2.5): Grundsaetzlich vernuenftig, manchmal emotional. Niedrig (0-1): Vernunft scheint keine primaere Leitlinie.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I04",  # page 49
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "... oft durch eine zwingende Logik überzeuge.",
        "scoring_guidance": "Hoch (3-4): Argumentiert mit klarer, unanfechtbarer Logik. Mittel (1.5-2.5): Logik ist erkennbar, aber nicht immer zwingend. Niedrig (0-1): Logik ist nicht offensichtlich oder fehlerhaft.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I05",  # page 83
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "... die Sache vom Gefühl zu trennen vermag.",
        "scoring_guidance": "Hoch (3-4): Kann sachliche und emotionale Ebene klar trennen. Mittel (1.5-2.5): Trennung gelingt manchmal, nicht immer. Niedrig (0-1): Vermischt Sache und Gefuehl haeufig.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I06",  # page 99
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "... primär durch meine Sachlichkeit gewinne.",
        "scoring_guidance": "Hoch (3-4): Ueberzeugt hauptsaechlich durch faktische, nuchterne Argumentation. Mittel (1.5-2.5): Sachlichkeit ist vorhanden, aber nicht primaer. Niedrig (0-1): Sachlichkeit ist nicht das Hauptmerkmal.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Analytik (I07-I12) --- pages: 9, 53, 59, 63, 71, 79
    {
        "id": "I07",  # page 9
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "... ihre Bedürfnisse gut analysiert habe.",
        "scoring_guidance": "Hoch (3-4): Erkennt und versteht Beduerfnisse anderer praezise. Mittel (1.5-2.5): Analyse gelingt teilweise, nicht immer vollstaendig. Niedrig (0-1): Beduerfnisse werden nicht erkannt oder falsch eingeschaetzt.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I08",  # page 53
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "... auch in unübersichtlichen Momenten den Überblick behalte.",
        "scoring_guidance": "Hoch (3-4): Behaelt in komplexen Situationen den Durchblick. Mittel (1.5-2.5): Meist Ueberblick, gelegentlich ueberfordert. Niedrig (0-1): Verliert schnell den Ueberblick bei Komplexitaet.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I09",  # page 59
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "... komplexe Sachverhalte gut erfasse.",
        "scoring_guidance": "Hoch (3-4): Versteht komplexe Zusammenhaenge schnell und praezise. Mittel (1.5-2.5): Erfasst Komplexitaet, braucht aber Zeit. Niedrig (0-1): Schwierigkeiten mit komplexen Sachverhalten.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I10",  # page 63
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "... über ein ausgeprägtes analytisches Geschick verfüge.",
        "scoring_guidance": "Hoch (3-4): Wird als analytisch stark wahrgenommen, zerlegt Probleme geschickt. Mittel (1.5-2.5): Analytische Faehigkeiten vorhanden, nicht herausragend. Niedrig (0-1): Analytisches Denken ist nicht erkennbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I11",  # page 71
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "... meine Themen inhaltlich gründlich durchdrungen habe.",
        "scoring_guidance": "Hoch (3-4): Tiefes Verstaendnis der Themen ist deutlich spuerbar. Mittel (1.5-2.5): Gute Kenntnis, aber nicht in allen Details. Niedrig (0-1): Oberflaechliches Verstaendnis erkennbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I12",  # page 79
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "... über abstraktes Denkvermögen verfüge.",
        "scoring_guidance": "Hoch (3-4): Kann abstrakt denken und konzeptionell arbeiten. Mittel (1.5-2.5): Abstraktes Denken moeglich, aber nicht Staerke. Niedrig (0-1): Bevorzugt konkretes, praktisches Denken.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Struktur (I13-I19) --- pages: 7, 19, 30, 38, 75, 87, 91
    {
        "id": "I13",  # page 7
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... gründlich vorbereitet wirke.",
        "scoring_guidance": "Hoch (3-4): Wirkt immer gut vorbereitet, kennt Details. Mittel (1.5-2.5): Meist vorbereitet, manchmal lueckenhaft. Niedrig (0-1): Wirkt unvorbereitet oder improviserend.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I14",  # page 19
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... einen sehr strukturierten Eindruck vermittle.",
        "scoring_guidance": "Hoch (3-4): Wirkt sehr geordnet und systematisch. Mittel (1.5-2.5): Grundsaetzlich strukturiert, manchmal chaotisch. Niedrig (0-1): Wirkt unstrukturiert oder planlos.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I15",  # page 30
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... meine geplante Gliederung konsequent einhalte.",
        "scoring_guidance": "Hoch (3-4): Haelt sich an Plan und Struktur, bleibt beim roten Faden. Mittel (1.5-2.5): Meist planmaessig, gelegentliche Abweichungen. Niedrig (0-1): Weicht haeufig vom Plan ab.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I16",  # page 38
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... überzeugend strukturiere.",
        "scoring_guidance": "Hoch (3-4): Strukturiert Inhalte so, dass sie ueberzeugen und einleuchten. Mittel (1.5-2.5): Struktur erkennbar, aber nicht immer ueberzeugend. Niedrig (0-1): Struktur fehlt oder ueberzeugt nicht.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I17",  # page 75
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... meine Ausführungen stets gut gliedere.",
        "scoring_guidance": "Hoch (3-4): Ausfuehrungen sind klar gegliedert und nachvollziehbar. Mittel (1.5-2.5): Grundgliederung vorhanden, nicht immer optimal. Niedrig (0-1): Ausfuehrungen wirken ungegliedert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I18",  # page 87
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... stets gut und gründlich vorbereitet wirke.",
        "scoring_guidance": "Hoch (3-4): Immer hervorragend vorbereitet, keine Luecken. Mittel (1.5-2.5): Meist gut vorbereitet, manchmal Luecken. Niedrig (0-1): Vorbereitung ist nicht erkennbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I19",  # page 91
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "... meine Inhalte logisch folgerichtig vermittle.",
        "scoring_guidance": "Hoch (3-4): Inhalte werden logisch und nachvollziehbar praesent. Mittel (1.5-2.5): Meist logisch, gelegentliche Gedankenspruenge. Niedrig (0-1): Logik und Folgerichtigkeit fehlen oft.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Zielorientierung (I20-I25) --- pages: 22, 35, 43, 67, 95, 97
    {
        "id": "I20",  # page 22
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "... mich konsequent an das Thema halte.",
        "scoring_guidance": "Hoch (3-4): Bleibt strikt beim Thema, keine Abschweifungen. Mittel (1.5-2.5): Meist beim Thema, gelegentliche Exkurse. Niedrig (0-1): Schweift haeufig ab, verliert das Thema.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I21",  # page 35
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "... das Gespräch oder die Diskussion gut lenke.",
        "scoring_guidance": "Hoch (3-4): Fuehrt Gespraeche zielgerichtet und souveraen. Mittel (1.5-2.5): Kann lenken, verliert manchmal die Kontrolle. Niedrig (0-1): Gespraeche entgleiten oder werden nicht gefuehrt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I22",  # page 43
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "... sehr zielgerichtet und ergebnisorientiert wirke.",
        "scoring_guidance": "Hoch (3-4): Klare Zielorientierung, arbeitet konsequent auf Ergebnisse hin. Mittel (1.5-2.5): Grundsaetzlich zielorientiert, manchmal abgelenkt. Niedrig (0-1): Ziele unklar, wenig Ergebnisorientierung.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I23",  # page 67
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "... bei abschweifenden Diskussionen immer wieder auf den Punkt komme.",
        "scoring_guidance": "Hoch (3-4): Bringt Diskussionen zurueck auf den Punkt, haelt Fokus. Mittel (1.5-2.5): Versucht es, gelingt nicht immer. Niedrig (0-1): Laesst Abschweifungen zu, findet nicht zurueck.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I24",  # page 95
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "... meine Ziele klar verständlich vermittle.",
        "scoring_guidance": "Hoch (3-4): Ziele werden klar und verstaendlich kommuniziert. Mittel (1.5-2.5): Ziele erkennbar, aber nicht immer klar. Niedrig (0-1): Ziele bleiben unklar oder werden nicht kommuniziert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I25",  # page 97
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "... die Menschen emotional erreiche.",
        "scoring_guidance": "Hoch (3-4): Erreicht andere emotional, schafft Verbindung zum Ziel. Mittel (1.5-2.5): Teilweise emotionale Verbindung, nicht durchgaengig. Niedrig (0-1): Emotionale Ebene wird nicht erreicht.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # =====================================================================
    # LINGUA (L01-L25) — Sprachliche Wirkung, verbale Ausstrahlung
    # =====================================================================

    # --- Stimme (L01-L06) --- pages: 10, 44, 50, 64, 76, 88
    {
        "id": "L01",  # page 10
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "... eine angenehme Stimme habe.",
        "scoring_guidance": "Hoch (3-4): Stimme wird als sehr angenehm und wohlklingend beschrieben. Mittel (1.5-2.5): Stimme ist akzeptabel, weder positiv noch negativ. Niedrig (0-1): Stimme wirkt unangenehm oder stoerend.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "L02",  # page 44
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "... ein gutes Sprechtempo habe.",
        "scoring_guidance": "Hoch (3-4): Sprechtempo ist angenehm und dem Inhalt angemessen. Mittel (1.5-2.5): Tempo meist passend, manchmal zu schnell oder langsam. Niedrig (0-1): Tempo ist problematisch, hektisch oder einschlaefelnd.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "L03",  # page 50
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "... durch mein Stimmvolumen sehr präsent bin.",
        "scoring_guidance": "Hoch (3-4): Stimme traegt gut, ist praesent ohne aufdringlich zu sein. Mittel (1.5-2.5): Stimmvolumen ist angemessen, nicht besonders praesent. Niedrig (0-1): Stimme ist zu leise oder uebertrieben laut.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L04",  # page 64
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "... durch meine Stimme gezielt Stimmungen beeinflusse.",
        "scoring_guidance": "Hoch (3-4): Nutzt Stimme bewusst um Atmosphaere zu gestalten. Mittel (1.5-2.5): Stimmliche Wirkung vorhanden, aber nicht gezielt eingesetzt. Niedrig (0-1): Stimme beeinflusst Stimmung kaum oder negativ.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L05",  # page 76
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "... u.a. auch durch Sprechpausen Spannung erzeuge.",
        "scoring_guidance": "Hoch (3-4): Setzt Pausen gezielt und wirkungsvoll ein. Mittel (1.5-2.5): Nutzt Pausen gelegentlich, nicht immer bewusst. Niedrig (0-1): Nutzt keine Pausen oder sie wirken unbeholfen.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L06",  # page 88
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "... durch Veränderung der stimmlichen Lautstärke Aufmerksamkeit erzeuge.",
        "scoring_guidance": "Hoch (3-4): Variiert Lautstaerke bewusst fuer Wirkung und Aufmerksamkeit. Mittel (1.5-2.5): Etwas Variation, aber nicht durchgehend. Niedrig (0-1): Monotone Lautstaerke, keine bewusste Variation.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Artikulation (L07-L12) --- pages: 13, 20, 39, 68, 72, 80
    {
        "id": "L07",  # page 13
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "... sehr gut betone.",
        "scoring_guidance": "Hoch (3-4): Betonung ist klar, sinnvoll und unterstuetzt den Inhalt. Mittel (1.5-2.5): Betonung vorhanden, nicht immer optimal. Niedrig (0-1): Betonung fehlt oder ist falsch gesetzt.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L08",  # page 20
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "... eine deutliche Aussprache habe.",
        "scoring_guidance": "Hoch (3-4): Spricht sehr klar und deutlich, jedes Wort verstaendlich. Mittel (1.5-2.5): Meist deutlich, gelegentlich undeutlich. Niedrig (0-1): Nuschelt oder spricht undeutlich.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "L09",  # page 39
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "... sehr akzentuiert spreche.",
        "scoring_guidance": "Hoch (3-4): Setzt Akzente gezielt und wirkungsvoll. Mittel (1.5-2.5): Einige Akzente, nicht durchgehend. Niedrig (0-1): Spricht ohne Akzente, monoton.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L10",  # page 68
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "... meine Sprache dem jeweiligen Gegenüber gut anpasse.",
        "scoring_guidance": "Hoch (3-4): Passt Sprache perfekt an Zuhoerer und Kontext an. Mittel (1.5-2.5): Teilweise Anpassung, nicht immer konsistent. Niedrig (0-1): Spricht immer gleich, ohne Anpassung.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L11",  # page 72
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "... mich gewählt ausdrücke.",
        "scoring_guidance": "Hoch (3-4): Drueckt sich elegant und gewaehlt aus. Mittel (1.5-2.5): Sprachlich angemessen, aber nicht besonders gewaehlt. Niedrig (0-1): Ausdruck ist schlicht oder unangemessen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L12",  # page 80
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "... durch meine Betonung den Inhalt unterstreiche.",
        "scoring_guidance": "Hoch (3-4): Betonung verstaerkt und unterstreicht den Inhalt wirkungsvoll. Mittel (1.5-2.5): Betonung unterstuetzt teilweise den Inhalt. Niedrig (0-1): Betonung und Inhalt passen nicht zusammen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Beredsamkeit (L13-L19) --- pages: 8, 26, 36, 60, 84, 92, 96
    {
        "id": "L13",  # page 8
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... gekonnt argumentiere.",
        "scoring_guidance": "Hoch (3-4): Argumentiert geschickt und ueberzeugend. Mittel (1.5-2.5): Argumentiert solide, nicht immer ueberzeugend. Niedrig (0-1): Argumentation ist schwach oder unstrukturiert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L14",  # page 26
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... über einen reichhaltigen Wortschatz verfüge.",
        "scoring_guidance": "Hoch (3-4): Breiter, differenzierter Wortschatz ist erkennbar. Mittel (1.5-2.5): Angemessener Wortschatz, nicht besonders reich. Niedrig (0-1): Begrenzter Wortschatz, Wiederholungen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L15",  # page 36
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... überzeugend formuliere.",
        "scoring_guidance": "Hoch (3-4): Formulierungen sind treffend und ueberzeugend. Mittel (1.5-2.5): Formuliert verstaendlich, nicht immer ueberzeugend. Niedrig (0-1): Formulierungen sind schwach oder unklar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L16",  # page 60
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... Einwände gut für meine eigene Argumentation zu nutzen weiß.",
        "scoring_guidance": "Hoch (3-4): Nutzt Einwaende geschickt, staerkt dadurch Position. Mittel (1.5-2.5): Geht auf Einwaende ein, nutzt sie aber nicht immer. Niedrig (0-1): Einwaende werden abgewehrt oder ignoriert.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L17",  # page 84
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... sehr redegewandt bin.",
        "scoring_guidance": "Hoch (3-4): Wird als sehr eloquent und redegewandt wahrgenommen. Mittel (1.5-2.5): Kann sich ausdruecken, nicht besonders eloquent. Niedrig (0-1): Ausdruck ist holprig oder unbeholfen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L18",  # page 92
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... in Dialogen sehr schlagfertig wirke.",
        "scoring_guidance": "Hoch (3-4): Reagiert schnell und treffend in Gespraechen. Mittel (1.5-2.5): Manchmal schlagfertig, nicht durchgehend. Niedrig (0-1): Braucht lange fuer Antworten, wirkt unschlagfertig.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L19",  # page 96
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "... sprachlich überzeuge.",
        "scoring_guidance": "Hoch (3-4): Ueberzeugt allein durch Sprache und Wortwahl. Mittel (1.5-2.5): Sprachlich angemessen, nicht besonders ueberzeugend. Niedrig (0-1): Sprache ueberzeugt nicht.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Bildhaftigkeit (L20-L25) --- pages: 4, 23, 29, 54, 65, 100
    {
        "id": "L20",  # page 4
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "... eine bildhafte Sprache habe.",
        "scoring_guidance": "Hoch (3-4): Nutzt Bilder und Metaphern wirkungsvoll. Mittel (1.5-2.5): Gelegentlich bildhafte Ausdruecke. Niedrig (0-1): Spricht rein sachlich, ohne Bilder.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L21",  # page 23
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "... es mir liegt, Geschichten zu erzählen.",
        "scoring_guidance": "Hoch (3-4): Erzaehlt fesselnd und einpraegsam Geschichten. Mittel (1.5-2.5): Kann Geschichten erzaehlen, nicht besonders packend. Niedrig (0-1): Geschichten werden nicht erzaehlt oder sind langweilig.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L22",  # page 29
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "... mich durch Sprachwitz auszeichne.",
        "scoring_guidance": "Hoch (3-4): Nutzt Sprachwitz gekonnt und charmant. Mittel (1.5-2.5): Gelegentlich witzige Formulierungen. Niedrig (0-1): Kein Sprachwitz erkennbar.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L23",  # page 54
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "... es liebe, mit Worten zu spielen.",
        "scoring_guidance": "Hoch (3-4): Spielt kreativ mit Sprache, macht Freude am Wort sichtbar. Mittel (1.5-2.5): Gelegentliches Wortspiel. Niedrig (0-1): Nutzt Sprache rein funktional.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L24",  # page 65
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "... exzellent Spannung aufbauen kann.",
        "scoring_guidance": "Hoch (3-4): Baut Spannung meisterhaft auf, haelt Zuhoerer gefesselt. Mittel (1.5-2.5): Etwas Spannung vorhanden, nicht durchgehend. Niedrig (0-1): Erzaehlung ist spannungslos.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L25",  # page 100
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "... selbst komplizierte Gedanken verständlich formuliere.",
        "scoring_guidance": "Hoch (3-4): Macht Komplexes einfach und verstaendlich. Mittel (1.5-2.5): Kann vereinfachen, nicht immer erfolgreich. Niedrig (0-1): Kompliziertes bleibt kompliziert oder wird unverstaendlicher.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
]


# ---------------------------------------------------------------------------
# Hilfsfunktionen fuer den Item Pool
# ---------------------------------------------------------------------------

# Alle Frequenzen pro Area (konsistent mit scil_scoring.py)
AREA_FREQUENCIES: dict[str, list[str]] = {
    "sensus": ["innere_praesenz", "innere_ueberzeugung", "prozessfokussierung", "emotionalitaet"],
    "corpus": ["erscheinungsbild", "mimik", "gestik", "raeumliche_praesenz"],
    "intellektus": ["sachlichkeit", "analytik", "struktur", "zielorientierung"],
    "lingua": ["stimme", "artikulation", "beredsamkeit", "bildhaftigkeit"],
}

# Area-Reihenfolge fuer Cluster-Rotation
CLUSTER_ORDER: list[str] = ["sensus", "corpus", "intellektus", "lingua"]


def get_items_for_area(area: str) -> list[SCILItem]:
    """Alle Items fuer einen SCIL-Bereich (z.B. 'sensus' → 25 Items)."""
    return [item for item in SCIL_ITEM_POOL if item["area"] == area]


def get_items_for_frequency(area: str, freq: str) -> list[SCILItem]:
    """Alle Items fuer eine spezifische Frequenz (z.B. 'sensus', 'innere_praesenz' → 6 Items)."""
    return [
        item for item in SCIL_ITEM_POOL
        if item["area"] == area and item["frequency"] == freq
    ]


def get_next_item_block(
    answered_ids: set[str],
    current_area: str | None = None,
    block_size: int = 3,
) -> list[SCILItem]:
    """
    Naechster Block von Items fuer den Agent.

    Cluster-Rotation: S→C→I→L→S→C→I→L... (je 6-7 Items pro Runde, 4 Runden)
    Innerhalb eines Clusters werden Items nach Frequenz rotiert, damit nicht
    alle Items einer Frequenz hintereinander kommen.

    Args:
        answered_ids: Set der bereits beantworteten Item-IDs
        current_area: Aktueller Cluster (None = von vorne beginnen)
        block_size: Anzahl Items pro Block (default 3-4)

    Returns:
        Liste der naechsten Items (kann leer sein wenn alles beantwortet)
    """
    # Bestimme den aktuellen Cluster basierend auf Fortschritt
    if current_area is None:
        current_area = _determine_current_area(answered_ids)

    if current_area is None:
        return []  # Alles beantwortet

    # Unbeantwortete Items im aktuellen Cluster
    area_items = get_items_for_area(current_area)
    unanswered = [item for item in area_items if item["id"] not in answered_ids]

    if not unanswered:
        # Cluster ist fertig, naechsten Cluster bestimmen
        next_area = _next_area(current_area, answered_ids)
        if next_area is None:
            return []
        unanswered = [
            item for item in get_items_for_area(next_area)
            if item["id"] not in answered_ids
        ]

    # Frequenz-Rotation: Items verschiedener Frequenzen mischen
    unanswered_by_freq: dict[str, list[SCILItem]] = {}
    for item in unanswered:
        freq = item["frequency"]
        if freq not in unanswered_by_freq:
            unanswered_by_freq[freq] = []
        unanswered_by_freq[freq].append(item)

    # Round-Robin ueber Frequenzen
    block: list[SCILItem] = []
    freq_keys = list(unanswered_by_freq.keys())
    idx = 0
    while len(block) < block_size and any(unanswered_by_freq.values()):
        freq = freq_keys[idx % len(freq_keys)]
        if unanswered_by_freq[freq]:
            block.append(unanswered_by_freq[freq].pop(0))
        idx += 1
        # Safety: Vermeidung von Endlosschleifen
        if idx > block_size * len(freq_keys):
            break

    return block


def get_cluster_progress(answered_ids: set[str]) -> dict[str, dict[str, int]]:
    """
    Fortschritt pro Cluster und Gesamt.

    Returns:
        {
            "sensus": {"answered": 18, "total": 25},
            "corpus": {"answered": 12, "total": 25},
            "intellektus": {"answered": 0, "total": 25},
            "lingua": {"answered": 0, "total": 25},
            "total": {"answered": 30, "total": 100},
        }
    """
    progress: dict[str, dict[str, int]] = {}
    total_answered = 0
    total_items = 0

    for area in CLUSTER_ORDER:
        area_items = get_items_for_area(area)
        area_answered = sum(1 for item in area_items if item["id"] in answered_ids)
        progress[area] = {
            "answered": area_answered,
            "total": len(area_items),
        }
        total_answered += area_answered
        total_items += len(area_items)

    progress["total"] = {
        "answered": total_answered,
        "total": total_items,
    }

    return progress


def get_frequency_progress(answered_ids: set[str]) -> dict[str, dict[str, int]]:
    """
    Fortschritt pro Frequenz (feinere Granularitaet als get_cluster_progress).

    Returns:
        {
            "innere_praesenz": {"answered": 4, "total": 6},
            "innere_ueberzeugung": {"answered": 5, "total": 7},
            ...
        }
    """
    progress: dict[str, dict[str, int]] = {}

    for area, freqs in AREA_FREQUENCIES.items():
        for freq in freqs:
            freq_items = get_items_for_frequency(area, freq)
            freq_answered = sum(1 for item in freq_items if item["id"] in answered_ids)
            progress[freq] = {
                "answered": freq_answered,
                "total": len(freq_items),
            }

    return progress


def get_item_by_id(item_id: str) -> SCILItem | None:
    """Item anhand der ID finden (z.B. 'S01', 'C12', 'I03', 'L25')."""
    for item in SCIL_ITEM_POOL:
        if item["id"] == item_id:
            return item
    return None


def get_items_by_ids(item_ids: list[str]) -> list[SCILItem]:
    """Mehrere Items anhand der IDs finden."""
    id_set = set(item_ids)
    return [item for item in SCIL_ITEM_POOL if item["id"] in id_set]


def validate_item_pool() -> dict[str, object]:
    """
    Validiert den Item Pool auf Vollstaendigkeit und Konsistenz.

    Returns:
        {
            "valid": True/False,
            "total_items": 100,
            "items_per_area": {"sensus": 25, ...},
            "items_per_frequency": {"innere_praesenz": 6, ...},
            "issues": ["..."]
        }
    """
    issues: list[str] = []
    items_per_area: dict[str, int] = {}
    items_per_freq: dict[str, int] = {}
    seen_ids: set[str] = set()

    for item in SCIL_ITEM_POOL:
        # Duplicate ID check
        if item["id"] in seen_ids:
            issues.append(f"Duplicate ID: {item['id']}")
        seen_ids.add(item["id"])

        # Count per area
        area = item["area"]
        items_per_area[area] = items_per_area.get(area, 0) + 1

        # Count per frequency
        freq = item["frequency"]
        items_per_freq[freq] = items_per_freq.get(freq, 0) + 1

        # Validate frequency belongs to area
        if area in AREA_FREQUENCIES and freq not in AREA_FREQUENCIES[area]:
            issues.append(f"Item {item['id']}: Frequency '{freq}' does not belong to area '{area}'")

    # Check totals
    total = len(SCIL_ITEM_POOL)
    if total != 100:
        issues.append(f"Expected 100 items, got {total}")

    for area in CLUSTER_ORDER:
        count = items_per_area.get(area, 0)
        if count != 25:
            issues.append(f"Area '{area}' has {count} items, expected 25")

    return {
        "valid": len(issues) == 0,
        "total_items": total,
        "items_per_area": items_per_area,
        "items_per_frequency": items_per_freq,
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Private Hilfsfunktionen
# ---------------------------------------------------------------------------

def _determine_current_area(answered_ids: set[str]) -> str | None:
    """Bestimmt den aktuellen Cluster basierend auf dem Fortschritt."""
    for area in CLUSTER_ORDER:
        area_items = get_items_for_area(area)
        unanswered = [item for item in area_items if item["id"] not in answered_ids]
        if unanswered:
            return area
    return None  # Alle Items beantwortet


def _next_area(current_area: str, answered_ids: set[str]) -> str | None:
    """Bestimmt den naechsten Cluster nach Cluster-Rotation."""
    idx = CLUSTER_ORDER.index(current_area)
    for i in range(1, len(CLUSTER_ORDER) + 1):
        next_idx = (idx + i) % len(CLUSTER_ORDER)
        next_area = CLUSTER_ORDER[next_idx]
        area_items = get_items_for_area(next_area)
        unanswered = [item for item in area_items if item["id"] not in answered_ids]
        if unanswered:
            return next_area
    return None  # Alle Cluster abgeschlossen


# ---------------------------------------------------------------------------
# Self-validation at import time (development safety)
# ---------------------------------------------------------------------------
_validation = validate_item_pool()
if not _validation["valid"]:
    import warnings
    warnings.warn(
        f"SCIL Item Pool validation failed: {_validation['issues']}",
        stacklevel=2,
    )
