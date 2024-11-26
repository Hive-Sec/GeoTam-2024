def create_map(self):
    manchester_coords = (53.4808, -2.2426)
    m = folium.Map(location=manchester_coords, zoom_start=12)

    if self.db_conn:
        companies = self.db_conn.execute('''
            SELECT CompanyName, RegAddress_PostTown, RegAddress_PostCode, CompanyCategory
            FROM companies
            LIMIT 100
        ''').fetchdf()

        for _, company in companies.iterrows():
            folium.Marker(
                location=self.get_coordinates(company['RegAddress_PostCode']),
                popup=f"{company['CompanyName']} - {company['CompanyCategory']}",
                tooltip=f"{company['RegAddress_PostTown']}, {company['RegAddress_PostCode']}",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)

    data = io.BytesIO()
    m.save(data, close_file=False)
    self.map_view.setHtml(data.getvalue().decode())

def get_coordinates(self, postcode):
    # This is a placeholder function. In a real application, you would use a geocoding service
    # to convert postcodes to coordinates. For now, we'll return random coordinates near Manchester.
    import random
    return (53.4808 + random.uniform(-0.1, 0.1), -2.2426 + random.uniform(-0.1, 0.1))
