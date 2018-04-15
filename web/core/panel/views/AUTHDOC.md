# User API

* url : '/api/panel/users/[<user_id>/]'
* content-type: 'application/json'
* Authorization header with access token required

## GET method

* If user_id is provided it responses like:

```
(200): {
	"user":	{
        'id':"Number", 'first_name':'First Name', 'last_name':"Last Name",
        'email':'Email' [,'group': 'Group Name'] [,'is_admin': true] [,'is_staff':true]
    }
}
```

* If user_id is not provided it responses like:

```
(200): {
	"users": [user, user, user]
}
```

* If user_id is not valid:

```
(400): {
	'message': 'User not found'
}
```

## POST method

* required data to create
	* email
	* password
* optional fields
	* first_name
	* last_name
	* group_id
	* confirmed
	* is_admin
	* is_staff

* It responses successfully :

```
{
    'message': "User successfully added"
    'user': user_object
}
```

* If form is not valid:

```
(422): {
	'message':'{field} must be provided.'
}
```

* If already exists:
```
(422): {
	"message": "User already exists"
}
```

## DELETE method

* required data to delete
	* user_id (in url directory)

```
(200): {
	"message":"User successfully deleted"
}
***** OR *****
(200): {
	"message":"Users successfully deleted" (I know there's no way for more than one user to have an ID)
}
```

* It responses if there's no user with this user_id:
```
(404): {
	"message":"No user deleted"
}
```

* If you try to delete yourself ?

```
(422): {
	"message":"You can't delete yourself"
} 
```

## PUT method

* required data to update
	* user_id (in url directory)


```
(200): {
	"message":"User successfully updated", 'user':user_object
}
```

* If user_id is not valid

```
(404): {
	"message": "User not found"
}
```