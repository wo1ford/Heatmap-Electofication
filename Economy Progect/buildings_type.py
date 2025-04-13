import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
from shapely.geometry import Polygon


def load_data(file_path):
    """Загружает GeoJSON-файл с данными зданий."""
    gdf = gpd.read_file(file_path)
    return gdf


def plot_building_types(gdf, top_n=10, figsize=(12, 6)):
    """
    Визуализирует распределение типов зданий.
    
    Параметры:
        gdf (GeoDataFrame): GeoDataFrame с данными зданий
        top_n (int): Сколько топовых типов показать (остальные объединяются в 'other')
        figsize (tuple): Размер графика
    """
    # Подготовка данных
    types = gdf['type'].fillna('unknown').apply(lambda x: x.lower() if isinstance(x, str) else 'unknown')
    type_counts = Counter(types)
    
    # Группировка редко встречающихся типов в 'other'
    if len(type_counts) > top_n:
        top_types = {k: v for k, v in type_counts.most_common(top_n)}
        other_count = sum(v for k, v in type_counts.items() if k not in top_types)
        top_types['other'] = other_count
    else:
        top_types = dict(type_counts.most_common())
    
    # Создание DataFrame для визуализации
    df_plot = pd.DataFrame({
        'Building Type': list(top_types.keys()),
        'Count': list(top_types.values())
    }).sort_values('Count', ascending=False)
    
    # Настройка стиля
    sns.set_style("whitegrid")
    plt.figure(figsize=figsize)
    
    # Построение графика
    ax = sns.barplot(
        data=df_plot,
        x='Building Type',
        y='Count',
        palette="viridis",
        edgecolor='black',
        linewidth=0.5
    )
    
    # Добавление аннотаций
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center',
            xytext=(0, 5),
            textcoords='offset points'
        )
    
    # Настройка оформления
    plt.title(f'Распределение типов зданий (топ-{top_n})', fontsize=14, pad=20)
    plt.xlabel('Тип здания', fontsize=12)
    plt.ylabel('Количество', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Сохранение и отображение
    plt.savefig('building_types_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Вывод статистики
    print("\nСтатистика по типам зданий:")
    print(df_plot.to_string(index=False))

# Пример использования в вашем основном скрипте:
if __name__ == "__main__":
    buildings_gdf = load_data("ulyanovsk_buildings.geojson")
    plot_building_types(buildings_gdf, top_n=8)