# textSimilarity
Simple API written in Python for text similarity using NLP. 

### Requirements 

Docker

### Setup

docker-compose build
docker-compose up

### Routes for testing

```localhost:5000/register```

Method: POST

Body: 
```
    "username": "test",
    "password": "test123",
```

```localhost:5000/detect```

Method: POST

Body: 
```
    "username": "test",
    "password": "test123",
    "text1": "I have a dog. He is very cute"
    "text2": "My dog is very cute"
```

```localhost:5000/refill```

Method: POST

Body: 
```
    "username": "test",
    "admin_pw": "test123", (hardcoded in app.py for testing purposes)
    "refill": 5
```

### Description

Only done for fun, was looking at the flask changes and seeing what was new. So I added 
text similarity just while testing, so nothing mayor as a real authorization is created.
Mongodb is used for storing if someone was wondering and could not find where it is.