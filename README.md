Included here is IPython Notebook code for:
 * resolving ISO regions to OSM relations ; and
 * extracting ferries from OSM.

Python libraries you'll need for `spatialite-to-bin.py` are:
 * pyspatialite (Spatialite database access)
 * shapely (geometric object manipulation)

In Ubuntu you can simply execute:
```
sudo aptitude install pyspatialite python-shapely
```

Other Python libraries you might need are:
 * imposm (OSM parser)
 * osmapi (OSM API access)
 * goslate (Google translate)
 * pycountry (ISO database - need ISO 3166-1alpa2 and 3166-2)

