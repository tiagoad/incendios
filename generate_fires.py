#!/usr/bin/env python
# -*- coding: utf-8 -*-

# generate.py
# Generates the fires.json file with all the fire and fire hazard information

# Logging
import logging

# System
import os

# HTTP
import requests

# Parsing
from tidylib import tidy_document
import HTMLParser
import xml.etree.ElementTree as ElementTree
import re

# Serializing
import json
import yaml

# Date and Time
import datetime

# Coordinates
import pyproj

# Decimal type
from decimal import Decimal, getcontext

# Load the config
config = yaml.load(open(os.path.dirname(os.path.realpath(__file__)) + '/config.yml', 'r'))

# Set the loglevel
log_level = logging.ERROR
if config['debug']:
	log_level = logging.INFO
logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)

def clean(string):
	"""
	Strips strings from HTML escape codes and leading/trailing spaces
	"""
	h = HTMLParser.HTMLParser()
	return h.unescape(string).strip()

# Request the HTML page from Proteção Cívil
logging.info('Requesting HTML')
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.73.11 (KHTML, like Gecko) Version/7.0.1 Safari/537.73.11' # Extremely common User Agent
}
r = requests.get('http://www.prociv.pt/Publico/fogoslist2007.asp', headers=headers, timeout=10)

# List that will be filled with the fires
output = {}
output['fires']  = {}
output['hazard'] = {}

# Page was not properly retrieved
if r.status_code != 200:
	logging.fatal('Error downloading HTML: Status code %s' % r.status_code)
	exit()

# Fix the disgusting HTML retrieved
logging.info('Cleaning HTML')
tidyhtml, errors = tidy_document(r.content, options = {
	'char-encoding': 'utf8',
	'numeric-entities': True
})

logging.info('Parsing HTML')

# Remove xmlns tag
tidyhtml = re.sub('xmlns="[^"]+"', '', tidyhtml, count=1)

# Create an ElementTree root from the tidyied HTML
root = ElementTree.fromstring(tidyhtml)

# Get the individual fire tables
incendios = root.findall(".//table[@id='ewlistmainNew']/tr/td/table")

# Parse each table
for i, incendio in enumerate(incendios):
	logging.info('Parsing fire %s/%s' % (i+1, len(incendios)))
	data = {}

	# Get the individual data rows
	info = incendio.findall("tr")

	## Basic data
	basic = info[1].findall("td/table/tr")[1].findall("td")

	# Extract coordinates from map url 
	coord_match = re.search(r"x=(?P<x>[0-9.]+)&y=(?P<y>[0-9.]+)", basic[0].find('a').attrib['href'].replace(',', '.'))

	data['id'] = clean(ElementTree.tostringlist(basic[1].find('span'))[5])
	
	pt_x = coord_match.group('x')
	pt_y = coord_match.group('y')

	lisboa_militar = pyproj.Proj("+init=epsg:20790 +nadgrids=pt73_e89.gsb")
	wgs84 = pyproj.Proj("+init=epsg:4326")
	
	wgs_x, wgs_y = pyproj.transform(lisboa_militar, wgs84, pt_x, pt_y)
	
	data['coordinates'] = {
		'x': wgs_x,
		'y': wgs_y
	}
	data['location'] = clean(ElementTree.tostringlist(basic[1].find('span'))[2])
	data['concelho'] = basic[4].find('span').text
	data['distrito'] = basic[5].find('span').text
	data['tipo'] = basic[7].find('span').text
	if data['tipo'] == 'Inc. em Mato':
		data['tipo'] = 'Incêndio em Mato'
	elif data['tipo'] == 'Inc. em Floresta':
		data['tipo'] = 'Incêndio em Floresta'

	data['fase'] = basic[6].find('span/font').text
	if data['fase'] == None:
		data['fase'] = basic[6].find('span/font/strong').text

	date = basic[2].find('div/span').text
	time = basic[3].find('div/span').text
	splitdate = date.split('/')
	splittime = time.split(':')
	dt = datetime.datetime(int(data['id'][:4]), int(splitdate[1]), int(splitdate[0]), int(splittime[0]), int(splittime[1]))
	
	data['timestamp'] = dt.strftime("%s")
	data['datetime'] = dt.strftime("%Y.%m.%d %H:%M")

	## Firefighting Means
	data['meios'] = {}
	meios = [int(meio.text) for meio in info[2].findall("td/table/tr")[2].findall("td/span")]

	# Operationais
	operacionais = data['meios']['operacionais'] = {}
	operacionais['Bombeiros'] = meios[0]
	operacionais['Grupo de Intervenção de Proteção e Socorro'] = meios[1]
	operacionais['Força Especial de Bombeiros'] = meios[2]
	operacionais['Sapadores Florestais'] = meios[3]
	operacionais['Grupo de Análise e Uso de Fogo'] = meios[4]
	operacionais['Outros'] = meios[5]
	operacionais['total'] = sum(operacionais.values())

	# Veículos Operacionais
	veiculos = data['meios']['veiculos'] = {}
	veiculos['Veículos Operacionais'] = meios[7]
	veiculos['Viaturas Médicas'] = meios[9]
	veiculos['Outros Veículos'] = meios[8]
	veiculos['total'] = sum(veiculos.values())

	# Meios Aérios
	aerios = data['meios']['aerios'] = {}
	aerios['Helicópteros de Ataque Inicial'] = meios[10]
	aerios['Helicópteros Bombardeiros'] = meios[11]
	aerios['Aviões de Ataque Inicial'] = meios[12]
	aerios['Aviões Bombardeiros'] = meios[13]
	aerios['Helicóptero de Socorro e Assistência'] = meios[14]
	aerios['Outros'] = meios[15]
	aerios['total'] = sum(aerios.values())

	# Outros Meios
	data['meios']['outros'] = meios[16]

	## Details
	detalhes = info[3].find('td/table').findall('tr/td')
	
	data['ponto_situacao'] = clean(detalhes[0].find('span').text)
	
	onclick = detalhes[1].find('a').attrib['onclick']
	m = re.search(r"open\('(?P<link>.+?)'", onclick)
	
	data['link'] = 'http://www.prociv.pt/Publico/' + m.group('link')
	data['cos'] = clean(detalhes[2].find('span').text)
	
	regex_coord = r"(?P<lat_sig>[NS]) (?P<lat_deg>\d+). (?P<lat_min>\d+)' (?P<lat_sec>\d+)'' (?P<long_sig>[EW]) (?P<long_deg>\d+). (?P<long_min>\d+)' (?P<long_sec>\d+)''"

	try:
		m = re.search(regex_coord, clean(detalhes[3].find('span').text))
		
		# Convert Deg,Min,Sec Latitude to Decimal
		latitude = float(m.group('lat_deg')) + float(m.group('lat_min'))/60 + float(m.group('lat_sec'))/3600
		if m.group('lat_sig') == 'S':
			latitude = -latitude

		# Convert Deg,Min,Sec Longitude to Decimal
		longitude = float(m.group('long_deg')) + float(m.group('long_min'))/60 + float(m.group('long_sec'))/3600
		if m.group('long_sig') == 'W':
			longitude = -longitude

		data['posto_operacional'] = {
			'x': longitude,
			'y': latitude
		}
	except AttributeError:
		pass

	output['fires'][data['id']] = data

# Generation time
output['gentimestamp'] = datetime.datetime.today().strftime("%s")

logging.info('Saving json')
json.dump(output, open(os.path.dirname(os.path.realpath(__file__)) + '/html/fires.json', 'w'))
