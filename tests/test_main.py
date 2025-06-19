import subprocess
import os
import sys

def test_cli_dry_run(tmp_path):
    # Path to the sample shapefile
    shp = os.path.join(os.getcwd(), "data/samples/ghana_mines.shp")
    assert os.path.exists(shp), "Sample Shapefile not found"

    # Create two minimal dummy rasters
    import rasterio
    from rasterio.transform import from_origin
    import numpy as np

    meta = {
        "driver": "GTiff", "dtype": "uint8", "count": 1,
        "width": 5, "height": 5,
        "crs": "EPSG:4326",
        "transform": from_origin(0, 5, 1, 1),
    }
    tif_a = tmp_path / "a.tif"
    tif_b = tmp_path / "b.tif"
    for path in (tif_a, tif_b):
        with rasterio.open(path, "w", **meta) as dst:
            dst.write(np.zeros((1, 5, 5), dtype="uint8"))

    # Run our CLI in dry-run mode
    cmd = [
        sys.executable, "-m", "mfca.main",
        "--polygons", shp,
        "--raster-a", str(tif_a),
        "--raster-b", str(tif_b),
        "--aoi", "GHA",
        "--dry-run"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    # Verify it completed successfully and printed expected lines
    assert proc.returncode == 0
    out = proc.stdout
    assert "Dry run: would process polygons" in out
    assert "Dry run: would open rasters" in out
    assert "Dry run: would clip to AOI GHA" in out
