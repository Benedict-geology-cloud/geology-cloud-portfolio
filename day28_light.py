import ee
print("=== DAY 28 FIX: Fullscreen Map ===")
try:
    ee.Initialize(project='geology-mineral-hunt')
except:
    ee.Initialize()

aoi = ee.Geometry.Rectangle([8.0, 8.4, 9.0, 9.0])

s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")\
  .filterBounds(aoi)\
  .filterDate('2023-11-01','2024-02-28')\
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',20))\
  .median().clip(aoi)

ndvi = s2.normalizedDifference(['B8','B4']).rename('NDVI')
clay = s2.select('B11').divide(s2.select('B12')).rename('CLAY')
iron = s2.select('B4').divide(s2.select('B2')).rename('IRON')
composite = s2.select(['B4','B8','B11','B12']).addBands([ndvi, clay, iron])

high = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([8.15,8.55]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.20,8.52]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.65,8.78]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.90,8.80]), {'class':1}),
])
low = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([8.30,8.40]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.60,8.45]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.10,8.90]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.70,8.60]), {'class':0}),
])
training_fc = high.merge(low)
training = composite.sampleRegions(collection=training_fc, properties=['class'], scale=20)

rf = ee.Classifier.smileRandomForest(50).train(training, 'class', composite.bandNames())
classified = composite.classify(rf)
prob = composite.classify(rf.setOutputMode('PROBABILITY'))

map_id_class = classified.getMapId({'min':0, 'max':1, 'palette':['blue','yellow','red']})
map_id_prob = prob.getMapId({'min':0, 'max':1, 'palette':['white','orange','red']})
map_id_s2 = s2.getMapId({'bands':['B11','B8','B4'], 'min':0, 'max':3000})
map_id_clay = clay.getMapId({'min':0.8, 'max':1.5, 'palette':['blue','white','orange']})

print("Map IDs ready")

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Day 28 ML Heatmap</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
html,body{{margin:0; padding:0; height:100%;}}
#map{{height:85vh; width:100%;}}
.header{{padding:10px; background:#1a1a1a; color:white; text-align:center; font-family:sans-serif;}}
.legend{{background:white; padding:10px; line-height:1.5;}}
</style>
</head>
<body>
<div class="header">
<b>Day 28 - Random Forest Lithium Heatmap (50 trees)</b> | CLAY B11/B12 | Nasarawa Tile 32/N/MK<br>
<span style="font-size:12px;">🔴 Red=High Lithium  🟡 Yellow=Med  🔵 Blue=Low | Yellow circles = Training points</span>
</div>
<div id="map"></div>
<script>
var map = L.map('map').setView([8.65, 8.5], 10);

// Base layers - 3 options
var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom:18}}).addTo(map);
var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{maxZoom:18}});
var terrain = L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom:17}});

// AI Layers from GEE
var s2Layer = L.tileLayer('{map_id_s2['tile_fetcher'].url_format}', {{opacity:0.6, maxZoom:18}});
var clayLayer = L.tileLayer('{map_id_clay['tile_fetcher'].url_format}', {{opacity:0.6, maxZoom:18}});
var mlLayer = L.tileLayer('{map_id_class['tile_fetcher'].url_format}', {{opacity:0.7, maxZoom:18}}).addTo(map);
var probLayer = L.tileLayer('{map_id_prob['tile_fetcher'].url_format}', {{opacity:0.5, maxZoom:18}});

var baseMaps = {{"OSM": osm, "Satellite": satellite, "Terrain": terrain}};
var overlayMaps = {{"Sentinel SWIR B11/B8/B4": s2Layer, "Clay Ratio B11/B12": clayLayer, "ML Potential (Blue-Yellow-Red)": mlLayer, "Probability Heatmap": probLayer}};

L.control.layers(baseMaps, overlayMaps).addTo(map);

// Training markers
L.circleMarker([8.55, 8.15], {{color:'yellow', fillColor:'yellow', fillOpacity:0.8, radius:10, weight:3}}).addTo(map).bindPopup('<b>High 1</b><br>Lithium Training<br>8.15,8.55');
L.circleMarker([8.52, 8.20], {{color:'yellow', fillColor:'yellow', fillOpacity:0.8, radius:10, weight:3}}).addTo(map).bindPopup('<b>High 2</b><br>8.20,8.52');
L.circleMarker([8.78, 8.65], {{color:'yellow', fillColor:'yellow', fillOpacity:0.8, radius:10, weight:3}}).addTo(map).bindPopup('<b>High 3</b><br>8.65,8.78');
L.circleMarker([8.80, 8.90], {{color:'yellow', fillColor:'yellow', fillOpacity:0.8, radius:10, weight:3}}).addTo(map).bindPopup('<b>High 4</b><br>8.90,8.80');

// Fit to AOI
map.fitBounds([[8.4, 8.0], [9.0, 9.0]]);
</script>
<div style="text-align:center; padding:8px; font-family:sans-serif; font-size:13px;">
<b>Interpretation:</b> Orange/Red areas = AI detected Lithium pegmatite signature (high clay ratio B11/B12 + low vegetation). Built on Termux Android | Model: smileRandomForest(50)
</div>
</body>
</html>
"""

with open("Day28_ML_Heatmap.html","w") as f:
    f.write(html)

print("✅ FIXED: Day28_ML_Heatmap.html now fullscreen with satellite option")
