|  | Develop  | Master |
| ------------- | ------------- | ------------- |
| Travis CI  | [![Build Status](https://travis-ci.org/mimischi/django-clock.svg?branch=develop)](https://travis-ci.org/mimischi/django-clock)  | [![Build Status](https://travis-ci.org/mimischi/django-clock.svg?branch=master)](https://travis-ci.org/mimischi/django-clock)  |
| Pyup.io  | [![Updates](https://pyup.io/repos/github/mimischi/django-clock/shield.svg)](https://pyup.io/repos/github/mimischi/django-clock/) | [![Updates](https://pyup.io/repos/github/mimischi/django-clock/shield.svg)](https://pyup.io/repos/github/mimischi/django-clock/) |
| Coverage  | [![codecov](https://codecov.io/gh/mimischi/django-clock/branch/develop/graph/badge.svg)](https://codecov.io/gh/mimischi/django-clock/branch/develop) | [![codecov](https://codecov.io/gh/mimischi/django-clock/branch/master/graph/badge.svg)](https://codecov.io/gh/mimischi/django-clock) |

# Clock

Genervt den Stundenzettel für deinen HiWi-Job dauernd per Hand ausfüllen zu müssen? Willst du eine komfortable, mobile und einfache Lösung? Dann ist das Projekt hier genau das richtige.
Clock erlaubt dem Nutzer seine Arbeitszeit zu stechen, nachträglich hinzuzufügen oder zu editieren.

## Mitarbeit

Das Projekt ist öffentlich zugänglich und kann deswegen gerne geforked werden. Um es lokal zu nutzen sind allerdings einige Einstellungen zu erledigen.
Das aktuelle Layout dieser Repository basiert auf [cookiecutter-django](https://github.com/pydanny/cookiecutter-django). Dementsprechend findet sich die generelle Nutzungsanleitung in [deren ReadTheDocs](http://cookiecutter-django.readthedocs.org/en/latest/developing-locally.html).

### Anleitung

Zur Mitarbeit sind `docker` und `docker-compose` notwendig.

#### 1. Develop branch klonen

    git clone https://github.com/mimischi/django-clock.git --branch develop

#### 2. Container bauen und starten

    docker-compose -f dev.yml build
    docker-compose -f dev.yml up -d
   
#### 4. Datenbank migrieren

    docker-compose -f dev.yml run django python manage.py migrate

Dazu kann jetzt noch ein Superuser erstellt werden. Grundsätzlich läuft das System jetzt. Unter Linux ist die Seite nun unter localhost:8000 aufrufbar.
