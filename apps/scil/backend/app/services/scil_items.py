"""
SCIL Item Pool — 100 strukturierte Items fuer wissenschaftlich fundierte Erhebung.

Jedes Item misst eine spezifische SCIL-Frequenz der Wirkungskompetenz (Aussenwirkung).
SCIL misst NICHT Persoenlichkeit, sondern wie eine Person auf andere wirkt.

Verteilung: 25 Items pro Cluster (Sensus, Corpus, Intellektus, Lingua)
Pro Frequenz: 6-7 Items (25 Items / 4 Frequenzen = 6.25)

Scoring: 0-4 Skala (0=schwache Auspraegung, 4=ausgepragte Staerke)
Bewertungsstufen: a) 3.5-4.0, b) 2.5-3.5, c) 1.5-2.5, d) 0.5-1.5, e) 0.0-0.5

IRT-Parameter (initial neutral, werden nach Datensammlung kalibriert):
  - difficulty: 0.5 = mittlere Schwierigkeit
  - discrimination: 1.0 = mittlere Trennschaerfe

Autor: SCIL Performance Strategie (c) Andreas Bornhaeusser
Framework: S.C.I.L. = Sensus, Corpus, Intellektus, Lingua
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
# SCIL ITEM POOL — 100 Items
# ---------------------------------------------------------------------------

SCIL_ITEM_POOL: list[SCILItem] = [
    # =====================================================================
    # SENSUS (S01-S25) — Innere Haltung, Empathie, Beziehungsgestaltung
    # =====================================================================

    # --- Innere Praesenz (S01-S06) ---
    {
        "id": "S01",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Wenn Sie in einem wichtigen Gespraech sind — wie wuerden andere beschreiben, wie praesent und aufmerksam Sie wirken?",
        "scoring_guidance": "Hoch (3-4): Andere berichten aktives Zuhoeren, Blickkontakt, keine Ablenkung, volle Zuwendung. Mittel (1.5-2.5): Gelegentliches Abschweifen, manchmal auf Handy/Uhr schauen. Niedrig (0-1): Haeufig abwesend wirkend, Multitasking, unruhig.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S02",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Stellen Sie sich vor, ein Kollege erzaehlt Ihnen von einem persoenlichen Problem. Wie reagieren Sie typischerweise — und was wuerde der Kollege ueber Ihre Reaktion sagen?",
        "scoring_guidance": "Hoch (3-4): Gibt dem Moment volle Aufmerksamkeit, stellt Rueckfragen, laesst ausreden, wirkt zugewandt. Mittel (1.5-2.5): Hoert zu, gibt aber schnell Ratschlaege oder lenkt auf eigene Erfahrungen. Niedrig (0-1): Wirkt ungeduldig, wechselt schnell das Thema, gibt oberflaechliche Antworten.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S03",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Wie erleben andere Ihre Faehigkeit, in stressigen Situationen ruhig und geerdet zu bleiben?",
        "scoring_guidance": "Hoch (3-4): Wird als Ruhepol beschrieben, strahlt Gelassenheit aus, bleibt zentriert. Mittel (1.5-2.5): Meistens ruhig, gelegentlich sichtbar angespannt. Niedrig (0-1): Stress ist deutlich sichtbar, wirkt getrieben oder ueberfordert auf andere.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S04",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Wenn Sie in einer Gruppendiskussion sind — wie beschreiben andere Ihr Zuhoerverhalten?",
        "scoring_guidance": "Hoch (3-4): Wird als aufmerksamer Zuhoerer wahrgenommen, greift Punkte anderer auf, nickt, zeigt nonverbale Resonanz. Mittel (1.5-2.5): Hoert phasenweise zu, ist aber auch mit eigenen Beitraegen beschaeftigt. Niedrig (0-1): Wartet nur auf die eigene Redezeit, unterbricht, wirkt desinteressiert.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "S05",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Beschreiben Sie eine Situation, in der Sie jemandem Ihre ungeteilte Aufmerksamkeit geschenkt haben. Was hat die andere Person daran bemerkt?",
        "scoring_guidance": "Hoch (3-4): Konkrete Beispiele mit beobachtbarer Wirkung auf den Gegenueberr (z.B. 'Sie hat gesagt, sie fuehlt sich wirklich gehoert'). Mittel (1.5-2.5): Beispiel vorhanden, aber Wirkung auf andere unklar oder nicht reflektiert. Niedrig (0-1): Kann kein Beispiel nennen oder verwechselt Praesenz mit bloesser Anwesenheit.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S06",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Wie schnell bemerken andere Menschen, dass Sie ihnen wirklich zuhoeren — und woran machen sie das fest?",
        "scoring_guidance": "Hoch (3-4): Sofort erkennbar durch Koerpersprache, Nachfragen, Paraphrasieren. Mittel (1.5-2.5): Nach einiger Zeit, wenn inhaltlich Bezug genommen wird. Niedrig (0-1): Gegenueberr ist sich unsicher, ob zugehoert wird.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Innere Ueberzeugung (S07-S13) ---
    {
        "id": "S07",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Wenn Sie eine Idee oder Position vertreten — wie erleben andere Ihre innere Sicherheit dabei?",
        "scoring_guidance": "Hoch (3-4): Wirkt authentisch ueberzeugt, Haltung und Worte stimmen ueberein, strahlt Zuversicht aus. Mittel (1.5-2.5): Vertritt Position, aber mit spuerbarer Unsicherheit oder Einschraenkungen. Niedrig (0-1): Wirkt zoegerich, relativiert staendig, andere zweifeln an der Ueberzeugung.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S08",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Wie reagieren Sie, wenn Ihre Meinung in einer Gruppe auf Widerstand stoesst? Was beobachten andere an Ihnen?",
        "scoring_guidance": "Hoch (3-4): Bleibt standhaft, argumentiert ruhig aber bestimmt, wirkt nicht defensiv sondern souveraen. Mittel (1.5-2.5): Haelt zunaechst dagegen, gibt aber bei Druck nach. Niedrig (0-1): Knickt schnell ein, passt Meinung an die Mehrheit an, wirkt unsicher.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S09",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Denken Sie an eine Entscheidung, die Sie gegen Widerstaende durchgesetzt haben. Wie haben andere Ihre Entschlossenheit wahrgenommen?",
        "scoring_guidance": "Hoch (3-4): Konkretes Beispiel mit klarer Wirkung — andere beschreiben die Person als entschlossen, klar, ueberzeugend. Mittel (1.5-2.5): Hat durchgesetzt, aber mit sichtbarem Zwoegern oder Kompromissen. Niedrig (0-1): Kann kein Beispiel nennen, oder andere nahmen die Entscheidung als aufgezwungen/unsicher wahr.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },
    {
        "id": "S10",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Wie wuerden Ihre engsten Mitarbeiter Ihre Faehigkeit beschreiben, andere von Ihren Ideen zu begeistern?",
        "scoring_guidance": "Hoch (3-4): Wird als inspirierend, mitreissend, ueberzeugend beschrieben — Menschen folgen freiwillig. Mittel (1.5-2.5): Kann ueberzeugen, aber eher rational als emotional mitreissend. Niedrig (0-1): Ideen werden als unklar oder wenig inspirierend wahrgenommen.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S11",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Wie stark spueren andere Ihre Leidenschaft fuer Themen, die Ihnen wichtig sind?",
        "scoring_guidance": "Hoch (3-4): Leidenschaft ist deutlich spuerbar und ansteckend, authentische Begeisterung. Mittel (1.5-2.5): Interesse ist erkennbar, aber eher sachlich als leidenschaftlich. Niedrig (0-1): Wirkt gleichgueltig oder distanziert, Begeisterung kommt nicht rueber.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S12",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Stellen Sie sich vor, Sie muessen ein Team fuer ein schwieriges Projekt motivieren. Wie wuerden Ihre Teammitglieder Ihre Ueberzeugungskraft beschreiben?",
        "scoring_guidance": "Hoch (3-4): Team fuehlt sich mitgenommen, spuert die Ueberzeugung, glaubt an den Erfolg wegen der Fuehrungskraft. Mittel (1.5-2.5): Team ist informiert, aber nicht emotional mitgenommen. Niedrig (0-1): Team bleibt skeptisch, die Motivation kommt nicht an.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S13",
        "area": "sensus",
        "frequency": "innere_ueberzeugung",
        "text_de": "Wie authentisch wirken Sie auf andere, wenn Sie ueber Ihre Werte und Ueberzeugungen sprechen?",
        "scoring_guidance": "Hoch (3-4): Wird als sehr authentisch wahrgenommen, Worte und Handeln stimmen ueberein. Mittel (1.5-2.5): Grundsaetzlich glaubwuerdig, aber manchmal inkonsistent. Niedrig (0-1): Andere empfinden Diskrepanz zwischen Worten und Verhalten.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Prozessfokussierung (S14-S19) ---
    {
        "id": "S14",
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "Wie erleben andere Ihre Faehigkeit, Gruppenprozesse zu steuern und dabei alle Beteiligten mitzunehmen?",
        "scoring_guidance": "Hoch (3-4): Wird als exzellenter Moderator wahrgenommen, achtet auf Dynamik, integriert alle Stimmen. Mittel (1.5-2.5): Kann Prozesse fuehren, verliert aber manchmal Einzelne aus dem Blick. Niedrig (0-1): Andere erleben die Prozessfuehrung als chaotisch oder dominierend.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S15",
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "Wie bewusst nehmen andere wahr, dass Sie auf die Beziehungsebene in Gespraechen achten — nicht nur auf den Inhalt?",
        "scoring_guidance": "Hoch (3-4): Andere bemerken aktiv, dass die Person Stimmungen aufgreift, Konflikte adressiert, Beziehungsdynamik managt. Mittel (1.5-2.5): Gelegentlich, aber nicht konsistent. Niedrig (0-1): Wird als rein sachorientiert wahrgenommen, Beziehungsebene wird ignoriert.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S16",
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "Beschreiben Sie, wie Sie in einem Meeting die Gesamtdynamik im Blick behalten. Was bemerken andere an Ihrem Vorgehen?",
        "scoring_guidance": "Hoch (3-4): Andere schaetzen die Faehigkeit, Stille einzubeziehen, Konflikte zu entschaerfen, den roten Faden zu halten. Mittel (1.5-2.5): Hat ein gewisses Gespuer, aber es geht manchmal in der eigenen Beteiligung unter. Niedrig (0-1): Nimmt Dynamik nicht wahr, reagiert nur auf direkte Ansprache.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S17",
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "Wie nehmen andere wahr, dass Sie sich an unterschiedliche Gespraechspartner und Situationen anpassen koennen?",
        "scoring_guidance": "Hoch (3-4): Wird als chamaeleonartig beschrieben — passt Kommunikationsstil bewusst an, ohne unecht zu wirken. Mittel (1.5-2.5): Passt sich teilweise an, bleibt aber oft im eigenen Muster. Niedrig (0-1): Kommuniziert immer gleich, unabhaengig vom Gegenueberr.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S18",
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "Wie beschreiben andere Ihre Sensibilitaet fuer unausgesprochene Spannungen oder Konflikte in einer Gruppe?",
        "scoring_guidance": "Hoch (3-4): Spuert Spannungen frueh, spricht sie angemessen an, wird als feinfuehlig erlebt. Mittel (1.5-2.5): Bemerkt offensichtliche Spannungen, aber subtile Dynamiken entgehen. Niedrig (0-1): Andere sagen, die Person bemerkt Spannungen nicht oder ignoriert sie.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S19",
        "area": "sensus",
        "frequency": "prozessfokussierung",
        "text_de": "Wie erleben andere Ihre Faehigkeit, bei einem Thema sowohl den Inhalt als auch den Prozess gleichzeitig zu steuern?",
        "scoring_guidance": "Hoch (3-4): Meistert Doppelfokus — liefert inhaltlich und haelt den Prozess fuer alle produktiv. Mittel (1.5-2.5): Entweder Inhalt oder Prozess, selten beides gleichzeitig. Niedrig (0-1): Verliert entweder den roten Faden oder die Gruppe.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },

    # --- Emotionalitaet (S20-S25) ---
    {
        "id": "S20",
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "Wie erleben andere Ihre emotionale Ausstrahlung — spueren Menschen in Ihrer Naehe Ihre Gefuehle?",
        "scoring_guidance": "Hoch (3-4): Emotionen sind authentisch spuerbar, wirkt warmherzig und emotional zugaenglich. Mittel (1.5-2.5): Zeigt Emotionen gelegentlich, bleibt aber eher kontrolliert. Niedrig (0-1): Wirkt emotional verschlossen oder kuenstlich.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S21",
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "Wie wuerden andere beschreiben, wie gut Sie Empathie zeigen koennen — nicht nur fuehlen, sondern sichtbar ausdruecken?",
        "scoring_guidance": "Hoch (3-4): Empathie ist fuer andere deutlich erlebbar, fuehlen sich verstanden und gesehen. Mittel (1.5-2.5): Zeigt Verstaendnis, aber eher verbal als emotional spuerbar. Niedrig (0-1): Andere spueren wenig emotionale Resonanz.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "S22",
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "Wie reagieren andere auf Ihre Art, mit emotionalen Themen umzugehen — etwa bei Konflikten oder persoenlichen Anliegen?",
        "scoring_guidance": "Hoch (3-4): Wird als einfuehlsam erlebt, schafft sicheren Raum fuer Emotionen, reagiert angemessen. Mittel (1.5-2.5): Kann damit umgehen, aber wirkt manchmal unsicher oder ausweichend. Niedrig (0-1): Meidet emotionale Themen sichtbar, wirkt unbeholfen.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S23",
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "Wie beschreiben andere die Waerme, die Sie in persoenliche Interaktionen einbringen?",
        "scoring_guidance": "Hoch (3-4): Wird als warmherzig, nahbar, menschlich erlebt. Menschen oeffnen sich in ihrer Naehe. Mittel (1.5-2.5): Freundlich, aber eher professionell distanziert. Niedrig (0-1): Wirkt kuehl oder unnahbar auf andere.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "S24",
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "Wie erleben andere Ihre Faehigkeit, angemessen mit Freude, Enttaeuschung oder Aerger umzugehen — wirken Ihre emotionalen Reaktionen fuer andere nachvollziehbar?",
        "scoring_guidance": "Hoch (3-4): Emotionen sind angemessen, transparent und nachvollziehbar — weder uebertrieben noch unterdrueckt. Mittel (1.5-2.5): Meistens angemessen, gelegentlich ueberraschende oder fehlende Reaktionen. Niedrig (0-1): Emotionale Reaktionen wirken auf andere unangemessen oder fehlend.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "S25",
        "area": "sensus",
        "frequency": "emotionalitaet",
        "text_de": "Wie beurteilen andere Ihre Faehigkeit, durch emotionale Offenheit Vertrauen aufzubauen?",
        "scoring_guidance": "Hoch (3-4): Emotionale Offenheit wird als Staerke erlebt, schafft schnell Vertrauensbasis. Mittel (1.5-2.5): Oeffnet sich in engem Kreis, wirkt im professionellen Kontext eher reserviert. Niedrig (0-1): Emotionale Verschlossenheit wird als Barriere fuer Vertrauen erlebt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # =====================================================================
    # CORPUS (C01-C25) — Koerperliche Wirkung, Praesenz, Ausdruck
    # =====================================================================

    # --- Erscheinungsbild (C01-C06) ---
    {
        "id": "C01",
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "Wie bewusst achten Sie auf Ihr aeusseres Erscheinungsbild — und was sagen andere ueber den Eindruck, den Sie damit hinterlassen?",
        "scoring_guidance": "Hoch (3-4): Bewusst gepflegt, situationsangemessen, andere kommentieren positiv. Mittel (1.5-2.5): Grundsaetzlich gepflegt, aber nicht besonders reflektiert. Niedrig (0-1): Erscheinungsbild wird von anderen als nachlassig oder unangemessen wahrgenommen.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "C02",
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "Wie beschreiben andere den ersten Eindruck, den Sie bei einem neuen Kontakt hinterlassen?",
        "scoring_guidance": "Hoch (3-4): Positiver, professioneller, einpraegsamer erster Eindruck — wirkt kompetent und sympathisch. Mittel (1.5-2.5): Neutraler Eindruck, weder besonders positiv noch negativ. Niedrig (0-1): Erster Eindruck wird als negativ oder unbemerkt beschrieben.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C03",
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "Wie gut passen Sie Ihr Erscheinungsbild an verschiedene Kontexte an — z.B. formelle Meetings vs. kreative Workshops?",
        "scoring_guidance": "Hoch (3-4): Passt Kleidung und Auftreten bewusst an den Kontext an, wird als angemessen und souveraen wahrgenommen. Mittel (1.5-2.5): Hat ein Standard-Auftreten, variiert wenig. Niedrig (0-1): Kontext wird ignoriert, Auftreten wirkt fehl am Platz.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C04",
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "Wie bewusst setzen Sie Ihr Erscheinungsbild als Teil Ihrer Gesamtwirkung ein?",
        "scoring_guidance": "Hoch (3-4): Versteht Erscheinungsbild als Kommunikationsmittel, setzt es strategisch ein. Mittel (1.5-2.5): Achtet darauf, aber ohne strategische Intention. Niedrig (0-1): Kein Bewusstsein fuer die Wirkung des Erscheinungsbilds.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C05",
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "Wie wuerden Kollegen Ihre allgemeine aeussere Ausstrahlung beschreiben — gepflegt, dynamisch, zurueckhaltend?",
        "scoring_guidance": "Hoch (3-4): Beschreibungen wie dynamisch, gepflegt, selbstbewusst, einpraegsam. Mittel (1.5-2.5): Unauffaellig, solide, normal. Niedrig (0-1): Nachlassig, unscheinbar, ungepflegt.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "C06",
        "area": "corpus",
        "frequency": "erscheinungsbild",
        "text_de": "Wie viel Aufmerksamkeit schenken Sie der Wirkung Ihrer Koerperhaltung im Stehen und Sitzen — und was beobachten andere?",
        "scoring_guidance": "Hoch (3-4): Aufrechte, offene Haltung, wirkt praesent und selbstbewusst. Mittel (1.5-2.5): Akzeptable Haltung, aber nicht bewusst eingesetzt. Niedrig (0-1): Zusammengesunkene Haltung, verschlossene Koerpersprache.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Mimik (C07-C13) ---
    {
        "id": "C07",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie lebendig und ausdrucksstark ist Ihre Mimik — koennen andere Ihre Reaktionen gut an Ihrem Gesicht ablesen?",
        "scoring_guidance": "Hoch (3-4): Sehr ausdrucksstarke Mimik, spiegelt Emotionen, lebendiges Gesicht. Mittel (1.5-2.5): Grundsaetzlich lesbar, aber nicht besonders expressiv. Niedrig (0-1): Poker-Face, andere koennen nichts ablesen, wirkt starr.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C08",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie beschreiben andere Ihren Blickkontakt — halten Sie ihn, und wie wirkt er?",
        "scoring_guidance": "Hoch (3-4): Angemessener, warmer Blickkontakt, weder starrend noch ausweichend. Wird als verbindend erlebt. Mittel (1.5-2.5): Haelt Blickkontakt, aber ungleichmaessig oder manchmal ausweichend. Niedrig (0-1): Vermeidet Blickkontakt oder starrt, wirkt unsicher oder einschuechternd.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C09",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie gut koennen Sie mit Ihrem Gesichtsausdruck Zustimmung, Interesse oder Nachdenklichkeit signalisieren?",
        "scoring_guidance": "Hoch (3-4): Mimik unterstreicht die Kommunikation, signalisiert klar und authentisch. Mittel (1.5-2.5): Gelegentlich, aber nicht konsistent oder bewusst eingesetzt. Niedrig (0-1): Gesichtsausdruck steht im Widerspruch oder gibt kein Signal.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C10",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie wirkt Ihr Laecheln auf andere — natuerlich, gewinnend, oder eher selten?",
        "scoring_guidance": "Hoch (3-4): Natuerliches, gewinnendes Laecheln, das Waerme ausstrahlt und oeffnend wirkt. Mittel (1.5-2.5): Laechelt gelegentlich, wirkt freundlich aber nicht besonders einnehmend. Niedrig (0-1): Laechelt selten, oder Laecheln wirkt aufgesetzt/unsicher.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "C11",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie bewusst setzen Sie Ihre Mimik ein, um Gespraechspartner zu ermutigen oder Ihren Aussagen Nachdruck zu verleihen?",
        "scoring_guidance": "Hoch (3-4): Bewusster Einsatz von Mimik als Kommunikationswerkzeug, verstaerkt die verbale Botschaft. Mittel (1.5-2.5): Teilweise bewusst, aber noch nicht als strategisches Mittel genutzt. Niedrig (0-1): Kein Bewusstsein fuer die kommunikative Funktion der Mimik.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C12",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie beschreiben andere die Kongruenz zwischen dem, was Sie sagen, und dem, was Ihr Gesicht ausdrueckt?",
        "scoring_guidance": "Hoch (3-4): Hohe Kongruenz — Worte und Mimik stimmen ueberein, wirkt authentisch. Mittel (1.5-2.5): Meistens kongruent, aber gelegentlich widerspruchlich. Niedrig (0-1): Haeufig widerspruchliche Signale, andere vertrauen eher dem Gesicht als den Worten.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C13",
        "area": "corpus",
        "frequency": "mimik",
        "text_de": "Wie spiegeln Sie mimisch die Emotionen Ihres Gegenueber — und bemerken andere das?",
        "scoring_guidance": "Hoch (3-4): Natuerliches Spiegeln — Gegenueberr fuehlt sich verstanden durch mimische Resonanz. Mittel (1.5-2.5): Teilweise Spiegelung, aber nicht konsistent. Niedrig (0-1): Keine mimische Resonanz, Gegenueberr fueht sich nicht gespiegelt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Gestik (C14-C19) ---
    {
        "id": "C14",
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "Wie setzen Sie Ihre Haende ein, wenn Sie sprechen — und wie beschreiben andere Ihre Gestik?",
        "scoring_guidance": "Hoch (3-4): Offene, unterstuetzende Gesten die den Inhalt verstaerken, wirkt dynamisch und lebendig. Mittel (1.5-2.5): Gelegentliche Gesten, aber eher zurueckhaltend. Niedrig (0-1): Keine Gestik, Haende in Taschen/verschraenkt, oder nervoeseHektische Bewegungen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C15",
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "Wie erleben andere Ihre koerperliche Energie und Dynamik, wenn Sie praesentieren oder diskutieren?",
        "scoring_guidance": "Hoch (3-4): Dynamisch, energiegeladen, Gesten verstaerken die Botschaft, wirkt ueberzeugend. Mittel (1.5-2.5): Akzeptable Energie, aber nicht besonders mitreissend. Niedrig (0-1): Steif, monoton, oder uebertrieben hektisch — Gestik lenkt ab.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C16",
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "Wie bewusst ist Ihnen, dass Ihre Gesten eine Botschaft senden — und stimmen diese mit Ihren Worten ueberein?",
        "scoring_guidance": "Hoch (3-4): Hohe Awareness, Gesten und Worte bilden eine Einheit, verstaerken sich gegenseitig. Mittel (1.5-2.5): Teilweise bewusst, aber nicht konsistent. Niedrig (0-1): Gestik widerspricht den Worten oder ist nicht vorhanden.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C17",
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "Wie beschreiben andere Ihre Koerpersprache in Verhandlungen oder schwierigen Gespraechen?",
        "scoring_guidance": "Hoch (3-4): Offene, souveraene Koerpersprache die Staerke und Offenheit signalisiert. Mittel (1.5-2.5): Neutrale Koerpersprache, weder offen noch verschlossen. Niedrig (0-1): Verschlossene, angespannte oder einschuechternde Koerpersprache.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C18",
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "Wie nutzen Sie Gesten, um anderen zuzustimmen, sie einzuladen oder Grenzen zu setzen?",
        "scoring_guidance": "Hoch (3-4): Differenzierter Gestik-Einsatz fuer verschiedene Situationen — einladende Gesten, bestaetigende Gesten, abgrenzende Gesten. Mittel (1.5-2.5): Grundlegende Gesten vorhanden, aber nicht differenziert. Niedrig (0-1): Kaum gestische Kommunikation in sozialen Situationen.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },
    {
        "id": "C19",
        "area": "corpus",
        "frequency": "gestik",
        "text_de": "Wie beschreiben andere Ihre Faehigkeit, mit Koerpersprache eine Atmosphaere zu schaffen — z.B. Offenheit, Autoritaet oder Entspannung?",
        "scoring_guidance": "Hoch (3-4): Bewusster Einsatz von Koerpersprache zur Atmosphaerengestaltung, andere spueren die Wirkung. Mittel (1.5-2.5): Natuerliche Koerpersprache, aber ohne bewusste Steuerung der Atmosphaere. Niedrig (0-1): Koerpersprache erzeugt eher Distanz oder Unbehagen.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },

    # --- Raeumliche Praesenz (C20-C25) ---
    {
        "id": "C20",
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "Wie nehmen andere wahr, wenn Sie einen Raum betreten — faellt Ihre Anwesenheit auf?",
        "scoring_guidance": "Hoch (3-4): Praesenz ist sofort spuerbar, Menschen nehmen den Eintritt wahr, ohne dass gesprochen wird. Mittel (1.5-2.5): Wird wahrgenommen, aber nicht besonders auffaellig. Niedrig (0-1): Betritt Raeume unbemerkt, keine besondere Praesenz.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C21",
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "Wie bewusst nutzen Sie den Raum bei Praesentationen — bewegen Sie sich, nutzen Sie die Buehne?",
        "scoring_guidance": "Hoch (3-4): Nutzt den Raum aktiv, bewegt sich gezielt, nimmt verschiedene Positionen ein, bindet das Publikum raeumlich ein. Mittel (1.5-2.5): Bewegt sich gelegentlich, bleibt aber meistens an einem Platz. Niedrig (0-1): Steht festgenagelt, versteckt sich hinter dem Pult.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C22",
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "Wie beschreiben andere Ihre physische Praesenz in Meetings — nehmen Sie Raum ein oder halten Sie sich zurueck?",
        "scoring_guidance": "Hoch (3-4): Nimmt angemessen Raum ein, sitzt aufrecht, ist physisch praesent und sichtbar. Mittel (1.5-2.5): Durchschnittliche Praesenz, weder dominant noch zurueckhaltend. Niedrig (0-1): Macht sich klein, sitzt am Rand, ist physisch kaum wahrnehmbar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "C23",
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "Wie souveraen bewegen Sie sich im Raum, wenn alle Augen auf Sie gerichtet sind?",
        "scoring_guidance": "Hoch (3-4): Voellig souveraen, natuerliche Bewegungen, wirkt wie auf einer Buehne zu Hause. Mittel (1.5-2.5): Kommt zurecht, aber mit spuerbarer Anspannung. Niedrig (0-1): Steif, gehemmt, Bewegungen wirken unnatuerlich oder nervoes.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "C24",
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "Wie beschreiben andere Ihre Faehigkeit, durch Ihre physische Praesenz Aufmerksamkeit zu binden — ohne ein Wort zu sagen?",
        "scoring_guidance": "Hoch (3-4): Allein durch Praesenz und Haltung bindet die Person Aufmerksamkeit — eine natuerliche Autoritaet. Mittel (1.5-2.5): Kann Aufmerksamkeit halten, wenn aktiv kommuniziert wird, aber nicht allein durch Praesenz. Niedrig (0-1): Praesenz reicht nicht, um Aufmerksamkeit zu binden.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },
    {
        "id": "C25",
        "area": "corpus",
        "frequency": "raeumliche_praesenz",
        "text_de": "Wie bewusst waehlen Sie Ihren Platz in einem Raum — und welche Wirkung hat das auf andere?",
        "scoring_guidance": "Hoch (3-4): Waehlt Position strategisch (z.B. Kopfende, zentral, nah bei Entscheidern), andere nehmen die bewusste Positionierung wahr. Mittel (1.5-2.5): Setzt sich irgendwo hin, manchmal strategisch, manchmal zufaellig. Niedrig (0-1): Kein Bewusstsein fuer raeumliche Positionierung, setzt sich zurueck oder in die Ecke.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # =====================================================================
    # INTELLEKTUS (I01-I25) — Analytische und strukturelle Wirkung
    # =====================================================================

    # --- Sachlichkeit (I01-I06) ---
    {
        "id": "I01",
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "Wie erleben andere Ihre Faehigkeit, in Diskussionen sachlich und faktenbasiert zu argumentieren?",
        "scoring_guidance": "Hoch (3-4): Wird als sachlich, kompetent und fundiert wahrgenommen, trennt Fakten von Meinungen. Mittel (1.5-2.5): Grundsaetzlich sachlich, vermischt aber manchmal Fakten mit Annahmen. Niedrig (0-1): Argumentiert eher emotional oder unstrukturiert, Fakten fehlen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I02",
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "Wie beschreiben andere Ihre Faehigkeit, komplexe Sachverhalte praeznise und verstaendlich darzustellen?",
        "scoring_guidance": "Hoch (3-4): Kann Komplexes einfach erklaeren, wird als klar und verstaendlich erlebt. Mittel (1.5-2.5): Erklaerungen sind korrekt, aber nicht immer leicht verstaendlich. Niedrig (0-1): Verliert sich in Details oder ueberspringt wichtige Zusammenhaenge.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I03",
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "Wie erleben andere Ihre Objektivitaet — koennen Sie verschiedene Perspektiven gleichwertig darstellen?",
        "scoring_guidance": "Hoch (3-4): Stellt verschiedene Sichtweisen fair dar, eigene Meinung wird klar als solche gekennzeichnet. Mittel (1.5-2.5): Grundsaetzlich fair, neigt aber dazu, die eigene Position zu bevorzugen. Niedrig (0-1): Wirkt voreingenommen, stellt nur die eigene Sicht dar.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I04",
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "Wie gehen Sie mit Situationen um, in denen jemand unsachlich oder emotional argumentiert — und wie wirkt Ihre Reaktion auf andere?",
        "scoring_guidance": "Hoch (3-4): Bleibt sachlich ohne kalt zu wirken, fuehrt Diskussion zurueck auf Fakten, wird als deeskalierend erlebt. Mittel (1.5-2.5): Versucht sachlich zu bleiben, laesst sich aber gelegentlich provozieren. Niedrig (0-1): Reagiert selbst emotional oder wird unangemessen kuhl.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I05",
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "Wie bewerten andere die Qualitaet Ihrer fachlichen Beitraege in Meetings oder Diskussionen?",
        "scoring_guidance": "Hoch (3-4): Beitraege werden als fundiert, relevant und bereichernd geschaetzt. Mittel (1.5-2.5): Solide Beitraege, aber nicht immer herausragend. Niedrig (0-1): Beitraege werden als oberflaechlich oder irrelevant wahrgenommen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I06",
        "area": "intellektus",
        "frequency": "sachlichkeit",
        "text_de": "Wie gut koennen Sie Ihre Argumente mit konkreten Daten, Beispielen oder Referenzen untermauern — und bemerken andere das?",
        "scoring_guidance": "Hoch (3-4): Liefert regelmaessig Belege, wird als gut vorbereitet und faktenbasiert wahrgenommen. Mittel (1.5-2.5): Gelegentlich mit Belegen, oft aber aus dem Bauch argumentierend. Niedrig (0-1): Selten konkrete Belege, Argumente wirken duenn.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Analytik (I07-I12) ---
    {
        "id": "I07",
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "Wie erleben andere Ihre Faehigkeit, Probleme systematisch zu analysieren und Ursachen zu identifizieren?",
        "scoring_guidance": "Hoch (3-4): Wird als analytisch stark wahrgenommen, findet Kernursachen, denkt in Systemen. Mittel (1.5-2.5): Kann analysieren, bleibt aber manchmal an der Oberflaeche. Niedrig (0-1): Analyse wirkt unstrukturiert, springt zu Schlussfolgerungen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I08",
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "Wie beschreiben andere Ihre Faehigkeit, Muster in komplexen Informationen zu erkennen?",
        "scoring_guidance": "Hoch (3-4): Erkennt Zusammenhaenge die andere uebersehen, wird als scharfsinnig erlebt. Mittel (1.5-2.5): Erkennt offensichtliche Muster, aber subtile Verbindungen entgehen. Niedrig (0-1): Sieht Informationen isoliert, keine Mustererkennung.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I09",
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "Wie erleben andere Ihre Faehigkeit, kritisch zu hinterfragen, ohne dabei destruktiv zu wirken?",
        "scoring_guidance": "Hoch (3-4): Stellt kluge, weiterfuehrende Fragen, die andere zum Nachdenken bringen. Wird als konstruktiv erlebt. Mittel (1.5-2.5): Hinterfragt, aber manchmal zu direkt oder selten. Niedrig (0-1): Hinterfragt zu wenig (akzeptiert alles) oder zu aggressiv (wird als noerelnd erlebt).",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I10",
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "Wie bewerten andere Ihre Entscheidungsfindung — als durchdacht oder eher intuitiv?",
        "scoring_guidance": "Hoch (3-4): Entscheidungen werden als gut durchdacht, abgewochen und logisch nachvollziehbar erlebt. Mittel (1.5-2.5): Mischung aus Analyse und Intuition, nicht immer transparent. Niedrig (0-1): Entscheidungen wirken willkuerlich oder schlecht durchdacht.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I11",
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "Wie reagieren andere auf Ihre Faehigkeit, in Krisen schnell die relevanten Faktoren zu identifizieren?",
        "scoring_guidance": "Hoch (3-4): Wird in Krisen als ruhiger Analytiker geschaetzt, identifiziert schnell das Wesentliche. Mittel (1.5-2.5): Braucht Zeit fuer die Analyse, ist dann aber solide. Niedrig (0-1): In Krisen ueberfodert, verliert den analytischen Ueberblick.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I12",
        "area": "intellektus",
        "frequency": "analytik",
        "text_de": "Wie erleben andere die Schaerfe und Praezision Ihrer Fragen — bringen Ihre Fragen die Diskussion voran?",
        "scoring_guidance": "Hoch (3-4): Fragt gezielt, Fragen oeffnen neue Perspektiven, werden als wertvoll erlebt. Mittel (1.5-2.5): Stellt gute Fragen, aber nicht immer auf den Punkt. Niedrig (0-1): Fragen sind unklar, oberflaechlich oder abschweifend.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Struktur (I13-I19) ---
    {
        "id": "I13",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie erleben andere die Struktur und Logik in Ihren Praesentationen oder Vortraegen?",
        "scoring_guidance": "Hoch (3-4): Klar gegliedert, roter Faden erkennbar, Zuhoerer koennen gut folgen. Mittel (1.5-2.5): Grundstruktur vorhanden, aber mit Abschweifungen. Niedrig (0-1): Chaotisch, kein erkennbarer Aufbau, Zuhoerer verlieren den Faden.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I14",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie beschreiben andere Ihre Faehigkeit, Informationen zu ordnen und priorisieren?",
        "scoring_guidance": "Hoch (3-4): Strukturiert Informationen klar, trennt Wichtiges von Unwichtigem, andere schaetzen die Ordnung. Mittel (1.5-2.5): Kann priorisieren, aber nicht immer konsistent. Niedrig (0-1): Informationen wirken ungeordnet, Prioritaeten unklar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I15",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie erleben andere Ihre Faehigkeit, einem Gespraech einen klaren Rahmen zu geben — Anfang, Mitte, Ende?",
        "scoring_guidance": "Hoch (3-4): Gibt Gespraechen bewusst Struktur, setzt Agenda, fasst zusammen, schliesst sauber ab. Mittel (1.5-2.5): Teilweise strukturiert, manchmal offene Enden. Niedrig (0-1): Gespraeche verlaufen sich, kein klarer Rahmen.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I16",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie gut koennen Sie komplexe Zusammenhaenge auf das Wesentliche reduzieren — und wie erleben andere diese Faehigkeit?",
        "scoring_guidance": "Hoch (3-4): Bringt Dinge auf den Punkt, Reduktion auf das Wesentliche wird als Staerke erlebt. Mittel (1.5-2.5): Kann vereinfachen, aber manchmal zu stark oder zu wenig. Niedrig (0-1): Verliert sich in Details oder vereinfacht zu stark.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I17",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie beschreiben andere Ihre E-Mails, Berichte oder schriftlichen Unterlagen — strukturiert und klar oder eher unuebersichtlich?",
        "scoring_guidance": "Hoch (3-4): Schriftliche Kommunikation ist klar gegliedert, pointiert, leicht verstaendlich. Mittel (1.5-2.5): Verstaendlich, aber nicht immer optimal strukturiert. Niedrig (0-1): Unuebersichtlich, zu lang, schwer nachvollziehbar.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "I18",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie erleben andere Ihre Faehigkeit, in einer chaotischen Situation Ordnung herzustellen?",
        "scoring_guidance": "Hoch (3-4): Wird als ordnende Kraft geschaetzt, bringt Struktur in Chaos, andere orientieren sich daran. Mittel (1.5-2.5): Kann helfen, ist aber nicht die erste Anlaufstelle fuer Struktur. Niedrig (0-1): Traegt eher zum Chaos bei oder ist davon ueberfordert.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I19",
        "area": "intellektus",
        "frequency": "struktur",
        "text_de": "Wie klar und nachvollziehbar sind fuer andere Ihre Gedankengaenge — koennen sie Ihren Argumentationsketten leicht folgen?",
        "scoring_guidance": "Hoch (3-4): Gedanken sind transparent, logisch aufgebaut, andere folgen muehelos. Mittel (1.5-2.5): Meistens nachvollziehbar, gelegentlich Gedankenspruenge. Niedrig (0-1): Gedankengaenge wirken sprunghaft oder undurchsichtig.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Zielorientierung (I20-I25) ---
    {
        "id": "I20",
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "Wie erleben andere Ihre Faehigkeit, klare Ziele zu kommunizieren und konsequent zu verfolgen?",
        "scoring_guidance": "Hoch (3-4): Ziele sind klar kommuniziert, Fortschritt sichtbar, andere erleben hohe Konsequenz. Mittel (1.5-2.5): Hat Ziele, kommuniziert sie aber nicht immer klar oder verfolgt sie inkonsistent. Niedrig (0-1): Ziele sind unklar, wirkt orientierungslos oder sprunghaft.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I21",
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "Wie beschreiben andere Ihre Faehigkeit, Gespraeche und Meetings ergebnisorientiert zu fuehren?",
        "scoring_guidance": "Hoch (3-4): Fokussiert auf Ergebnisse, sorgt fuer klare Vereinbarungen und naechste Schritte. Mittel (1.5-2.5): Hat Ergebnisorientierung, verliert sie aber manchmal in Diskussionen. Niedrig (0-1): Meetings enden ohne klare Ergebnisse, kein roter Faden zum Ziel.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I22",
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "Wie gut koennen Sie andere dazu bringen, sich auf ein gemeinsames Ziel auszurichten — und wie erleben andere diesen Prozess?",
        "scoring_guidance": "Hoch (3-4): Schafft Alignment, alle ziehen an einem Strang, wird als richtungsweisend erlebt. Mittel (1.5-2.5): Kann Teams ausrichten, aber nicht alle werden gleich gut mitgenommen. Niedrig (0-1): Kein gemeinsames Zielverstaendnis entsteht, jeder verfolgt eigene Agenda.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "I23",
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "Wie erleben andere Ihre Prioritaetensetzung — wissen sie, was Ihnen am wichtigsten ist?",
        "scoring_guidance": "Hoch (3-4): Prioritaeten sind klar, konsistent und transparent. Andere wissen, woran sie sind. Mittel (1.5-2.5): Hat Prioritaeten, kommuniziert sie aber nicht immer. Niedrig (0-1): Prioritaeten aendern sich staendig oder sind unklar.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I24",
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "Wie beschreiben andere Ihre Konsequenz — halten Sie durch, auch wenn es schwierig wird?",
        "scoring_guidance": "Hoch (3-4): Wird als beharrlich und konsequent erlebt, gibt nicht auf bei Widerstand. Mittel (1.5-2.5): Meistens konsequent, gibt aber bei anhaltendem Widerstand nach. Niedrig (0-1): Wechselt haeufig die Richtung, andere erleben das als unzuverlaessig.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "I25",
        "area": "intellektus",
        "frequency": "zielorientierung",
        "text_de": "Wie erleben andere Ihre Balance zwischen Zielstrebigkeit und Flexibilitaet — wissen Sie, wann Anpassung noetig ist?",
        "scoring_guidance": "Hoch (3-4): Balanciert Zielstrebigkeit mit Anpassungsfaehigkeit, andere erleben das als souveraen. Mittel (1.5-2.5): Entweder zu stur oder zu flexibel, Balance noch nicht gefunden. Niedrig (0-1): Entweder starr oder voellig ohne Richtung.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },

    # =====================================================================
    # LINGUA (L01-L25) — Sprachliche Wirkung, verbale Ausstrahlung
    # =====================================================================

    # --- Stimme (L01-L06) ---
    {
        "id": "L01",
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "Wie beschreiben andere Ihre Stimme — angenehm, kraftvoll, monoton, leise?",
        "scoring_guidance": "Hoch (3-4): Wird als angenehm, tragend, warm und ueberzeugend beschrieben. Mittel (1.5-2.5): Akzeptable Stimme, aber weder besonders positiv noch negativ auffallend. Niedrig (0-1): Monoton, zu leise, unangenehm, oder zu laut — irritierend fuer Zuhoerer.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L02",
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "Wie bewusst variieren Sie Lautstaerke, Tempo und Betonung — und bemerken andere diese Variation?",
        "scoring_guidance": "Hoch (3-4): Bewusste Modulation, Pausen, Tempowechsel — wirkt lebendig und fesselnd. Mittel (1.5-2.5): Etwas Variation, aber nicht konsistent oder bewusst eingesetzt. Niedrig (0-1): Monotone Sprechweise, keine stimmliche Dynamik.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L03",
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "Wie gut koennen Sie durch Ihre Stimmführung Aufmerksamkeit erzeugen und halten — z.B. durch gezielte Pausen oder Betonungen?",
        "scoring_guidance": "Hoch (3-4): Setzt Pausen gezielt ein, variiert Betonung, Zuhoerer haengen an den Lippen. Mittel (1.5-2.5): Gelegentlich wirkungsvolle Stimmfuehrung, aber nicht durchgehend. Niedrig (0-1): Keine bewusste Stimmfuehrung, Zuhoerer driften ab.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L04",
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "Wie erleben andere Ihre Stimme in Stresssituationen — bleibt sie ruhig und kontrolliert?",
        "scoring_guidance": "Hoch (3-4): Stimme bleibt stabil, ruhig und kontrolliert auch unter Druck, wirkt beruhigend auf andere. Mittel (1.5-2.5): Meistens stabil, gelegentlich hoerbar angespannt. Niedrig (0-1): Stimme wird unter Stress hoeher, schneller, zittrig — Unsicherheit hoerbar.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L05",
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "Wie beschreiben andere die emotionale Wirkung Ihrer Stimme — kann sie begeistern, beruhigen, motivieren?",
        "scoring_guidance": "Hoch (3-4): Stimme hat hohe emotionale Wirkung, kann je nach Situation verschiedene Stimmungen erzeugen. Mittel (1.5-2.5): Stimme ist angemessen, hat aber keine besondere emotionale Kraft. Niedrig (0-1): Stimme wirkt emotional flat oder unangemessen zum Inhalt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L06",
        "area": "lingua",
        "frequency": "stimme",
        "text_de": "Wie gut traegt Ihre Stimme in grossen Raeumen oder Gruppen — koennen alle Sie problemlos verstehen?",
        "scoring_guidance": "Hoch (3-4): Stimme traegt muehelos, auch ohne Mikrofon, klare Projektion. Mittel (1.5-2.5): Reicht fuer mittelgrosse Gruppen, in grossen Raeumen wird es schwierig. Niedrig (0-1): Stimme ist zu leise, nuschelig oder reicht nicht bis zu den hinteren Reihen.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Artikulation (L07-L12) ---
    {
        "id": "L07",
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "Wie klar und deutlich sprechen Sie — koennen andere Sie immer gut verstehen?",
        "scoring_guidance": "Hoch (3-4): Sehr klare Aussprache, jedes Wort verstaendlich, angenehmes Sprechtempo. Mittel (1.5-2.5): Grundsaetzlich verstaendlich, gelegentlich nuschelig oder zu schnell. Niedrig (0-1): Schwer verstaendlich, nuschelt, verschluckt Silben.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "L08",
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "Wie praezise waehlen Sie Ihre Worte — druecken Sie sich genau aus oder eher ungefaehr?",
        "scoring_guidance": "Hoch (3-4): Wortwahl ist praezise, treffend und dem Kontext angemessen. Mittel (1.5-2.5): Meistens passende Worte, gelegentlich unpraezise oder umstaendlich. Niedrig (0-1): Ungenaue Wortwahl, Missverstaendnisse durch unpraezise Ausdruecke.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L09",
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "Wie beschreiben andere Ihr Sprechtempo — angemessen, zu schnell, zu langsam?",
        "scoring_guidance": "Hoch (3-4): Angemessenes Tempo, passt sich an Situation und Zuhoerer an, Pausen wirken natuerlich. Mittel (1.5-2.5): Akzeptables Tempo, aber gelegentlich zu schnell oder zu langsam. Niedrig (0-1): Sprechtempo ist problematisch — entweder hektisch oder einschlaefelnd.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "L10",
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "Wie gut koennen Sie Ihre Gedanken muendlich auf den Punkt bringen — ohne lange Umwege?",
        "scoring_guidance": "Hoch (3-4): Kommt schnell zum Punkt, drueckt sich praegnant und klar aus. Mittel (1.5-2.5): Erreicht den Punkt, aber mit Umwegen. Niedrig (0-1): Verliert sich in Nebensaetzen, kommt nicht zum Punkt.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },
    {
        "id": "L11",
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "Wie erleben andere Ihren Einsatz von Fuellwoertern — 'aehm', 'also', 'sozusagen' — stoeren diese den Redefluss?",
        "scoring_guidance": "Hoch (3-4): Kaum Fuellwoerter, fliesssender Redefluss, Pausen statt Fueller. Mittel (1.5-2.5): Gelegentliche Fuellwoerter, stoeren nicht massiv. Niedrig (0-1): Haeufige Fuellwoerter die den Redefluss unterbrechen und unprofessionell wirken.",
        "reverse_scored": False,
        "difficulty": 0.45,
        "discrimination": 1.0,
    },
    {
        "id": "L12",
        "area": "lingua",
        "frequency": "artikulation",
        "text_de": "Wie passen Sie Ihre sprachliche Ausdruecksweise an verschiedene Zuhoerer an — z.B. Fachpublikum vs. Laien?",
        "scoring_guidance": "Hoch (3-4): Passt Sprache bewusst an das Gegenueber an, benutzt passende Fachbegriffe oder einfache Sprache. Mittel (1.5-2.5): Teilweise Anpassung, aber nicht konsistent. Niedrig (0-1): Spricht immer gleich, unabhaengig vom Zuhoerer — entweder zu fachlich oder zu simpel.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },

    # --- Beredsamkeit (L13-L19) ---
    {
        "id": "L13",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie beschreiben andere Ihre rhetorischen Faehigkeiten — koennen Sie eine Gruppe fesseln und mitreissen?",
        "scoring_guidance": "Hoch (3-4): Wird als exzellenter Redner wahrgenommen, Zuhoerer haengen an den Lippen. Mittel (1.5-2.5): Solider Redner, kann informieren, aber nicht immer fesseln. Niedrig (0-1): Redekunst ist nicht ueberzeugend, Zuhoerer driften ab.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L14",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie gut koennen Sie spontan und ueberzeugend auf unerwartete Fragen oder Einwaende reagieren?",
        "scoring_guidance": "Hoch (3-4): Reagiert schlagfertig, souveraen und inhaltlich treffend — Spontanitaet wird als Staerke erlebt. Mittel (1.5-2.5): Kann reagieren, braucht aber einen Moment, wirkt nicht immer souveraen. Niedrig (0-1): Wird von Ueberraschungen aus dem Konzept gebracht, reagiert unsicher.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L15",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie erleben andere Ihre Faehigkeit, eine Geschichte oder Anekdote zu erzaehlen, die einen Punkt verdeutlicht?",
        "scoring_guidance": "Hoch (3-4): Erzaehlt fesselnd, Geschichten haben einen klaren Bezug zum Thema und bleiben im Gedaechtnis. Mittel (1.5-2.5): Kann Geschichten erzaehlen, aber der Bezug ist nicht immer klar. Niedrig (0-1): Geschichten sind lang, ohne Punkt, oder werden gar nicht eingesetzt.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L16",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie wuerden andere Ihre Wortgewandtheit einschaetzen — verfuegen Sie ueber einen reichen, differenzierten Wortschatz?",
        "scoring_guidance": "Hoch (3-4): Breiter Wortschatz, nutzt treffende und differenzierte Ausdruecke, wirkt eloquent. Mittel (1.5-2.5): Angemessener Wortschatz, aber nicht besonders differenziert. Niedrig (0-1): Begrenzter Wortschatz, Wiederholungen, kann Nuancen nicht ausdruecken.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L17",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie gut koennen Sie Ihre Zuhoerer verbal fuehren — spueren andere eine klare Dramaturgie in dem, was Sie sagen?",
        "scoring_guidance": "Hoch (3-4): Baut Spannung auf, fuehrt Zuhoerer durch das Thema, hat Anfang-Mitte-Schluss. Mittel (1.5-2.5): Informiert gut, aber ohne besondere Dramaturgie. Niedrig (0-1): Reiht Informationen aneinander, kein narrativer Bogen.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },
    {
        "id": "L18",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie erleben andere Ihre Ueberzeugungskraft rein durch Sprache — ohne Hilfsmittel wie Slides oder Daten?",
        "scoring_guidance": "Hoch (3-4): Kann allein mit Worten ueberzeugen, Sprache ist das primaere Werkzeug. Mittel (1.5-2.5): Braucht Hilfsmittel zur Unterstuetzung, allein reicht die Sprache nicht. Niedrig (0-1): Ohne visuelle Unterstuetzung wenig ueberzeugend.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },
    {
        "id": "L19",
        "area": "lingua",
        "frequency": "beredsamkeit",
        "text_de": "Wie schlagfertig und humorvoll koennen Sie sprachlich agieren — und wie wirkt das auf andere?",
        "scoring_guidance": "Hoch (3-4): Schlagfertig, kann Humor gezielt einsetzen, lockert Stimmung auf, ohne unprofessionell zu wirken. Mittel (1.5-2.5): Gelegentlich humorvoll, aber Humor kommt nicht immer an. Niedrig (0-1): Kein Humor oder Humor wirkt deplatziert.",
        "reverse_scored": False,
        "difficulty": 0.5,
        "discrimination": 1.0,
    },

    # --- Bildhaftigkeit (L20-L25) ---
    {
        "id": "L20",
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "Wie gut koennen Sie durch Sprachbilder, Metaphern oder Vergleiche abstrakte Konzepte greifbar machen?",
        "scoring_guidance": "Hoch (3-4): Nutzt treffende Metaphern und Bilder, macht Abstraktes erlebbar und einpraegsam. Mittel (1.5-2.5): Gelegentlich bildhafte Sprache, aber nicht konsistent oder manchmal unpassend. Niedrig (0-1): Spricht rein abstrakt oder technisch, keine Bilder.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L21",
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "Wie erleben andere Ihre Faehigkeit, Visionen und Zukunftsbilder sprachlich so zu zeichnen, dass andere sie vor sich sehen koennen?",
        "scoring_guidance": "Hoch (3-4): Erzeugt lebhafte mentale Bilder, Zuhoerer koennen die Vision sehen und fuehlen. Mittel (1.5-2.5): Beschreibt Zukunft, aber eher abstrakt als bildlich. Niedrig (0-1): Visionen bleiben vage, andere koennen sich nichts darunter vorstellen.",
        "reverse_scored": False,
        "difficulty": 0.6,
        "discrimination": 1.0,
    },
    {
        "id": "L22",
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "Wie beschreiben andere die Lebendigkeit Ihrer Sprache — nutzen Sie Bilder und Beispiele, die im Gedaechtnis bleiben?",
        "scoring_guidance": "Hoch (3-4): Sprachbilder werden noch lange erinnert, Zuhoerer zitieren sie. Mittel (1.5-2.5): Gelegentlich einpraegsam, aber nicht durchgehend. Niedrig (0-1): Sprache ist funktional aber nicht einpraegsam.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L23",
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "Wie gut koennen Sie Analogien einsetzen, um neue Ideen in bekannte Referenzrahmen einzubetten?",
        "scoring_guidance": "Hoch (3-4): Nutzt treffende Analogien die komplexe Ideen sofort verstaendlich machen. Mittel (1.5-2.5): Gelegentlich gute Analogien, aber nicht durchgehend. Niedrig (0-1): Nutzt keine Analogien oder sie passen nicht.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L24",
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "Wie wuerden andere beschreiben, ob Ihre Praesentationen oder Erklaerungen visuelle Qualitaet haben — entstehen 'Bilder im Kopf'?",
        "scoring_guidance": "Hoch (3-4): Zuhoerer sehen, was beschrieben wird — 'Kopfkino' entsteht, hohe sensorische Sprache. Mittel (1.5-2.5): Teilweise bildhaft, aber viel bleibt abstrakt. Niedrig (0-1): Rein verbale Information ohne visuelle Qualitaet.",
        "reverse_scored": False,
        "difficulty": 0.55,
        "discrimination": 1.0,
    },
    {
        "id": "L25",
        "area": "lingua",
        "frequency": "bildhaftigkeit",
        "text_de": "Wie kreativ und originell empfinden andere Ihre sprachlichen Ausdruecke — nutzen Sie eigene Bilder oder eher Standardformulierungen?",
        "scoring_guidance": "Hoch (3-4): Kreiert eigene Bilder und Formulierungen, wird als originell und kreativ sprachlich erlebt. Mittel (1.5-2.5): Nutzt bekannte Redewendungen, gelegentlich eigene Bilder. Niedrig (0-1): Ausschliesslich Standardformulierungen, keine sprachliche Kreativitaet.",
        "reverse_scored": False,
        "difficulty": 0.55,
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
