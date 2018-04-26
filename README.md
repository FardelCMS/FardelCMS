# Another But Complete CMS

![docs badge](https://readthedocs.org/projects/boghche/badge/?version=latest)


Boghche is another but complete cms. Its server is written in python and has Vue + Nuxt, iOS and Android clients. Currently it has a complete blog and a complete eCommerce. Its goal is to make costumization very easy and simple.

[Documents](http://boghche.readthedocs.io/en/latest/)

## Installation

###### Requirements:

* python +3.5
* postgresql database

###### Install Postgresql database and database

Create development database (Postgresql):
```
$ sudo -u postgres psql

postgres=# CREATE USER dev_shop WITH PASSWORD '123';
postgres=# CREATE DATABASE dev_shop;
postgres=# GRANT ALL PRIVILEGES ON DATABASE dev_shop to dev_shop;
```

###### Install python dependencies:

```
$ pip install -r requirements.txt
```

###### Setup tables:
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

###### Run Tests:

```
$ python test.py
```

###### Run server:

```
$ python wsgi.py
```

###### To have sample data

```
$ pip install mimesis
$ python manage.py generate_fake
```
