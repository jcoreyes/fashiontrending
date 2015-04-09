from crawler_loop import * 

def main():
	tag_dict = {}
	textfile = file('tag_crawler_output.txt','wt')
	
	# loop this part
	media_info = get_info()
	get_tags(media_info, tag_dict)
	for key in tag_dict.keys():
		strr = str(key) + " , " + str(tag_dict[key]) + "\n"
		textfile.write(strr)

	textfile.close()

if __name__ == "__main__":
    main()


