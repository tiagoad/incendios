#!/usr/bin/env python
# -*- coding: utf-8 -*-

# risco.py
# Generates the hazard.json file with all the fire hazard information

# Logging
import logging

# System
import os

# HTTP
import requests

# Processing
from PIL import Image, ImageFile
import StringIO
import operator

# Serializing
import json
import yaml

# Load the config
config = yaml.load(open(os.path.dirname(os.path.realpath(__file__)) + '/config.yml', 'r'))

# Set the loglevel
log_level = logging.ERROR
if config['debug']:
	log_level = logging.INFO
logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)


def subtract_tups(a, b):
	"""
	Subtracts two tuples
	"""
	return tuple(map(operator.sub, a, b))

def average_tup(tup):
	"""
	Averages all the values in a tuple
	"""
	return sum(tup)/len(tup)
	
def difference(a, b):
	"""
	Shows the average difference between two tuples
	"""
	return abs(average_tup(subtract_tups(a, b)))

# Download today's fire hazard image from the ipma website
logging.info('Downloading image')
r = requests.get('http://www.ipma.pt/resources.www/transf/indices/rcm_dh.jpg')

# Load the image's pixels into an array
ImageFile.LOAD_TRUNCATED_IMAGES = True
logging.info('Loading image')
im = Image.open(StringIO.StringIO(r.content))
image = im.load()

def getLevel(x, y):
	"""
	Get the fire hazard level from a pixel by checking which level is closer to it's color
	"""
	levels = {
		5: image[350,570],
		4: image[350,590],
		3: image[350,610],
		2: image[350,630],
		1: image[350,650]
	}

	differences = {k: difference(image[x, y], v) for k, v in levels.items()}
	return min(differences, key=differences.get)

# List of municipalities and location of a pixel that's within it's limits
concelhos = {
	#Lisboa
	'Cascais': (118, 429),
	'Oeiras': (130, 430),
	'Sintra': (123, 419),
	'Amadora': (135, 426),
	'Lisboa': (142, 428),
	'Mafra': (127, 402),
	'Torres Vedras': (131, 388),
	'Lourinhã': (131, 369),
	'Cadaval': (151, 371),
	'Alenquer': (153, 385),
	'Azambuja': (166, 388),
	'Odivelas': (138, 422),
	'Loures': (140, 415),
	'Arruda dos Vinhos': (145, 402),
	'Sobral de Monte Agraço': (143, 397),
	'Vila Franca de Xira': (155, 409),
	
	#Leiria
	'Peniche': (129, 358),
	'Bombarral': (143, 365),
	'Óbidos': (137, 355),
	'Caldas da Rainha': (150, 350),
	'Alcobaça': (162, 339),
	'Nazaré': (154, 328),
	'Marinha Grande': (159, 308),
	'Leiria': (177, 308),
	'Pombal': (185, 290),
	'Porto de Mós': (174, 336),
	'Batalha': (180, 324),
	'Ansião': (206, 288),
	'Alvaiázere': (210, 303),
	'Figueiró dos Vinhos': (222, 297),
	'Castanheira de Pêra': (228, 282),
	'Pedrógão Grande': (230, 291),
	
	#Coimbra
	'Arganil': (250, 256),
	'Cantanhede': (190, 241),
	'Coimbra': (207, 257),
	'Condeixa-a-Nova': (201, 270),
	'Figueira da Foz': (174, 257),
	'Góis': (238, 268),
	'Lousã': (226, 267),
	'Mira': (181, 233),
	'Miranda do Corvo': (217, 272),
	'Montemor-o-Velho': (187, 254),
	'Oliveira do Hospital': (260, 240),
	'Pampilhosa da Serra': (257, 271),
	'Penacova': (222, 248),
	'Penela': (214, 281),
	'Soure': (188, 272),
	'Tábua': (243, 245),
	'Vila Nova de Poiares': (224, 257),
	
	#Aveiro
	'Águeda': (211, 215),
	'Albergaria-a-Velha': (205, 197),
	'Anadia': (208, 229),
	'Arouca': (226, 175),
	'Aveiro': (189, 204),
	'Castelo de Paiva': (221, 164),
	'Espinho': (191, 167),
	'Estarreja': (195, 195),
	'Ílhavo': (183, 210),
	'Mealhada': (206, 240),
	'Murtosa': (187, 195),
	'Oliveira de Azeméis': (204, 185),
	'Oliveira do Bairro': (196, 223),
	'Ovar': (191, 181),
	'Santa Maria da Feira': (200, 170),
	'São João da Madeira': (203, 177),
	'Sever do Vouga': (213, 195),
	'Vagos': (184, 221),
	'Vale de Cambra': (216, 183),
	
	#Porto
	'Amarante': (242, 134),
	'Baião': (247, 147),
	'Felgueiras': (229, 125),
	'Gondomar': (202, 152),
	'Lousada': (223, 133),
	'Maia': (192, 136),
	'Marco de Canaveses': (234, 146),
	'Matosinhos': (188, 142),
	'Paços de Ferreira': (214, 133),
	'Paredes': (212, 142),
	'Penafiel': (220, 149),
	'Porto': (193, 147),
	'Póvoa de Varzim': (180, 117),
	'Santo Tirso': (207, 128),
	'Trofa': (192, 129),
	'Valongo': (203, 141),
	'Vila do Conde': (185, 127),
	'Vila Nova de Gaia': (194, 156),
	
	# Braga
	'Amares': (215, 91),
	'Barcelos': (189, 102),
	'Braga': (208, 103),
	'Cabeceiras de Basto': (248, 103),
	'Celorico de Basto': (242, 119),
	'Esposende': (180, 103),
	'Fafe': (232, 111),
	'Guimarães': (220, 112),
	'Póvoa de Lanhoso': (223, 97),
	'Terras de Bouro': (230, 80),
	'Vieira do Minho': (238, 91),
	'Vila Nova de Famalicão': (205, 116),
	'Vila Verde': (204, 88),
	'Vizela': (221, 124),
	
	#Viana do Castelo
	'Arcos de Valdevez': (213, 61),
	'Caminha': (178, 67),
	'Melgaço': (225, 42),
	'Monção': (208, 47),
	'Paredes de Coura': (196, 59),
	'Ponte da Barca': (222, 72),
	'Ponte de Lima': (196, 75),
	'Valença': (194, 49),
	'Viana do Castelo': (181, 82),
	'Vila Nova de Cerveira': (185, 59),

	#Setúbal
	'Alcochete': (167, 431),
	'Alcácer do Sal': (206, 474),
	'Almada': (138, 439),
	'Barreiro': (153, 443),
	'Grândola': (197, 494),
	'Moita': (155, 437),
	'Montijo': (188, 428),
	'Palmela': (172, 440),
	'Santiago do Cacém': (198, 520),
	'Seixal': (144, 443),
	'Sesimbra': (144, 456),
	'Setúbal': (155, 453),
	'Sines': (177, 527),
	
	#Beja
	'Aljustrel': (228, 527),
	'Almodôvar': (236, 573),
	'Alvito': (242, 487),
	'Barrancos': (339, 497),
	'Beja': (257, 516),
	'Castro Verde': (242, 546),
	'Cuba': (255, 494),
	'Ferreira do Alentejo': (230, 503),
	'Moura': (305, 493),
	'Mértola': (272, 557),
	'Odemira': (193, 561),
	'Ourique': (220, 548),
	'Serpa': (292, 524),
	'Vidigueira': (276, 495),
	
	#Évora
	'Alandroal': (303, 444),
	'Arraiolos': (252, 423),
	'Borba': (291, 424),
	'Estremoz': (285, 416),
	'Montemor-o-Novo': (229, 435),
	'Mora': (229, 435),
	'Mourão': (307, 472),
	'Portel': (270, 479),
	'Redondo': (281, 438),
	'Reguengos de Monsaraz': (292, 467),
	'Vendas Novas': (206, 434),
	'Viana do Alentejo': (226, 468),
	'Vila Viçosa': (301, 425),
	'Évora': (254, 452),
	
	#Portalegre
	'Alter do Chão': (268, 370),
	'Arronches': (314, 384),
	'Avis': (256, 392),
	'Campo Maior': (335, 398),
	'Castelo de Vide': (292, 345),
	'Crato': (279, 361),
	'Elvas': (319, 406),
	'Fronteira': (283, 388),
	'Gavião': (258, 352),
	'Marvão': (303, 352),
	'Monforte': (298, 392),
	'Nisa': (275, 338),
	'Ponte de Sor': (235, 378),
	'Portalegre': (299, 368),
	'Sousel': (266, 402),
	
	#Faro
	'Albufeira': (222, 216),
	'Alcoutim': (276, 585),
	'Aljezur': (174, 593),
	'Castro Marim': (287, 595),
	'Faro': (253, 627),
	'Lagoa': (206, 616),
	'Lagos': (179, 611),
	'Loulé': (240, 606),
	'Monchique': (195, 590),
	'Olhão': (265, 624),
	'Portimão': (193, 609),
	'Silves': (212, 600),
	'São Brás de Alportel': (256, 609),
	'Tavira': (276, 606),
	'Vila do Bispo': (166, 618),
	'Vila Real de Santo António': (288, 603),
	
	#Santarém
	'Abrantes': (230, 349),
	'Alcanena': (186, 345),
	'Almeirim': (188, 377),
	'Alpiarça': (194, 371),
	'Benavente': (173, 414),
	'Cartaxo': (176, 381),
	'Chamusca': (211, 367),
	'Constância': (218, 344),
	'Coruche': (203, 407),
	'Entroncamento': (204, 344),
	'Ferreira do Zêzere': (220, 313),
	'Golegã': (200, 354),
	'Mação': (251, 326),
	'Ourém': (197, 315),
	'Rio Maior': (164, 360),
	'Salvaterra de Magos': (184, 394),
	'Santarém': (183, 359),
	'Sardoal': (234, 332),
	'Tomar': (212, 328),
	'Torres Novas': (195, 341),
	'Vila Nova da Barquinha': (208, 342),
	
	#Bragança
	'Alfândega da Fé': (338, 126),
	'Bragança': (360, 74),
	'Carrazeda de Ansiães': (306, 140),
	'Freixo de Espada À Cinta': (347, 157),
	'Macedo de Cavaleiros': (346, 105),
	'Miranda do Douro': (383, 111),
	'Mirandela': (320, 110),
	'Mogadouro': (371, 123),
	'Torre de Moncorvo': (332, 142),
	'Vila Flor': (321, 127),
	'Vimioso': (372, 94),
	'Vinhais': (326, 68),

	#Vila Real
	'Alijó': (293, 130),
	'Boticas': (274, 86),
	'Chaves': (292, 81),
	'Mesão Frio': (256, 146),
	'Mondim de Basto': (255, 121),
	'Montalegre': (261, 72),
	'Murça': (295, 117),
	'Peso da Régua': (270, 146),
	'Ribeira de Pena': (260, 109),
	'Sabrosa': (280, 140),
	'Santa Marta de Penaguião': (264, 140),
	'Valpaços': (302, 97),
	'Vila Pouca de Aguiar': (276, 108),
	'Vila Real': (269, 127),
	
	#Guarda
	'Aguiar da Beira': (290, 190),
	'Almeida': (339, 209),
	'Celorico da Beira': (300, 210),
	'Figueira de Castelo Rodrigo': (340, 180),
	'Fornos de Algodres': (290, 205),
	'Gouveia': (282, 221),
	'Guarda': (309, 220),
	'Manteigas': (287, 236),
	'Mêda': (312, 173),
	'Pinhel': (329, 196),
	'Sabugal': (340, 239),
	'Seia': (272, 236),
	'Trancoso': (305, 188),
	'Vila Nova de Foz Côa': (320, 159),
	 
	#Viseu
	'Armamar': (274, 153),
	'Carregal do Sal': (247, 229),
	'Castro Daire': (250, 177),
	'Cinfães': (238, 159),
	'Lamego': (262, 156),
	'Mangualde': (271, 213),
	'Moimenta da Beira': (280, 169),
	'Mortágua': (224, 231),
	'Nelas': (258, 219),
	'Oliveira de Frades': (223, 197),
	'Penalva do Castelo': (278, 202),
	'Penedono': (300, 170),
	'Resende': (250, 156),
	'Santa Comba Dão': (236, 236),
	'Sernancelhe': (292, 178),
	'Sátão': (275, 193),
	'São João da Pesqueira': (295, 147),
	'São Pedro do Sul': (239, 189),
	'Tabuaço': (284, 157),
	'Tarouca': (266, 165),
	'Tondela': (237, 219),
	'Vila Nova de Paiva': (267, 180),
	'Viseu': (254, 202),
	'Vouzela': (236, 204),
	
	#Castelo Branco
	'Belmonte': (305, 243),
	'Castelo Branco': (290, 298),
	'Covilhã': (290, 250),
	'Fundão': (297, 266),
	'Idanha-a-Nova': (322, 289),
	'Oleiros': (258, 289),
	'Penamacor': (318, 261),
	'Proença-a-Nova': (259, 311),
	'Sertã': (239, 302),
	'Vila de Rei': (232, 318),
	'Vila Velha de Ródão': (275, 317),
}

# Process each pixel
logging.info('Processing pixels')
hazard = {}
for concelho, posicao in concelhos.items():
	hazard[concelho] = getLevel(posicao[0], posicao[1])

logging.info('Saving json')
json.dump(hazard, open(os.path.dirname(os.path.realpath(__file__)) + '/html/hazard.json', 'w'))