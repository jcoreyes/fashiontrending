import urllib
import os
import sys

def get_images(input_file, output_folder):
	img_format = '.jpg'
	name = '00000'
	with open (input_file) as f:
		count = 0
		for line in f:
			print line
			path = os.path.join(output_folder, name + str(count) + '.' + img_format)
			urllib.urlretrieve(line, path)
			count += 1

			



if __name__ == '__main__':
	input_file = sys.argv[1]
	output_folder = sys.argv[2]
	get_images(input_file, output_folder)

