# Gr8hub — Personal Development Platform

## Vollstaendige Projekt-Dokumentation

**Version:** 0.2.0
**Stand:** Februar 2026
**Inhaber:** Bornhaeusser & Friends GmbH (Leonardo Bornhaeusser, Gesellschafter)
**Repository:** `/Projects/git/gr8hub`

---

## Inhaltsverzeichnis

1. [Vision & Mission](#1-vision--mission)
2. [Was ist SCIL?](#2-was-ist-scil)
3. [Produkt-Architektur](#3-produkt-architektur)
4. [Diagnostik-Suite (25 Tools)](#4-diagnostik-suite-25-tools)
5. [360-Grad-Feedback-System](#5-360-grad-feedback-system)
6. [KI-Agent-System](#6-ki-agent-system)
7. [Berater-Netzwerk & Matching](#7-berater-netzwerk--matching)
8. [Token-System & Monetarisierung](#8-token-system--monetarisierung)
9. [Diversifizierte Revenue-Streams](#9-diversifizierte-revenue-streams)
10. [Technische Architektur](#10-technische-architektur)
11. [Aktueller Implementierungsstand](#11-aktueller-implementierungsstand)
12. [IP-Rechte & Urheberrecht](#12-ip-rechte--urheberrecht)
13. [DSGVO & Datenschutz](#13-dsgvo--datenschutz)
14. [EU AI Act Compliance](#14-eu-ai-act-compliance)
15. [Marktkontext & Differenzierung](#15-marktkontext--differenzierung)
16. [Roadmap](#16-roadmap)
17. [Verifikation & Qualitaetssicherung](#17-verifikation--qualitaetssicherung)

---

## 1. Vision & Mission

### Vision

Gr8hub ist eine KI-gestuetzte Personal Development Plattform, die:

1. Die **SCIL-Diagnostik** (Wirkungskompetenz) uebernimmt, verbessert und durch Agentic AI erlebbar macht
2. Alle etablierten Diagnostiken kennt und als **modulare Suite** anbietet (12 eigene + 13 Import)
3. Nutzer nach der Diagnostik an ein **Netzwerk qualifizierter Berater/Coaches** vermittelt
4. Den gesamten Entwicklungsprozess durch **KI-Coaching** begleitet

### Mission

Persoenliche Entwicklung demokratisieren: Von der statischen PDF-Auswertung zum interaktiven, KI-gefuehrten Entwicklungserlebnis. Diagnostik wird zur Konversation, Ergebnisse werden erlebbar, Coaching wird zugaenglich.

### Kernthese

Charisma und Wirkungskompetenz sind **erlernbar und trainierbar** — nicht statische Persoenlichkeitsmerkmale. Gr8hub macht diesen Entwicklungsprozess messbar, begleitbar und skalierbar.

---

## 2. Was ist SCIL?

### Ueberblick

**S.C.I.L.** steht fuer **Sensus, Corpus, Intellektus, Lingua** und misst Wirkungs- und Wahrnehmungskompetenz ueber 4 Frequenzbereiche mit insgesamt 16 Interaktionsfaktoren.

- Entwickelt von **Andreas Bornhaeusser** mit der **Universitaet Duisburg-Essen** ueber 30+ Jahre
- ~**140.000+ Teilnehmer**, 143 zertifizierte Partner in 7 Laendern
- **92% Uebereinstimmung** zwischen Selbst- und Fremdbild
- Eigenes IP der Bornhaeusser & Friends GmbH

### Die 4 Frequenzbereiche

| Bereich | Fokus | 4 Frequenzen |
|---------|-------|--------------|
| **Sensus** | Beziehung & Emotion | Innere Praesenz, Innere Ueberzeugung, Momentfokussierung, Emotionalitaet |
| **Corpus** | Koerpersprache & Praesenz | Aeussere Erscheinung, Gestik, Mimik, Raumpraesenz |
| **Intellektus** | Logik & Struktur | Analytik, Zielorientierung, Struktur, Sachlichkeit |
| **Lingua** | Sprache & Ausdruck | Stimme, Artikulation, Eloquenz, Bildhaftigkeit |

### SCIL Status Quo vs. Gr8hub-Vision

| Aspekt | SCIL (bisherig) | Gr8hub (neu) |
|--------|-----------------|--------------|
| Format | Statischer Fragebogen, ~100 Fragen | Konversationelles KI-Assessment, adaptiv |
| Ergebnis | 35-seitige PDF | Interaktives Polygon, Drill-Down, Live-Exploration |
| Feedback | Optional mit zertifiziertem Master | KI-Coaching + menschliche Berater |
| Tracking | Einmalige Messung | Wiederholte Assessments, Fortschritts-Tracking |
| Integration | Stand-alone | Multi-Diagnostik-Suite, 360-Grad, Import |
| Zugang | Ab ~350 Euro | Ab 9 Euro (Token-Tiers S/M/L/XL) |

---

## 3. Produkt-Architektur

### Zwei-Seiten-Marktplatz

Gr8hub ist ein Zwei-Seiten-Marktplatz mit zwei Hauptzielgruppen:

**Trainee-Seite (Endnutzer):**
- Diagnostik durchfuehren und Ergebnisse interaktiv erkunden
- KI-Coaching fuer persoenliche Entwicklung
- Passende menschliche Berater finden und buchen
- Lernmaterialien und Micro-Learning
- Fortschritts-Tracking ueber Zeit

**Experten-Seite (Berater/Coaches):**
- Klienten-Management mit KI-gestuetzter Session-Vorbereitung
- Token-Inventory (Kauf, Zuweisung, Reselling)
- Eigene Kurse im LMS veroeffentlichen
- Revenue-Analytics und Matching-Performance
- White-Label-Optionen fuer eigenes Branding

### Nutzer-Journey

```
1. Onboarding
   -> KI-Agent begruesst, versteht Kontext und Ziele
   -> Empfiehlt passende Diagnostik-Kombination

2. Diagnostik-Phase
   -> Konversationelles Assessment (adaptiv, multimodal)
   -> Echtzeit-Visualisierung der Ergebnisse
   -> Interaktive Ergebnis-Exploration mit dem Agenten

3. Entwicklungsplan
   -> Agent erstellt personalisierten Plan
   -> Priorisierung der Entwicklungsfelder
   -> Konkrete Uebungen und Verhaltensexperimente

4. Coaching-Phase
   -> Taegliche/woechentliche KI-Coaching-Impulse
   -> Situatives Coaching on-demand
   -> Fortschritts-Tracking mit Re-Assessment

5. Berater-Vermittlung
   -> Agent empfiehlt passende menschliche Berater
   -> Nahtlose Uebergabe mit Kontext (Diagnostik + Coaching-Historie)
   -> Berater erhaelt aufbereitetes Profil (mit Nutzer-Einwilligung)

6. Langzeit-Begleitung
   -> Kontinuierliches Tracking
   -> Re-Assessments zeigen Entwicklung
   -> Adaptive Anpassung der Empfehlungen
```

---

## 4. Diagnostik-Suite (25 Tools)

### A. Eigene Implementierungen (12 Diagnostiken)

Diagnostiken, die Gr8hub mit eigenen Items konversationell implementiert:

| # | Slug | Diagnostik | Konstrukt | Rechtsgrundlage | Status |
|---|------|-----------|-----------|-----------------|--------|
| 1 | `scil` | S.C.I.L. Profile | Wirkungskompetenz (16 Frequenzen) | Eigenes IP — Bornhaeusser & Friends GmbH | Implementiert |
| 2 | `big_five` | Big Five / OCEAN | Persoenlichkeit (5 Faktoren, 30 Facetten) | IPIP = Public Domain (3.329 Items frei nutzbar) | Implementiert |
| 3 | `values_schwartz` | Werteprofil (Schwartz) | 19 Grundwerte | CC BY-NC-ND 3.0, eigene Items fuer Konstrukt | Implementiert |
| 4 | `eq_trait` | Emotionale Intelligenz | 15 Facetten in 4 Faktoren | Eigene Items fuer EI-Konstrukt (Konstrukt frei) | Implementiert |
| 5 | `resilience` | Resilienz-Profil | 5 Dimensionen | Eigene Items, APA-Framework | Implementiert |
| 6 | `feedback_360` | 360-Grad Feedback | Multi-Rater Kompetenz-Assessment | Eigene Implementierung (Open360, Apache 2.0) | Implementiert |
| 7 | `stress_coping` | Stressbewaeltigungs-Profil | 6 Coping-Dimensionen | Eigene Items, Lazarus & Folkman Transactional Model | Implementiert |
| 8 | `team_roles` | Teamrollen-Profil | 8 Teamrollen | Eigenes Modell, Big-Five-basiert | Implementiert |
| 9 | `communication_style` | Kommunikationsstil-Analyse | 6 Kommunikationsdimensionen | NLP-basierte Analyse, eigene Implementierung | Implementiert |
| 10 | `motivation_sdt` | Motivationsprofil (SDT) | 5 Motivationstypen + 3 Grundbeduerfnisse | Self-Determination Theory (Deci & Ryan), eigene Items | Implementiert |
| 11 | `thinking_styles` | Denkstilpraeferenzen | 4-Quadranten Denkmuster | Eigenes Modell (HBDI ist geschuetzt) | Implementiert |
| 12 | `cognitive_flexibility` | Kognitive Flexibilitaet | 4 Dimensionen, adaptiv | IRT-basiert, eigene Implementierung | Implementiert |

### B. Partner-Integrationen / Import (13 proprietaere Tools)

Nutzer koennen Ergebnisse aus proprietaeren Tests importieren. Gr8hub speichert ausschliesslich Score-Werte — **keine geschuetzten Items, Texte oder Reports**:

| # | Slug | Tool | Rechteinhaber | Import-Felder |
|---|------|------|---------------|---------------|
| 13 | `mbti` | MBTI | The Myers-Briggs Company | type_code, E/I, S/N, T/F, J/P Scores |
| 14 | `disc` | DISC/DiSG | Wiley / persolog GmbH | D, I, S, C Scores |
| 15 | `insights` | Insights Discovery | Insights Learning & Development | fiery_red, sunshine_yellow, earth_green, cool_blue |
| 16 | `reiss` | Reiss Motivation Profile | IDS Publishing Corp. | 16 Motiv-Scores (-2 bis +2) |
| 17 | `lumina` | Lumina Spark | Lumina Learning | 24 Qualitaeten-Scores |
| 18 | `9levels` | 9 Levels | 9Levels Institute / axiocon GmbH | 9 Wertesystem-Level-Scores |
| 19 | `captain` | CAPTain | CNT Gesellschaften | Kompetenz- und Potenzial-Scores |
| 20 | `hogan` | Hogan Assessments | Hogan Assessment Systems | HPI, HDS, MVPI Scores |
| 21 | `cliftonstrengths` | CliftonStrengths | Gallup | Top 5-34 Staerken-Ranking |
| 22 | `pcm` | PCM | Kahler Communications | 6 Persoenlichkeitstyp-Scores |
| 23 | `hbdi` | HBDI | Herrmann International | A, B, C, D Quadranten-Scores |
| 24 | `biostruktur` | Biostruktur-Analyse | IBSA (Structogram) | gruen, rot, blau Prozent-Scores |
| 25 | `profilingvalues` | Profilingvalues | profilingvalues GmbH | Werteprofil-Scores |

### Diagnostik-Tiers (Preismodell)

Jede eigene Diagnostik ist in 4 Tiers verfuegbar:

| Tier | Umfang | Inhalt | Preis |
|------|--------|--------|-------|
| **S** (Small) | Quick-Check | Kurzversion (z.B. 24 Fragen), KI-Zusammenfassung, Basis-Polygon | 9-19 Euro |
| **M** (Medium) | Tiefenevaluation | Vollstaendige konversationelle Diagnostik, interaktiver Report, Entwicklungsempfehlungen | 49-89 Euro |
| **L** (Large) | + Personal Coaching | Alles aus M + 1x Coaching-Gespraech (60 Min) mit Experte | 199-349 Euro |
| **XL** (Extra Large) | Premium Package | Alles aus L + 3x Coaching-Sessions, Entwicklungsplan, 3-Monats-KI-Begleitung, 360-Grad | 599-999 Euro |

### Multi-Diagnostik-Bundles

| Bundle | Enthalt | Rabatt |
|--------|---------|--------|
| **Starter** | 1x SCIL (M) + 1x Big Five (M) | 15% |
| **Professional** | 3x beliebige Diagnostiken (M) + 1x Coaching | 20% |
| **Full Suite** | Alle 12 Diagnostiken (M) + 2x Coaching | 30% |

---

## 5. 360-Grad-Feedback-System

### Architektur

Das 360-Grad-Feedback-System nutzt einen KI-Agenten, der Feedback-Geber durch ein natuerliches Gespraech fuehrt (statt starrer Frageboegen). Es integriert:

- **Conversational Layer**: Rater-Fuehrung mit STAR-Methodik, empathisches Prompting
- **Adaptive Questioning Engine**: Dynamische Follow-ups, SCIL-Frequenz-Mapping, Bias-Erkennung
- **Analysis & Aggregation Layer**: Multi-Rater Aggregation, NLP-Analyse, Johari-Window-Berechnung
- **Output & Visualization Layer**: SCIL-Polygon Overlay, Johari-Window, Kompetenz-Heatmap

### 5 Perspektiven

| Perspektive | Min. Rater | Anonymitaet | Besonderheiten |
|-------------|-----------|-------------|----------------|
| **Selbstbild** | 1 (Nutzer selbst) | Nicht anonym | Konversationelles Self-Assessment |
| **Vorgesetzte** | 1-2 | Optional identifizierbar | Fuehrungsperspektive, strategische Einordnung |
| **Peers** | 3-5 (min. 3!) | Vollstaendig anonym | Zusammenarbeit, Teamdynamik |
| **Unterstellte** | 3-5 (min. 3!) | Vollstaendig anonym | Fuehrungsverhalten, Delegation |
| **Externe** | 2-3 | Vollstaendig anonym | Kundenperspektive, Aussenwirkung |

**Wichtig:** Gruppenebene nur ab 3 oder mehr Ratern — schuetzt individuelle Anonymitaet.

### Konversationeller Feedback-Prozess

```
Phase 1: KONTEXTUALISIERUNG (2 Min)
  -> Agent begruesst Rater, erklaert Zweck und Anonymitaet
  -> Fragt nach Beziehungskontext
  -> Bestaetigt DSGVO-Einwilligung

Phase 2: ADAPTIVE GESPRAECHSFUEHRUNG (10-15 Min)
  -> STAR-basierte Fragen
  -> Agent passt Fragen basierend auf bisherigen Antworten an
  -> Vertieft bei relevanten Themen, ueberspringt bei wenig Kontakt
  -> Deckt alle SCIL-relevanten Kompetenzen ab

Phase 3: EINGEBETTETE BEWERTUNG (3 Min)
  -> Gezieltes Rating auf 1-10 Skala fuer Kernkompetenzen
  -> Forced-Choice bei kritischen Dimensionen (reduziert Bias)

Phase 4: ZUSAMMENFASSUNG & VALIDIERUNG (2 Min)
  -> Agent fasst zusammen, Rater bestaetigt oder korrigiert
```

### SCIL-Mapping der 360-Grad-Kompetenzen

Jede gemessene Kompetenz wird gewichtet auf SCIL-Frequenzen abgebildet:

| Kompetenz | Primaere SCIL-Frequenz | Sekundaere | Gewichtung |
|-----------|----------------------|-----------|------------|
| Ueberzeugungskraft | Innere Ueberzeugung (S) | Eloquenz (L), Gestik (C) | 40/30/30 |
| Analytisches Denken | Analytik (I) | Struktur (I), Sachlichkeit (I) | 50/30/20 |
| Empathie | Emotionalitaet (S) | Innere Praesenz (S), Mimik (C) | 40/35/25 |
| Praesenz/Auftreten | Raumpraesenz (C) | Aeussere Erscheinung (C), Stimme (L) | 40/30/30 |
| Strategisches Denken | Zielorientierung (I) | Analytik (I), Struktur (I) | 40/30/30 |
| Storytelling | Bildhaftigkeit (L) | Eloquenz (L), Emotionalitaet (S) | 40/30/30 |
| Teamfuehrung | Momentfokussierung (S) | Raumpraesenz (C), Zielorientierung (I) | 35/35/30 |
| Klarheit | Artikulation (L) | Struktur (I), Sachlichkeit (I) | 35/35/30 |

### Johari-Window-Integration

Das 360-Grad-Feedback berechnet automatisch ein Johari-Window aus der Diskrepanz zwischen Selbst- und Fremdbild:

| Quadrant | Bedeutung | Selbst vs. Fremd | Handlungsempfehlung |
|----------|-----------|-------------------|---------------------|
| **Oeffentlich** | Staerken-Match | Selbst ~ Fremd | Bestaetigen und weiter staerken |
| **Blinder Fleck** | Entwicklungsfeld | Selbst < Fremd | KI hebt hervor, Coach thematisiert |
| **Verborgen** | Potenzial | Selbst > Fremd | Sichtbarkeit erhoehen |
| **Unbekannt** | Exploration | Weder Selbst noch Andere | Experiment und Entdeckung |

---

## 6. KI-Agent-System

### Architektur: Agentic AI mit spezialisierten Sub-Agenten

Gr8hub nutzt eine Multi-Agent-Architektur mit drei spezialisierten Agenten unter einem Orchestrator:

```
Personal Development Agent (Orchestrator / Meta-Agent)
  |
  |-- Diagnose-Agent
  |     -> Fuehrt konversationelle Assessments durch
  |     -> Waehlt passende Diagnostik-Kombination basierend auf Nutzerziel
  |     -> Adaptiv: passt Fragen, Tiefe und Reihenfolge dynamisch an
  |     -> Erklaert Ergebnisse interaktiv und kontextuell
  |
  |-- Coaching-Agent
  |     -> Erstellt personalisierte Entwicklungsplaene
  |     -> Fuehrt Check-ins und Micro-Coaching-Sessions
  |     -> Situatives Echtzeit-Coaching (z.B. vor Praesentation)
  |     -> Trackt Fortschritt, eskaliert an menschliche Coaches bei Bedarf
  |
  |-- Vermittlungs-Agent
  |     -> Matcht Nutzer mit qualifizierten Beratern/Coaches
  |     -> Koordiniert Terminbuchung und Follow-up
  |     -> Sammelt Feedback fuer Matching-Optimierung
  |
  |-- 360-Grad-Feedback-Agent
  |     -> Fuehrt Rater durch konversationelles Feedback
  |     -> STAR-Methodik, Bias-Erkennung
  |     -> SCIL-Mapping und Johari-Window-Berechnung
  |
  |-- Wissens-Layer (RAG via Qdrant)
  |     -> Diagnostik-Frameworks und Normdaten
  |     -> Coaching-Methoden und Interventionen
  |     -> Berater-Profile und Spezialisierungen
  |
  |-- Nutzerprofil-Layer
        -> Diagnostik-Ergebnisse (alle Tools)
        -> Entwicklungsziele und Fortschritt
        -> Coaching-Historie und Feedback
```

### LLM-Technologie

- **Primaeres Modell:** Claude API (Anthropic)
- **RAG:** Qdrant Vector Database fuer Diagnostik-Wissen und Coaching-Frameworks
- **Assessment Engine:** Adaptive Testung basierend auf Item Response Theory (IRT)

### Agent-Kommunikation

- **Frontend -> Agent:** WebSocket-Verbindung (Port 8001) fuer Echtzeit-Chat
- **Agent -> Backend:** REST-API (Port 8000) fuer Datenpersistenz
- **Feedback-Agent:** Eigener WebSocket-Endpoint `/ws/feedback/{round_id}/{rater_id}`

---

## 7. Berater-Netzwerk & Matching

### Netzwerk-Aufbau (3 Phasen)

**Phase 1: SCIL-Master-Netzwerk**
- 143 bestehende SCIL-zertifizierte Partner als Kern-Netzwerk
- Nahtlose Integration ihrer Expertise und Verfuegbarkeit

**Phase 2: Erweitertes Berater-Netzwerk**
- Zertifizierte Coaches (ICF, EMCC, DBVC)
- Spezialisierte Berater (Fuehrung, Karriere, Kommunikation, Resilienz)
- Therapeuten (fuer Faelle, die ueber Coaching hinausgehen)
- Branchenexperten und Mentoren

**Phase 3: Internationales Netzwerk**
- Mehrsprachig (DE, EN, FR, NL — aufbauend auf SCIL-Praesenz in 7 Laendern)
- Kulturspezifisches Matching

### Matching-Algorithmus

```
Score = w1 x Diagnostik-Fit         // Berater-Expertise passt zu Nutzer-Profil
      + w2 x Methodik-Fit           // Coaching-Stil passt zu Kommunikationspraeferenz
      + w3 x Erfahrungs-Fit         // Branche, Senioritaet, Kontext
      + w4 x Verfuegbarkeits-Fit    // Zeitliche Passung
      + w5 x Historischer-Erfolg    // Bisherige Outcomes bei aehnlichen Profilen
      + w6 x Sprach-Kultur-Fit      // Sprache und kultureller Hintergrund
```

Gewichte (w1-w6) werden durch ML-Modell kontinuierlich aus Outcome-Daten optimiert.

---

## 8. Token-System & Monetarisierung

### Einmal-Nutzungs-Token (Core Billing Unit)

Gr8hub verwendet ein Token-basiertes Abrechnungsmodell. Jeder Token:

- Ist gebunden an eine **UID** (User ID) + einen spezifischen **Run/Result**
- Wird beim **Link-Klick** aktiviert und verbraucht (einmalige Nutzung)
- Enthaelt kryptographisch: Diagnostik-Typ, Tier (S/M/L/XL), User-UID, Ablaufdatum
- Ist **nicht uebertragbar** (UID-gebunden, HMAC-signiert)

### Token-Struktur

```
TOKEN_ID | UID | DIAG_TYPE | TIER | RUN_ID | EXPIRY | SIGNATURE (HMAC-SHA256)
```

### Token-Lifecycle

```
1. EMISSION      -> System Owner generiert Token-Batch
2. VERKAUF       -> Direkt an User ODER an Experten (Staffelpreis)
3. ZUWEISUNG     -> Token wird einer UID zugeordnet
4. AKTIVIERUNG   -> User klickt Link -> Token consumed -> Diagnostik startet
5. ERGEBNIS      -> Run-Result wird permanent mit Token-ID + UID gespeichert
6. ARCHIV        -> Ergebnis jederzeit abrufbar (kein neuer Token noetig)
```

### Community-Scaling-Modell (Experten als Reseller)

Zertifizierte Experten erhalten Staffelrabatte und koennen Tokens weiterverkaufen:

| Volumen (Tokens/Jahr) | Rabatt auf Retail | Beispiel S-Token |
|------------------------|-------------------|------------------|
| 10-49 | 20% | 15,20 Euro statt 19 Euro |
| 50-199 | 30% | 13,30 Euro statt 19 Euro |
| 200-499 | 40% | 11,40 Euro statt 19 Euro |
| 500+ (Partner-Tier) | 50% | 9,50 Euro statt 19 Euro |

---

## 9. Diversifizierte Revenue-Streams

### Uebersicht (5 Saeulen)

| # | Revenue-Stream | Anteil | Beschreibung |
|---|---------------|--------|--------------|
| 1 | **Diagnostik-Tokens** | 35-40% | Direkt-Verkauf (B2C), Community-Scaling (B2B2C), Enterprise-Bulk |
| 2 | **Plattform-Subscriptions (SaaS)** | 25-30% | Experten-Dashboards, Enterprise-Lizenzen |
| 3 | **LMS (Bildung & Zertifizierung)** | 15-20% | Online-Kurse, Zertifizierungen, Live-Workshops |
| 4 | **eCommerce (Einmal-Produkte)** | 5-10% | E-Books, Templates, Toolkits, Events |
| 5 | **Berater-Vermittlung (Provision)** | 5-10% | 15-25% pro vermittelter Session |

### LMS - Learning Management System

**Fuer Endnutzer (Trainees):**

| Angebot | Format | Preis |
|---------|--------|-------|
| Micro-Learning | 5-15 Min Lektionen, KI-kuratiert | Inkl. in M/L/XL-Token |
| Online-Kurse | Strukturierte Kurse | 49-199 Euro/Kurs |
| Lernpfade | Multi-Kurs-Programme mit Zertifikat | 299-599 Euro/Pfad |
| Live-Workshops | Interaktive Sessions mit Experten | 99-299 Euro/Workshop |

**Fuer Experten (Berater/Coaches):**

| Angebot | Format | Preis |
|---------|--------|-------|
| SCIL-Zertifizierung | Blended Learning: Online + Live | 1.500-3.500 Euro |
| Diagnostik-Zusatzzertifizierungen | Online-Kurse pro Tool | 299-799 Euro |
| Methoden-Masterclasses | Fortgeschrittene Coaching-Techniken | 199-499 Euro |

### eCommerce

| Kategorie | Beispiele | Preisbereich |
|-----------|-----------|--------------|
| Digitale Produkte | E-Books, Workbooks, Audio-Guides | 9-49 Euro |
| Templates & Toolkits | Coaching-Vorlagen, Workshop-Kits | 29-149 Euro |
| Print-Produkte | Buecher, Journals | 19-39 Euro |
| Live-Events | Workshops, Konferenzen, Retreats | 99-1.999 Euro |

### Experten-Dashboard Pricing

| Tier | Features | Preis |
|------|----------|-------|
| **Starter** | Basis-Dashboard, 10 Tokens/Monat inkl., Klienten-Management | 49 Euro/Monat |
| **Professional** | + Experten-Agent, 50 Tokens/Monat inkl., White-Label | 149 Euro/Monat |
| **Enterprise** | + API-Zugang, unbegrenzte Tokens (Staffelpreis), eigene LMS-Kurse | 299 Euro/Monat |

### Enterprise-Lizenzmodell

| Tier | Mitarbeiter | Features | Preis |
|------|-------------|----------|-------|
| **Team** | bis 50 | Team-Diagnostik, KI-Coaching, Basis-LMS | ab 15 Euro/MA/Monat |
| **Business** | 50-500 | + 360-Grad, internes Coach-Matching, Analytics | ab 25 Euro/MA/Monat |
| **Corporate** | 500+ | + HRIS-API, Custom Diagnostiken, Account Manager | Custom Pricing |

---

## 10. Technische Architektur

### System-Uebersicht

```
Frontend Layer
  Next.js 15 + React 19 + TailwindCSS (Port 3000)
  |
API Gateway
  REST (Port 8000) + WebSocket (Port 8001)
  |
  |-- Backend API (FastAPI, Python 3.12)
  |     |-- Auth, Diagnostics, Tokens, Experts Routes
  |     |-- 360-Grad Feedback Routes
  |     |-- Import Routes (13 Tools)
  |     |-- Compliance Layer (EU AI Act, DSGVO)
  |
  |-- Agent Service (FastAPI + WebSocket, Python 3.12)
  |     |-- Diagnosis Agent
  |     |-- Coaching Agent
  |     |-- 360-Grad Feedback Agent
  |
Data Layer
  |-- PostgreSQL 16 (Port 5432) - Nutzerdaten, Diagnostik, Feedback
  |-- Redis 7 (Port 6379) - Sessions, Cache, Pub/Sub
  |-- Qdrant v1.12.5 (Port 6333) - Vector Embeddings fuer RAG
```

### Tech-Stack

| Komponente | Technologie | Version |
|------------|-------------|---------|
| Frontend | Next.js + React + TailwindCSS | 15.1 / 19.0 / 3.4 |
| Backend API | Python + FastAPI + SQLAlchemy | 3.12 / 0.115 / 2.0 |
| Agent Service | Python + FastAPI + WebSocket | 3.12 |
| LLM | Claude API (Anthropic) | Claude 3.5+ |
| Datenbank | PostgreSQL | 16-alpine |
| Cache/PubSub | Redis | 7-alpine |
| Vector DB | Qdrant | v1.12.5 |
| Container | Docker Compose | v3 |
| Auth | OAuth 2.0 + OIDC + JWT (HS256) | - |

### Projekt-Struktur

```
gr8hub/
|-- docker-compose.yml
|-- .env.example
|-- .gitignore
|
|-- backend/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- db/init.sql
|   |-- app/
|       |-- main.py                      # FastAPI App, Lifespan, Router
|       |-- agents_bridge.py             # SCIL-Mapping Bridge
|       |-- core/
|       |   |-- config.py                # Pydantic Settings
|       |   |-- database.py              # AsyncSession, Engine
|       |   |-- seed.py                  # 12 Diagnostiken Seed-Daten
|       |   |-- compliance.py            # EU AI Act + DSGVO Layer
|       |-- models/
|       |   |-- user.py                  # User Model
|       |   |-- diagnostic.py            # Diagnostic, DiagnosticRun, DiagnosticResult
|       |   |-- token.py                 # DiagnosticToken (HMAC-signiert)
|       |   |-- expert.py                # Expert Model
|       |   |-- feedback.py              # FeedbackRound, FeedbackRater, FeedbackResponse, ImportedResult
|       |-- schemas/
|       |   |-- user.py, diagnostic.py, token.py, feedback.py
|       |-- api/routes/
|           |-- auth.py                  # Authentifizierung
|           |-- diagnostics.py           # Diagnostik CRUD + Runs
|           |-- tokens.py                # Token-Management
|           |-- experts.py               # Berater-Verzeichnis
|           |-- feedback.py              # 360-Grad Feedback API
|           |-- import_results.py        # Import 13 proprietaerer Tools
|
|-- agent-service/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- src/
|       |-- main.py                      # WebSocket Endpoints
|       |-- agents/
|           |-- diagnosis_agent.py       # Diagnose-Agent
|           |-- coaching_agent.py        # Coaching-Agent
|           |-- feedback_360_agent.py    # 360-Grad Feedback-Agent
|
|-- frontend/
    |-- Dockerfile
    |-- package.json
    |-- tailwind.config.ts               # Gr8hub Farben (Navy, Neon, Purple)
    |-- src/
        |-- app/
        |   |-- globals.css              # Light Theme, Gr8hub CSS Variables
        |   |-- layout.tsx               # Navigation (6 Links)
        |   |-- page.tsx                 # Dashboard
        |   |-- diagnostics/page.tsx     # 12 Diagnostiken + Bundles
        |   |-- feedback/page.tsx        # 360-Grad Dashboard (3 Tabs)
        |   |-- coaching/page.tsx        # KI-Coaching Chat
        |   |-- import/page.tsx          # Import Wizard (13 Tools)
        |   |-- experts/page.tsx         # Berater-Netzwerk
        |-- components/
            |-- chat/ChatInterface.tsx    # Chat-Komponente
            |-- diagnostics/
                |-- SCILPolygon.tsx       # SCIL 16-Frequenz Radar-Chart (Canvas)
                |-- JohariWindow.tsx      # 4-Quadranten Johari-Visualisierung
                |-- PolygonOverlay.tsx    # Selbst-/Fremdbild SCIL-Overlay
```

### Design-System / Branding

| Element | Wert |
|---------|------|
| **Primaerfarbe (Navy)** | #0B1437 |
| **Akzent (Neon Green)** | #00E676 |
| **Sekundaer (Purple)** | #7C3AED |
| **Navy Light** | #1B2559 |
| **Neon Dark** | #00C853 |
| **Purple Light** | #A78BFA |
| **Purple Dark** | #5B21B6 |
| **Theme** | Light (Background #F8FAFC) |
| **Logo** | Gr8hub (animiertes Video vorhanden) |

### Docker-Container (6 Services)

| Container | Image | Port | Health |
|-----------|-------|------|--------|
| `gr8hub-frontend-1` | gr8hub-frontend (Node 20) | 3000 | Up |
| `gr8hub-backend-1` | gr8hub-backend (Python 3.12) | 8000 | Up |
| `gr8hub-agent-service-1` | gr8hub-agent-service (Python 3.12) | 8001 | Up |
| `gr8hub-db-1` | postgres:16-alpine | 5432 | Healthy |
| `gr8hub-redis-1` | redis:7-alpine | 6379 | Healthy |
| `gr8hub-qdrant-1` | qdrant/qdrant:v1.12.5 | 6333/6334 | Up |

### API-Endpoints

**Backend (Port 8000):**

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | `/health` | Health-Check |
| POST | `/api/v1/auth/register` | Registrierung |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/diagnostics/` | Alle 12 Diagnostiken |
| GET | `/api/v1/diagnostics/{slug}` | Einzelne Diagnostik |
| POST | `/api/v1/diagnostics/{slug}/start` | Diagnostik-Run starten |
| POST | `/api/v1/tokens/generate` | Token generieren |
| POST | `/api/v1/tokens/{code}/activate` | Token aktivieren |
| GET | `/api/v1/experts/` | Berater-Verzeichnis |
| POST | `/api/v1/feedback/rounds` | Feedback-Runde erstellen |
| GET | `/api/v1/feedback/rounds` | Meine Feedback-Runden |
| POST | `/api/v1/feedback/rounds/{id}/raters` | Rater hinzufuegen |
| POST | `/api/v1/feedback/rounds/{id}/launch` | Runde starten (Anonymitaet pruefen) |
| GET | `/api/v1/feedback/rater/{token}` | Rater-Einstieg |
| POST | `/api/v1/feedback/rater/{token}/consent` | DSGVO-Einwilligung |
| POST | `/api/v1/feedback/responses` | Feedback abgeben |
| GET | `/api/v1/feedback/rounds/{id}/results` | Aggregierte Ergebnisse + Johari |
| GET | `/api/v1/import/tools/` | 13 Import-Tools |
| POST | `/api/v1/import/results/` | Ergebnis importieren |
| GET | `/api/v1/import/results/` | Importierte Ergebnisse |
| DELETE | `/api/v1/import/results/{id}` | DSGVO-Loeschung |

**Agent Service (Port 8001):**

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | `/health` | Health-Check |
| WebSocket | `/ws/coaching/{session_id}` | Coaching-Chat |
| WebSocket | `/ws/diagnosis/{session_id}` | Diagnostik-Gespraech |
| WebSocket | `/ws/feedback/{round_id}/{rater_id}` | 360-Grad Rater-Gespraech |

---

## 11. Aktueller Implementierungsstand

### Was ist fertig (Februar 2026)

**Backend:**
- [x] FastAPI-Anwendung mit Lifespan-Events (Tabellen + Seed)
- [x] User, Diagnostic, DiagnosticRun, DiagnosticResult Models
- [x] DiagnosticToken Model mit HMAC-Signierung
- [x] Expert Model
- [x] FeedbackRound, FeedbackRater, FeedbackResponse Models
- [x] ImportedResult Model
- [x] 12 Diagnostiken als Seed-Daten
- [x] Auth-Routes (Register, Login)
- [x] Diagnostik-Routes (CRUD, Start Run)
- [x] Token-Routes (Generate, Activate)
- [x] Expert-Routes
- [x] Vollstaendige 360-Grad Feedback-Routes (Lifecycle)
- [x] Import-Routes fuer 13 proprietaere Tools
- [x] EU AI Act + DSGVO Compliance Layer
- [x] SCIL-Mapping Bridge (Kompetenz -> Frequenz)

**Agent Service:**
- [x] Diagnosis Agent (Basis-Konversation)
- [x] Coaching Agent (Chat-Interface)
- [x] 360-Grad Feedback Agent (STAR-Methodik, SCIL-Mapping)
- [x] WebSocket-Endpoints fuer alle Agenten

**Frontend:**
- [x] Gr8hub Branding (Navy, Neon Green, Purple, Light Theme)
- [x] Dashboard mit Feature-Cards
- [x] Diagnostik-Suite (12 Tools, 4 Tiers, 3 Bundles)
- [x] 360-Grad Feedback Dashboard (3 Tabs: Uebersicht, Ergebnisse, Neue Runde)
- [x] KI-Coaching Chat-Interface mit Quick-Actions
- [x] Import Wizard (13 proprietaere Tools)
- [x] Berater-Netzwerk mit Beispiel-Profilen
- [x] SCIL-Polygon Canvas-Visualisierung (16 Frequenzen)
- [x] Johari-Window-Visualisierung (4 Quadranten)
- [x] Polygon-Overlay (Selbst-/Fremdbild)

**Infrastruktur:**
- [x] Docker Compose mit 6 Services
- [x] PostgreSQL 16 + Redis 7 + Qdrant v1.12.5
- [x] Hot-Reload fuer Entwicklung
- [x] Git Repository initialisiert

### Was noch fehlt (naechste Schritte)

- [ ] Anthropic API Key Integration (LLM-Anbindung fuer Agenten)
- [ ] RAG-Pipeline (Qdrant Embeddings fuer Diagnostik-Wissen)
- [ ] Tatsaechliche Item-Formulierungen fuer alle 12 Diagnostiken
- [ ] Adaptive IRT-Algorithmus fuer Assessment Engine
- [ ] OAuth 2.0 / OIDC Integration (Google, Microsoft)
- [ ] Stripe/Payment Integration fuer Token-Kauf
- [ ] E-Mail-Service (Rater-Einladungen, Token-Links)
- [ ] Berater-Onboarding und Kalender-Integration
- [ ] ML-Matching-Algorithmus
- [ ] Mobile App (React Native)
- [ ] Enterprise-Features (Admin-Dashboard, HRIS-API)
- [ ] LMS-Integration
- [ ] eCommerce-Shop

---

## 12. IP-Rechte & Urheberrecht

### Was ist geschuetzt (NICHT kopieren)

- Konkrete Fragebogen-Items (Formulierungen) aus proprietaeren Tests
- Auswertungstexte und Report-Bausteine
- Marken (MBTI, DiSG, Insights Discovery etc.)
- Grafische Gestaltungen (Farb-Wheels, Polygone anderer Anbieter)
- Manuale und Handanweisungen

### Was ist FREI nutzbar

- Wissenschaftliche Theorien und Konstrukte (Big Five, Extraversion, Werte etc.)
- IPIP-Items (3.329 Items, Public Domain, kommerziell nutzbar)
- Mathematische Formeln und Berechnungsmethoden
- Eigene Items fuer gleiche Konstrukte (mit ausreichender kreativer Distanz)
- Import und Anzeige reiner Score-Werte (keine Texte) mit Nutzer-Einwilligung

### "Inspired by" Regel

Eigene Items duerfen dasselbe Konstrukt messen, wenn:

1. Ausreichende kreative Distanz zum Original besteht
2. Keine Item-Formulierungen uebernommen/paraphrasiert werden
3. Eigene, unabhaengige Validierung erfolgt
4. Keine geschuetzten Marken verwendet werden

### SCIL-Rechte

SCIL Profile ist eigenes IP der Bornhaeusser & Friends GmbH. Leonardo Bornhaeusser ist Gesellschafter — volle Nutzungsrechte fuer Gr8hub.

---

## 13. DSGVO & Datenschutz

### Kernprinzipien

- Psychologische Daten = **besondere Kategorie** (Art. 9 DSGVO)
- **Ausdrueckliche Einwilligung** fuer jede Diagnostik-Verarbeitung
- Daten ausschliesslich in **EU-Rechenzentren**
- **Pseudonymisierung** vor LLM-Verarbeitung
- Automatische **Loeschfristen** (Standard: 24 Monate)
- **DPIA** (Data Protection Impact Assessment) vor Launch

### Datenschutz bei 360-Grad-Feedback

| Anforderung | Umsetzung |
|-------------|-----------|
| Rechtsgrundlage | Art. 6 Abs. 1 lit. a DSGVO (Einwilligung) + Art. 9 |
| Einwilligung | Jeder Rater bestaetigt DSGVO-Einwilligung vor Start |
| Anonymitaet | Individuelle Antworten anonymisiert; Gruppenebene nur ab >= 3 Ratern |
| De-Identifikation | KI entfernt automatisch identifizierende Informationen aus Freitext |
| Recht auf Auskunft | Feedback-Empfaenger sieht nur aggregierte Ergebnisse |
| Recht auf Loeschung | Rater kann Feedback zurueckziehen |
| AVV | Art. 28 DSGVO bei externer Verarbeitung |
| Betriebsrat | Enterprise-Kontext: Mitbestimmung nach Paragraf 87 BetrVG |
| Aufbewahrung | Automatische Loeschung nach 24 Monaten |

### Compliance-Features (implementiert)

- `compliance.py` mit Funktionen fuer:
  - `classify_ai_act_risk()` — Risiko-Einstufung nach Kontext
  - `deidentify_text()` — PII-Entfernung aus Feedback-Texten
  - `get_consent_text()` — DSGVO-Einwilligungstexte
  - `validate_ip_rights()` — IP-Rechte-Pruefung pro Diagnostik
  - `ComplianceAuditLog` — Audit-Logging

---

## 14. EU AI Act Compliance

### Einstufung der Plattform

| Kontext | AI Act Einstufung | Deadline |
|---------|-------------------|----------|
| Persoenlichkeitsdiagnostik fuer **Selbst-Coaching** (B2C) | **Nicht High-Risk** | — |
| Diagnostik im **HR/Recruiting-Kontext** | **High-Risk** (Annex III, Bereich 4) | **2. August 2026** |
| **Profiling** natuerlicher Personen | **Automatisch High-Risk** | 2. August 2026 |
| Emotionserkennung aus **Text** | **Erlaubt** | — |
| Emotionserkennung aus **Biometrie** am Arbeitsplatz | **VERBOTEN** (Art. 5) | Ab 2. Februar 2025 |

### High-Risk Compliance-Anforderungen (Enterprise/HR)

- Risikomanagementsystem (Art. 9)
- Datenqualitaet und Data Governance (Art. 10)
- Technische Dokumentation (Art. 11)
- Transparenz und Informationspflichten (Art. 13)
- Menschliche Aufsicht (Art. 14)
- Genauigkeit, Robustheit und Cybersicherheit (Art. 15)
- EU-Konformitaetserklaerung + CE-Kennzeichnung

### Strategie

1. **B2C (Selbst-Coaching):** Nicht High-Risk -> schneller Launch moeglich
2. **Enterprise/HR:** High-Risk-Compliance parallel aufbauen -> Launch August 2026
3. **Keine biometrische Emotionserkennung** -> nur Textanalyse

---

## 15. Marktkontext & Differenzierung

### Wettbewerb

| Wettbewerber | Fokus | Schwaeche (= unsere Chance) |
|--------------|-------|---------------------------|
| BetterUp | Enterprise Coaching + KI | Keine eigene Diagnostik-Suite, kein SCIL |
| CoachHub | Coach-Marktplatz + AIMY | Diagnostik rudimentaer |
| Cloverleaf | Assessment-Hub + Nudges | Nur DISC/Enneagram/16Types, kein konversationelles Assessment |
| Deeper Signals | Big-Five-basiert | Kein Coaching-Agent, kein Berater-Netzwerk |
| SCIL (aktuell) | Wirkungskompetenz | Keine KI, kein Multi-Diagnostik, statischer Fragebogen |

### 5 Differenzierungsmerkmale von Gr8hub

1. **Einzige Plattform mit SCIL + Multi-Diagnostik + KI-Agent + Berater-Netzwerk**
2. **Konversationelle Diagnostik** statt statischer Frageboegen
3. **Agentic AI**: Proaktives Coaching, nicht nur reaktiv
4. **Nahtlose Journey**: Diagnostik -> Coaching -> Berater in einer Plattform
5. **DSGVO-first**: Europaeische Datensouveraenitaet als Differenzierungsmerkmal

---

## 16. Roadmap

### Phase 1: MVP (Monate 1-4) — Aktuell

- [x] SCIL-Diagnostik Grundstruktur (12 Diagnostiken geseeded)
- [x] Token-System (S/M/L/XL) mit HMAC-Signierung
- [x] Web-Frontend: interaktives SCIL-Polygon, Chat-Interface, Diagnostik-Suite
- [x] 360-Grad-Feedback System (Backend + Frontend + Agent)
- [x] Import-Schnittstelle fuer 13 proprietaere Tools
- [x] Einfaches Berater-Verzeichnis
- [x] DSGVO-Einwilligungsmanagement
- [x] EU AI Act Compliance Layer
- [ ] **SCIL-Diagnostik als konversationelles KI-Assessment** (LLM-Anbindung)
- [ ] **Big Five (IPIP-Items)** als zweite konversationelle Diagnostik
- [ ] **Basis-Coaching-Agent** mit RAG-basiertem Wissen
- [ ] Payment-Integration (Stripe)
- [ ] E-Mail-Service (Rater-Einladungen)

### Phase 2: Erweiterung + Go-Live (Monate 4-8)

- [ ] Eigene Items fuer alle 12 Diagnostiken entwickeln und validieren
- [ ] Johari-Window Live-Berechnung aus echten 360-Grad-Daten
- [ ] ML-basiertes automatisches Coach-Matching
- [ ] LMS-Integration (Kurse, Zertifizierungen)
- [ ] Community-Scaling: Experten-Dashboard mit Token-Reselling
- [ ] Multimodale Erfassung (Sprach-Analyse fuer Lingua-Frequenzen)
- [ ] OAuth 2.0 / Social Login

### Phase 3: Enterprise + Compliance (Monate 8-12)

- [ ] Enterprise-Features: Team-Diagnostik, Admin-Dashboard, HRIS-API
- [ ] **EU AI Act High-Risk-Compliance** (fuer HR-Kontext, Deadline Aug 2026)
- [ ] DIN 33430-konforme Dokumentation
- [ ] eCommerce-Shop (digitale Produkte, Templates, Events)
- [ ] Internationalisierung (EN, FR, NL)
- [ ] Mobile App (React Native)

### Phase 4: Skalierung (Monate 12-18)

- [ ] Video-Analyse fuer Corpus-Frequenzen (NUR B2C, nicht HR!)
- [ ] Erweitertes Berater-Netzwerk mit Qualitaetssicherung
- [ ] Marketplace: Experten veroeffentlichen eigene LMS-Kurse
- [ ] API-Zugang fuer Partner-Integrationen
- [ ] Adaptive IRT-Algorithmus fuer alle Diagnostiken

---

## 17. Verifikation & Qualitaetssicherung

### Diagnostik-Qualitaet

- **Konvergente Validitaet**: KI-Assessment vs. traditioneller SCIL-Fragebogen (Ziel: r > 0.5)
- **Item-Validierung**: Eigene Items mit N >= 200 Probanden validieren
- **DIN 33430**: Qualitaetsstandards fuer Eignungsdiagnostik beruecksichtigen

### 360-Grad-Agent

- Test mit min. 5 Rater-Gruppen
- Vergleich konversationell vs. Fragebogen (Ziel: +70% Completion Rate)
- Bias-Analyse: Leniency, Halo-Effekt, zentrale Tendenz

### IP-Compliance

- Juristischer Review aller eigenen Items
- Keine Paraphrasierung proprietaerer Items
- Markenrecht: Korrekte Kennzeichnung aller Marken

### Agent-Qualitaet

- User-Testing mit 20+ Personen
- Qualitatives Feedback auf Coaching-Erlebnis
- A/B-Test: konversationell vs. traditionell

### Matching-Qualitaet

- A/B-Test manuelles vs. algorithmisches Matching
- Outcome-Tracking (Zufriedenheit, Zielerreichung)

### Compliance

- DSGVO-Audit durch externen Datenschutzbeauftragten vor Launch
- EU AI Act Compliance-Check fuer Enterprise/HR vor August 2026
- Penetration Testing vor Go-Live

### Technisch

- E2E-Tests: Onboarding -> Diagnostik -> 360-Grad -> Coaching -> Vermittlung
- Load Testing: 1000+ gleichzeitige WebSocket-Verbindungen
- Monitoring: Uptime, Latenz, Error-Rate

---

## Schnellstart (Entwicklung)

### Voraussetzungen

- Docker + Docker Compose
- Git

### Setup

```bash
cd /Users/leonardobornhausser/Projects/git/gr8hub

# Optional: .env-Datei mit API-Keys erstellen
cp .env.example .env
# ANTHROPIC_API_KEY eintragen

# Container starten
docker compose up -d --build

# Status pruefen
docker ps --filter "name=gr8hub"
```

### URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **Agent Service** | http://localhost:8001 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **Qdrant Dashboard** | http://localhost:6333/dashboard |

### Health-Checks

```bash
curl http://localhost:8000/health   # -> {"status":"healthy","service":"gr8hub-api"}
curl http://localhost:8001/health   # -> {"status":"healthy","service":"gr8hub-agent-service"}
```

---

*Gr8hub - Personal Development Platform*
*Copyright 2026 Bornhaeusser & Friends GmbH. Alle Rechte vorbehalten.*
