import numpy as np
import rasterio
from rasterio.io import DatasetReader
import geopandas as gpd

def classify(
    raster: DatasetReader,
    polygons: gpd.GeoDataFrame
) -> np.ndarray:
    """
    Simple threshold classifier: reads the first band of the raster,
    computes the mean pixel value, and returns a 2D array of
    0/1 labels (1 where pixel > mean, else 0).
    The polygons argument is reserved for future per-polygon logic.
    """
    # Read the first band into a NumPy array
    arr = raster.read(1).astype(float)

    # Compute threshold as the mean of all pixel values
    thresh = np.nanmean(arr)

    # Generate binary labels: 1 for pixels strictly greater than threshold
    labels = (arr > thresh).astype(np.uint8)

    return labels
