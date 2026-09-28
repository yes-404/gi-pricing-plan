#!/bin/bash
# usage: size.sh <frontend dir> <label>; prints raw and gzip byte totals of dist js+css
F=$1; L=$2
( cd $F && npx vite build >/dev/null 2>&1 ); rc=$?
raw=$(find $F/dist -name '*.js' -o -name '*.css' | xargs cat | wc -c)
gz=$(for f in $(find $F/dist -name '*.js' -o -name '*.css'); do gzip -9c $f | wc -c; done | awk '{s+=$1}END{print s}')
echo "$L rc=$rc raw=$raw gzip=$gz"
