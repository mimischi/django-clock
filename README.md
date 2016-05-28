|  | Develop  | Master |
| ------------- | ------------- | ------------- |
| Travis CI  | [![Build Status](https://travis-ci.org/mimischi/django-clock.svg?branch=develop)](https://travis-ci.org/mimischi/django-clock)  | [![Build Status](https://travis-ci.org/mimischi/django-clock.svg?branch=master)](https://travis-ci.org/mimischi/django-clock)  |
| Require.io  | [![Requirements Status](https://requires.io/github/mimischi/django-clock/requirements.svg?branch=develop)](https://requires.io/github/mimischi/django-clock/requirements/?branch=develop)  | [![Requirements Status](https://requires.io/github/mimischi/django-clock/requirements.svg?branch=master)](https://requires.io/github/mimischi/django-clock/requirements/?branch=master)  |

# Clock

Genervt den Stundenzettel für deinen HiWi-Job dauernd per Hand ausfüllen zu müssen? Willst du eine komfortable, mobile und einfache Lösung? Dann ist das Projekt hier genau das richtige.
Clock erlaubt dem Nutzer seine Arbeitszeit zu stechen, nachträglich hinzuzufügen oder zu editieren.


## Nutzung

Folgt.


## Zukunft

Im fertigen Produkt soll gerade der Export der eingetragenen Arbeitszeit in ein gewünschtes Dateiformat möglich sein. Dies lässt sich dann beim Arbeitgeber bzw. der Personalabteilung der Goethe-Universität einreichen, um seinen Soll als HiWi zu erfüllen. Für die genaue Thematik siehe: [Mindestlohngesetz](https://de.wikipedia.org/wiki/Mindestlohngesetz_%28Deutschland%29) oder [MiLoG](http://www.gesetze-im-internet.de/milog/).

## Mitarbeit

Das Projekt ist öffentlich zugänglich und kann deswegen gerne geforked werden. Um es lokal zu nutzen sind allerdings einige Einstellungen zu erledigen.
Das aktuelle Layout dieser Repository basiert auf [cookiecutter-django](https://github.com/pydanny/cookiecutter-django). Dementsprechend findet sich die generelle Nutzungsanleitung in [deren ReadTheDocs](http://cookiecutter-django.readthedocs.org/en/latest/developing-locally.html).

### Anleitung


Hier für muss die aktuelle Version von Docker installiert sein. Am einfachsten erledigt sich das mit der Docker-Engine. Da die Entwicklung auf Windows aktuell (2016-04) noch Probleme bereitet, sollte OS X oder ein anderes UNIX System zur Entwicklung werden.

#### 1. Develop branch klonen

    git clone https://github.com/mimischi/django-clock.git --branch develop

#### 2. Für OS X (nicht nötig auf Linux)

Aktuell muss auf OS X (und Windows) eine extra VM eingerichtet werden, damit Docker läuft. Dazu muss auch [VirtualBox](https://www.virtualbox.org/) installiert sein.

    docker-machine create --driver virtualbox clock
    
Danach muss die soeben erstellte Maschine zur aktuell genutzten gesetzt werden:

    eval "$(docker-machine env clock)"

#### 3. System aufbauen & starten

    docker-compose -f dev.yml build
    docker-compose -f dev.yml up -d
   
#### 4. Datenbank migrieren

    docker-compose -f dev.yml run django python manage.py migrate


Dazu kann jetzt noch ein Superuser erstellt werden. Grundsätzlich läuft das System jetzt. Unter Linux ist die Seite nun unter localhost:8000 aufrufbar. Unter OS X/Windows führt man folgenden Befehl aus und findet die zugehörige IP heraus:

    docker-machine env clock

Für weitere Hilfe einfach der [offiziellen Anleitung von cookiecutter-django](http://cookiecutter-django.readthedocs.org/en/latest/developing-locally-docker.html) folgen.
