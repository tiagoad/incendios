incendios.ttsda.cc
==================
*A map of forest fires in Portugal.*

The fire data is scraped from the "Proteção Cívil" website, and the fire hazard data from the "IPMA" website.

Dependencies
----------

###pip [(site)](http://pip-installer.org)
    pip install -r requirements

Usage
-----
1. Set up a crontab to run `generate_fires.py` and `generate_hazard.py` regularly.  
The recommended rates are every minute for `generate_fires.py` and every hour for `generate_hazard.py`.

2. Point your webserver to the `html` directory

Press
-----
There have been a few press references to this project (please change this file and pull request if you find more, or e-mail me the article)

* [Sapo Tek](http://tek.sapo.pt/tek_mobile/apps/aplicacao_localiza_incendios_no_mapa_do_pais_1338121.html)
