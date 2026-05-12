#! /bin/bash

set -e

echo "Publish Web"

python bin/generate_quickstart_json.py mod_guide_table.md mod_guide_player.md mod_guide_gm.md

cp companion_app/*.* /tmp/1kfa_companion_app/

echo ""
echo "Now to see it run:"
echo "  cd /tmp/1kfa_companion_app/; python3 -m http.server"
echo ""

read -p "Push (rclone) to Cloudflare? (y/n)?" choice
case "$choice" in
  y|Y ) echo "Continuing...";;
  n|N ) exit 0;;
  * ) echo "invalid";;
esac

echo "rclone copy /tmp/1kfa_companion_app/ r2:apps-1kfa-com/companion/"
rclone copy /tmp/1kfa_companion_app/ r2:apps-1kfa-com/companion/

echo ""
echo " OPTIONALLY"
echo "publish from ~/work/togetherness/publish_to_cloudflare.sh"
echo ""
echo "Then sync www_1kfa_com"
