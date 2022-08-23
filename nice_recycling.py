import os.path
import urllib.request
import geojson
import csv
import math
import pandas as pd 
import csv
import unidecode

######################################################
	  	  ### VARIABLES ###
######################################################

region_name="Nice Côte d'Azur"
project_folder = "/home/erwan/Downloads/OSM-Automation/"
api_json = project_folder + "nice.geojson"
city_name = "Vence"
file_location = project_folder + region_name.replace(" ", "").replace("'", "").replace("ô", "o") + ".txt"
number_bins_min = 25

bins_columns = ['city','longitude','latitude','recycling:paper','recycling:glass_bottles', 'recycling:clothes', \
                'recycling:waste','recycling:beverage_carton','recycling:metal_packaging','recycling:cans', \
                'recycling:plastic_bottles','recycling:plastic_packaging','recycling_type', 'location', \
                'source:url', 'source', 'amenity', 'source:date'
               ]

dict_osm_nod = {'ORDURES MENAGERES': {'recycling:waste':'yes'}, 
                'PAPIER': {'recycling:paper':'yes'}, 
                'TEXTILE': {'recycling:clothes':'yes'},
                'VERRE': {'recycling:glass_bottles':'yes'},
                'EMBALLAGES MENAGERS': {'recycling:beverage_carton':'yes', 'recycling:metal_packaging':'yes', 'recycling:cans':'yes', 'recycling:plastic_packaging':'yes', 'recycling:plastic_bottles':'yes'}, 
                'AERIEN':{'recycling_type':'container'},
                'ENTERRE': {'recycling_type':'container', 'location':'underground'},
                'SEMI ENTERRE': {'recycling_type':'container', 'location':'underground'},
                'ASCENSEUR': {'recycling_type':'container', 'location':'underground'}
               }

######################################################
		  ### FUNCTIONS ###
######################################################

def all_exist(avalue, bvalue):
    return all(any(i in j for j in bvalue) for i in avalue)

def download_region_cities_osm(region_name):
    get_region_cities = "http://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3Barea%5B%22name%22%3D%22" + region_name.replace(" ", "%20").replace("'", "%27").replace("ô", "%C3%B4") + "%22%5D%2D%3E%2EsearchArea%3B%28node%5B%22place%22%7E%22city%7Ctown%7Cvillage%7Chamlet%22%5D%28area%2EsearchArea%29%3B%29%3Bout%3B%3E%3Bout%20skel%20qt%3B%0A"
    file_location = project_folder + region_name.replace(" ", "").replace("'", "").replace("ô", "o") + ".txt"

    with urllib.request.urlopen(get_region_cities) as f: 
        gg_osm = geojson.load(f)
    
    with open(file_location, "w") as h:
        for i in range(len(gg_osm["elements"])):
            h.write(gg_osm["elements"][i]["tags"]["name"])
            h.write(',')
    print("Saved cities to file:\n" + file_location)
    
    return file_location

def clean_api_data(api_json):
    count_city_miss=0
    miss_cities = []

    with open(api_json) as f:
        gj = geojson.load(f)

    #Count how many items are in the Nice Open-Data file
    for x in range(len(gj['features'])):
        if "COMMUNE" in gj['features'][x]["properties"]:
                count_city_miss=count_city_miss+1
        else:
            miss_cities.append(gj['features'][x]["id"])

    print("\nCounted", len(gj['features']), "items with a city defined in Nice Open-Data file -", len(gj['features']) - count_city_miss, "missing with id(s)", miss_cities)

    #Remove items without city defined
    if miss_cities:
        del gj['features'][miss_cities[0]-1]
        print(' -> Removed id', miss_cities, 'with missing city', "\n")
    
    return gj

######################################################
		   ### SCRIPT ###
######################################################

print("\n\033[4mChecking for", region_name, "file\033[0m:\n")

### Gather all towns, village, cities names for Nice Cote d'Azur
if not os.path.exists(file_location):
    print("Downloading file from OSM.")
    download_region_cities_osm(region_name)
else:
    print("File", region_name.replace(" ", "").replace("'", "").replace("ô", "o") + ".txt", "already exists.")


####Extract all cities from Nice Open-Data file
unique_api_cities = []
    
with open(api_json) as f:
        gj = geojson.load(f)

for x in range(len(gj['features'])):
    if "COMMUNE" in gj['features'][x]["properties"] and gj['features'][x]["properties"]["COMMUNE"] not in unique_api_cities:
            unique_api_cities.append(gj['features'][x]["properties"]["COMMUNE"])
unique_api_cities = list(set(unique_api_cities))

print(len(unique_api_cities), "distinct cities were found in this file.\n")
#print(', '.join(unique_api_cities))

#Create list of matching cities between Nice Open Data & OSM
i=0
perfect_match=[]
unmatched_list=[]
remain_list=[]
extended_content_list = []
extended_unique_api_cities = []
city_match_list = []

print("\033[4mCleaning data from the Nice Open-Data file\033[0m:")    

with open(region_name.replace(" ", "").replace("'", "").replace("ô", "o") + ".txt") as f:
    gh = f.read()
    content_list = gh.split(",")

for i in range(len(content_list)):
    extended_content_list.append([content_list[i].lower().replace("-", " ").replace("è", "e").replace("é", "e").split(" "), content_list[i]])
for i in range(len(unique_api_cities)):
    extended_unique_api_cities.append([unique_api_cities[i].lower().replace("-", " ").replace("è", "e").replace("é", "e").split(" ")
, unique_api_cities[i]])

i=0
for x in extended_unique_api_cities:
    for y in extended_content_list:
        if x[0] == y[0]:
            perfect_match.append(x[0])
            city_match_list.append([x[1],y[1]])
            i=i+1

unmatched_list = [item for item in extended_unique_api_cities if item[0] not in perfect_match]
remain_list = [item for item in extended_content_list if item[0] not in perfect_match]

print("\nThere are", i, "cities exactly matching between Nice Open-Data and OSM files.")
print("|---", len(unmatched_list), "remaining cities that need to be matched.")

i=0
for x in unmatched_list:
    for y in remain_list:
        if all_exist(x[0],y[0]):
            #print("Match on second pass:", x, y, "\n")
            perfect_match.append(x[0])
            city_match_list.append([x[1],y[1]]) 
            i=i+1

unmatched_list = [item for item in unmatched_list if item[0] not in perfect_match]
remain_list = [item for item in remain_list if item[0] not in perfect_match]

print("    |---", "There are", i, "cities matching on second pass.")
print("        |---", "!!", len(unmatched_list), "cities left unmatched. PROBABLY WON'T WORK ON BELOW TOWNS:")

for m in unmatched_list:
    print("              ---> ", m[1])
#print("\n")

#Stats about Nice Open-Data file
citybins = []
gj = clean_api_data(api_json)

#Get number of recycling bins per city and sort
for y in city_match_list:
    
    count = 0    
    for x in range(len(gj['features'])): 
        if (gj['features'][x]["properties"]["COMMUNE"] == y[0]):
            count = count + 1
            
    citybins.append((count, y[0]))
citybins.sort(reverse=True)

#Count total number of recycling bins in json file
total_bins = 0
for x,y in citybins:
    total_bins = total_bins + x

#Sort and display cities with higest number of bins in Nice Open-Data file
print("\033[4mCities with more than", number_bins_min ,"bins in the Nice Open-Data json file\033[0m:\n")
for x,y in citybins:
    if x>number_bins_min:
        print(y, ":", x, "recycling bins -", int(100*x/total_bins), "%")


#Getting recycling data from OSM for specific city
print("\n\033[4mComparing data from Nice Open-Data & OSM for\033[0m: " + "\033[1m" + city_name + "\033[0m\n")

for n in city_match_list:
    if n[0] == city_name:
        clean_city_name = n[1]

clean_city_name = clean_city_name.replace(" ", "%20").replace("é","%C3%A9").replace("è", "%C3%A8").replace("È","%C3%88").replace("É","%C3%89")
osm_url_json = "http://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%3Barea%5B%22name%22%3D%22" \
        + clean_city_name + "%22%5D%2D%3E%2EsearchArea%3B%28node%5B%22amenity%22%3D%22recycling%22%5D%28area%2EsearchArea%29%3B%29%3Bout%3B%3E%3Bout%20skel%20qt%3B%0A"

with urllib.request.urlopen(osm_url_json) as f: 
    gj_osm = geojson.load(f)

print("Overpass API found", len(gj_osm['elements']) , "recycling bins in", city_name)

#Getting recycling data from Nice Open-Data for the same city
city_bins = []

#For specific city, create a new list that includes all relevant data
for x in range(len(gj['features'])): 
    if gj['features'][x]["properties"]["COMMUNE"] == city_name:
        city_bins.append(gj['features'][x])

print("There are", len(city_bins), "separate recycling bins in", city_name, "listed by Open-Data Nice.")

#Compare OSM and Nice Open-Data latitude & longitude items to find potentially overlapping recycling bins
bins_to_map = []
bins_mapped = []

for e in city_bins:
    for dd in gj_osm['elements']:
        
        #Complicated with lat/long *floating* values - Need to use math package to iterate on them
        long_diff = math.modf(e["geometry"]["coordinates"][0])[0]-math.modf(dd["lon"])[0]
        lat_diff = math.modf(e["geometry"]["coordinates"][1])[0]-math.modf(dd["lat"])[0]
        
        #Rounding to 3 decimals (seems close enough) for comparing lat/long
        if round(abs(long_diff),4)<0.001 and round(abs(lat_diff),4)<0.001 and e not in bins_mapped:
            bins_mapped.append(e)
        
        #Prevent any duplicates from being in bins_to_map list (previous 1st-if for bins_mapped)
        elif e not in bins_to_map and e not in bins_mapped:
            bins_to_map.append(e)

#Prevent any duplicates from being in bins_to_map list
for l in bins_mapped:
    if l in bins_to_map:
        bins_to_map.remove(l)

if not len(bins_mapped) == 0:
    print("There are", len(bins_mapped), "separate bins that seem to match between OSM and Nice Open-Data.")        
#for f in bins_mapped:
    #print(f["geometry"]["coordinates"], f["properties"]["COMMUNE"], f["properties"]["CONTENEUR"], f["properties"]["TYPE"])
    
print("There are", len(bins_to_map), "separate bins from Nice Open-Data API that don't seem to be mapped in OSM:\n")        
#for g in bins_to_map:
    #print(g["geometry"]["coordinates"], g["properties"]["COMMUNE"], g["properties"]["CONTENEUR"], g["properties"]["TYPE"])

#Within Nice Open-Data list, find bins_to_map items very close to each other and merge them
list_coord = []
to_avg_list = []
all_bin_types = []
avg_bins_to_map = bins_to_map
reduce_list = []
index_indent = 0

for h in bins_to_map:
    
    #Rounding to 3 decimals (seems close enough) for comparing lat/long
    lat_long = [round(math.modf(h["geometry"]["coordinates"][0])[0],3), round(math.modf(h["geometry"]["coordinates"][1])[0],3)]
    list_coord.append(lat_long)

for m in list_coord:
    
    #Find all locations close to each other (if their rounded lat/loc are the same)
    indices = [n for n, x in enumerate(list_coord) if x == m]
    #print(indices,"|", [avg_bins_to_map[i]["geometry"]["coordinates"] for i in indices])
    
    #Get all lat/long & recycling types of locations close to each other
    to_avg_list = [avg_bins_to_map[i]["geometry"]["coordinates"] for i in indices]
    all_bin_types = [avg_bins_to_map[i]["properties"]["CONTENEUR"] for i in indices]
    
    #Sum lat/long for each locations close to each other
    res = [sum(i) for i in zip(*to_avg_list)]
    #print(all_bin_types)

    #Get average for each locations close to each other
    avg_bins_to_map[indices[0]]["geometry"]["coordinates"][0] = round(res[0]/len(to_avg_list),6)
    avg_bins_to_map[indices[0]]["geometry"]["coordinates"][1] = round(res[1]/len(to_avg_list),6)
    
    #Only keep the first bin of all the ones close to each other - add all recycling types to that first one
    if index_indent == indices[0]:
        avg_bins_to_map[indices[0]]["properties"]["CONTENEUR"] = all_bin_types
        reduce_list.append(avg_bins_to_map[indices[0]])
    
    index_indent = index_indent + 1

#Prepare formatting that can be fed in OSM
final_list = []

print("\n------------------------------------------------------------------------")
print("\033[1m - Job - Add", len(reduce_list),"merged recycling bins to OSM for the city of", city_name , "-\033[0m")
print("------------------------------------------------------------------------\n")
for m in reduce_list:
    
    #Removing unwanted fields and duplicated recycling_type
    m["properties"]["CONTENEUR"] = list(set(m["properties"]["CONTENEUR"]))
    m.pop("id")
    m.pop("type")
    m["geometry"].pop("type")
    m["properties"].pop("ID_NCA")
    m["properties"].pop("JOUR")
    print(m["properties"]["ADRESSE"], "-", m["properties"]["TYPE"],"-", m["geometry"]["coordinates"],m["properties"]["CONTENEUR"])
    
    #Mapping Nice Open-Data API field names to OSM field names
    final_list.append([m["properties"]["COMMUNE"], \
                       m["geometry"]["coordinates"][0], \
                       m["geometry"]["coordinates"][1], \
                       dict_osm_nod["PAPIER"]['recycling:paper'] if "PAPIER" in m["properties"]["CONTENEUR"] else '', \
                       dict_osm_nod["VERRE"]['recycling:glass_bottles'] if "VERRE" in m["properties"]["CONTENEUR"] else '', \
                       dict_osm_nod["TEXTILE"]['recycling:clothes'] if "TEXTILE" in m["properties"]["CONTENEUR"] else '', \
                       dict_osm_nod["ORDURES MENAGERES"]['recycling:waste'] if "ORDURES MENAGERES" in m["properties"]["CONTENEUR"] else '', \
                       dict_osm_nod["EMBALLAGES MENAGERS"]['recycling:beverage_carton'] if "EMBALLAGES MENAGERS" in m["properties"]["CONTENEUR"] else '', \
                       dict_osm_nod["EMBALLAGES MENAGERS"]['recycling:metal_packaging'] if "EMBALLAGES MENAGERS" in m["properties"]["CONTENEUR"] else '' , \
                       dict_osm_nod["EMBALLAGES MENAGERS"]['recycling:cans'] if "EMBALLAGES MENAGERS" in m["properties"]["CONTENEUR"] else '' , \
                       dict_osm_nod["EMBALLAGES MENAGERS"]['recycling:plastic_bottles'] if "EMBALLAGES MENAGERS" in m["properties"]["CONTENEUR"] else '' , \
                       dict_osm_nod["EMBALLAGES MENAGERS"]['recycling:plastic_packaging'] if "EMBALLAGES MENAGERS" in m["properties"]["CONTENEUR"] else '' , \
                       dict_osm_nod[m["properties"]["TYPE"]]['recycling_type'], \
                       dict_osm_nod[m["properties"]["TYPE"]]['location'] if m["properties"]["TYPE"]=="ENTERRE" else '', \
                       'http://opendata.nicecotedazur.org/data/storage/f/2020-09-02T13%3A44%3A50.928Z/pav.geojson', \
                       'Métropole Nice Côte d\'Azur', \
                       'recycling', \
                       '2020-09-02'                      
                      ])

print("\n")
#print(final_list)

#Prettify everything and make ready for import as csv
df = pd.DataFrame(final_list, columns = bins_columns)
pd.set_option('display.width', 1500)
print(df)

for n in city_match_list:
    if n[0] == city_name:
        clean_city_name = n[1]

clean_city_name = unidecode.unidecode(clean_city_name)

bins_columns.pop(0)
for m in final_list:
    m.pop(0)
    
with open(project_folder + clean_city_name + ".csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(bins_columns)
    writer.writerows(final_list)

print("\n\033[4mCSV file saved at\033[0m: " + project_folder + clean_city_name + ".csv\n")
