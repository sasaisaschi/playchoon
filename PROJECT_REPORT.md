# PlayChoon – Technischer Bericht & Entwicklungsleitfaden

> Erstellt am: 2026-03-22
> Analysiert von: Lara (Claude Code – claude-sonnet-4-6)

---

## 1. Projektübersicht

**Name:** PlayChoon
**Zweck:** Spotify Playlist Generator – Nutzer geben Lieblingskünstler und gewünschte Songanzahl ein und erhalten eine fertige Spotify-Playlist direkt in ihrem Account.
**Status:** Funktionsfähig, deployed auf Vercel. Kein aktives Testing, keine CI/CD-Pipeline. Mehrere kritische Sicherheitslücken vorhanden.
**Live-Demo:** https://playchoon.vercel.app/
**Repository:** https://github.com/sasaisaschi/playchoon

---

## 2. Tech Stack

| Schicht | Technologie | Version |
|---|---|---|
| Backend | Python / Flask | nicht fixiert (requirements.txt ohne Versionen) |
| Spotify-Integration | Spotipy | nicht fixiert |
| Authentifizierung | Spotipy OAuth2 (`SpotifyOAuth`) | – |
| CORS | flask-cors | nicht fixiert |
| Formular | flask-wtf, wtforms | nicht fixiert (installiert aber ungenutzt) |
| Umgebungsvariablen | python-dotenv | nicht fixiert |
| Frontend | Vanilla HTML/CSS/JS + jQuery 3.5.1 | extern via CDN |
| CSS-Framework | Webflow-generiertes CSS | `style.css` (statisch) |
| Deployment | Vercel (Serverless Python) | ^33.2.0 (npm) |
| Node/npm | Nur für Vercel-Tooling | – |

---

## 3. Architektur & Ordnerstruktur

```
playchoon/
├── api/
│   ├── app.py                  # Flask-App, alle Routes & Logik
│   ├── .cache                  # Spotify OAuth Token-Cache (SICHERHEITSRISIKO – siehe §6)
│   ├── .gitignore              # Ignoriert nur __pycache__
│   ├── README.md               # Kurze interne Entwicklernotiz
│   ├── serverless-example.js   # Unbenutztes Beispiel-File (Vercel JS handler)
│   ├── static/
│   │   ├── favicon.ico/.png/.svg
│   │   ├── main.js             # Client-seitiger JS (Fetch API)
│   │   ├── style.css           # Webflow-generiertes CSS
│   │   └── playchoon-header-rm*.png  # Logo-Assets
│   └── templates/
│       └── index.html          # Einziges HTML-Template (Jinja2)
├── .env                        # Spotify Credentials (SICHERHEITSRISIKO – im gitignore, aber war commitet)
├── .env.local                  # Lokale Env-Vorlage (leer)
├── .gitignore                  # Enthält .env, .venv, node_modules etc.
├── .gitattributes
├── package.json                # Nur Vercel + Hilfspakete
├── package-lock.json
├── requirements.txt            # Python-Abhängigkeiten (ohne Versionen)
├── vercel.json                 # URL-Rewriting: alle Requests → /api/app
└── README.md                   # Projektbeschreibung (GitHub-facing)
```

**Architekturmuster:** Monolithische Flask-App als Serverless Function auf Vercel. Alle Routes, Business-Logik und OAuth-Flow befinden sich in einer einzigen Datei (`api/app.py`).

**Datenfluss:**
1. Nutzer öffnet `/` → Flask rendert `index.html`
2. Nutzer gibt Künstler + Songanzahl ein → `main.js` sendet `POST /generate_playlist`
3. Falls kein Session-Token: Flask gibt `auth_url` zurück → Browser-Redirect zu Spotify
4. Spotify-Callback landet auf `/callback` → Token wird in `session` gespeichert
5. Nutzer wiederholt Schritt 2 → Flask erstellt Playlist via Spotipy
6. Erfolg: Frontend zeigt Link zur neuen Spotify-Playlist

---

## 4. Features & Funktionalität

### Implementierte Features

| Feature | Beschreibung | Datei / Zeile |
|---|---|---|
| Startseite | Formular mit Künstler-Input und Song-Anzahl-Auswahl | `templates/index.html:19-55` |
| Spotify OAuth | Authentifizierung via `SpotifyOAuth`, scope: `playlist-modify-public` | `app.py:21-24` |
| Auth-URL-Abruf | `GET /get_auth_url` gibt JSON mit `auth_url` zurück oder redirected | `app.py:30-39` |
| OAuth Callback | `GET /callback` tauscht Code gegen Token, speichert in Session | `app.py:41-46` |
| Playlist-Generierung | `POST /generate_playlist` sucht Tracks per Artist, erstellt Playlist | `app.py:48-102` |
| Token-Refresh | Automatisches Refresh bei abgelaufenem Token (SpotifyException) | `app.py:56-64` |
| Songanzahl-Mapping | Dropdown-Werte (`First/Second/Third`) → 10/20/30 Songs | `app.py:72-77` |
| Erfolgsanzeige | Formular wird ausgeblendet, Link zur Playlist angezeigt | `main.js:19-28` |
| Fehleranzeige | Fehlermeldung bei API-Fehler oder Netzwerkproblem | `main.js:29-41` |
| Tooltip | Info-Overlay mit Nutzungsanleitung (hover auf "info"-Button) | `index.html:67-75` |
| CORS | Erlaubt Requests von vercel.app, localhost:8888 und localhost:5000 | `app.py:15` |

### Nicht implementierte / fehlende Features

- Keine Anzeige der generierten Songs im Browser
- Keine Möglichkeit, Playlists umzubenennen oder zu löschen
- Kein Logout / Session-Beendigung
- Kein Feedback während der Ladezeit (kein Spinner/Loading-State)
- Kein Input-Debouncing oder Artist-Validierung vor dem API-Call

---

## 5. UI/UX Beschreibung

**Layout:** Zentriertes Single-Page-Layout, dunkler Hintergrund (#1a1a2e o.ä.), Webflow-generiertes Grid-System (`w-container`, `w-row`, `w-col`).

**Komponenten:**
- `PLAYCHOON` – großes Logo als `<h1>` mit Custom-Font
- `SPOTIFY PLAYLIST GENERATOR` – Untertitel
- `Try for free` – dekorativer Trenner mit Linien (`beta-line`)
- Textfeld für Künstler (kommagetrennt, `maxlength="256"`)
- Dropdown: „Select Choons…" / „10 Choons" / „20 Choons" / „30 Choons"
- Button: „Push Button"
- Erfolgs- und Fehler-Div (initial ausgeblendet, per JS eingeblendet)
- Footer mit Copyright (`© 2024 TobisStudio`) und E-Mail-Link
- Info-Button mit Tooltip (CSS-only hover)

**Design-Sprache:** Dark-Mode, minimalistische Typografie, eigenwillige Terminologie (`Choons` statt Songs, `Push Button` statt Submit). Kein Responsive-Breakpoint-Handling sichtbar (Webflow-Klassen vorhanden, CSS aber statisch).

**Externe Abhängigkeiten im Frontend:**
- jQuery 3.5.1 via Webflow CDN (`d3e54v103j8qbb.cloudfront.net`) – **wird im eigenen JS nicht genutzt**
- Webflow-Script (`webflow.0d154b862.js`) – für Interaktionen aus Webflow-Export
- SVG-Icon-Assets von `assets-global.website-files.com` (Webflow-Hosting) – externe Abhängigkeit

---

## 6. Sicherheit & Abhängigkeiten

### Kritische Sicherheitsprobleme

> **Status:** Spotify API Credentials wurden am 2026-03-22 rotiert. Die alten Werte in `.env` (lokal, nicht getrackt) und `api/.cache` sind ungültig. Neue Credentials wurden im Spotify Developer Dashboard ausgestellt und als Umgebungsvariablen auf Vercel hinterlegt.

| Priorität | Problem | Datei | Beschreibung |
|---|---|---|---|
| 🔴 KRITISCH | ~~Echter API Secret im Repository~~ | ~~`.env`~~ | **ERLEDIGT (2026-03-22):** `.env` war lokal vorhanden, aber laut git-Historie **nie getrackt** – kein echter Commit mit Credentials. Spotify Credentials wurden vorsorglich rotiert. |
| 🔴 KRITISCH | Spotify Token im Repository | `api/.cache` Zeile 1 | Vollständiges OAuth Token-Objekt (access + refresh token) liegt im Repo – muss via `git rm --cached api/.cache` entfernt werden |
| 🟠 HOCH | Typo in Env-Variable | `.env.local` Zeile 3 | `BAS_URL` statt `BASE_URL` → `base_url` in `app.py:18` liest `BASE_URL`, Variable bleibt leer/unbemerkt |
| 🟠 HOCH | `os.urandom(24)` als Fallback-Secret | `app.py:13` | Bei jedem Serverless Cold Start wird ein neuer `secret_key` generiert → alle laufenden Sessions werden ungültig |
| 🟡 MITTEL | CSRF – niedriges Restrisiko | `app.py:15, 67` | CORS auf 3 Domains begrenzt + Endpoint liest JSON (`request.get_json()`), kein klassischer CSRF-Pfad. `flask-wtf` trotzdem entfernen oder gezielt einsetzen. |
| 🟡 MITTEL | Kein Input-Sanitizing | `app.py:93` | Künstlername wird ungefiltert in `sp.search(q='artist:' + artist.strip())` eingebaut – Injection in Spotify-Querys möglich |
| 🟡 MITTEL | `debug=True` in Produktion | `app.py:105` | Flask läuft lokal mit `debug=True` – auf Env-Variable umstellen |
| 🟢 NIEDRIG | `api/.cache` nicht in .gitignore | `api/.gitignore` | Enthält nur `__pycache__` – Token-Cache-File wird nicht ignoriert |

### Abhängigkeiten (requirements.txt)

```
flask          # keine Version fixiert
spotipy        # keine Version fixiert
flask-wtf      # installiert aber NICHT GENUTZT
wtforms        # installiert aber NICHT GENUTZT
python-dotenv  # keine Version fixiert
cors           # falsches Paket! (sollte flask-cors sein)
flask-cors     # korrekt
```

> **Problem:** `cors` (Zeile 6) ist kein gültiges PyPI-Paket für Flask. `flask-cors` (Zeile 7) ist die korrekte Abhängigkeit. `cors` kann zu einem Installationsfehler oder zur Installation eines falschen Pakets führen.

### npm-Abhängigkeiten (package.json)

```json
"@nuxt/ui": "^2.13.0"    // nicht genutzt – kein Nuxt im Projekt
"debug": "^4.3.4"         // nicht genutzt
"uuid": "^9.0.1"          // nicht genutzt
"vercel": "^33.2.0"       // korrekt – Deployment-Tool
```

> `@nuxt/ui`, `debug` und `uuid` sind ungenutzte npm-Abhängigkeiten.

---

## 7. Testing-Status

| Typ | Status |
|---|---|
| Unit Tests | ❌ Keine vorhanden |
| Integrationstests | ❌ Keine vorhanden |
| E2E-Tests | ❌ Keine vorhanden |
| Manuelle Tests | ✅ Manuell getestet (live Demo funktioniert) |
| CI/CD | ❌ Keine Pipeline konfiguriert |

---

## Entwicklungs-Roadmap

### Phase 1 – Kritische Fixes & Stabilisierung
> Muss vor jeder weiteren Entwicklung erledigt werden

- [x] **ERLEDIGT:** Spotify Credentials rotiert (2026-03-22) – neue `SPOTIFY_CLIENT_ID` und `SPOTIFY_CLIENT_SECRET` auf Vercel hinterlegen
- [x] `api/.cache` aus dem Repository entfernt (`git rm --cached api/.cache`)
- [x] `api/.gitignore` um `.cache`, `*.token`, `__pycache__/`, `*.pyc` erweitert
- [x] Typo `BAS_URL` → `BASE_URL` in `.env.local` korrigiert, Zeile `BASE_URL=https://playchoon.vercel.app` ergänzt
- [x] `app.secret_key` Fallback entfernt – `SECRET_KEY` ist jetzt Pflicht-Umgebungsvariable, App wirft `RuntimeError` wenn nicht gesetzt (`app.py:13-16`)
- [x] `debug=True` ersetzt durch `os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'` (`app.py:108`)
- [x] `cors` (falsches Paket) und `flask-wtf`, `wtforms` (ungenutzt) aus `requirements.txt` entfernt
- [x] `@nuxt/ui`, `debug`, `uuid` aus `package.json` entfernt – `name`, `version`, `description`, `scripts` (`dev`, `deploy`, `preview`) ergänzt

### Phase 2 – Core-Verbesserungen
> Architektur, Performance, Codequalität

- [x] Python-Abhängigkeiten mit fixen Versionen gepinnt: `flask==3.0.3`, `spotipy==2.23.0`, `python-dotenv==1.0.1`, `flask-cors==4.0.1`
- [x] `SECRET_KEY` als Pflicht-Umgebungsvariable gesetzt (Vercel Dashboard – durch Nutzer erledigt)
- [x] `api/app.py` aufgeteilt in `api/config.py` (Konfiguration), `api/spotify_service.py` (Spotify-Logik), `api/app.py` (Routes + App-Factory)
- [x] Input-Validierung eingebaut: leere Names gefiltert, max. 10 Artists, max. 100 Zeichen pro Name (`app.py:38-54`, `config.py:21-23`)
- [x] Loading-State implementiert: Button deaktiviert + „Loading..." während Fetch-Request (`main.js:setLoading`)
- [x] `flask-wtf` / `wtforms` bereits in Phase 1 entfernt – kein Handlungsbedarf
- [x] jQuery-CDN und Webflow-Script aus `index.html` entfernt (beide ungenutzt)
- [x] Fehlerbehandlung verfeinert: Server-Fehler werden abgefangen, benutzerfreundliche deutsche Fehlermeldungen zurückgegeben (`app.py`, `main.js`)
- [x] **Bugfix:** `vercel dev` Recursive-Invocation-Error behoben – `"dev"` Script aus `package.json` entfernt. `vercel dev` direkt im Terminal aufrufen; ein `dev`-Script ist für dieses serverless Python-Projekt nicht sinnvoll.

### Phase 3 – Feature-Erweiterungen
> Geplante Verbesserungen und neue Features

- [ ] **Playlist-Vorschau:** Generierte Songs im Browser anzeigen (Trackliste mit Cover, Künstler, Dauer) bevor Playlist erstellt wird
- [ ] **Playlist-Name:** Nutzer kann der Playlist einen eigenen Namen geben (Eingabefeld im Formular)
- [ ] **Logout-Funktion:** Session löschen und Spotify-Autorisierung widerrufen
- [ ] **Erweiterte Songanzahl:** Freitext-Eingabe oder größerer Range (z.B. 5–100 Songs)
- [ ] **Genre-Filter:** Spotify-Suche um Genre-Parameter erweitern
- [ ] **Responsive Design:** Mobile-Breakpoints prüfen und CSS anpassen
- [ ] **Ladeindikator:** Animierter Fortschrittsbalken während der Playlist-Erstellung
- [ ] **Erfolgsseite:** Eigene Seite nach Playlist-Erstellung mit Embeddable Spotify Player

### Phase 4 – Zukunft & Vision
> Langfristige Ideen und optionale Upgrades

- [ ] **Empfehlungsalgorithmus:** Spotify `recommendations`-Endpoint nutzen statt simpler Artist-Suche, für qualitativ hochwertigere Playlists
- [ ] **Nutzerkonto-Feature:** Playlist-Historie pro Nutzer speichern (Datenbank nötig, z.B. Supabase oder PlanetScale)
- [ ] **Social Sharing:** Playlist-Link direkt per E-Mail oder Social Media teilen
- [ ] **Mehrsprachigkeit:** i18n für DE/EN/ES – die App hat schon `lang="de"` im HTML, aber alle Texte sind englisch
- [ ] **CI/CD Pipeline:** GitHub Actions für automatisches Linting, Tests und Vercel Preview Deployments
- [ ] **Monitoring:** Error-Tracking via Sentry, Vercel Analytics aktivieren
- [ ] **PWA:** App als Progressive Web App konfigurieren (Service Worker, Manifest) für Offline-Fähigkeit
- [ ] **Eigene Domain:** Custom Domain statt `playchoon.vercel.app`

---

## Notizen & Offene Fragen

1. **`serverless-example.js` (api/serverless-example.js):** Dieses File scheint ein Überbleibsel aus der Vercel-Einrichtung zu sein. Es wird nicht verwendet. Klärung nötig: löschen oder Grundlage für eine zukünftige JS-API?

2. **`package.json`-Abhängigkeiten:** `@nuxt/ui` deutet auf eine geplante Nuxt.js-Migration hin. Ist das beabsichtigt? Wenn ja, müsste die gesamte Frontend-Architektur überarbeitet werden.

3. **Session-Persistenz auf Vercel Serverless:** Flask-Sessions sind Cookie-basiert und erfordern einen stabilen `secret_key`. Bei Serverless Functions wird bei jedem Cold Start ein neuer Key generiert (wenn kein `SECRET_KEY` in Env gesetzt ist), was alle laufenden Sessions ungültig macht. Dies muss vor dem Produktionsbetrieb gelöst werden.

4. **Spotify-Scope:** Aktuell wird nur `playlist-modify-public` angefragt. Wenn private Playlists gewünscht sind, muss `playlist-modify-private` ergänzt werden.

5. **`.idea`-Ordner:** IntelliJ/PyCharm-Projektdaten sind im Repository (nur im `.gitignore` für `.vscode` gelistet, nicht für `.idea`). Empfehlung: `.idea/` zu `.gitignore` hinzufügen.

6. **Copyright-Jahr:** Footer zeigt `© 2024 TobisStudio` – sollte auf `© 2026` aktualisiert werden.
