src_file=$1
sort -u -k9 -t"|" $src_file > $src_file".sorted"
grep -v True $src_file".sorted" | grep -v "|-1" > $src_file".filtered"  # remove unfound/closed restaurants
