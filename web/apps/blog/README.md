# Blog Api Documentation

## Objects:

Category object:
```javascript
{
	"id":Integer, "name":"Name"
	"posts": [list of post_objects] // If gettig a spacific Category
}
```


Tag object:

```javascript
{
	"id":Integer, "name":"Name", "frequency":Integer,
	"posts": [list of post_objects] // If getting a spacific Tag
}
```

post object:

```javascript
{
	"id": Integer, "title":"Title",
    "allow_comment": Boolean, "created_time":Timestamp(Integer),
    "update_time":Timestamp(Integer),
    "category":category_object, "tags":[list of tag_objects]
    "content": "content of post"
    "summarized": "Summarized text of content"
    "comments_count": Integer,
    // We have summarized or content ( not both together )
}
```

Comment object:
```javascript
{	
    "author_email":self.author_email, "author_name":self.author_name, // If commenter wasn"t registed user
    "user": user_object // If commenter was registered
    "id":Integer, "content":"Content", "create_time":Integer,
    "replies": [list of comment_objects]
}
```

## Post Api

###### get

* url: ```/posts/```
* query parameters:
	* page
	* per_page

```javascript
{
	"posts": [list of post_objects]
}
```

* url: ```/posts/<post_id>/```

```javascript
{
	"post": post_object
}
```

* Errors: [404]

```javascript
(404): {
	"message":"No post with this id"
}
```

## Comment Api

###### get

* url ```/api/blog/posts/<post_id>/comments/```
* query parameters:
	* page
	* per_page

```javascript
{
	"comment": [list of comment_objects]
}
```

###### post

* url ```/api/blog/posts/<post_id>/comment/```
* Authorization token is not required but optional
* required data:
	* author_name (if you dont use access_token)
	* author_email (if you dont use access_token)
	* content
* optional data:
	* parent_comment_id

```
{
	"message":"Comment successfuly added"
}
```

###### Errors

If you give invalid post id:

```javascript
(404): {
	"message":"No post with this id"
}
```

If you dont provide content for post

```
(422): {
	"message":"Comment needs content"
}
```

If you try to post without authorization token or you dont provide author_name and author_email

```
(422): {
	"message":"Author name and Author email are required to post a comment or you need to sign in"
}
```

## TagApi

###### get

* url: ```/api/blog/tags/<post_id>/posts/```

```
{
	"tags": [list of tag_object]
}
```

* url: ```/api/blog/tags/<post_id>/posts/```

```
{
	"tag": tag_object
}
```

###### Errors

If id is invalid

```
(404): {
	"message": "No tag found with this id"
}
```