import cPickle
import shadow from shadow_words
from collections import defaultdict
import operator

# input_file: complete information about fashion posts
#   organized by blocks
# tag_by_block_file: a dict(1) of dict(2) of tags and counts of occurences for each tag
#   organized by blocks. key(1) = time, value(2) = dictionary
# tag_file: file holds stats gathered from information from tag_by_block_file

def dsum(*dicts):
    """
    Add all the keys and their values in each dictionary together

    :param array dicts: array of dictionaries to add
    :return: a single dictionary that is the sum of all the values 
        and includes all keys
    """
    ret = defaultdict(int)
    for d in dicts:
        for k, v in d.items():
            ret[k] += v
    return dict(ret)


def find_useful_tags(tag_dict, data):
    """
    Selects relevant tags from complete media information related to fashion

    :param dict tag_dict: dictionary to populate with tags and occurences
    :param str data: string to parse containing tags
    :return: none
    """
    # for tags (starts with "#") found in the info
    for tag in re.findall(r"\b#[\w]*", data):
        # if the word might be useful to us
        if tag.lower() not in shadow:
            # add to dictionary if not already there
            if tag not in tag_dict.keys():
                tag_dict[tag.lower()] = 1
            # increment the count if already there
            else:
                tag_dict[tag.lower()] += 1


def main():
    """
    Update the tag information using the new block of data that we receive
    """
    # only for visual aid for coding. wont be used for anything significant
    textfile = file('tag_crawler_output.txt','wt')

    # data is the info for all fashion related media posts
    input_data = cPickle.load(input_file)

    # load previous data
    tag_by_block_data = cPickle.load(tag_by_block_file)

    # if we don't have anything in the file, it must be our first time
    # loading the data.
    if tag_by_block_data == {}:
            block_tag_dict = {}
            # loop through all the blocks of data
            for block in tag_by_block_data.keys():
                find_useful_tags(block_tag_dict, input_data[block])
            tag_by_block_data[block] = block_tag_dict
    else:
        block_tag_dict = {}
        # only use the new block of memory
        find_useful_tags(block_tag_dict, input_data[newest])
        tag_by_block_data[newest] = block_tag_dict
    cPickle.dump( tag_by_block_data, tag_by_block_file)


    # add all the data from each day for a total data dictionary
    total_dict = dsum(tag_by_block_data)

    # sort the data over all blocks
    sorted_total_dict = sorted(total_dict.items(), key=operator.itemgetter(1))

    # dump the final result to save
    cPickle.dump(sorted_total_dict, tag_file)

    for key in sorted_total_dict:
        strr = str(sorted_total_dict[0]) + " , " + str(sorted_total_dict[1]) + "\n"
        textfile.write(strr)

    textfile.close()







