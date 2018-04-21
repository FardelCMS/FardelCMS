# Another But Complete CMS

Implemented features are:

1. [Authentication](https://github.com/Boghche/Boghche/tree/master/web/core/auth)
	* Group-Permission based Users
	* Token base authentications
	* APIs are listed below:
		* Registeration API
		* Login API
		* RefreshToken API
		* Logout API
		* LogoutRefresh API
		* ProfileApi API
2. [Support for Media](https://github.com/Boghche/Boghche/tree/master/web/core/media)
3. [A complete Blog](https://github.com/Boghche/Boghche/tree/master/web/apps/blog)
3. [eCommerce](https://github.com/Boghche/Boghche/tree/master/web/apps/ecommerce)
3. Admin Panel
	* [Authentication API for admin](https://github.com/Boghche/Boghche/tree/master/web/core/panel/views/AUTHDOC.md)
	* [Media API for admin](https://github.com/Boghche/Boghche/tree/master/web/core/panel/views/MEDIADOC.md)
	* [Blog API for admin](https://github.com/Boghche/Boghche/tree/master/web/core/panel/views/BLOGDOC.md)

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