import os
import mfca.io as io

def test_clip_aoi_on_sample_gpkg():
    # locate the sample file we created (fix filename)
    sample_gpkg = os.path.join(os.getcwd(), "data/samples/ghanamine.shp")
    assert os.path.exists(sample_gpkg), "Sample shapefile not found"
    
    # load all features
    gdf = io.load_vector(sample_gpkg)
    print(f"Total features loaded: {len(gdf)}")
    
    # Check that we have both Ghana and USA data
    gha_count = len(gdf[gdf["ISO3_CODE"] == "GHA"])
    usa_count = len(gdf[gdf["ISO3_CODE"] == "USA"])
    print(f"Ghana features: {gha_count}, USA features: {usa_count}")
    
    # Verify we have the expected columns
    assert "ISO3_CODE" in gdf.columns
    assert "AREA" in gdf.columns
    
    # Test clipping to Ghana only
    clipped = io.clip_aoi(gdf, iso_code="GHA")
    assert len(clipped) == gha_count
    assert all(clipped["ISO3_CODE"] == "GHA")
    
    # Verify all clipped features are from the original Ghana data
    original_gha_areas = set(gdf[gdf["ISO3_CODE"] == "GHA"]["AREA"])
    clipped_areas = set(clipped["AREA"])
    assert clipped_areas == original_gha_areas