# Packaging with PyInstaller (Rasterio, Fiona, PyOgrio / GDAL)

## Step 1: Activate virtual environment and install PyInstaller
```bash
source .venv/bin/activate
pip install pyinstaller
```

## Step 2: Generate spec file with all hidden imports and bundled data
```bash
pyi-makespec \
  --onefile \
  --name mfca \
  --hidden-import rasterio.sample \
  --hidden-import rasterio._io \
  --hidden-import rasterio.vrt \
  --hidden-import affine \
  --hidden-import pyogrio._geometry \
  --hidden-import fiona \
  --collect-data rasterio \
  --collect-data affine \
  --collect-data pyogrio \
  --collect-data fiona \
  mfca/main.py
```

## Step 3: (Optional) Edit mfca.spec to set GDAL_DATA environment variable if needed

## Step 4: Build the standalone executable
```bash
pyinstaller mfca.spec
```

## Step 5: Test the bundled CLI

### Dry-run mode (no output files written):
```bash
./dist/mfca \
  --polygons data/samples/ghana_mines.shp \
  --raster-a a.tif \
  --raster-b b.tif \
  --aoi GHA \
  --dry-run
```

### Full analysis (writes a per-polygon CSV):
```bash
./dist/mfca \
  --polygons data/samples/ghana_mines.shp \
  --raster-a a.tif \
  --raster-b b.tif \
  --aoi GHA
```
