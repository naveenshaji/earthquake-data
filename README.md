# Visualizing seismic action around the Himalayas

![Screenshot of the project](https://user-images.githubusercontent.com/10815281/44892891-ef3c9700-ad04-11e8-973d-b7faa35cd435.png)

The idea was to visualize and estimate the accurate extent and intensity of earthquakes around the Himalayan region. All data including GIS shapefiles are from USGS.

## The Process
It wasn't really straightforward to get to this result or this data, so I'll be detailing the steps I took, in case someone else wants to use this dataset for better visualizing their story.
### Procuring the data
The data was spread across multiple file sources on USGS. The shapefiles were separately available for each earthquake - pure shape data without magnitude. The first challenge was combining the shape data and the proper magnitude for each earthquake before aggregating them to one big file with shape geometry as polygons and magnitude values ad properties.

From the [Earthquake Catalog Search](https://earthquake.usgs.gov/earthquakes/search/), the required earthquakes were identified and filtered out. This produced a JSON file with date, id, magnitude, and a few other properties for each earthquake.

From here, there was no easy way to query the shapefiles, but what could be done was to request more information. The "detail" key-value pair in the above JSON provides a URL from which you can request a more detailed version of the earthquake information.

`import urllib, json`
`detailed_data = json.loads(urllib.urlopen(data["features"][0]["properties"]["detail"]))`

This gives you another longer JSON - one per earthquake, with a large amount of data - which includes links to request all linked files. 

`url2 = detailed_data["properties"]["products"]["shakemap"][0]["contents"]["download/cont_pgv.json"]["url"]`

Requesting a response from that URL gives you the required shapefiles. 

Now comes another problem - the shapefiles are not in the FeatureCollection polygons format that Mapbox works with - which means we have to parse through the geometry that is already there and generate our own GeoJSON file that includes geometries from the multiple shapefiles, and magnitude from the details JSON. 

The shapefiles come with a value property for each polygon. However, that property is very inconsistent among datasets from different years. Some earthquakes have values on a scale of 0.2 to 0.8, while some others of the same magnitude have values over a hundred. However, they were only accurate relative to other polygons in the same earthquake data. 

In order to normalize this, the magnitude can be taken as a factor and using the maximum value in each scale, we can obtain fairly accurate normalized data. I'm gonna store this as the height property for each polygon.

`polygon_num["properties"]["height"] = float(datai["properties"]["mag"])*float(polygon_num["properties"]["value"])/max`

Running the code against the USGS server made me realize that some earthquakes have incomplete shapefiles. These cases are rare, but they exist, and you don't want that stopping your code from querying all the data. We just need to drop in a `try-except` block to catch the errors to fix that.

`try:`
        `url2 = datai["properties"]["products"]["shakemap"][0]["contents"]["download/cont_pgv.json"]["url"]`
    `except:`
       ` print "No Shapefile for this"`
        `continue`
    `response = urllib.urlopen(url2)`
    `datai2 = json.loads(response.read())`

And, that's it. We should be good to go!

![screen shot of terminal](https://user-images.githubusercontent.com/10815281/44894706-c02b2300-ad0e-11e8-97fd-a6a91cd86f6c.png)

Just testing it against a random data set. - and, it works. The generated GeoJSON file is over 5MB, for just 20 earthquakes. This means that I won't be able to upload the GeoJSON to Mapbox without using their APIs. The alternative here is to generate your own tilesets offline and then upload the generated vector tilesets to Mapbox. The upload limit is much higher for tilesets, and we should be able to upload large files without any issues. 

I'm using the Mapbox recommended command line tool[ tippecanoe](https://github.com/mapbox/tippecanoe) to generate tilesets from my GeoJSON.

![screen shot 2018-08-31 at 11 19 31 am](https://user-images.githubusercontent.com/10815281/44894947-c4a40b80-ad0f-11e8-8677-347c026f0bb3.png)

This takes a while depending on how big your data is, and how fast your computer is. It took around 7 minutes for the data that I was working on. Once it's done, you're left with a *.MBTILES file which can then be uploaded to Mapbox.

Mapbox then takes some time to process it (forever!). 

### Visualizing the procured data
The data is essentially different groups of stacked polygons, and as such can be extruded in Mapbox. I've used the height value that we calculated earlier to set the heights, as well as a color scale as it's a function of the relative scale and the magnitude, and therefore is ultimately a function of that earthquake's magnitude.

![screen shot 2018-08-31 at 11 30 29 am](https://user-images.githubusercontent.com/10815281/44895284-4ba5b380-ad11-11e8-901f-0c21ac2e4ab4.png)

You can also see how the form produced by an earthquake in land differs greatly from one at sea which tend to mostly be uniform and circular.

![screen shot 2018-08-31 at 11 31 48 am](https://user-images.githubusercontent.com/10815281/44895356-9a534d80-ad11-11e8-9b86-7acdb7e198cd.png)
