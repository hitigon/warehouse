Warehouse
=========

![In Process](http://img.shields.io/badge/build-processing-red.svg "In Process")

![Python 2.7.6](http://img.shields.io/badge/Python-2.7.6-blue.svg "Python 2.7.6")
![Tornado 3.2](http://img.shields.io/badge/Tornado-3.2-orange.svg "Tornado 3.2")
![bcrypt 1.0.2](http://img.shields.io/badge/bcrypt-1.0.2-red.svg "bcrypt 1.0.2")
![pygit2 0.20.3](http://img.shields.io/badge/pygit2-0.20.3-yellow.svg "pygit2 0.20.3")
![pymongo 2.7](http://img.shields.io/badge/pymongo-2.7-lightgrey.svg "pymongo 2.7")
![mongoengine 0.8.7](http://img.shields.io/badge/mongoengine-0.8.7-brightgreen.svg "mongoengine 0.8.7")
![oauthlib 0.6.3](http://img.shields.io/badge/oauthlib-0.6.3-green.svg "oauthlib 0.6.3")

Warehouse provides a service to manage your projects with your team members. It includes the basic functions of project management systems, including task assginment, code management via Git, and team management etc. You are able to use this system to schedule your plans/tasks, report bugs and do code reviews with your team members. Warehouse only provides a set of RESTFul APIs, you can build your client on any platforms by using these APIs. The purpose of Warehouse is to simplify the project management system and the process of team project development.

Clients
-------

As I mentioned, Warehouse is only a set of APIs, and you can build your own clients. But, I will provide a web-server based client in future, and a mobile app as well (maybe).

REST API
--------

#### Projects

`GET /projects/`

`GET /projects/:name`

`POST /projects/`

`PUT /projects/:name`

`DELETE /projects/:name`

#### Tasks

#### Repos

#### Teams

#### Profile

#### Auth