# Flask Blog
SQLAlchemy, Bootstrap, Flask, Jinja, password hashing/salting, and User Authentication

```
Note: I am aware this project could use considerable refactoring to make it more robust, implement OOP, etc. 
This was a training exercise uploaded as-is.
I am currently focused on exploring new concepts rather than perfecting what currently exists. 
```

## Project Features

### Users & an Admin Account
This blog supports user registration and login confirmation using decorators. The database saves users and encrypts their passwords using SHA256.

The first user in the database is designated the admin. Decorators are also used to ensure only the admin can create, edit, and delete posts.

### Dynamic Displays
Using user authentication, the header and other features will change. If logged in, the 'register' and 'login' links in the header will not display, a 'logout' link will appear instead.

If logged in as the admin, buttons to delete and edit posts will display. Otherwise they will not.

### Comments
The database also stores and serves the comments on each post. Any user is allowed to comment, but one must be logged into an account to post a comment.

### Bootstrap
The Bootstrap functionality is a provided template (clean-blog). While I have done a little exploration of bootstrap and template inheritance, that was not put into practice here. The focus was Flask, database functionality, and user authentication.
