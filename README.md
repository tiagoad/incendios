incendios
=========
*A map of forest fires in Portugal.*

**THIS NO LONGER WORKS:** Although the fire hazard script still works, prociv removed the HTML fire occurence table from their website and replaced it with a generated PDF (why?), making the `generate_fires.py` script useless.
---

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

* [Sapo Tek](https://tek.sapo.pt/mobile/apps/artigos/aplicacao-localiza-incendios-no-mapa-do-pais)
