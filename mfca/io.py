import geopandas as gpd
import os

def load_vector(path):
    """Read any vector file (e.g., GeoPackage) into a GeoDataFrame."""
    # Set GDAL config to restore missing .shx files for shapefiles
    os.environ['SHAPE_RESTORE_SHX'] = 'YES'
    return gpd.read_file(path)

def clip_aoi(gdf, iso_code):
    """Return only rows whose ISO3_CODE equals the request."""
    if "ISO3_CODE" not in gdf.columns:
        raise KeyError("ISO3_CODE column missing")
    return gdf[gdf["ISO3_CODE"].str.upper() == iso_code.upper()].copy()