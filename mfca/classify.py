import rasterio
import geopandas as gpd

def classify(
    raster: rasterio.io.DatasetReader, 
    polygons: gpd.GeoDataFrame
):
    """
    Stub classifier: returns an empty array or dict.
    """
    # In the future, this will label each pixel.
    return None
