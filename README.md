# Lab Item Assistant

## Deploy

```bash
python manage.py makemigrations inventory login
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Modular item manage system

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
