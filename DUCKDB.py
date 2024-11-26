import duckdb
import pandas as pd

# Specified Company Categories
COMPANY_CATEGORIES = [
    "Private Limited Company",
    "Charitable Incorporated Organisation",
    "PRI/LBG/NSC (Private, Limited by guarantee, no share capital, use of 'Limited' exemption)",
    "Limited Partnership",
    "Royal Charter Company"
]

def create_duckdb_from_csv(csv_path):
    """
    Create a DuckDB database from the CSV file with filtered company categories
    """
    # Connect to DuckDB
    conn = duckdb.connect('company_database.db')
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Filter for specified company categories
    filtered_df = df[df['CompanyCategory'].isin(COMPANY_CATEGORIES)]
    
    # Create a table in DuckDB
    conn.register('companies_temp', filtered_df)
    conn.execute('''
        CREATE TABLE companies AS 
        SELECT * FROM companies_temp
    ''')
    
    # Verify the table creation
    print("Table created successfully!")
    print(f"Total records: {conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]}")
    
    return conn

# Example usage
def main():
    # Replace with your actual CSV file path
    csv_path = 'Filtered-BSD.csv'
    
    # Create DuckDB database
    db_connection = create_duckdb_from_csv(csv_path)
    
    # Example query to show data
    print("\nSample Company Data:")
    sample_data = db_connection.execute('''
        SELECT CompanyName, CompanyCategory, CompanyStatus 
        FROM companies 
        LIMIT 5
    ''').fetchdf()
    print(sample_data)
    
    # Close the connection
    db_connection.close()

if __name__ == "__main__":
    main()
