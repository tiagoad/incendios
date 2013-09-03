/* Continental Portugal Boundaries */
var SW = new L.LatLng(42.20, -9.54),
	NE = new L.LatLng(36.95, -6.15),
	bounds = new L.LatLngBounds(SW, NE)

/* Create the map */
var map = L.map('map').fitBounds(bounds)


/* Initialize constants */
var fires = {} // id: fireMarker
var layers = {
	fireLayer: L.layerGroup().addTo(map),
	controlPostLayer: L.layerGroup(),
	hazardLayer: L.layerGroup(),
}
var ready = false;

/* Set the tiles and attribution */
L.tileLayer('http://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}.png', {
	attribution: '<a href="http://mapicons.nicolasmollet.com">Map Icons Collection</a>' + ' | ' +
	'<a href="http://www.esri.com/software/arcgis/arcgisonline/maps/maps-and-map-layers">ESRI</a>' + ' | ' + 
	'<a href="http://www.prociv.pt/cnos/Pages/ListaFogos.aspx">Dados</a>' + ' | ' +
	'Alojado numa <a href="http://www.raspberrypi.org/">Raspberry Pi</a>',
	maxZoom: 18
}).addTo(map)

/* Icons */
var icons = {
	activeFireMarker: L.icon({
		iconUrl: 'img/fire_active.png',
		iconSize: [32, 37],
		iconAnchor: [16, 35],
		popupAnchor: [0, -40]
	}),

	controlledFireMarker: L.icon({
		iconUrl: 'img/fire_controlled.png',
		iconSize: [32, 37],
		iconAnchor: [16, 35],
		popupAnchor: [0, -37]
	}),

	otherFireMarker: L.icon({
		iconUrl: 'img/fire_other.png',
		iconSize: [32, 37],
		iconAnchor: [16, 35],
		popupAnchor: [0, -37]
	}),

	controlPostMarker: L.icon({
		iconUrl: 'img/binoculars.png',
		iconSize: [32, 37],
		iconAnchor: [16, 35],
		popupAnchor: [0, -37]
	}),
}

/* Create spinner div */
var spinner = L.control({position: 'bottomleft'})
spinner.onAdd = function (map){
	var div = L.DomUtil.create('div')
	div.setAttribute("id", "spinner")
	div.setAttribute("style", "width: 30px; height: 31px")
	return div
}
spinner.addTo(map)

spinnerCount = 0;
/* Start spinner */
function startSpinner() {
	if (spinnerCount <= 0)
	{
		var opts = {
			lines: 11,
			length: 3,
			width: 2,
			radius: 7,
			rotate: 8,
			color: '#fff'
		};
		var target = document.getElementById('spinner');
		var spinner = new Spinner(opts).spin(target);
	}
	spinnerCount += 1
}

/* Stop spinner */
function stopSpinner() {
	spinnerCount -= 1
	if (spinnerCount <= 0)
	{
		$('#spinner').html('')
	}
}

/* Icon Legend */
var legend = L.control({position: 'bottomright'})
legend.onAdd = function (map){
	var div = L.DomUtil.create('div', 'info')
	div.innerHTML += '<img class="markericon" src="img/fire_active.png"> Em Curso<br>'
	div.innerHTML += '<img class="markericon" src="img/fire_controlled.png"> Dominado<br>'
	div.innerHTML += '<img class="markericon" src="img/fire_other.png"> Outros<br>'
	div.innerHTML += '<hr>'
	div.innerHTML += '<img class="markericon" src="img/binoculars.png"> Comando Operacional<br>'
	return div
}
legend.addTo(map)

/* Layer Toggles */
var toggles = L.control({position: 'topleft'})
toggles.onAdd = function (map){
	var div = L.DomUtil.create('div', 'info')

	div.innerHTML += '<img class="markericon" src="img/hazard.png"><input type="checkbox" id="showhazard" disabled="disabled" onchange="javascript:toggleLayer(layers.hazardLayer, \'showhazard\', $(this).is(\':checked\'))"/><br><br>'
	div.innerHTML += '<img class="markericon" src="img/binoculars.png"><input type="checkbox" id="showposts" onchange="javascript:toggleLayer(layers.controlPostLayer, \'showposts\', $(this).is(\':checked\'))"/>'

	return div
}
toggles.addTo(map)

/* Toggle a layer */
function toggleLayer(layer, id, status)
{
	$.cookie(id, status, {expires: 365*10})
	if (status == true)
		map.addLayer(layer)
	else
		map.removeLayer(layer)
}

/* Update/Add the fire to the map */
function addFire(id, data)
{
	/* Create the marker if it doesn't exist */
	if (fires[id] == undefined) {
		fires[id] = L.marker([data.coordinates.y, data.coordinates.x]).addTo(layers.fireLayer)
	}
	
	var fireMarker = fires[id]
	
	/* Update the icon */
	// Pick appropriate icon
	if (data.fase == 'Em Curso') {
		icon = icons.activeFireMarker
	} else if (data.fase == 'Dominado') {
		icon = icons.controlledFireMarker
	} else {
		icon = icons.otherFireMarker
	}
	
	// Set the icon
	fireMarker.setIcon(icon)
	
	/* Update the popup */
	fireMarker.bindPopup(
		'<div style="text-align: center" data-fireid="' + data.id + '"><strong><a href="javascript:void(0)" onclick="javascript:openPopup(\'' + data.location + '\', \'' + data.link + '\');">' + data.location + '</a></strong></div><hr>' + 
		'<strong>Tipo: </strong>' + data.tipo + '<br>' +
		'<strong>Início: </strong>' + data.datetime + '<br>' + 
		'<strong>Distrito: </strong>' + data.distrito + '<br>' + 
		'<strong>Concelho: </strong>' + data.concelho + '<hr>' +
		'<strong>Operacionais: </strong>' + data.meios.operacionais.total + '<br>' +
		'<strong>Veículos: </strong>' + data.meios.veiculos.total + '<br>' +
		'<strong>Meios Aéreos: </strong>' + data.meios.aerios.total + '<br>' +
		'<strong>Outros Meios: </strong>' + data.meios.outros)
	
	/* Create the control post marker and line if there is a control post */
	if (data.posto_operacional !== undefined) {
		var controlPostMarker = L.marker([data.posto_operacional.y, data.posto_operacional.x], {icon: icons.controlPostMarker}).addTo(layers.controlPostLayer)
		var controlPostLine   = L.polyline([fireMarker.getLatLng(), controlPostMarker.getLatLng()], {
			color: 'black',
			weight: 2
		}).addTo(layers.controlPostLayer)
	}
}

/* Refresh iframe contents */
function refreshIframe(frameid)
{
	document.getElementById(frameid).src = document.getElementById(frameid).src
}

/* Open popup */
function openPopup(title, url)
{
	var tag = $('<div style="padding: 4px 0 0 0; overflow: hidden"></div>')
	var frameid = Date.now()
	tag.html(
		'<iframe id="' + frameid + '" src="' + url + '" style="width: 100%; height: 100%; border: none"></iframe>' +
		'<div style="text-align: center; position: absolute; bottom: 0"><a href="javascript:void(0)" onclick="javascript:refreshIframe(\'' + frameid + '\')" style="outline: none;" ><img src="/img/refresh.png"/></a></div>').dialog({
		title: title,
		position: [100, 10],
		width: 495,
		minWidth: 495,
		maxWidth: 495,
		height: 430,
		resizable: true
	}).dialog('open')
}

/* Set URL fragment when marker is expanded */
map.on('popupopen', function(e) {
	window.location.hash = '#' + $(e.popup._content).attr('data-fireid')
});

/* Unset URL fragment when marker is unexpanded */
map.on('popupclose', function(e) {
	window.location.hash = ''
});

/* Pull the data from the server */
function pullFireData()
{
	startSpinner()

	/* Download fires.json */
	$.getJSON('/fires.json', function(data) {
		layers.controlPostLayer.clearLayers()
		
		/* Delete fires that no longer exist */
		var newIdList = Array()
		for(var k in data.fires) newIdList.push(k)
		for(var k in fires) {
			if ($.inArray(k, newIdList) == -1) {
				layers.fireLayer.removeLayer(fires[k].fireMarker) // Remove the fire marker from the fire layer
			}
		}
	
		$.each(data.fires, function(key, value) {
			/* Add each fire to the map */
			addFire(key, value)
		})
		
		/* Check for the URL fragment if this is the first time the map is populated */
		if (!ready)
		{
			ready = true

			if(window.location.hash) {
				if (fires[window.location.hash.substring(1)] != undefined)
				{
					fires[window.location.hash.substring(1)].openPopup()
				}
			}
		}

		setTimeout(function() {stopSpinner()}, 1000)
	})
}

function pullHazardData()
{
	startSpinner()
	
	$.getJSON('/hazard.json', function(hazardData) {
		/* Apply the hazard color to each municipality */
		function getStyle(feature) {
			var color = 'grey'
			if (hazardData[feature.properties.municipio] != undefined)
			{
				switch(hazardData[feature.properties.municipio])
				{
					case 1:
						color = '#289e26'
						break;
					case 2:
						color = '#fee818'
						break;
					case 3:
						color = '#ec6e00'
						break;
					case 4:
						color = '#cc292a'
						break;
					case 5:
						color = '#75263b'
						break;
				}
			}
			
			return {
				color: 'white',
				fillColor: color,
				weight: 1,
				opacity: 1,
				fillOpacity: 0.7
			}
		}
		
		$.getJSON('/js/concelhos.json', function(municipalityData) {
			L.geoJson(municipalityData, {
				style: getStyle
			}).addTo(layers.hazardLayer)
			
			$('#showhazard').prop('disabled', false);
			setTimeout(function() {stopSpinner()}, 1000)
		})
	})
}

/* Pull fire data every 15 seconds */
(function(){
    pullFireData()
    setTimeout(arguments.callee, 15*1000)
})();

/* Pull fire hazard every 600 seconds */
(function(){
    pullHazardData()
    setTimeout(arguments.callee, 600*1000)
})();

/* Check cookies */
if ($.cookie('showposts') == 'true')
{
	$('#showposts').prop('checked', true)
	map.addLayer(layers.controlPostLayer)
}

if ($.cookie('showhazard') == 'true')
{
	$('#showhazard').prop('checked', true)
	map.addLayer(layers.hazardLayer)
}