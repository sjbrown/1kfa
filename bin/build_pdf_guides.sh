#! /bin/bash

set -e
set -o xtrace

# Resolve repo root relative to this script's location
KFAREPO="$(cd "$(dirname "$0")/.." && pwd)"

PUBLISH=$KFAREPO/publish

BUILDDIR=/tmp/1kfa_guide_build
rm -rf $BUILDDIR
mkdir $BUILDDIR
cp -a $KFAREPO/images $BUILDDIR/images
cp $PUBLISH/*.pdf $BUILDDIR/

mkdir -p ~/.fonts/
cp $KFAREPO/fonts/*.[ot]tf ~/.fonts/

cd $KFAREPO

SRC_PLAYER=$BUILDDIR/mod_guide_player.md
cp $KFAREPO/mod_guide_player.md $SRC_PLAYER
SRC_GM=$BUILDDIR/mod_guide_gm.md
cp $KFAREPO/mod_guide_gm.md $SRC_GM

DATE=$(date -I)
source $KFAREPO/resolution_cards/version.py

sed --in-place -e "s/VERSION/$VERSION/" $SRC_PLAYER
sed --in-place -e "s/VERSION/$VERSION/" $SRC_GM

python3 $KFAREPO/bin/preprocess_guides.py $SRC_PLAYER
python3 $KFAREPO/bin/preprocess_guides.py $SRC_GM

#-s                puts the utf-8 header in
#--self-contained  puts data: URLs in
#-t html           to HTML
pandoc \
 --from=markdown+line_blocks \
 -s \
 --self-contained \
 --include-in-header=$PUBLISH/tracking.html \
 --toc \
 -t html \
 --css=$PUBLISH/markdown.css \
 --metadata pagetitle="1kFA Player Guide" \
 $SRC_PLAYER -o $BUILDDIR/1kfa_guide_player.html

pandoc \
 --from=markdown+line_blocks \
 -s \
 --self-contained \
 --include-in-header=$PUBLISH/tracking.html \
 --toc \
 -t html \
 --css=$PUBLISH/markdown.css \
 --metadata pagetitle="1kFA GM Guide" \
 $SRC_GM -o $BUILDDIR/1kfa_guide_gm.html

cd $BUILDDIR

cat $PUBLISH/frontmatter_player.yml $SRC_PLAYER > $BUILDDIR/player_pdf_src.md
pandoc \
  $BUILDDIR/player_pdf_src.md --pdf-engine=xelatex \
  --from=markdown+line_blocks \
  -o $BUILDDIR/1kfa_guide_player.pdf

cat $PUBLISH/frontmatter_player_phone.yml $SRC_PLAYER > $BUILDDIR/player_phone_pdf_src.md
pandoc \
  $BUILDDIR/player_phone_pdf_src.md --pdf-engine=xelatex \
  --from=markdown+line_blocks \
  -o $BUILDDIR/1kfa_guide_player_phone.pdf

cat $PUBLISH/frontmatter_gm.yml $SRC_GM > $BUILDDIR/gm_pdf_src.md
pandoc \
  $BUILDDIR/gm_pdf_src.md --pdf-engine=xelatex \
  --from=markdown+line_blocks \
  -o $BUILDDIR/1kfa_guide_gm.pdf

cat $PUBLISH/frontmatter_gm_phone.yml $SRC_GM > $BUILDDIR/gm_phone_pdf_src.md
pandoc \
  $BUILDDIR/gm_phone_pdf_src.md --pdf-engine=xelatex \
  --from=markdown+line_blocks \
  -o $BUILDDIR/1kfa_guide_gm_phone.pdf
