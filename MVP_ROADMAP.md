# SCIL Platform — MVP Roadmap

> Abgeleitet aus Product-Owner-Gespraech vom 13.03.2026 + bestehendem Masterplan
> Stakeholder: Andreas Bornhaeusser (Urheber/PO), Leonardo Bornhaeusser (Tech Lead)

---

## Transkript-Analyse: Kernerkenntnisse

### 1. Zwei klar definierte User-Rollen

| Rolle | Bezeichnung | Beschreibung |
|-------|-------------|--------------|
| **Coach** (SCIL Expert/Master) | Der Trainer/Berater | Kauft Codes, verwaltet Coachees, sieht Ergebnisse, kauft Learning-Content, plant Breakout-Sessions |
| **Coachee** (Endnutzer) | Der Klient | Fuehrt Diagnostik durch, trainiert taeglich mit KI-Agent, hat Breakout-Sessions mit Coach, bekommt Learning-Content |

### 2. Zwei Zugangs-Wege fuer Coachees (KRITISCH)

| Zugang | Beschreibung |
|--------|--------------|
| **Via Coach** | Coach kauft Code → gibt Code an Coachee → Coachee wird aktiviert. Coach bleibt im Loop. |
| **Via Plattform (Self-Service)** | Coachee kauft selbst direkt auf der SCIL-Plattform. Kein Coach involviert. |

### 3. Code-basiertes Geschaeftsmodell (BESTEHEND — NICHT AENDERN)

- **1 Code = 1 Diagnostik-Durchlauf**
- Codes koennen einzeln oder in Paketen (z.B. 100 Stueck) gekauft werden
- Coach kauft Codes → verteilt an Coachees
- Coachee loest Code ein → Diagnostik wird freigeschaltet

### 4. Coach Dashboard — Admin-Perspektive

Der Coach braucht:
- **Code-Verwaltung**: Kaufen, Zuweisen, Tracking (welcher Code an welchen Coachee)
- **Coachee-Uebersicht**: Alle zugeordneten Coachees mit deren Diagnostik-Status/Ergebnissen
- **Learning-Content**: Kauf + Zuweisung von Video-Coaching-Programmen aus der SCIL-Bibliothek
- **Breakout-Sessions**: Terminverwaltung fuer regelmaessige 1:1-Sessions mit Coachees
- **Aktivitaets-Historie**: Was hat jeder Coachee gemacht, wie ist der Fortschritt

### 5. Coachee-Erlebnis — Trainings-Perspektive

Der Coachee hat:
- **Diagnostik-Durchfuehrung**: Chat-basierte SCIL-Diagnostik (100 Items, 4 Cluster)
- **Daily Training**: Interaktives KI-gesteuertes Tagestraining (Agent als Coach-Ersatz)
- **Breakout-Sessions**: Regelmaessige Live-Sessions mit dem echten Coach
- **Learning-Content**: On-Demand Lernmaterialien (Videos, Nuggets)
- **Trainings-Historie**: Ueberblick ueber eigenen Fortschritt

### 6. Strategische Leitplanke: "Human in the Loop"

**KRITISCH — vom PO klar formuliert:**
> "Der Coach darf nicht arbeitslos gemacht werden."

- Der KI-Agent uebernimmt die Daily-Arbeit (Diagnostik, Tagestraining, Erinnerungen)
- Der Coach bleibt in regelmaessigen Zyklen eingebunden (z.B. woechentliche Breakout-Sessions)
- Der Coach sieht und steuert den Trainingsfortschritt seiner Coachees
- Die KI ergaenzt den Coach, ersetzt ihn NICHT

### 7. Vision (Langfristig — NICHT MVP)

- Digitaler Avatar von Andreas Bornhaeusser basierend auf seinen Inhalten/Stimme
- KI die situativ das richtige Coaching-Material bereitstellt
- Allerdings: "Praktisch darf der Coach nicht arbeitslos werden"

### 8. AWS Deployment

- Andreas hat bestehendes AWS-Konto (aktuell nur fuer Video-Storage genutzt, ~3 EUR/Monat)
- MFA am Root-Account → Leonardo braucht IAM-User-Zugang (noch einzurichten)
- Deployment-Ziel: AWS ECS (wie im Masterplan geplant)

### 9. Offener Punkt: Echte SCIL-Items

- Andreas bestaetigt: "Ja, nutze die richtigen Frageitems"
- Frageitems muessen von Andreas geliefert werden
- Aktuell sind AI-generierte Platzhalter-Items im System

---

## Aktuelle Ist-Situation (Was bereits gebaut ist)

| Komponente | Status | Details |
|------------|--------|---------|
| Monorepo-Struktur (S0) | ✅ Fertig | `bfg-platform/` mit `packages/core`, `apps/scil` |
| Shared Core (S1) | ✅ Fertig | AIService, Auth, Models, DB, Context Budgeting |
| SCIL Backend (S2) | ✅ Fertig | Routes, Scoring Engine, Seed Data |
| SCIL Agent (S3) | ✅ Fertig | 100-Item Assessment, Per-Item Scoring, Cluster-Rotation |
| SCIL Frontend (S4) | ✅ Fertig | Three-Panel Dashboard, Chat, Polygon, Cluster Progress |
| Suggestion Chips | ✅ Fertig | 4 Antwort-Vorschlaege pro Frage (gerade implementiert) |
| Token/Code-System | ⚠️ Basis | DiagnosticToken Model existiert, Lifecycle-Stubs, kein Payment |
| Coach Dashboard | ❌ Fehlt | Komplett neue Entwicklung noetig |
| Coachee Training | ❌ Fehlt | Daily Training Agent, Learning Content |
| Breakout-Sessions | ❌ Fehlt | Terminbuchung, Video-Integration |
| Payment (Stripe) | ❌ Fehlt | Code-Kauf, Abo-Modell |
| AWS Deployment | ❌ Fehlt | Infrastruktur-Setup noetig |

---

## MVP Roadmap — 6 Epics

### Priorisierung: Was generiert am schnellsten Umsatz?

1. ✅ Diagnostik funktioniert → Kern-Wertversprechen steht
2. 💰 Code-Kauf ermöglichen → Revenue-Start
3. 👤 Coach Dashboard → Partner koennen arbeiten
4. 🎓 Coachee Portal → Endnutzer-Erlebnis
5. 🚀 AWS Deployment → Produktiv-Betrieb
6. 📚 Learning & Breakout → Vollstaendiges Oekosystem

---

### Epic M1: Code-System & Payment (Revenue-Critical)
**Ziel:** Coaches koennen Codes kaufen und an Coachees verteilen
**Prioritaet:** 🔴 HIGHEST — ohne das kein Umsatz
**Aufwand:** L (2-3 Wochen)

| Task | Beschreibung | Datei(en) |
|------|-------------|-----------|
| M1.1 | Stripe-Integration in `bfg_core` | `services/payment_service.py` |
| M1.2 | Code-Kauf API: Einzeln + Pakete (10/25/50/100) | `scil_routes.py` |
| M1.3 | Code-Aktivierung: Coach kauft → Coachee loest ein | `token_service.py` |
| M1.4 | Self-Service Kauf: Coachee kauft direkt auf Plattform | Neue Route |
| M1.5 | Code-Sharing: Coach teilt Code-Link/QR per E-Mail | `email_service.py` |
| M1.6 | Token-Guard: Diagnostik nur mit gueltigem Code startbar | `scil_routes.py` |
| M1.7 | Pricing-Page im Frontend | Neue Page |

**Abhaengigkeit:** Keine — kann sofort starten
**Output:** Coach kann Codes kaufen, Coachee kann Diagnostik mit Code freischalten

---

### Epic M2: Coach Dashboard (Partner-Enablement)
**Ziel:** SCIL-Partner koennen ihre Coachees verwalten
**Prioritaet:** 🔴 HIGH — Partner brauchen das zum Arbeiten
**Aufwand:** XL (3-4 Wochen)

| Task | Beschreibung | Datei(en) |
|------|-------------|-----------|
| M2.1 | Coach-Rolle im User-Model (role: "coach") | `models/user.py` |
| M2.2 | Coach-Coachee-Beziehung (CoachAssignment Model) | Neues Model |
| M2.3 | Code-Verwaltungs-Dashboard: Gekaufte/Zugewiesene/Offene | Neue Components |
| M2.4 | Coachee-Uebersicht: Liste aller Coachees + Status | Neue Components |
| M2.5 | Coachee-Detail: Diagnostik-Ergebnis einsehen (Polygon + Scores) | Neue Page |
| M2.6 | Coachee einladen: E-Mail mit Aktivierungs-Code | `email_service.py` |
| M2.7 | Activity Feed: Letzte Aktionen aller Coachees | Neue API + Component |
| M2.8 | Coach-Registrierung: Separater Onboarding-Flow | Neue Pages |

**Abhaengigkeit:** M1 (Code-System)
**Output:** Coach sieht alle Coachees, deren Ergebnisse, kann Codes zuweisen

---

### Epic M3: Coachee-Portal & Zugangs-Flows
**Ziel:** Coachees koennen sich registrieren (via Coach ODER Self-Service)
**Prioritaet:** 🟡 HIGH — Endnutzer-Zugang
**Aufwand:** L (2-3 Wochen)

| Task | Beschreibung | Datei(en) |
|------|-------------|-----------|
| M3.1 | Zwei Registrierungs-Flows: Via Einladung (Code) / Self-Service | Neue Pages |
| M3.2 | Code-Einloesung: Landing-Page fuer Einladungs-Link | Neue Page |
| M3.3 | Coachee-Dashboard: Trainings-Uebersicht + Diagnostik-Historie | Refactor Dashboard |
| M3.4 | Diagnostik-Ergebnis-Ansicht fuer Coachee (eigenes Profil) | Erweitern RightSidebar |
| M3.5 | Coach-Sichtbarkeit: Coachee sieht seinen zugewiesenen Coach | Neue Component |
| M3.6 | Profil-Seite: Eigene Daten, Passwort aendern | Neue Page |

**Abhaengigkeit:** M1 (Code-System), M2 (Coach-Beziehung)
**Output:** Coachee registriert sich, loest Code ein, fuehrt Diagnostik durch, sieht Ergebnisse

---

### Epic M4: AWS Deployment & Go-Live
**Ziel:** Plattform ist oeffentlich erreichbar
**Prioritaet:** 🟡 HIGH — ohne Deployment kein produktiver Betrieb
**Aufwand:** M (1-2 Wochen)

| Task | Beschreibung |
|------|-------------|
| M4.1 | IAM User auf Andreas' AWS Konto einrichten |
| M4.2 | ECS Cluster + Service-Definitionen (Backend + Frontend) |
| M4.3 | RDS PostgreSQL (shared) + ElastiCache Redis |
| M4.4 | ALB + HTTPS (ACM Certificate) |
| M4.5 | Domain-Setup (scil-profile.de oder aehnlich) |
| M4.6 | CI/CD Pipeline (GitHub Actions → ECR → ECS) |
| M4.7 | Environment-Variablen: Stripe Keys, Anthropic API Key, DB Credentials |
| M4.8 | Monitoring: CloudWatch + Sentry |

**Abhaengigkeit:** Keine technische — braucht AWS-Zugang von Andreas (MFA-Problem loesen)
**Output:** App erreichbar unter `scil-profile.de` mit HTTPS

---

### Epic M5: Daily Training Agent & Coaching-Content
**Ziel:** Coachee kann nach der Diagnostik taeglich trainieren
**Prioritaet:** 🟢 MEDIUM — Retention + Wertschoepfung
**Aufwand:** XL (3-4 Wochen)

| Task | Beschreibung |
|------|-------------|
| M5.1 | Coaching-Agent: Taeglliches Mikro-Training basierend auf SCIL-Profil |
| M5.2 | Trainingslektionen: Uebungen pro Frequenz (basierend auf Schwaechen) |
| M5.3 | Learning-Content Bibliothek: Video-Nuggets von Andreas' Bestand |
| M5.4 | Content-Zuweisung: Coach kann Lernmaterialien an Coachee zuweisen |
| M5.5 | Content-Kauf: Coach kauft Learning-Pakete (Stripe) |
| M5.6 | Fortschritts-Tracking: Welche Uebungen gemacht, Wiederholung planen |
| M5.7 | Push-Erinnerungen / E-Mail-Nudges fuer taegliches Training |

**Abhaengigkeit:** M1, M2, M3 (Grundstruktur muss stehen)
**Output:** Coachee trainiert taeglich mit KI-Agent + bekommt Video-Content

---

### Epic M6: Breakout-Sessions & Terminbuchung
**Ziel:** Coach und Coachee koennen regelmaessige Live-Sessions planen
**Prioritaet:** 🟢 MEDIUM — "Human in the Loop" sicherstellen
**Aufwand:** L (2-3 Wochen)

| Task | Beschreibung |
|------|-------------|
| M6.1 | Terminslot-System: Coach definiert verfuegbare Zeiten |
| M6.2 | Buchungs-Flow: Coachee bucht 15-Min-Slot bei seinem Coach |
| M6.3 | Kalender-Integration (Google Calendar / Outlook via API) |
| M6.4 | Video-Call: Embedded oder Link zu Zoom/Teams/Google Meet |
| M6.5 | Session-Vorbereitung: Agent erstellt Briefing fuer Coach (basierend auf Coachee-Daten) |
| M6.6 | Session-Notizen: Coach kann Notizen zur Session hinterlegen |
| M6.7 | Regelmaessige Zyklen: Automatische Wiederbuchung (z.B. jeden Montag) |

**Abhaengigkeit:** M2, M3 (Coach-Coachee-Beziehung)
**Output:** Regelmaessige Coach-Coachee-Sessions, KI bereitet vor, Coach challenged

---

## Timeline-Uebersicht

```
Phase 1: Revenue + Partner-Enablement (Wochen 1-6)
  M1: Code-System & Payment       [W1------W3]
  M2: Coach Dashboard                [W2--------W5]
  M3: Coachee-Portal                    [W4------W6]
  M4: AWS Deployment               [W3----W4]  (parallel)
                                           |
                         MVP 1.0 LIVE -----+ (Woche 6)
                         Coach kann Codes kaufen
                         Coachee kann Diagnostik machen
                         Coach sieht Ergebnisse

Phase 2: Training & Retention (Wochen 7-12)
  M5: Daily Training Agent          [W7--------W10]
  M6: Breakout-Sessions                [W9--------W12]
                                                   |
                         MVP 2.0 LIVE -------------+ (Woche 12)
                         Vollstaendiger Coach-Coachee-Zyklus
                         Diagnostik + Training + Live-Sessions
```

---

## Kosten-Schaetzung MVP

| Posten | EUR/Monat |
|--------|-----------|
| AWS Infra (ECS + RDS + Redis + ALB) | ~100-150 |
| Anthropic API (Diagnostik + Training) | ~100-300 |
| Stripe Gebuehren | 2.9% + 0.30/Txn |
| Domain + SSL | ~5 |
| **Total** | **~200-450** |

### Break-Even
- 1 Code = z.B. 79 EUR (Einzelpreis) / 49 EUR (im 10er-Paket)
- Break-Even bei ~4-6 Diagnostik-Codes pro Monat
- 143 bestehende SCIL Master Partner → sofortiges Umsatzpotential

---

## Offene Punkte (Klaerung mit PO noetig)

| # | Frage | Status |
|---|-------|--------|
| 1 | **Echte SCIL-Items**: Andreas muss den offiziellen Fragebogen liefern | ⏳ Warten auf Input |
| 2 | **Pricing**: Konkreter Preis pro Code / Paketpreise / Coach-Abo? | ❓ Offen |
| 3 | **AWS-Zugang**: MFA-Problem loesen (IAM User fuer Leonardo anlegen) | ⏳ Warten auf Andreas |
| 4 | **Video-Bibliothek**: Format/Hosting der bestehenden Learning-Videos? | ❓ Offen |
| 5 | **Domain**: scil-profile.de oder andere Domain? | ❓ Offen |
| 6 | **Self-Service vs. Coach-Only**: Sollen Endnutzer wirklich auch ohne Coach kaufen koennen? | ✅ Ja (bestaetigt im Call) |
| 7 | **Bestehende Partner-Daten**: Liste der 143 SCIL Master zum Seeden? | ❓ Offen |
| 8 | **MyCloud/NAS**: Andreas erwaehnt "kleine weisse Kiste" — relevanter Storage? | ❓ Klaeren |

---

## Naechster Schritt

**Empfehlung:** Mit **M1 (Code-System & Payment)** + **M4 (AWS Deployment)** parallel starten:
- M1 generiert sofort Revenue-Faehigkeit
- M4 macht die App fuer Andreas und Partner zugaenglich
- Beides hat keine Abhaengigkeit und kann sofort beginnen
- Blockiert: AWS-Zugang (IAM User einrichten mit Andreas)
