# Lab Item Assistant

[![Build Status](https://travis-ci.org/zyayoung/lab-item-tracking.svg?branch=master)](https://travis-ci.org/zyayoung/lab-item-tracking)

## Deploy

```bash
python manage.py makemigrations inventory login
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Modular item managing system

```python
class Object:
    name = ""
    category = ""  # Options: item, client, contacts, etc.
    attr = "json string"  # main
    """
    Attr Description:
        Contain a list of tuples (name, category, item):
            name:     name of the item
            category: type(category) of the item. Including number, string, other categories, etc.
            item:     related information
    """
```
