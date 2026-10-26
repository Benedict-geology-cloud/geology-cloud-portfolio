import folium

# Nasarawa AOI center
center = [8.5, 8.1]
m = folium.Map(location=center, zoom_start=9, tiles='Esri.WorldImagery')

# Your 4 lithium prospects
prospects = [
    {"name":"Kokona Lithium", "coords":[8.84, 7.93]},
    {"name":"Keffi Lithium", "coords":[8.84, 7.87]},
    {"name":"Akwanga Lithium", "coords":[8.91, 8.40]},
    {"name":"Wamba Lithium", "coords":[8.93, 8.60]},
]

for p in prospects:
    folium.Marker(
        p["coords"],
        popup=f"<b>{p['name']}</b><br>Lat: {p['coords'][0]}<br>Lon: {p['coords'][1]}<br><i>Copy this!</i>",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

# DAY 24 NEW: Click anywhere to get coordinate
m.add_child(folium.LatLngPopup())

# Also add clickable copy
m.get_root().html.add_child(folium.Element("""
<script>
map.on('click', function(e){
  var lat = e.latlng.lat.toFixed(5);
  var lng = e.latlng.lng.toFixed(5);
  L.popup()
   .setLatLng(e.latlng)
   .setContent("<b>YOU CLICKED:</b><br>Lat: "+lat+"<br>Lon: "+lng+"<br><button onclick='navigator.clipboard.writeText(\""+lat+", "+lng+"\")'>COPY COORD</button>")
   .openOn(map);
});
</script>
"""))

m.save("Nasarawa_Lithium_Day24.html")
print("Day 24 map done!")
