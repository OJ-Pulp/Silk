        variant_manufacturer = variant_base_product.manufacturer
        possible_manufacturer_locations = list(manufacturer_keys[variant_manufacturer]["Locations"])
        variant_manufacturer_location = FAKER_GEN.random_element(elements=possible_manufacturer_locations)