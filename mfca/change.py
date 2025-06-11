import numpy as np
import geopandas as gpd
from rasterio.features import rasterize

def detect_change(
    class_a: np.ndarray,
    class_b: np.ndarray,
    polygons  # reserved for future per-polygon operations
) -> np.ndarray:
    """
    Simple change detector: returns a 2D array where
    1 indicates a change in class (class_a != class_b),
    and 0 indicates no change.
    The polygons argument is currently unused.
    """
    # Ensure arrays have the same shape
    if class_a.shape != class_b.shape:
        raise ValueError("Input arrays must have the same shape")

    # Compute change mask
    change_mask = (class_a != class_b).astype(np.uint8)
    return change_mask
def summarize_change_by_polygon(
    change_mask: np.ndarray,
    polygons: gpd.GeoDataFrame,
    transform
) -> gpd.GeoDataFrame:
    """
    For each polygon in the GeoDataFrame, rasterize it to the same grid as the change_mask
    (using the provided Affine transform) and compute:
      total_pixels: count of pixels inside the polygon
      changed_pixels: sum of change_mask inside the polygon
      pct_changed: changed_pixels / total_pixels
    
    Returns a copy of polygons with three new columns: total_pixels, changed_pixels, pct_changed.
    """
    results = polygons.copy()
    total = []
    changed = []

    # Prepare geometry-transform pair for rasterize
    shapes = [(geom, idx) for idx, geom in enumerate(polygons.geometry)]

    # Rasterize an index mask: each pixel holds the polygon index or 0
    poly_index_mask = rasterize(
        shapes=shapes,
        out_shape=change_mask.shape,
        transform=transform,
        fill=-1,
        all_touched=False,
        dtype=np.int32
    )
    # poly_index_mask == i means that pixel belongs to polygons.iloc[i]
    for i in range(len(polygons)):
        mask = poly_index_mask == i
        total_i = int(mask.sum())
        changed_i = int((change_mask[mask] == 1).sum()) if total_i > 0 else 0
        total.append(total_i)
        changed.append(changed_i)

    results["total_pixels"] = total
    results["changed_pixels"] = changed
    # Avoid division by zero
    results["pct_changed"] = results.apply(
        lambda row: (row.changed_pixels / row.total_pixels) if row.total_pixels > 0 else 0.0,
        axis=1
    )
    return results
