import rasterio
from rasterio.io import DatasetReader

def check_raster_compatibility(ra: DatasetReader, rb: DatasetReader) -> bool:
    """
    Return True if both rasters share the same CRS and the same pixel size.
    """
    # If CRSs differ, not compatible
    if ra.crs != rb.crs:
        return False

    # Extract pixel width (a) and height (e is negative)
    res_a = (ra.transform.a, abs(ra.transform.e))
    res_b = (rb.transform.a, abs(rb.transform.e))

    return res_a == res_b
