import rasterio
import numpy as np
import pytest
from rasterio.transform import from_origin
import geopandas as gpd
from shapely.geometry import box

from mfca.classify import classify

@pytest.fixture
def make_test_raster(tmp_path):
    data = np.array([[0, 0],
                     [10, 10]], dtype=np.uint8)
    meta = {
        "driver": "GTiff",
        "dtype": "uint8",
        "count": 1,
        "width": 2,
        "height": 2,
        "crs": "EPSG:4326",
        "transform": from_origin(0, 2, 1, 1),
    }
    path = tmp_path / "test.tif"
    with rasterio.open(path, "w", **meta) as dst:
        dst.write(data, 1)
    return str(path)

@pytest.fixture
def dummy_polygons():
    gdf = gpd.GeoDataFrame(
        {"ISO3_CODE": ["GHA"]},
        geometry=[box(0, 0, 1, 1)],
        crs="EPSG:4326"
    )
    return gdf

def test_classify_threshold(make_test_raster, dummy_polygons):
    path = make_test_raster
    with rasterio.open(path) as src:
        labels = classify(src, dummy_polygons)

    # Mean = (0+0+10+10)/4 = 5 → pixels > 5 are labeled 1
    expected = np.array([[0, 0],
                         [1, 1]], dtype=np.uint8)

    assert isinstance(labels, np.ndarray)
    assert labels.shape == expected.shape
    np.testing.assert_array_equal(labels, expected)
