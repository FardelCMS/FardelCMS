# Authentication Module

All the endpoints starts with '/api/auth/{function}/'

## Registeration API

* url : '/api/auth/register/'
* content-type: 'application/json'

###### POST

* required arguments:
	* email
	* password
* optional arguments:
	* first_name
	* last_name
* responses with access_token + refresh_token

```
Successful response (200):
{
    'message': 'Successfully registered',
	'access_token': '????',
	'refresh_token': '????',
}
-----------------------
Unsuccessful responses:
409: {
    'message': 'A user with this email already exists.'
}
400: {
	'message':'Unvalid form submitted'
}
```


## Login API

* url : '/api/auth/login/'
* content-type: 'application/json'

###### POST

* required arguments:
	* email
	* password

```
Successful response (200):
{
    'message':'Successfully logined',
	'access_token': '????',
	'refresh_token': '????'
}
-----------------------
Unsuccessful responses:
(400): {
	'message':'Unvalid form submitted'
}
(401): {
    'message':'Username or password is not correct'
}
```

## RefreshToken API

* url : '/api/auth/refresh-token/'
* content-type: 'application/json'
* Authorization header with refresh token required

###### POST

```
Successful response (200):
{
	'access_token': '????'
}
```

## Logout API

* url : '/api/auth/logout/'
* content-type: 'application/json'
* Authorization header with access token required

###### POST

```
Successful response (200):
{
	'message': 'Access token has been revoked'
}
```

## LogoutRefresh API

* url : '/api/auth/logout-refresh/'
* content-type: 'application/json'
* Authorization header with refresh token required

###### POST

```
Successful response (200):
{
	'message': 'Refresh token has been revoked'
}
```

## ProfileApi API

* url : '/api/auth/profile/'
* content-type: 'application/json'
* Authorization header with access token is optional

###### GET

```
Successful response (200):
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

###### PUT

* To update your user profile
* Optional fields are
	* first_name
	* last_name
	* email
	* password

```
(200): {
	"message":"Profile successfully updated"
}
```

```
(204): {
	"message": "No profile to update"
}
```


## Errors

If a token needs to be refreshed:
```
(401): {
	"message": "Fresh token required"
}
```

Invalid token:
```
(422): {
	"message": reason
}
```

Expired token:
```
(401): {
	"message": "Token has expired"
}
```

Revoked token:
```
(401): {
	'message':'Token has been revoked'
}
```