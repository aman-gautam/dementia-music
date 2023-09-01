import pandas as pd

def get_all_states():
    df = pd.read_csv('data/all-states.csv')
    return df.apply(lambda x: x['name'] + ' (' + x['country_name'] + ')', axis=1).to_list()
    
def find_country_code(country_name):
    with open('data/country-codes.csv', 'r') as db:
        while True:
            line = db.readline()
            if country_name in line:
                values = line.split(',')
                if values[0] == country_name:
                    return values[1]
            elif not line:
                break

def parse_location(location):
    if not location:
        return

    start_idx = location.index('(')
    end_idx = location.index(')')
    state = location[0: start_idx].strip()
    country = location[start_idx + 1: end_idx].strip()
    country_code = find_country_code(country)
    return {
        'state': state,
        'country': country,
        'country_code': country_code
    }
