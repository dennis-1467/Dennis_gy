import sys
import click
import rasterio
import geopandas as gpd
from mfca.io import load_vector
from mfca.preprocess import check_raster_compatibility
from mfca.classify import classify
from mfca.change import detect_change

@click.command()
@click.option("--polygons", "poly_path", required=True, type=click.Path(exists=True), help="Path to vector file (GeoPackage or Shapefile)")
@click.option("--raster-a", "raster_a", required=True, type=click.Path(exists=True), help="Path to first raster (GeoTIFF)")
@click.option("--raster-b", "raster_b", required=True, type=click.Path(exists=True), help="Path to second raster (GeoTIFF)")
@click.option("--aoi", default="GHA", show_default=True, help="ISO-3 code for the area of interest")
@click.option("--dry-run", "dry_run", is_flag=True, help="Show planned actions without executing classifier or change detection")
def main(poly_path: str, raster_a: str, raster_b: str, aoi: str, dry_run: bool) -> None:
    """Mine-Footprint Change Analyzer CLI."""
    # Load and validate polygons
    gdf = load_vector(poly_path)
    if gdf.crs.to_epsg() != 4326:
        click.echo(click.style(f"Error: expected EPSG 4326 polygons, found {gdf.crs}", fg="red"), err=True)
        sys.exit(1)

    # Open rasters
    try:
        ra = rasterio.open(raster_a)
        rb = rasterio.open(raster_b)
    except Exception as exc:
        click.echo(click.style(f"Error opening rasters: {exc}", fg="red"), err=True)
        sys.exit(1)

    # Check compatibility
    if not check_raster_compatibility(ra, rb):
        click.echo(click.style("Error: rasters differ in CRS or resolution", fg="red"), err=True)
        sys.exit(1)

    # Clip to AOI
    sub_polys = gdf[gdf["ISO3_CODE"].str.upper() == aoi.upper()].copy()
    if sub_polys.empty:
        click.echo(click.style(f"Error: no polygons intersect AOI {aoi}", fg="red"), err=True)
        sys.exit(1)

    # Dry-run mode: show what would happen
    if dry_run:
        click.echo(f"Dry run: would process polygons from {poly_path}")
        click.echo(f"Dry run: would open rasters {raster_a} and {raster_b}")
        click.echo(f"Dry run: would clip to AOI {aoi} and find {len(sub_polys)} polygons")
        sys.exit(0)

    # Normal execution: classify and detect change
    class_a = classify(ra, sub_polys)
    class_b = classify(rb, sub_polys)
    detect_change(class_a, class_b, sub_polys)

    click.echo(click.style("Processing complete.", fg="green"))

if __name__ == "__main__":
    main()
