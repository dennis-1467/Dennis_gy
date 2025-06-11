import rasterio
import numpy as np
import rasterio.transform
import pytest
from mfca.preprocess import check_raster_compatibility

@pytest.fixture
def make_tiffs(tmp_path):
    # Base metadata: 10×10 px, EPSG:4326, 1×1 degree resolution
    meta = {
        "driver": "GTiff",
        "dtype": "uint8",
        "count": 1,
        "width": 10,
        "height": 10,
        "crs": "EPSG:4326",
        "transform": rasterio.transform.from_origin(0, 10, 1, 1),
    }
    # Raster A: resolution 1×1
    path_a = tmp_path / "a.tif"
    with rasterio.open(path_a, "w", **meta) as dst:
        dst.write(np.ones((1, 10, 10), dtype="uint8"))

    # Raster B: change resolution to 2×2
    meta2 = meta.copy()
    meta2["transform"] = rasterio.transform.from_origin(0, 10, 2, 2)
    path_b = tmp_path / "b.tif"
    with rasterio.open(path_b, "w", **meta2) as dst:
        dst.write(np.ones((1, 10, 10), dtype="uint8"))

    return str(path_a), str(path_b)

def test_compatibility(make_tiffs):
    a, b = make_tiffs
    # identical rasters should be compatible
    with rasterio.open(a) as ra, rasterio.open(a) as rb:
        assert check_raster_compatibility(ra, rb)
    # differing resolution should be incompatible
    with rasterio.open(a) as ra, rasterio.open(b) as rb:
        assert not check_raster_compatibility(ra, rb)
