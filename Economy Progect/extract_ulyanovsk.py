import osmium as osm
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
import os

class BuildingHandler(osm.SimpleHandler):
    def __init__(self):
        super(BuildingHandler, self).__init__()
        self.buildings = []
        
    def way(self, w):
        if 'building' in w.tags:
            try:
                geometry = []
                for n in w.nodes:
                    geometry.append((n.lon, n.lat))
                
                if len(geometry) > 2:  # Минимум 3 точки для полигона
                    self.buildings.append({
                        'id': w.id,
                        'type': w.tags.get('building', 'unknown'),
                        'name': w.tags.get('name', ''),
                        'levels': w.tags.get('building:levels', '1'),
                        'geometry': Polygon(geometry)
                    })
            except Exception as e:
                print(f"Error processing way {w.id}: {e}")

# Ульяновск bounding box (примерные координаты)
ulyanovsk_bbox = (48.20, 54.25, 48.50, 54.40)

def extract_buildings(pbf_file, output_file):
    print("Извлечение зданий...")
    handler = BuildingHandler()
    
    # Применяем фильтр по bounding box
    handler.apply_file(pbf_file, locations=True, idx='flex_mem')
    
    # Фильтрация по bounding box
    buildings_gdf = gpd.GeoDataFrame(handler.buildings)
    buildings_gdf = buildings_gdf[buildings_gdf.geometry.centroid.within(
        Polygon([(ulyanovsk_bbox[0], ulyanovsk_bbox[1]),
                 (ulyanovsk_bbox[2], ulyanovsk_bbox[1]),
                 (ulyanovsk_bbox[2], ulyanovsk_bbox[3]),
                 (ulyanovsk_bbox[0], ulyanovsk_bbox[3])]))]
    
    # Добавляем примерное энергопотребление
    def estimate_energy(row):
        energy_per_level = {
            'residential': 50000,
            'apartments': 75000,
            'commercial': 150000,
            'retail': 100000,
            'industrial': 300000,
            'school': 200000,
            'hospital': 500000
        }
        levels = int(row['levels']) if row['levels'].isdigit() else 1
        base = energy_per_level.get(row['type'], 50000)
        return base * levels
    
    buildings_gdf['energy'] = buildings_gdf.apply(estimate_energy, axis=1)
    
    # Сохраняем в GeoJSON
    buildings_gdf.to_file(output_file, driver='GeoJSON')
    print(f"Данные сохранены в {output_file}")

if __name__ == "__main__":
    extract_buildings('volga-fed-district-latest.osm.pbf', 'ulyanovsk_buildings.geojson')