#! /bin/bash

set -e

# https://stackoverflow.com/questions/2013547/assigning-default-values-to-shell
: "${KFAREPO=/home/sjbrown/work/1kfa}"
source $KFAREPO/resolution_cards/version.py # populate VERSION variable

LOGFILE=/tmp/1kfa_check_deploy.log

function check {
  echo $1 >> $LOGFILE
  curl --silent --head $1 | egrep "(HTTP|etag)" >> $LOGFILE
  echo "" >> $LOGFILE
}

rm -rf $LOGFILE
touch $LOGFILE
check https://www.1kfa.com/playtest_files/index.html
check https://www.1kfa.com/playtest_files/1kfa_playtest.tgz
check https://www.1kfa.com/playtest_files/1kfa_guide_player.html
check https://www.1kfa.com/assets/cards_v$VERSION/index.html

cat $LOGFILE

echo ""
echo "Errors:"
grep HTTP $LOGFILE  | grep -v 200

