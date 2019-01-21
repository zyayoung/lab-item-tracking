# Lab Item Assistant

[![Build Status](https://travis-ci.org/zyayoung/lab-item-tracking.svg?branch=master)](https://travis-ci.org/zyayoung/lab-item-tracking)

## Deploy

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Modules

- Login
- Location
    - tree structure
- Items
    - attr
    - Location
    - owner
    - share
- Permission
    - public
    - private item
    - secret location
- Trace
    - Item location & quantity changes

## Modular item managing system

```json
{
    name: "",
    category: "",
    attr: {
        [{
        name: "",
        category: "",
        item: ""
        ]}
    }
}
"""
Attr Description:
    Contain a list of tuples (name, category, item):
        name:     name of the item
        category: type(category) of the item. Including number, string, other categories, etc.
        item:     related information (ForeighKey)
"""
```
