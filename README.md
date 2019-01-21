# Lab Item Assistant

[![Build Status](https://travis-ci.org/zyayoung/lab-item-tracking.svg?branch=master)](https://travis-ci.org/zyayoung/lab-item-tracking)

## Deploy

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Features

- Users
    - [ ] Admin
    - [x] Manager
    - [x] Normal User
- Location
    - [x] Tree structure
    - [x] QR Code
- Items
    - [ ] Add
    - [ ] Attr
    - [x] Location
    - [x] Owner
    - [ ] Share (link & unlink)
    - [ ] Edit
    - [x] Delete
- Trace
    - [x] Item location & quantity
    - [x] Operater
    - [x] Time
    - [ ] Attr changes
- Permission
    - [x] Public
    - [x] Private item
    - [x] Secret location
    - [ ] Apply for permission

## Modular item managing system

```json
{
    "name": "",
    "category": "",
    "attr":
        [{
        "name": "",
        "category": "",
        "item": ""
        }]
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
