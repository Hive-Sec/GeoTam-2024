#First Mission, getting the data and staging it where we can work on it.
import duckdb

# Create the database we'll save our work to and load the extensions we'll need
con = duckdb.connect("conflation_demonstration.ddb")
con.sql("install spatial")
con.sql("install httpfs")
con.sql("load spatial")
con.sql("load httpfs")

# Load the CSV from the BSD Rebalance earth DataSet
con.sql("CREATE TABLE inspections AS SELECT * FROM read_csv('/home/whoami/running-hive-projects/GEOTAM/DataSets/BSD-big.csv', ignore_errors=True)")
# We need to get this CSV into a form where we can interrogate it and compare it to other datasets. For that, we’re going to use DuckDB. 
# Let’s set up our database and load our inspections into a table:
# Download the Overture Places data. 
# 1. Create a bounding box around all the Manchester records
# 2. Get all the places from Overture in that bounding box, with a confidence score > 0.5
# 3. Finally transform these results into a format that matches manchester Data

con.sql("""
    CREATE TABLE IF NOT EXISTS places AS 
    WITH bounding_box AS (
        SELECT max(Latitude) as max_lat, min(Latitude) as min_lat, max(Longitude) as max_lon, min(Longitude) as min_lon
        FROM inspections
    )
    SELECT 
        id, 
        upper(names['primary']) as Facility_Name, 
        upper(addresses[1]['freeform']) as Address, 
        upper(addresses[1]['locality']) as City, 
        upper(addresses[1]['region']) as State, 
        left(addresses[1]['postcode'], 5) as Zip, 
        geometry, 
        ST_X(geometry) as Longitude,
        ST_Y(geometry) as Latitude,
        categories 
    FROM (
        SELECT * 
        FROM read_parquet('s3://overturemapsNOT_RECORDED IN CSV/release/2024-09-18.0/theme=places/type=place/*', filename=true, hive_partitioning=1),
             bounding_box
        WHERE addresses[1] IS NOT NULL AND
            bbox.xmin BETWEEN bounding_box.min_lon AND bounding_box.max_lon AND
            bbox.ymin BETWEEN bounding_box.min_lat AND bounding_box.max_lat AND
            confidence > 0.5
    );
""")

con.sql("INSTALL h3 FROM community")
con.sql("LOAD h3")

# Add H3 indexs to each table
con.sql("ALTER TABLE places ADD COLUMN IF NOT EXISTS h3 uint64")
con.sql("ALTER TABLE inspections ADD COLUMN IF NOT EXISTS h3 uint64")
con.sql("UPDATE places SET h3 = h3_latlng_to_cell(Latitude, Longitude, 7)")
con.sql("UPDATE inspections SET h3 = h3_latlng_to_cell(Latitude, Longitude, 7)")

