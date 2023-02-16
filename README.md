# Foundational Template

This template is created to allow for quick and standardized development and structure.

*All code* should follow the [Pep 8 Style Guide](https://www.python.org/dev/peps/pep-0008/).
## Virtual Environment

This is a python 3.6 application.  To create your virtual environment use:

    virtualenv -p python3 noauth-marketing

## Organization

* /controller - Place of entry for major pieces of different functionality
* /service - Where all object based repeatable work is kept
* /service/dao - Data Access Objects, the only things allowed to directly access internal data

Crontrollers access Services.
Services access DAOs.
Controllers ***NEVER*** access DAOs directly.

* /common - Place for functions that can be used anywhere.
* /controller/common - Common only for controllers
* /service/common - Common only for services
* /config - Environmental variables
* /local - Application variables
* /tests - Place for all tests

## Get Started

Set your enviroment variable so that it uses the correct config file.

    export APP_CONFIG_FILE=<full path to>/config/<environment>.py

## Copyright 2016-2018

Copyright is claimed on all code by Simpledata, Inc 2016-2018
