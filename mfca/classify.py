# File: mfca/classify.py
import numpy as np
import rasterio
from rasterio.io import DatasetReader
import geopandas as gpd


def classify(
    raster: DatasetReader,
    polygons: gpd.GeoDataFrame,
    threshold: float | None = None,
    method: str = 'adaptive'
) -> tuple[str, tuple[int,int]]:
    """
    Improved classifier with no-data handling.
    """
    # Read sample for threshold computation, excluding no-data
    decimate = max(1, raster.height // 512)
    sample = raster.read(1, out_shape=(raster.height//decimate, raster.width//decimate))
    
    # Handle no-data properly
    nodata_val = raster.nodata if raster.nodata is not None else 0
    valid_mask = sample != nodata_val
    
    if not np.any(valid_mask):
        raise ValueError("No valid data found in raster!")
    
    sample_flat = sample[valid_mask].flatten()
    
    if threshold is not None:
        thresh = float(threshold)
        print(f"Using provided threshold: {thresh:.4f}")
    elif method == 'adaptive':
        # Use a more sophisticated threshold
        q75, q25 = np.percentile(sample_flat, [75, 25])
        thresh = q25 + 0.5 * (q75 - q25)  # Adaptive threshold
        print(f"Adaptive threshold: {thresh:.4f}")
    elif method == 'otsu':
        # Simplified Otsu's method
        thresh = otsu_threshold(sample_flat)
        print(f"Otsu threshold: {thresh:.4f}")
    elif method == 'percentile':
        # Use 70th percentile as threshold
        thresh = np.percentile(sample_flat, 70)
        print(f"70th percentile threshold: {thresh:.4f}")
    else:  # default to mean
        thresh = float(np.mean(sample_flat))
        print(f"Mean threshold: {thresh:.4f}")

    # Show classification preview (only on valid data)
    binary_preview = (sample_flat > thresh).astype(np.uint8)
    positive_pct = np.sum(binary_preview) / len(binary_preview) * 100
    print(f"Preview: {positive_pct:.1f}% of VALID pixels classified as positive")
    print(f"Valid data range: {np.min(sample_flat):.0f} - {np.max(sample_flat):.0f}")

    # Prepare output
    profile = raster.profile.copy()
    profile.update(dtype='uint8', count=1, compress='lzw', nodata=255)
    labels_path = raster.name.replace('.tif', '_labels.tif')

    # Write in blocks
    with rasterio.open(labels_path, 'w', **profile) as dst:
        for ji, window in dst.block_windows(1):
            block = raster.read(1, window=window).astype(float)
            
            # Handle no-data: keep as no-data in output
            valid_pixels = block != nodata_val
            lbl = np.full(block.shape, 255, dtype=np.uint8)  # Fill with no-data value
            lbl[valid_pixels] = (block[valid_pixels] > thresh).astype(np.uint8)
            
            dst.write(lbl, window=window, indexes=1)

    return labels_path, (raster.height, raster.width)


def otsu_threshold(data):
    """Simplified Otsu's method for automatic thresholding"""
    hist, bin_edges = np.histogram(data, bins=256)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Normalize histogram
    hist = hist.astype(float) / np.sum(hist)
    
    # Compute cumulative sums
    w0 = np.cumsum(hist)
    w1 = 1 - w0
    
    # Avoid division by zero
    w0[w0 == 0] = 1e-10
    w1[w1 == 0] = 1e-10
    
    # Compute means
    mu0 = np.cumsum(hist * bin_centers) / w0
    mu1 = (np.sum(hist * bin_centers) - np.cumsum(hist * bin_centers)) / w1
    
    # Compute between-class variance
    variance = w0 * w1 * (mu0 - mu1) ** 2
    
    # Find threshold that maximizes variance
    idx = np.argmax(variance)
    return bin_centers[idx]