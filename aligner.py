import piexif
from PIL import Image
import os
import shutil
from libxmp.utils import file_to_dict
from libxmp import XMPFiles, consts

# GPS
# http://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf
# XMP
# https://python-xmp-toolkit.readthedocs.io/en/latest/using.html

PHOTO_DIRECTORY = "./"
OUT_DIRECTORY = "out/"

def convert(pair):
	return pair[0]/pair[1]

for filename in os.listdir(PHOTO_DIRECTORY):
	if filename.split(".")[-1].lower() != "jpg":
		continue
	full_filename = PHOTO_DIRECTORY + filename
	out_filename = OUT_DIRECTORY + filename

	print(full_filename)

	print("################### EXIF ###################")

	shutil.copy(full_filename, out_filename, follow_symlinks=True)

	img = Image.open(out_filename)

	exif_dict = piexif.load(img.info['exif'])

	GPS_altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
	print("GPS_altitude:", convert(GPS_altitude))

	GPS_altitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef]
	print("GPS_altitude_ref:", GPS_altitude_ref)

	GPS_latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
	print("GPS_latitude:", convert(GPS_latitude[0]), convert(GPS_latitude[1]), convert(GPS_latitude[2]))

	GPS_latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef]
	print("GPS_altitude_ref:", GPS_latitude_ref)

	GPS_longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
	print("GPS_longitude:", convert(GPS_longitude[0]), convert(GPS_longitude[1]), convert(GPS_longitude[2]))

	GPS_longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef]
	print("GPS_longitude_ref:", GPS_longitude_ref)

	exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (140, 1)

	exif_bytes = piexif.dump(exif_dict)

	piexif.insert(exif_bytes, out_filename)

	break

	print("################### XMP ###################")

	xmpfile = XMPFiles(file_path=out_filename, open_forupdate=True)

	xmp = xmpfile.get_xmp()

	print(xmp)

	for thing in consts.__dict__:
		print(thing)
		if "dji" in thing.lower():
			print("\t\t\t!!")

	

	#print(xmp.get_property(consts.XMP_NS_DC, 'drone-dji:AbsoluteAltitude' ))

	#xmp.set_property(consts.XMP_NS_DC, u'format', u'application/vnd.adobe.illustrator' )

	xmp2 = file_to_dict(out_filename)
	xmp3 = xmp2

	for i, item in enumerate(xmp2):
		for j, jtem in enumerate(xmp2[item]):
			name = jtem[0]
			if "GPS" in name or "Altitude" in name:
				print(name)
				print(jtem[:2])
				if "exif:GPSAltitude" == name:
					print("!!!!!!!!!")
					print(i, j)
					print(xmp3)
					xmp3[item][j][1] = "10/3"

	for i, item in enumerate(xmp3):
		for j, jtem in enumerate(xmp3[item]):
			name = jtem[0]
			if "GPS" in name or "Altitude" in name:
				print(name)
				print(jtem[:2])



	# exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (140, 1)

	# altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
	# print(altitude)

	# exif_bytes = piexif.dump(exif_dict)

	# piexif.insert(exif_bytes, out_filename)

	break