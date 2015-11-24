.. image:: https://travis-ci.org/mimischi/django-clock.svg?branch=master
     :target: https://travis-ci.org/mimischi/django-clock.svg?branch=master
     :alt: Travis-CI Status

.. image:: https://requires.io/github/mimischi/django-clock/requirements.svg?branch=master
     :target: https://requires.io/github/mimischi/django-clock/requirements/?branch=master
     :alt: Requirements Status

Clock
==============================

Genervt den Stundenzettel für deinen HiWi-Job dauernd per Hand ausfüllen zu müssen? Willst du eine komfortable, mobile und einfache Lösung? Dann ist das Projekt hier genau das richtige.
Clock erlaubt dem Nutzer seine Arbeitszeit zu stechen, nachträglich hinzuzufügen oder zu editieren.


Zukunft
-------

Im fertigen Produkt soll gerade der Export der eingetragenen Arbeitszeit in ein gewünschtes Dateiformat möglich sein. Dies lässt sich dann beim Arbeitgeber bzw. der Personalabteilung der Goethe-Universität einreichen, um seinen Soll als HiWi zu erfüllen. Für die genaue Thematik siehe: [Mindestlohngesetzes](https://de.wikipedia.org/wiki/Mindestlohngesetz_%28Deutschland%29)
([MiLoG](http://www.gesetze-im-internet.de/milog/)).


Mitarbeit
---------

Das Projekt ist offensichtlich öffentlich zugänglich und kann deswegen gerne geforked werden. Um es lokal zu nutzen sind allerdings einige Einstellungen zu erledigen.
Das aktuelle Layout dieser Repository basiert auf [cookiecutter-django](https://github.com/pydanny/cookiecutter-django). Dementsprechend findet sich die generelle Nutzungsanleitung in [deren ReadTheDocs](http://cookiecutter-django.readthedocs.org/en/latest/developing-locally.html).


Anleitung (ohne Docker)
-----------------------

Git repository initialisieren und aktuellen master-branch klonen::
    git clone https://github.com/mimischi/django-clock.git

Standardmäßig zeigt [requirements.txt](requirements.txt) auf die [production.txt](requirements/production.txt). Wir wollen allerdings im lokalen Development keine Dependencies für die Produktion installieren.
requirements.txt anpassen und für git als un-modifiziert markieren::

    -r requirements/local.txt
    git update-index --assume-unchanged requirements.txt```

pip requirements installieren (bitte [virtualenv](https://virtualenv.pypa.io/en/latest/) nutzen!)
    pip install -r requirements.txt

Node.js Pakete installieren ([node.js](https://nodejs.org/) muss installiert sein)
    npm install

Für die lokale Entwicklungsumgebung muss noch eine Environmentvariable gesetzt werden, die auf einen [PostgreSQL-Server](http://www.postgresql.org/) zeigt.

    set DATABASE_URL=postgres://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>

Linux/OS X Nutzer fügen die Zeile hier hinzu:
    <path-to-the-Env>/<my-env-name-for-clock>/bin/activate
Windows Nutzer machen dies hier:
    <path-to-the-Env>/<my-env-name-for-clock>/Scripts/activate.bat

Bei mir sitzt die Zeile direkt nach der zweiten Zeile in der jeweiligen Datei.


Nutzung mit Docker
------------------

Anleitung zu finden (cookiecutter-django.readthedocs.org/en/latest/developing-locally-docker.html)[hier].

Die Datei [env.example](env.example) muss zu .env umbenannt und die jeweiligen Umgebungsvariablen angepasst werden.
