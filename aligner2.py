import piexif
from PIL import Image
import os
import shutil
# from libxmp.utils import file_to_dict
# from libxmp import XMPFiles, consts
import datetime

# GPS
# http://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf
# XMP
# https://python-xmp-toolkit.readthedocs.io/en/latest/using.html

MAVIC_PHOTO_DIRECTORY = "/home/george/drone/2020-03-30 55 Morilla Road/"
IR_PHOTO_DIRECTORY = "/home/george/Desktop/55 Morilla Road/"
OUT_DIRECTORY = "out/"

filenames = []
times = []
latitudes = []
longitudes = []
altitudes = []

def convert(pair):
	return pair[0]/pair[1]

def toDegrees(coord):
	return convert(coord[0]) + convert(coord[1])/60 + convert(coord[2])/3600

PRINT("Looking at mavic photos...")
for filename in sorted(os.listdir(MAVIC_PHOTO_DIRECTORY)):
	if filename.split(".")[-1].lower() != "jpg":
		continue
	full_filename = MAVIC_PHOTO_DIRECTORY + filename
	out_filename = OUT_DIRECTORY + filename

	# print("Looking at Mavic photo:", full_filename)

	filenames.append(full_filename)

	# print("################### EXIF ###################")

	#shutil.copy(full_filename, out_filename, follow_symlinks=True)

	img = Image.open(full_filename)

	exif_dict = piexif.load(img.info['exif'])

	capture_time = exif_dict['0th'][piexif.ImageIFD.DateTime].decode()
	# print("capture_time:", capture_time)
	# 2020:03:30 13:45:35
	capture_time_datetime = datetime.datetime.strptime(capture_time, "%Y:%m:%d %H:%M:%S")
	times.append(capture_time_datetime)

	GPS_altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
	# print("GPS_altitude:", convert(GPS_altitude))
	altitudes.append(convert(GPS_altitude))

	GPS_altitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef]
	# print("GPS_altitude_ref:", GPS_altitude_ref)

	GPS_latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
	# print(GPS_latitude)
	# print("GPS_latitude:", convert(GPS_latitude[0]), convert(GPS_latitude[1]), convert(GPS_latitude[2]))
	latitudes.append(toDegrees(GPS_latitude))

	GPS_latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef]
	# print("GPS_altitude_ref:", GPS_latitude_ref)

	GPS_longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
	# print(GPS_longitude)
	# print("GPS_longitude:", convert(GPS_longitude[0]), convert(GPS_longitude[1]), convert(GPS_longitude[2]))
	longitudes.append(toDegrees(GPS_longitude))

	GPS_longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef]
	# print("GPS_longitude_ref:", GPS_longitude_ref)

	# exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (140, 1)
	# exif_bytes = piexif.dump(exif_dict)
	# piexif.insert(exif_bytes, out_filename)

print(len(times), "images captured")

def timeToLat(capture_time):
	"""
	Takes a time
	Returns the actual lat and long of that time, and the file from just before the time
	"""
	# print("Checking against", capture_time)

	if capture_time in times:
		# print("Found exact match")
		i = times.index(capture_time)
		# print("Exactly", filenames[i])
		return latitudes[i], longitudes[i], altitudes[i], filenames[i]

	index1 = 0
	index2 = 0
	for i, reference_time in enumerate(times):
		if reference_time > capture_time:
			# print("Between", times[i-1], "and", times[i])
			index1 = i - 1
			index2 = i
			break

	if index1 <= 0 and index2 <= 0:
		# print("No time found")
		return None, None, None, None

	time1 = times[index1]
	time2 = times[index2]
	# print(time1, time2)
	time_diff = (time2 - time1).total_seconds()

	lat1 = latitudes[index1]
	lat2 = latitudes[index2]
	# print(lat1, lat2)
	lat_diff = lat2 - lat1

	long1 = longitudes[index1]
	long2 = longitudes[index2]
	# print(long1, long2)
	long_diff = long2 - long1

	altitude1 = altitudes[index1]
	altitude2 = altitudes[index2]
	# print(long1, long2)
	altitude_diff = altitude2 - altitude1

	# print(time_diff, lat_diff, long_diff)

	lat_m = lat_diff/time_diff
	long_m = long_diff/time_diff
	altitude_m = altitude_diff/time_diff

	delta_time = (capture_time - time1).total_seconds()
	delta_lat = delta_time * lat_m
	delta_long = delta_time * long_m
	delta_altitude = delta_time * altitude_m

	final_lat = lat1 + delta_lat
	final_long = long1 + delta_long
	final_altitude = altitude1 + delta_altitude

	# print("After", filenames[index1])
	# print("Before", filenames[index2])
	
	return final_lat, final_long, final_altitude, filenames[index1]

# test_time = datetime.datetime(2020, 3, 30, 13, 42, 57, 807011)
# print(timeToLat(test_time))

print("Looking at new photos...")
for filename in sorted(os.listdir(IR_PHOTO_DIRECTORY)):
	if filename.split(".")[-1].lower() != "jpg":
		continue
	full_filename = IR_PHOTO_DIRECTORY + filename
	out_filename = OUT_DIRECTORY + filename

	#print(out_filename)

	# print(full_filename)
	# 2020-03-30 13:51:21.766847
	this_file_time = ".".join(full_filename.split("/")[-1].split(".")[:-1]) # don't even worry about it
	this_file_time = datetime.datetime.strptime(this_file_time, "%Y-%m-%d %H:%M:%S.%f")

	lat, lng, alt, fname = timeToLat(this_file_time)

	if lat != None:
		# print(lat, lng, alt, fname)

		# Copy the IR file over
		shutil.copy(full_filename, out_filename, follow_symlinks=True)

		# Load the old image
		img = Image.open(fname)

		# Get the old exif
		exif_dict = piexif.load(img.info['exif'])

		# Get the new altitude
		alt1 = int(round(alt, 3) * 1000)
		alt2 = 1000

		# Get the new latitude
		lat1 = int(lat)
		lat2 = int((lat - lat1)*60)
		lat3 = int(round(10000 * (lat - lat1 - lat2/60) * 3600))
		# print(lat1, lat2, lat3)

		# Get the new latitude
		lng1 = int(lng)
		lng2 = int((lng - lng1)*60)
		lng3 = int(round(10000 * (lng - lng1 - lng2/60) * 3600))
		# print(lng1, lng2, lng3)

		# Create the EXIF
		exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (alt1, alt2)
		exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = ((lat1, 1), (lat2, 1), (lat3, 10000))
		exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = ((lng1, 1), (lng2, 1), (lng3, 10000))

		# Copy the exif over
		exif_bytes = piexif.dump(exif_dict)
		piexif.insert(exif_bytes, out_filename)

