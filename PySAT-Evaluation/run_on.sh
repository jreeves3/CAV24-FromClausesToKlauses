for file in encs-10/*
do
echo $file

./cadical-ple/cadical/build/cadical $file -c 0 -o temp.cnf --ple=1 > /dev/null

./Extractor/cnf2knf/cnf2knf --Write_KNF=true  temp.cnf | grep "^k"

./binaries/coprocessor-merge_bin  -verb=2 -search=0 -enabled_cp3 -cp3_stats  -cp3_fm_printproof=3 -cp3_fm_proof -no-xor -no-dense -no-unhide -no-bve -no-ee -no-bce -no-inprocess temp.cnf > temp.log 2>&1 
cat temp.log

./binaries/lingeling_bin -s -v -v -v temp.cnf  > temp.log
cat temp.log


echo
echo 

rm temp.cnf

done
