import time


def convert_timestamp(dt):
	return time.mktime(dt.timetuple())