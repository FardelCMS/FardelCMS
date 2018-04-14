# Authentication Module

All the endpoints starts with '/api/auth/{function}/'

## Registeration API

* url : '/api/auth/register/'
* content-type: 'application/json'
* required arguments:
	* email
	* password
* responses with access_token + refresh_token

```
{
    'message': 'Successfully registered',
	'access_token': '????',
	'refresh_token': '????',
}
```


## Login API

* url : '/api/auth/login/'
* content-type: 'application/json'
* required arguments:
	* email
	* password

```
{
    'message':'Successfully logined',
	'access_token': '????',
	'refresh_token': '????'
}
```

## RefreshToken API

* url : '/api/auth/login/'
* content-type: 'application/json'
* Authorization header with refresh token required

```
{
	'access_token': '????'
}
```

## Logout API

* url : '/api/auth/logout/'
* content-type: 'application/json'
* Authorization header with access token required

```
{'message': 'Access token has been revoked'}
```

## LogoutRefresh API

* url : '/api/auth/logout/'
* content-type: 'application/json'
* Authorization header with refresh token required

```
{'message': 'Refresh token has been revoked'}
```

## ProfileApi API

* url : '/api/auth/profile/'
* content-type: 'application/json'
* Authorization header with access token is optional

```
{
	"user":
	{
        'id':"Number", 'first_name':'First Name', 'last_name':"Last Name",
        'email':'Email' [,'group': 'Group Name'] [,'is_admin': true] [,'is_staff':true]
    }
}
******** OR **********
{'message':'Not login', 'user':None}
```