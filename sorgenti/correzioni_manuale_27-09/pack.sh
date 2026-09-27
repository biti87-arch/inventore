#!/bin/bash
# pack.sh <dir> <out.docx>
set -e
out=$(realpath -m "$2"); rm -f "$out"
cd "$1" && zip -q -X -0 "$out" '[Content_Types].xml' && zip -q -X -r -9 "$out" . -x '[Content_Types].xml'
