#!/bin/sh
echo "uploading mp4s"
./upload.py --schedule http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml --recordings /video/fossgis14/ --extension mp4 --finished /video/fossgis14/uploaded/ --auphonic-login ./login --auphonic-preset PgeXpchzojrrgM25vVPw3U

echo "uploading webms"
./upload.py --schedule http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml --recordings /video/fossgis14/ --extension webm --finished /video/fossgis14/uploaded/ --auphonic-login ./login --auphonic-preset hqvsm8SCL3QmCYkCDhbm7T
