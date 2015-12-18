import csv
import time, datetime

def load_538_pollster_tsv(tsv_filename):

                
        with open('sample.txt','rb') as tsvin, open('new.csv', 'wb') as csvout:
                tsvin = csv.reader(tsvin, delimiter='\t')
                csvout = csv.writer(csvout)
                
                for row in tsvin:
                        count = int(row[4])
                        if count > 0:
                                csvout.writerows([row[2:4] for _ in xrange(count)])
                        

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

senate_class_3_states = {
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MD': 'Maryland',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NH': 'New Hampshire',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'UT': 'Utah',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
}

presidential_candidates_dem = [
        "Clinton",
        "O'Malley",
        "Sanders"
        
]
presidential_candidates_gop = [
        "Trump",
        "Bush",
        "Cruz", 
        "Rubio",
        "Kasich",
        "Gilmore",
        "Huckabee",
        "Santorum",
        "Fiorina",
        "Carson",
        "Graham"
]

#election_day_president = time.struct_time(tm_year=2016, tm_mon=11, tm_mday=8, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=0, tm_yday=0, tm_isdst=-1)