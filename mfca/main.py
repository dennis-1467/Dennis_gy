import numpy as np
import sys, os, click, rasterio
from mfca.io import load_vector
from mfca.preprocess import check_raster_compatibility
from mfca.classify import classify
from mfca.change import detect_change, summarize_change_by_polygon


@click.command()
@click.option("--polygons", "poly_path", required=True, help="Vector file (GeoPackage or Shapefile)")
@click.option("--raster-a", "raster_a_path", required=True, help="First raster (GeoTIFF)")
@click.option("--raster-b", "raster_b_path", required=True, help="Second raster (GeoTIFF)")
@click.option("--aoi", "aoi", default="GHA", show_default=True, help="ISO3 code AOI")
@click.option("--dry-run", "-n", "dry_run", is_flag=True, help="Smoke-test I/O and clipping")
@click.option("--threshold", "threshold", type=float, default=None, help="Override classifier threshold")
@click.option("--bbox", "bbox", type=(float, float, float, float), default=None,
              help="Optional crop box: xmin ymin xmax ymax")
def main(poly_path, raster_a_path, raster_b_path, aoi, dry_run, threshold, bbox):
    """Mine-Footprint Change Analyzer CLI."""
    click.echo(f"Loading polygons: {poly_path}")
    gdf = load_vector(poly_path)
    if gdf.crs.to_epsg() != 4326:
        click.echo(f"Error: expected EPSG4326, found {gdf.crs}", err=True)
        sys.exit(1)

    click.echo(f"Opening rasters: {raster_a_path}, {raster_b_path}")
    try:
        ra = rasterio.open(raster_a_path)
        rb = rasterio.open(raster_b_path)
    except Exception as e:
        click.echo(f"Error opening rasters: {e}", err=True)
        sys.exit(1)

    click.echo("Checking CRS & resolution compatibility...")
    if not check_raster_compatibility(ra, rb):
        click.echo("Error: rasters differ", err=True)
        sys.exit(1)

    # Clip polygons by ISO or bbox
    if bbox:
        from shapely.geometry import box
        clip_geom = box(*bbox)
        sub = gdf[gdf.geometry.intersects(clip_geom)].copy()
        click.echo(f"Clipped by bbox → {len(sub)} features")
    else:
        sub = gdf[gdf["ISO3_CODE"].str.upper() == aoi.upper()].copy()
        click.echo(f"Filtered by ISO3 {aoi} → {len(sub)} features")
    
    if sub.empty:
        click.echo("Error: no polygons found", err=True)
        sys.exit(1)

    if dry_run:
        click.echo("Dry run: I/O and clipping successful. Exiting.")
        sys.exit(0)

    # Determine unified threshold from both rasters (excluding no-data)
    decimate = max(1, ra.height // 512)
    small_a = ra.read(1, out_shape=(ra.height//decimate, ra.width//decimate))
    small_b = rb.read(1, out_shape=(rb.height//decimate, rb.width//decimate))
    
    # Filter out no-data values
    nodata_a = ra.nodata if ra.nodata is not None else 0
    nodata_b = rb.nodata if rb.nodata is not None else 0
    
    valid_a = small_a[small_a != nodata_a]
    valid_b = small_b[small_b != nodata_b]
    
    if len(valid_a) == 0 or len(valid_b) == 0:
        click.echo("Error: No valid data found in rasters", err=True)
        sys.exit(1)
    
    combined_mean = float((np.mean(valid_a) + np.mean(valid_b)) / 2)
    
    click.echo(f"Before data range: {np.min(valid_a):.0f} - {np.max(valid_a):.0f} (mean: {np.mean(valid_a):.0f})")
    click.echo(f"After data range: {np.min(valid_b):.0f} - {np.max(valid_b):.0f} (mean: {np.mean(valid_b):.0f})")

    if threshold is None:
        thresh = combined_mean
        click.echo(f"Using combined mean threshold: {thresh:.4f}")
    else:
        thresh = threshold
        click.echo(f"Using user-specified threshold: {thresh:.4f}")

    # Classify each raster
    click.echo("Classifying raster A...")
    labels_a, shape = classify(ra, sub, thresh, method='adaptive')
    click.echo(f"Labels A → {labels_a}")

    click.echo("Classifying raster B...")
    labels_b, _ = classify(rb, sub, thresh, method='adaptive')
    click.echo(f"Labels B → {labels_b}")

    # Debug: Check classification results
    click.echo("Checking label files...")
    with rasterio.open(labels_a) as la, rasterio.open(labels_b) as lb:
        # Find a region with valid data instead of sampling corner
        found_data = False
        for row in range(0, la.height-100, la.height//10):
            for col in range(0, la.width-100, la.width//10):
                window = rasterio.windows.Window(col, row, 100, 100)
                sample_a = la.read(1, window=window)
                sample_b = lb.read(1, window=window)
                
                # Skip if all no-data (255)
                if np.all(sample_a == 255) or np.all(sample_b == 255):
                    continue
                    
                valid_a = np.sum(sample_a < 255)  # Not no-data
                valid_b = np.sum(sample_b < 255)  # Not no-data
                pos_a = np.sum(sample_a == 1)     # Positive pixels
                pos_b = np.sum(sample_b == 1)     # Positive pixels
                diff = np.sum(sample_a != sample_b)  # Different pixels
                
                click.echo(f"Data region at ({row},{col}):")
                click.echo(f"  Label A: {pos_a}/{valid_a} positive pixels")
                click.echo(f"  Label B: {pos_b}/{valid_b} positive pixels") 
                click.echo(f"  Different: {diff} pixels")
                found_data = True
                break
            if found_data:
                break
        
        if not found_data:
            click.echo("Warning: No valid data regions found in sample windows!")

    # Detect change
    click.echo("Detecting change...")
    change_path = detect_change(labels_a, labels_b, sub)
    click.echo(f"Change mask → {change_path}")

    # Summarize
    click.echo("Summarizing per-polygon change...")
    with rasterio.open(change_path) as cm:
        mask = cm.read(1)
        transform = cm.transform
    summary = summarize_change_by_polygon(mask, sub, transform)

    # Export CSV
    out_csv = os.path.splitext(poly_path)[0] + "_change_summary.csv"
    click.echo(f"Writing summary → {out_csv}")
    summary.drop(columns="geometry").to_csv(out_csv, index=False)

    click.echo("Analysis complete.")


if __name__ == "__main__":
    main()