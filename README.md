|  | Develop  | Master |
| ------------- | ------------- | ------------- |
| Travis CI  | [![Build Status](https://travis-ci.org/mimischi/django-clock.svg?branch=develop)](https://travis-ci.org/mimischi/django-clock)  | [![Build Status](https://travis-ci.org/mimischi/django-clock.svg?branch=master)](https://travis-ci.org/mimischi/django-clock)  |
| Pyup.io  | [![Updates](https://pyup.io/repos/github/mimischi/django-clock/shield.svg)](https://pyup.io/repos/github/mimischi/django-clock/) | [![Updates](https://pyup.io/repos/github/mimischi/django-clock/shield.svg)](https://pyup.io/repos/github/mimischi/django-clock/) |
| Coverage  | [![codecov](https://codecov.io/gh/mimischi/django-clock/branch/develop/graph/badge.svg)](https://codecov.io/gh/mimischi/django-clock/branch/develop) | [![codecov](https://codecov.io/gh/mimischi/django-clock/branch/master/graph/badge.svg)](https://codecov.io/gh/mimischi/django-clock) |

# Clock

Genervt den Stundenzettel für deinen HiWi-Job dauernd per Hand ausfüllen zu müssen? Willst du eine komfortable, mobile und einfache Lösung? Clock erlaubt dem Nutzer seine Arbeitszeit zu stechen, nachträglich hinzuzufügen oder zu editieren. Und am Ende gibt es einen schicken Export als PDF!

### Anleitung

Zur Mitarbeit sind `docker` und `docker-compose` notwendig.

#### 1. Repository klonen

```
git clone https://github.com/mimischi/django-clock.git --branch develop
```

#### 2. Container bauen

```
docker-compose build
```

#### 3. Web & Datenbank Container starten

```
docker-compose up -d
```

#### 4. Datenbank migrieren

```
docker-compose run --rm web python manage.py migrate
```

#### 5. Superuser erstellen

```
docker-compose run --rm web python manage.py createsuperuser
```

Die Webseite ist jetzt unter `localhost:8000` erreichbar.
