# Lab Item Assistant

[![Build Status](https://travis-ci.org/zyayoung/lab-item-tracking.svg?branch=master)](https://travis-ci.org/zyayoung/lab-item-tracking)

## Deploy

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

If you want to use full functions of it:

```bash
cp local_settings.py.template local_settings.py
vi local_settings.py
```

Edit the settings, then run:

```bash
python manage.py runserver
```

## Features

- Users
    - [x] Admin
    - [x] Manager
    - [x] Normal User
- Location
    - [x] Tree structure
    - [x] QR Code
- Items
    - [x] Add
    - [x] Attr
    - [x] Location
    - [x] Owner
    - [x] Share (link & unlink)
    - [x] Edit
    - [x] Delete
- Trace
    - [x] Location
    - [x] Quantity
    - [x] Operater
    - [x] Time
    - [ ] Attr
- Permission
    - [x] Public
    - [x] Private item
    - [x] Secret location
    - [x] Apply for permission
