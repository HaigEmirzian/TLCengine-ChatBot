from census import Census
from us import states

c = Census("79b2e8947a1cea9dbed56071e5cc95c875e01c1d") # API KEY to access Census Data

# The link below has the table correlating the codes to the data type.
# https://api.census.gov/data/2022/acs/acs5/variables.html

# Example use of the API to get data (Median Household Income) by state
print(c.acs5.state(('NAME', 'B19013_001E'), states.NJ.fips))

# Example use of the API to get data (Median Household Income) by zipcode
print(c.acs5.state_zipcode(('NAME', 'B19013_001E'), states.NJ.fips, "07030"))