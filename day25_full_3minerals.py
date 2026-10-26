import folium

# Fix for new folium - use default tiles
m = folium.Map(location=[9.0, 8.0], zoom_start=6)

# Add Esri Satellite with proper attribution
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Esri Satellite",
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer("OpenStreetMap", name="Streets").add_to(m)

# --- MINERAL DATA ---
lithium_targets = [
    [8.55, 8.15, "NAS-Li-01", "Kokona, Nasarawa - Pegmatite belt - SWIR high"],
    [8.52, 8.20, "NAS-Li-02", "Kokona - Near river, clay mineral high"],
    [8.78, 8.65, "NAS-Li-03", "Wamba - Migmatite gneiss contact"],
    [8.80, 8.90, "NAS-Li-04", "Nasarawa Eggon - Artisanal pit observed"],
]

gold_targets = [
    [7.62, 4.73, "GOLD-Ilesha-01", "Ilesha Schist Belt - Iron Oxide high"],
    [12.15, 6.25, "GOLD-Zamfara-01", "Zamfara - Quartz veins in schist"],
    [7.85, 6.75, "GOLD-Ekiti-01", "Ekiti - Alluvial gold zone"],
]

tin_targets = [
    [9.90, 8.90, "TIN-Jos-01", "Jos Plateau - Younger granite"],
    [9.85, 8.85, "TIN-Jos-02", "Jos - Rayfield district"],
    [10.20, 9.20, "TIN-Bauchi-01", "Bauchi - Tin belt extension"],
]

for lat, lon, tid, why in lithium_targets:
    folium.Marker(
        [lat, lon],
        popup=f"<b>{tid}</b><br>YELLOW LITHIUM<br>{why}<br>{lat},{lon}",
        icon=folium.Icon(color="orange", icon="star", prefix="fa")
    ).add_to(m)
    folium.Circle([lat, lon], radius=5000, color="yellow", fill=True, fill_opacity=0.3).add_to(m)

for lat, lon, tid, why in gold_targets:
    folium.Marker(
        [lat, lon],
        popup=f"<b>{tid}</b><br>RED GOLD<br>{why}<br>{lat},{lon}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    folium.Circle([lat, lon], radius=5000, color="red", fill=True, fill_opacity=0.2).add_to(m)

for lat, lon, tid, why in tin_targets:
    folium.Marker(
        [lat, lon],
        popup=f"<b>{tid}</b><br>BLUE TIN<br>{why}<br>{lat},{lon}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
    folium.Circle([lat, lon], radius=5000, color="blue", fill=True, fill_opacity=0.2).add_to(m)

folium.LayerControl().add_to(m)

legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; z-index:1000; background:white; padding:10px; border-radius:8px;">
<b>Day 25 - Mineral Zones</b><br>
<span style="color:orange">★</span> Yellow-Lithium<br>
<span style="color:red">●</span> Red-Gold<br>
<span style="color:blue">●</span> Blue-Tin<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

m.save("Day25_Full_Mineral_Map.html")
print("DONE: Day25_Full_Mineral_Map.html FIXED")
