import re
from os.path import expanduser
                
def getTopItems(infile):
    topItems=[]
    fp = open(infile, 'r')
    for i, line in enumerate(fp):
        if 'popularitem_title' in line:
            listLine = re.split('"',line)
            topItems.append(listLine[-2])
    fp.close()
    return topItems


def writeMultiTrendData(topItemsFN = 'top32_mod.json'):
    # given specific tags, write a file with all time data for those tagss

    home = expanduser("~")
    DBPath = home + '/Dropbox/fp_website_dump/'
    sitePath = 'fp_website/'
    viewsPath ='views/public/'

    topItemsPath = DBPath + sitePath + topItemsFN
    timeCountsPath = DBPath + 'time_tag_counts.txt'
    
    topItems = getTopItems(topItemsPath)
    
    # set up file for multi-trend data 
    multiFile = open(DBPath + sitePath + viewsPath + 'multitrenddata.tsv', 'w')
    
    # start headline for multi-trend file
    multiHeader = 'datetime'

    for i in range(len(topItems)):
        multiHeader += '\t' + topItems[i]
    
    multiFile.write(multiHeader + '\n')
 
    with open(timeCountsPath, 'r') as f:
        for line in f:
            # split line into list using : and space as delimeters
            listLine = re.split('[:]|\s', line)
             
            # date for the line
            date = listLine[0]
            
            dataline = date[:]

            for i in range(len(topItems)):
                # add a delimiting tag, regardless of whether data exists for that time
                dataline += '\t'
                
                # if a top item is included in the line, add its data to the line
                if topItems[i] in listLine:
                    dataline += listLine[listLine.index(topItems[i]) + 1]
            
            # print this time's data to the file
            multiFile.write(dataline + '\n')

    multiFile.close()

     

 
#if __name__ == '__main__':
#    writeMultiTrendData('time_tag_counts.txt')
#    getItemTrends('time_tag_counts.txt')
