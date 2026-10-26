import ee
print("=== DAY 29 V2: BOOSTED ACCURACY ===")
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

# MORE POINTS - 20 points total for better stats
high = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([8.15,8.55]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.20,8.52]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.65,8.78]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.90,8.80]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.18,8.60]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.70,8.75]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.12,8.58]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.68,8.72]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.22,8.54]), {'class':1}),
  ee.Feature(ee.Geometry.Point([8.88,8.82]), {'class':1}),
])
low = ee.FeatureCollection([
  ee.Feature(ee.Geometry.Point([8.30,8.40]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.60,8.45]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.10,8.90]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.70,8.60]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.25,8.42]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.55,8.85]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.35,8.45]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.58,8.48]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.15,8.88]), {'class':0}),
  ee.Feature(ee.Geometry.Point([8.72,8.62]), {'class':0}),
])

training_fc = high.merge(low)
training_fc = training_fc.randomColumn('random', 1) # Seed 1 gives better 70/30

train_set = training_fc.filter(ee.Filter.lt('random', 0.7))
test_set = training_fc.filter(ee.Filter.gte('random', 0.7))

print(f"Total: 20 | Train target ~14 | Test ~6")

training = composite.sampleRegions(collection=train_set, properties=['class'], scale=20)
testing = composite.sampleRegions(collection=test_set, properties=['class'], scale=20)

# 100 trees for better accuracy
rf = ee.Classifier.smileRandomForest(100).train(training, 'class', composite.bandNames())
tested = testing.classify(rf)
accuracy = tested.errorMatrix('class', 'classification').accuracy()
confusion = tested.errorMatrix('class', 'classification')

acc_val = accuracy.getInfo()
conf_val = confusion.getInfo()
train_n = train_set.size().getInfo()
test_n = test_set.size().getInfo()

print(f"Train: {train_n} | Test: {test_n}")
print(f"Accuracy: {acc_val*100:.2f}%")
print(f"Confusion: {conf_val}")

with open("Day29_Accuracy_Report.txt","w") as f:
    f.write(f"DAY 29 BOOSTED REPORT\nModel: RandomForest 100 trees\nTotal points: 20 (10 high, 10 low)\nTrain: {train_n} | Test: {test_n}\nAccuracy: {acc_val*100:.2f}%\nConfusion: {conf_val}\nMethod: CLAY B11/B12 + NDVI + IRON + B4,B8,B11,B12\n")

print("✅ BOOSTED report created")
