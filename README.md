# ifrOSS Knowledge Center

Urteils- und Lizenzsammlung des Instituts für Rechtsfragen der Freien und Open Source Software.

## Struktur

In der obersten Eben befinden sich `index.html` und seine englischsprachige Variante `index_en.html`. Beide beinhalten die Homepage, die bei einem öffnen der `*.github.io` erstmal erscheint dann zu den Inhaltsseiten verlinkt. Diese ist im Gegensatz zu den Inhaltsseiten in HTML formattiert

Die Inhaltsseiten befinden sich alle in `./Pages/`. Jede Seite hat ihren eigenen Ordner, so z.B. `./Pages/creative_commons_cases/`, der wiederrum jeweils zwei Markdown-Dateien enthält für jede Sprache, hier `./Pages/creative_commons_cases/de.md` und `./Pages/creative_commons_cases/en.md`. Es ist wichtig das beide Versionen immer Formatgleich bleiben, alles außer Textänderungen sollten immer wiedergespiegelt werden. Enthält eine Seite Unterseiten ändert dies nichts an der Struktur, beim Licence-Center befindet sich die deutsche Hauptseite bei `./Pages/licence_center/de.md`, dessen deutsche Unterseite über FOSS-Lizenzen befindet sich dann bei `./Pages/licence_center/foss/de.md`.

## To-do
