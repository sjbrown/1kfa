#! /bin/bash

set -e

echo "Publish Web"

#------------------------------------------------------------------------------
# If the last commit had the word NODEPLOY in the commit msg, halt.
cd $KFAREPO
git log -1 |grep NODEPLOY && exit 2
#------------------------------------------------------------------------------

source $KFAREPO/resolution_cards/version.py
cd /tmp/
rm -rf deckahedron_site
git clone https://github.com/sjbrown/deckahedron_site.git
mkdir -p deckahedron_site/dist/$VERSION
cd deckahedron_site/dist/$VERSION
cp /tmp/*tar.gz ./

git add .
git config credential.helper 'cache --timeout=120'
git config user.email "sjbrown@geeky.net"
git config user.name "Circle CI Deployment Bot"
git commit --allow-empty -m "Automatic Circle CI build $CIRCLE_BUILD_URL"
git push -q https://${GITHUB_TOKEN}@github.com/sjbrown/deckahedron_site.git master

