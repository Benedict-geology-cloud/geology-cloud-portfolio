import ee
print("=== DAY 29 FIXED: ACCURACY + EXPORT ===")
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
  ee.Feature(ee.Geometry.Point([8.18,8.60]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.70,8.75]), {'class':1}),
])
low = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([8.30,8.40]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.60,8.45]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.10,8.90]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.70,8.60]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.25,8.42]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.55,8.85]), {'class':0}),
])
training_fc = high.merge(low)
training_fc = training_fc.randomColumn('random', 42)

train_set = training_fc.filter(ee.Filter.lt('random', 0.7))
test_set = training_fc.filter(ee.Filter.gte('random', 0.7))

training = composite.sampleRegions(collection=train_set, properties=['class'], scale=20)
testing = composite.sampleRegions(collection=test_set, properties=['class'], scale=20)

rf = ee.Classifier.smileRandomForest(50).train(training, 'class', composite.bandNames())

# FIXED: classify test set first, then errorMatrix on FeatureCollection
tested = testing.classify(rf)
accuracy = tested.errorMatrix('class', 'classification').accuracy()
confusion = tested.errorMatrix('class', 'classification')

acc_val = accuracy.getInfo()
conf_val = confusion.getInfo()

print(f"Train size: {train_set.size().getInfo()} | Test size: {test_set.size().getInfo()}")
print(f"Accuracy: {acc_val*100:.2f}%")
print(f"Confusion Matrix: {conf_val}")

# Export
classified = composite.classify(rf)
task = ee.batch.Export.image.toDrive(
  image=classified,
  description='Day29_Lithium_RF_50trees',
  folder='GEE_Exports',
  fileNamePrefix='Nasarawa_Lithium_RF',
  region=aoi,
  scale=20,
  crs='EPSG:4326',
  maxPixels=1e13
)
task.start()
print(f"Export started: {task.id}")
print("Check: https://code.earthengine.google.com/tasks")

with open("Day29_Accuracy_Report.txt","w") as f:
    f.write("DAY 29 ACCURACY REPORT\n")
    f.write(f"Model: RandomForest 50 trees\n")
    f.write(f"Train: 70% | Test: 30%\n")
    f.write(f"Accuracy: {acc_val*100:.2f}%\n")
    f.write(f"Confusion Matrix: {conf_val}\n")
    f.write(f"Export: Nasarawa_Lithium_RF.tif to Drive/GEE_Exports\n")
    f.write(f"Task ID: {task.id}\n")

print("✅ Day29_Accuracy_Report.txt created")
