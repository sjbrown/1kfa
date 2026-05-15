#! /bin/bash

set -e

echo "Publish Web"

OUTDIR="/tmp/1kfa_companion_app/"

python bin/generate_quickstart_json.py mod_guide_table.md mod_guide_player.md mod_guide_gm.md

cp companion_app/*.* $OUTDIR

echo ""
echo "Now to see it run:"
echo "  cd $OUTDIR; python3 -m http.server"
echo ""

read -p "Push (rclone) to Cloudflare? (y/n)?" choice
case "$choice" in
  y|Y ) echo "Continuing...";;
  n|N ) exit 0;;
  * ) echo "invalid";;
esac

echo "rclone copy $OUTDIR r2:apps-1kfa-com/companion/"
rclone copy "$OUTDIR" r2:apps-1kfa-com/companion/

echo ""
echo " OPTIONALLY"
echo "publish from ~/work/togetherness/publish_to_cloudflare.sh"
echo ""
echo "Then sync www_1kfa_com"
