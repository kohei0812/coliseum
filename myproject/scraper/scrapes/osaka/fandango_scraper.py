import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from ...models import Fandango  # Use the correct model name
import re

def fandango_scraper():
    # 現在の月を取得
    current_month = datetime.now().month

    # URLを指定
    url = "https://www.fandango-japan.com/"

    # HTMLを取得
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 来月のリンクを取得
    next_month = current_month + 1 if current_month < 12 else 1
    next_month_link = None

    def fullwidth_to_halfwidth(text):
        # 全角数字を対応する半角数字に変換
        fullwidth_numbers = '０１２３４５６７８９'
        halfwidth_numbers = '0123456789'
        translation_table = str.maketrans(fullwidth_numbers, halfwidth_numbers)
        return text.translate(translation_table)

    # グローバルナビゲーションのリストを検索
    nav_items = soup.select('.global-nav__list .global-nav__item a')

    for item in nav_items:
        # 各リンクテキストを全角から半角に変換
        link_text = fullwidth_to_halfwidth(item.text)
        if f"SCHEDULE（{next_month:02}月）" in link_text:
            next_month_link = item['href']  # 見つかったらリンクを取得
            break

    # next_month_linkが見つかった場合に処理を実行

    if next_month_link:
        # ターゲットURLにリクエストを送信
        target_url = f"https://www.fandango-japan.com{next_month_link}"  # ベースURLを付加
        response_next = requests.get(target_url)
        soup_next = BeautifulSoup(response_next.text, 'html.parser')

        # イベント情報を格納するリスト
        events = []

        # 必要な情報を抽出
        event_blocks = soup_next.select('.page__main .block__outer')  # 具体的なCSSセレクタは必要に応じて調整
        for block in event_blocks:
            date_elem = block.select_one('.block-txt p:nth-child(1)')  # 日付
            title_elem = block.select_one('.block-txt p:nth-child(2)')  # タイトル
            performers_elem = block.select_one('.block-txt p:nth-child(4)')  # 出演者
            content_elem = block.select_one('.block-txt p:nth-child(5)')  # 内容
            image_elem = block.select_one('.block-type--image img')  # 画像

            # データの取得
            if date_elem and title_elem and performers_elem and content_elem:
                raw_date = date_elem.text.strip()  # '2024.11/1(金)' 形式

                # 正規表現を使って日付を抽出
                match = re.match(r'(\d{4})\.(\d{1,2})/(\d{1,2})\(.+?\)', raw_date)
                if match:
                    year, month, day = match.groups()  # 年、月、日を取得

                    # 日付オブジェクトを作成
                    event_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")

                    # イベント情報の辞書を作成
                    event = {
                        'date': event_date,  # datetimeオブジェクトを格納
                        'title': title_elem.text.strip(),
                        'performers': performers_elem.text.strip(),
                        'content': content_elem.text.strip(),
                        'image': image_elem['src'] if image_elem else None
                    }
                    events.append(event)

        # データベースに保存するための処理
        for event in events:
            # データベースに保存
            try:
                # update_or_createを使用して、既存のデータがあれば上書き
                event_instance, created = Fandango.objects.update_or_create(
                    date=event['date'],
                    defaults={
                        'title': event['title'],
                        'performers': event['performers'],
                        'content': event['content'],
                    }
                )

                # 画像の保存処理
                if event['image']:
                    image_url = urljoin(target_url, event['image'])  # 相対URLをフルURLに変換

                    # 既に画像が保存されているか確認
                    if not event_instance.image:
                        image_response = requests.get(image_url, stream=True)
                        
                        if image_response.status_code == 200:
                            ext = image_url.split('.')[-1]  # 拡張子を取得
                            image_name = f"{event_instance.title.replace(' ', '_')}.{ext}"  # ファイル名を作成
                            event_instance.image.save(image_name, ContentFile(image_response.content))  # 画像を保存
                            print(f"Image saved for event '{event['title']}'")
                        else:
                            print(f"Image could not be fetched from {image_url}")
                    else:
                        print(f"Image already exists for event '{event['title']}', skipping save.")

                if created:
                    print(f"Event '{event['title']}' created successfully")
                else:
                    print(f"Event '{event['title']}' updated successfully")

            except Exception as e:
                print(f"Error saving event '{event['title']}': {e}")
