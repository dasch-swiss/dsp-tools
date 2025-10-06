# Which GUI-Attributes have an effect

The following GUI-Attributes have no discernible effect.

It was possible to upload "erroneous" data through the API and the APP.

## Color

```json
    "gui_element": "Colorpicker",
    "gui_attributes": {
        "ncolors": 1
    }
```



## Decimal - Simple Text

```json
    "gui_element": "SimpleText",
    "gui_attributes": {
        "maxlength": 2,
        "size": 2
    }
```



## Decimal - Spinbox

```json
    "gui_element": "Spinbox",
    "gui_attributes": {
        "min": 1.0,
        "max": 3.0
    }
```


## Integer - Simple Text

```json
    "gui_element": "SimpleText",
    "gui_attributes": {
        "maxlength": 2,
        "size": 2
    }
```


## Integer - Spinbox

```json
    "gui_element": "Spinbox",
    "gui_attributes": {
        "min": 1,
        "max": 3
    }
```


## SimpleText

```json
    "gui_element": "SimpleText",
    "gui_attributes": {
        "maxlength": 3,
        "size": 3
    }
```


## Textarea

Note: It is not actually clear to me what effect these attributes should have.

```json
    "gui_element": "Textarea",
    "gui_attributes": {
        "cols": 1,
        "rows": 1,
        "width": "200%",
        "wrap": "hard"
    }
```


## UriValue

```json
    "gui_element": "SimpleText",
    "gui_attributes": {
        "maxlength": 3,
        "size": 3
    }
```
