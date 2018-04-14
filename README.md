# eCommerce Shop Restful Backend

Implemented features are:

1. [Authentication](https://github.com/Boghche/Boghche/tree/master/web/core/auth)
	1. Group-Permission based Users
	2. Token base authentications
	3. APIs are listed below:
		1. Registeration API
		2. Login API
		3. RefreshToken API
		4. Logout API
		6. LogoutRefresh API
		5. ProfileApi API

## Installation

Create development database (Postgresql):
```
$ sudo -u postgres psql

postgres=# CREATE USER dev_shop WITH PASSWORD '123';
postgres=# CREATE DATABASE dev_shop;
postgres=# GRANT ALL PRIVILEGES ON DATABASE dev_shop to dev_shop;
```

Install python dependencies:
```
$ pip install -r requirements.txt
```
