from pathlib import Path
import sys
import csv
import shutil

file_info = {
    'agency.txt':     {'table': 'agency',     'id': 'agency_id',  'subid': ''},
    'stops.txt':      {'table': 'stops',      'id': 'stop_id',    'subid': ''},
    'routes.txt':     {'table': 'routes',     'id': 'route_id',   'subid': ''},
    'trips.txt':      {'table': 'trips',      'id': 'trip_id',    'subid': ''},
    'stop_times.txt': {'table': 'stop_times', 'id': 'trip_id',    'subid': 'stop_sequence'},
    'pathways.txt':   {'table': 'pathways',   'id': 'pathway_id', 'subid': ''},
    'levels.txt':     {'table': 'levels',     'id': 'level_id',   'subid': ''}
}

def generate_translation_dictionary(translation_file):
    dictionary = {}
    #utf_8_sig はBOM付きUTF-8を指定。BOMがない場合もそのまま処理されるらしい（未確認）
    with open(translation_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'trans_id' not in row:
                print("translations.txt dosn't contain [trans_id].")
                return {}
            # setdefaultで、要素がない場合はlistを新たに追加
            # list内に、ja, ja-Hrkt, en などが含まれることになる
            element_list = dictionary.setdefault(row['trans_id'], [])
            element_list.append({'lang': row['lang'], 'translation': row['translation']})

    return dictionary

def apply_translation(gtfs_dir, dictionary):
    translations = []
    for file in gtfs_dir.glob("*.txt"):
        if file.name in file_info:
            print("analyze: {}".format(file.name))
            with open(file, "r", encoding="utf_8_sig") as f:
                reader = csv.DictReader(f)
                for row in reader:  
                    for field_name, value in row.items():
                        if field_name.endswith(('_name','_desc','_url','_headsign')):
                            if(len(value) > 0 and value in dictionary):
                                translation = dictionary[value]
                                table_name    = file_info[file.name]['table']
                                record_id     = row[file_info[file.name]['id']]
                                record_sub_id = row[file_info[file.name]['subid']] if file_info[file.name]['subid'] in row else ''
#                                print("{}: {}".format(field_name, value))
#                                print(translation)
#                                print("table_name: {}, filed_name: {}, record_id: {}, sub_id: {}".format(table_name, field_name, record_id, record_sub_id))
                                for trans in dictionary[value]:
                                    language = trans['lang']
                                    translation = trans['translation']
                                    translations.append({
                                        "table_name": table_name,
                                        "field_name": field_name,
                                        "language": language,
                                        "translation": translation,
                                        "record_id": record_id,
                                        "record_sub_id": record_sub_id
                                    })
    return translations

def backup_translation_file(gtfs_dir):
    print("backup")
    original_translation_file = Path(gtfs_dir,"translations.txt")
    backup_translation_file = Path(gtfs_dir,"translations.original")
    shutil.copy2(original_translation_file, backup_translation_file)


def write_csv(file, data, bom=False):
    encoding = 'utf-8-sig' if bom else 'utf-8'    
    with open(file, 'w', encoding=encoding) as f:
        writer = csv.DictWriter(f, ["table_name", "field_name", "language", "translation", "record_id", "record_sub_id"])
        writer.writeheader()
        for data in data:
            writer.writerow(data)

def has_bom(filename):
    ''' utf-8 ファイルが BOM ありかどうかを判定する
        thanks https://www.lifewithpython.com/2017/10/python-detect-bom-in-utf8-file.html
    ''' 
    line_first = open(filename, encoding='utf-8').readline()
    return (line_first[0] == '\ufeff')


def main(gtfs_dir):
    gtfs_path = Path(gtfs_dir)
    translation_file = Path(gtfs_path,"translations.txt")
    if not translation_file.exists():
        print("translations.txt is not exist.")
        return
    dictionary = generate_translation_dictionary(translation_file)    
    if(len(dictionary)) <= 0:
        print("no content in the translations.txt.")
        return
    translations = apply_translation(gtfs_path, dictionary)
    backup_translation_file(gtfs_path)
    file_has_bom = has_bom(translation_file)
    write_csv(translation_file, translations, file_has_bom)
        

if __name__ == '__main__':
    args=sys.argv
    main(args[1])
