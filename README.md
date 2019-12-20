# Another But Complete CMS

![docs badge](https://readthedocs.org/projects/boghche/badge/?version=latest)


Fardel is another but complete CMS. Its server is written in python and has Nuxt and iOS clients. Currently it has a complete blog and a complete eCommerce. Its goal is to make costumization very easy and simple.


## Installation

You can easily install fardel with pip command:

`pip install fardel`

## Manage commands

For migration command and costum commands:

```
from fardel.manager import FardelManager, Fardel
from fardel.config import BaseConfig

fardel = Fardel(BaseConfig)
manager = FardelManager(fardel)


if __name__ == "__main__":
    manager.run()
```

## WSGI Server

For deployment and tests:

```
from fardel import Fardel
from fardel.config import BaseConfig

fardel = Fardel(BaseConfig)
app = fardel.app

if __name__ == "__main__":
    fardel.app.run()
```