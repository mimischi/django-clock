# Changelog

## 2.0 (2017-11-01)

### Release 2.0

This release is supposed to be a "small restart" of the project.

* Update project structure.
* Change local development environment to use `docker-compose` only.
* Change Dokku deploy to `Dockerfile`.
* Use `pipenv` and `Pipfile` instead of old `requirements.txt`.
* Remove obsolete files

## 1.0 (2017-10-22)

* Final 1.0 release. Upcoming releases will introduce breaking changes.
* Added unit tests for Shifts
* Fixed several end-user bugs

## 0.9

* Added ability to add tags to shifts
    * It's not yet possible to do any filtering by tags
* Added reCAPTCHA
* Reformatted accounts-templates and its translations

## 0.8.0 (2016-06-13)

* First release, there was no CHANGELOG before that
* Features
    * Track your work time on a monthly basis
        * Start a current shift, pause and stop it
        * Add already finished shifts afterwards
        * Edit finished shifts or delete them
    * Add contracts to sort your shifts
        * Assign your monthly work hours for future analysis
    * Export finished shifts from each month as PDF

* Behind the scenes
    * Uses the newest Django version 1.9.7
    * Built on cookiecutter-django
    * Docker for independent host OS deployment
    * Compatible to Dokku 0.5.7 for easier heroku-like, zero-downtime deploys
    * Builds on Travis-CI
