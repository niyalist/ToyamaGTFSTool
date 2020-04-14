import sys
import shutil
from pathlib import Path

# ZIPを解凍した中にさらにディレクトリが作られているので、それを削除する
def fix_nanto(nanto_dir):
    inner_dir = [files for files in nanto_dir.iterdir()]
    if len(inner_dir) == 1 and inner_dir[0].is_dir():
        for file in inner_dir[0].glob('*'):
            new_file = Path(nanto_dir, file.name)
            print("{} to {}".format(file, new_file))
            file.rename(new_file)
        inner_dir[0].rmdir()

# stop_times.txt から trip_id が以下を含むものを削除
# "－_08時00分_系統53111" "－_12時40分_系統53112"
# tripsとstop_timesから service_id が"特別ダイヤ１"であるものを削除
def fix_kaetsunou_ippan(ippan_dir):

    stop_times = Path(ippan_dir, "stop_times.txt")
    keywords = ["－_08時00分_系統53111", "－_12時40分_系統53112", "特別ダイヤ１"]
    delete_line_with_keywords(stop_times, keywords)

    trips = Path(ippan_dir, "trips.txt")
    delete_line_with_keywords(trips, ["特別ダイヤ１"])

# tripsとstop_timesから service_id が以下を含むものを削除
# ["－_07時10分_系統54181", "－_08時10分_系統54181", "－_09時15分_系統54182", "－_10時15分_系統54182", "－_11時05分_系統54181", "－_12時45分_系統54181", "－_12時50分_系統54182", "－_15時35分_系統54182"]
def fix_kaetsunou_sekaiisan(sekaiisan_dir):
    stop_times = Path(sekaiisan_dir, "stop_times.txt")
    keywords = ["－_07時10分_系統54181", "－_08時10分_系統54181", "－_09時15分_系統54182", "－_10時15分_系統54182", "－_11時05分_系統54181", "－_12時45分_系統54181", "－_12時50分_系統54182", "－_15時35分_系統54182"]
    delete_line_with_keywords(stop_times, keywords)

    trips = Path(sekaiisan_dir, "trips.txt")
    delete_line_with_keywords(trips, keywords)



def delete_line_with_keywords(file, keywords):
    new_data = []
    with open(file, "r", encoding="utf_8_sig") as f:
        for line in f:
            contain = False
            for keyword in keywords:
                if keyword in line:
                    contain = True
                    print(line)
            if not contain:
                new_data.append(line)

    with open(file, "w", encoding="utf_8_sig") as f:
        for line in new_data:
            f.write(line)



def main(uncompressed_dir):
    uncompressed_path = Path(uncompressed_dir)
    nanto_path = uncompressed_path.glob('*city_nanto_gtfs*')
    kaetsunou_ippan_path = uncompressed_path.glob('*kaetsunou_gtfs_ippan*')
    kaetsunou_sekaiisan_path = uncompressed_path.glob('*kaetsunou_gtfs_sekaiisan*')

    for nanto in nanto_path:
        fix_nanto(nanto)

    for ki in kaetsunou_ippan_path:
        fix_kaetsunou_ippan(ki)

    for ks in kaetsunou_sekaiisan_path:
        fix_kaetsunou_sekaiisan(ks)

#zipファイルの中身を、zipファイル名のディレクトリ内に解凍した状態を想定
if __name__ == '__main__':
    args=sys.argv
    main(args[1])
