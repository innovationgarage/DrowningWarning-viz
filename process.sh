FILES=data/first/*.txt
for f in $FILES
do
    echo "Processing "$f" file..."
    python clean_data.py --ti data/first/telespor.csv --to data/first/telespor_clean.csv --ci $f --co $f.clean.csv --allout $f.merged.csv --starttime "2019-10-11 10:17:00"
done
cp data/first/capture_246058.txt.merged.csv all_data_1.csv

# FILES=data/second/*.txt
# for f in $FILES
# do
#     echo "Processing "$f" file..."
#     python clean_data.py --ti data/second/telespor.csv --to data/second/telespor_clean.csv --ci $f --co $f.clean.csv --allout $f.merged.csv --starttime "2019-10-22 16:34:00" 
# done
# cp data/second/capture_864481.txt.merged.csv all_data_2.csv
