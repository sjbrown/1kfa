#! /bin/bash

set -e
if [ $DEBUG ]; then
  set -x
fi

# https://stackoverflow.com/questions/2013547/assigning-default-values-to-shell
: "${KFAREPO=/home/sjbrown/work/1kfa}"

source $KFAREPO/resolution_cards/version.py

cd /tmp/

mkdir -p /tmp/1kfa_playtest
rm -f 1kfa_playtest.tar.gz
rm -f 1kfa_playtest.tar
cp /tmp/1kfa_guide_build/1kfa_guide_*.pdf 1kfa_playtest/
cp /tmp/1kfa_guide_build/1kfa_guide_*.html 1kfa_playtest/
cp /tmp/1kfa_pnp_build/*.pdf 1kfa_playtest/
cp $KFAREPO/publish/playtest_thankyou.pdf 1kfa_playtest/
tar -c --exclude=*.svg -f 1kfa_playtest.tar 1kfa_playtest/
gzip 1kfa_playtest.tar

rm -f cards_v$VERSION.tar.gz
rm -f cards_v$VERSION.tar
tar -c --exclude=*.svg -f cards_v$VERSION.tar cards_v$VERSION
gzip cards_v$VERSION.tar

