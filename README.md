incendios.ttsda.cc
==================
*A map of forest fires in Portugal.*

The fire data is scraped from the "Proteção Cívil" website, and the fire hazard data from the "IPMA" website.

Dependencies
----------
* [requests](http://python-requests.org) ([pypi](https://pypi.python.org/pypi/requests))
* [pyproj](http://code.google.com/p/pyproj) ([pypi](https://pypi.python.org/pypi/pyproj))
* [pyyaml](http://pyyaml.org) ([pypi](https://pypi.python.org/pypi/pyyaml))
* [Pillow](http://python-imaging.github.io/) ([pypi](https://pypi.python.org/pypi/Pillow))
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/) ([pypi](https://pypi.python.org/pypi/beautifulsoup4))

###pip [(site)](http://pip-installer.org)
    # pip install requests pyproj pyyaml pillow beautifulsoup4

###Archlinux

    // if you prefer python 3
    # pacman -S python-requests python-pyproj python-yaml python-pillow python-beautifulsoup4

    // or python 2
    # pacman -S python2-requests python2-pyproj python2-yaml python2-pillow python2-beautifulsoup4

###Debian/Ubuntu

    // if you prefer python 3
    # apt-get install python3-requests python3-pyproj python3-yaml python3-pillow python3-bs4

    // or python 2
    # apt-get install python-requests python-pyproj python-yaml python-pillow python-bs4

Usage
-----
1. Set up a crontab to run `generate_fires.py` and `generate_hazard.py` regularly.  
The recommended rates are every minute for `generate_fires.py` and every hour for `generate_hazard.py`.

2. Point your webserver to the `html` directory

Press
-----
There have been a few press references to this project (please change this file and pull request if you find more, or e-mail me the article)

* [Sapo Tek](http://tek.sapo.pt/tek_mobile/apps/aplicacao_localiza_incendios_no_mapa_do_pais_1338121.html)
