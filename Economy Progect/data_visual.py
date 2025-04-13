import numpy as np
from scipy import stats
import seaborn as sns  # Для более красивых графиков
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
from shapely.geometry import Polygon



def load_data(file_path):
    """Загружает GeoJSON-файл с данными зданий."""
    gdf = gpd.read_file(file_path)
    return gdf

def preprocess_data(gdf):
    """Вычисляет площадь зданий и плотность энергопотребления."""
    # Убедимся, что геометрия в правильной проекции (для расчета площади в м²)
    gdf = gdf.to_crs(epsg=3857)  # Web Mercator для расчета площади
    gdf['area'] = gdf.geometry.area
    gdf['energy_density'] = gdf['energy'] / gdf['area']  # Плотность энергии на м²
    
    # Возвращаем в WGS84 (широта/долгота) для отображения на карте
    gdf = gdf.to_crs(epsg=4326)
    gdf['centroid'] = gdf.geometry.centroid
    return gdf

def plot_statistics(gdf):
    """Улучшенная визуализация распределения плотности энергопотребления."""
    plt.figure(figsize=(12, 7))
    
    data = gdf['energy_density']
    
    # 1. Основная гистограмма с логарифмической шкалой
    ax1 = plt.subplot(2, 1, 1)
    positive_data = data[data > 0]  # Исключаем нулевые и отрицательные значения
    log_data = np.log10(positive_data)
    
    sns.histplot(log_data, bins=40, kde=True, color='teal', edgecolor='black')
    plt.title('Логарифмическое распределение плотности энергопотребления')
    plt.xlabel('log10(Плотность энергопотребления) [усл. ед./м²]')
    plt.ylabel('Количество зданий')
    plt.grid(True, alpha=0.3)
    
    # 2. Гистограмма с обрезкой выбросов (линейная шкала)
    ax2 = plt.subplot(2, 1, 2)
    q95 = data.quantile(0.95)  # 95-й перцентиль
    trimmed_data = data[data <= q95]
    
    sns.histplot(trimmed_data, bins=40, kde=True, color='royalblue', edgecolor='black')
    plt.title(f'Распределение плотности (95% данных, ≤ {q95:.2f} усл.ед./м²)')
    plt.xlabel('Плотность энергопотребления [усл. ед./м²]')
    plt.ylabel('Количество зданий')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('improved_energy_density_distribution.png', dpi=300)
    plt.show()
    
    # 3. Вывод статистики
    print("\nДетальная статистика:")
    print(f"Общее количество зданий: {len(data)}")
    print(f"Минимальное значение: {data.min():.4f}")
    print(f"Максимальное значение: {data.max():.2f}")
    print(f"Медиана: {data.median():.4f}")
    print(f"Среднее: {data.mean():.4f}")
    print(f"Стандартное отклонение: {data.std():.4f}")
    print(f"95-й перцентиль: {q95:.4f}")
    print(f"Доля данных > 95-го перцентиля: {len(data[data > q95])/len(data):.2%}")

# Основной скрипт (остается без изменений)
if __name__ == "__main__":
    buildings_gdf = load_data("ulyanovsk_buildings.geojson")
    processed_gdf = preprocess_data(buildings_gdf)
    
    print(f"Всего зданий: {len(processed_gdf)}")
    print(f"Средняя плотность: {processed_gdf['energy_density'].mean():.2f} усл.ед./м²")
    
    plot_statistics(processed_gdf)