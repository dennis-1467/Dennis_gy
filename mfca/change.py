import numpy as np
from rasterio.features import rasterize
import geopandas as gpd


def detect_change(
    path_a: str,
    path_b: str,
    polygons: gpd.GeoDataFrame
) -> str:
    """
    Compare two label rasters on disk in windows. Outputs a change-mask GeoTIFF path.
    Returns the file path to the generated change-mask.
    """
    import rasterio

    # Open label rasters
    with rasterio.open(path_a) as ra, rasterio.open(path_b) as rb:
        profile = ra.profile.copy()
        change_path = path_a.replace('_labels.tif', '_change.tif')
        # Write change mask on disk
        with rasterio.open(change_path, 'w', **profile) as dst:
            for ji, window in dst.block_windows(1):
                a_block = ra.read(1, window=window)
                b_block = rb.read(1, window=window)
                mask = (a_block != b_block).astype(np.uint8)
                dst.write(mask, window=window, indexes=1)
    return change_path


def summarize_change_by_polygon(
    change_mask: np.ndarray,
    polygons: gpd.GeoDataFrame,
    transform
) -> gpd.GeoDataFrame:
    """
    Compute per-polygon change statistics from a binary change mask array.
    Adds columns total_pixels, changed_pixels, pct_changed to the polygons GeoDataFrame.
    Returns a new GeoDataFrame with these stats.
    """
    results = polygons.copy()
    total = []
    changed = []

    # Rasterize polygons to index mask
    shapes = [(geom, idx) for idx, geom in enumerate(polygons.geometry)]
    poly_index_mask = rasterize(
        shapes=shapes,
        out_shape=change_mask.shape,
        transform=transform,
        fill=-1,
        all_touched=False,
        dtype=np.int32
    )

    for i in range(len(polygons)):
        mask = poly_index_mask == i
        total_i = int(mask.sum())
        changed_i = int((change_mask[mask] == 1).sum()) if total_i > 0 else 0
        total.append(total_i)
        changed.append(changed_i)

    results["total_pixels"] = total
    results["changed_pixels"] = changed
    results["pct_changed"] = results.apply(
        lambda row: (row.changed_pixels / row.total_pixels) if row.total_pixels > 0 else 0.0,
        axis=1
    )
    return results
