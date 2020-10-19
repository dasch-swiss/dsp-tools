import requests

base = 'http://127.0.0.1:5000/v2/metadata/'

r = requests.put(base + 'project', {
        "data": "something",
        "metadata": "Imagine this to be a dict with metadata"
    })

print(r.json())
