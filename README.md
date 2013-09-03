incendios.ttsda.cc
==================
*A map of forest fires in Portugal.*

The fire data is scraped from the "Proteção Cívil" website, and the fire hazard data from the "IPMA" website.

Dependencies
----------
* [requests](http://python-requests.org) ([pypi](https://pypi.python.org/pypi/requests))
* [pyproj](http://code.google.com/p/pyproj) ([pypi](https://pypi.python.org/pypi/pyproj))
* [pyyaml](http://pyyaml.org) ([pypi](https://pypi.python.org/pypi/pyyaml))
* [PIL](http://www.pythonware.com/products/pil) ([pypi](https://pypi.python.org/pypi/PIL))

Usage
-----
1. Set up a crontab to run `generate_fires.py` and `generate_hazard.py` regularly.  
The recommended rates are every minute for `generate_fires.py` and every hour for `generate_hazard.py`.

2. Point your webserver to the `html` directory