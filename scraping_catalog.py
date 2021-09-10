import requests
import urllib.parse
import datetime
import csv
import argparse
from bs4 import BeautifulSoup

def parse_ckan(html_url):
    # 例 http://opendata.pref.toyama.jp/dataset/city_toyama_maidohaya_gtfs
    parsed_url = urllib.parse.urlparse(html_url)
    dataset_id = parsed_url.path.split('/')[-1] # -1で配列の最後の要素にアクセス
    # 例 http://opendata.pref.toyama.jp/api/3/action/package_show?id=city_toyama_maidohaya_gtfs
    json_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, '/api/3/action/package_show', '', 'id='+dataset_id, ''))

    json = requests.get(json_url).json()

    metadata_created  = json['result']['metadata_created']
    metadata_modified = json['result']['metadata_modified']
    author            = json['result']['author']
    title             = json['result']['title']
    notes             = json['result']['notes']
    license           = json['result']['license_id']

    # 現状の運用にあわせて、データは1つしか存在しないことを前提にする
    # 過去や将来データなどを扱うようになったら要変更
    resource = json['result']['resources'][0]

    resource_name    = resource['name']
    resource_url     = resource['url']
    resource_created = resource['created']

    return {
        'metadata_created': metadata_created,
        'metadata_modified': metadata_modified,
        'author': author,
        'title': title,
        'notes': notes,
        'license': license,
        'resource_name': resource_name,
        'resource_url': resource_url,
        'resource_created': resource_created
    }

def write_csv(all_data):
    now = datetime.datetime.now()
    filename = "toyama_gtfs_{0:%Y-%m-%d}.csv".format(now)

    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, ['organization','service_name','metadata_created','metadata_modified','author','title','notes','license','resource_name','resource_url','resource_created','trip_update_url','vehicle_position_url'])

        writer.writeheader()
        for data in all_data:
            writer.writerow(data)

def write_text(all_data):
    now = datetime.datetime.now()
    filename = "gtfs_list_{0:%Y-%m-%d}.txt".format(now)

    with open(filename, 'w') as f:
        for data in all_data:
            f.write(data['resource_url'])
            f.write('\n')

def main():
    parser = argparse.ArgumentParser(description='富山県GTFSファイル一覧をCSV形式で取得.')
    parser.add_argument('--static_list', action='store_true', default=False, help='GTFS一覧URLを記述したtxtファイルを出力する')
    args = parser.parse_args()

    # スクレイピング対象の URL にリクエストを送り HTML を取得する
    res = requests.get('http://opendata.pref.toyama.jp/pages/gtfs_jp.htm')
    res.encoding = res.apparent_encoding  # 文字コードを自動判定して設定（富山県ページはShiftJIS）

    soup = BeautifulSoup(res.text, 'html.parser')

    all_data = []
    pre_organization = '' # organizationはコラムが結合されているので、空白の場合は上の欄の値を設定する
    for agency in soup.find_all('tr'):
        if agency['style'] == 'display:none':
            # GTFSの公開をやめたデータはdisplay:noneとなっている
            # 例：富山港線フィーダーバスGTFSは地鉄バスのGTFSに統合されたため公開終了
            #    入善新幹線ライナーは運休中のため公開中止
            continue

        texts = [td.get_text() for td in agency.find_all('td')]
        links = [url.get('href') for url in agency.find_all('a')]
        # タイトル部分から全てが一つのテーブルになっている
        # 良い方法ではないが、classなども設定されていないため、
        # データが入力されている列を判別するために要素数、リンク数を使っている
        if(len(texts) == 6 and len(links) == 3):
            organization = texts[1].strip()
            service_name = texts[2].strip()
            gtfs_page_url        = links[0]
            trip_update_url      = links[1]
            vehicle_position_url = links[2]

            #organizationコラムが連結されているため、空白の場合は前の値を設定する
            if len(organization) > 0:
                pre_organization = organization
            else:
                organization = pre_organization

            gtfs_data = parse_ckan(gtfs_page_url)

            data ={
                'organization': organization,
                'service_name': service_name,
                'trip_update_url': trip_update_url,
                'vehicle_position_url': vehicle_position_url
            }
            data.update(gtfs_data)

            all_data.append(data)
            print('Download: {}, {}'.format(organization, service_name))

    if args.static_list:
        write_text(all_data)
    else:
        write_csv(all_data)

if __name__ == '__main__':
    main()
