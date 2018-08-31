import urllib, json
json_ex = {
    "type": "FeatureCollection",
    "features":[]
}
with open('data/index3.geojson') as f:
    data = json.load(f)
count = 0
for quake_num in data["features"]:
    count=count+1
    url = quake_num["properties"]["detail"]
    response = urllib.urlopen(url)
    datai = json.loads(response.read())
    print "Got details for : ", quake_num["properties"]["title"]
    try:
        url2 = datai["properties"]["products"]["shakemap"][0]["contents"]["download/cont_pgv.json"]["url"]
    except:
        print "No Shapefile for this"
        continue
    response = urllib.urlopen(url2)
    datai2 = json.loads(response.read())
    max=0
    for polygon_num in datai2["features"]:
        if float(polygon_num["properties"]["value"])>max:
            max=float(polygon_num["properties"]["value"])
    for polygon_num in datai2["features"]:
        polygon_num["geometry"]["type"] = "Polygon"
        polygon_num["properties"]["height"] = float(datai["properties"]["mag"])*float(polygon_num["properties"]["value"])/max
        json_ex["features"].extend(datai2["features"]);
    print "Appended - ",count
print "Writing to file"
with open('json_ex.json', 'w') as outfile:
    json.dump(json_ex, outfile)