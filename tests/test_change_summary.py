import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from rasterio.transform import from_origin

from mfca.change import summarize_change_by_polygon

def test_summarize_change_by_polygon():
    # Build a 4×4 change mask with a small changed square in the upper left
    change_mask = np.zeros((4, 4), dtype=np.uint8)
    change_mask[0:2, 0:2] = 1

    # Two polygons: one covering the top-left 2×2, one covering bottom-right 2×2
    polys = gpd.GeoDataFrame({
        "id": [0, 1]
    }, geometry=[
        box(0, 2, 2, 4),   # covers rows 0–1, cols 0–1
        box(2, 0, 4, 2)    # covers rows 2–3, cols 2–3
    ], crs="EPSG:4326")

    # Transform: origin top-left at (0,4), pixel size 1×1
    transform = from_origin(0, 4, 1, 1)

    summary = summarize_change_by_polygon(change_mask, polys, transform)

    # Polygon 0 covers exactly 4 pixels, all of which are changed in our mask
    assert summary.loc[0, "total_pixels"] == 4
    assert summary.loc[0, "changed_pixels"] == 4
    assert summary.loc[0, "pct_changed"] == 1.0

    # Polygon 1 covers 4 pixels, none of which are changed
    assert summary.loc[1, "total_pixels"] == 4
    assert summary.loc[1, "changed_pixels"] == 0
    assert summary.loc[1, "pct_changed"] == 0.0
