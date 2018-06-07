from pyspatialite import dbapi2 as db
from shapely import wkt
import struct
import argparse
import gzip

class Ring:
	def __init__(self, outer, spatialiteRing, children):
		self.outer = outer
		self.ring = spatialiteRing
		self.children = children


def dump_coords(fp, coords):
	fp.write(struct.pack("=i", len(coords)))
	for lng, lat in coords:
		fp.write(struct.pack("=ff", lat, lng))
		
def dump_ring(fp, ring):
	dump_coords(fp, ring.ring.coords)
	fp.write(struct.pack("=i", len(ring.children)))
	for child in ring.children:
		dump_coords(fp, child.ring.coords)
		fp.write(struct.pack("=i", 0))  # zero grandchildren
		
def dump_ringset(filename, rings):
	with gzip.open(filename, "wb") as fp:
		fp.write(struct.pack("=i", len(rings)))
		for ring in rings:
			dump_ring(fp, ring)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Converts a Spatialite database to a multipolygon binary format')
	parser.add_argument('db', metavar='DBFILE', type=str, nargs=1, help='The Spatialite .db file')
	parser.add_argument('-o', dest='output', action='store', default='polys.bin.gz', help='The output filename (default: %(default)s)')
	args = parser.parse_args()

	assert struct.calcsize("=i") == 4
	assert struct.calcsize("=ff") == 8

	dbfile = args.db[0]
	outfile = args.output
	conn = db.connect(dbfile)
	cursor = conn.cursor()
	print "Connected to database", dbfile
	for row in cursor.execute('select sqlite_version(), spatialite_version()'):
		print "Sqlite version %s, Spatialite version %s" % (row[0], row[1])

	print "Stage 1/3: Loading shapes"
	shapes = []
	response = cursor.execute('select AsText(Geometry) from land_polygons')
	for row in response:
		shapes.append(wkt.loads(row[0]))
	print "- Loaded %d shapes" % len(shapes)
	print "Stage 2/3: Constructing rings"
	outer_rings = []
	inner_rings = []
	for poly in [x for x in shapes if x.type == "Polygon"]:
		children = [Ring(False, ring, []) for ring in poly.interiors]
		inner_rings.extend(children)
		outer_rings.append(Ring(True, poly.exterior, children))
	
	print "Stage 3/3: Serializing data to", outfile
	dump_ringset(outfile, outer_rings)

	print "Done."

