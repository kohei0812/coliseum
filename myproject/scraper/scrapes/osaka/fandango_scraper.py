import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from ...models import Fandango  # モデルのインポート
import re
import logging

# ロガーの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def download_image_from_url(image_url):
    try:
        logger.debug(f"Attempting to access image page: {image_url}")

        # 画像ページにアクセス
        image_page_response = requests.get(image_url)
        image_page_response.raise_for_status()  # HTTPエラーをチェック

        # BeautifulSoupでページを解析
        image_page_soup = BeautifulSoup(image_page_response.text, 'html.parser')

        # 画像の実際のURLを取得（例えば、src属性が埋め込まれている場合）
        actual_image_url = image_page_soup.find('img')['src']  # imgタグからsrcを取得

        # 画像URLが絶対URLでない場合、相対URLを修正
        if not actual_image_url.startswith('http'):
            actual_image_url = requests.compat.urljoin(image_url, actual_image_url)

        # 実際の画像をダウンロード
        logger.debug(f"Downloading image from: {actual_image_url}")
        image_response = requests.get(actual_image_url, stream=True)
        image_response.raise_for_status()  # HTTPエラーをチェック

        return image_response.content  # 画像のバイナリデータを返す

    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing or downloading image from {image_url}: {e}")
        return None


def fandango_scraper():
    print("------------fandango start----------------")
    # 現在の月を取得
    current_month = datetime.now().month

    # URLを指定
    url = "https://www.fandango-japan.com/"
    response = requests.get(url)
    response.raise_for_status()

    # BeautifulSoupでHTMLを解析
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
        target_url = f"https://www.fandango-japan.com{next_month_link}"
        response = requests.get(target_url)
        response.raise_for_status()

        # 次の月のページを解析
        soup_next = BeautifulSoup(response.text, 'html.parser')

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
                    image_url = event['image']  # 画像URLが絶対URLの場合、そのまま使用
                    logger.debug(f"Attempting to download image from: {image_url}")

                    # 画像のページから画像をダウンロード
                    image_content = download_image_from_url(image_url)

                    if image_content:
                        # 拡張子を取得
                        ext = image_url.split('.')[-1]
                        image_name = f"{event_instance.title.replace(' ', '_')}.{ext}"  # ファイル名を作成
                        event_instance.image.save(image_name, ContentFile(image_content))  # 画像を保存
                        logger.info(f"Image saved for event '{event['title']}'")
                    else:
                        logger.error(f"Failed to download image for event '{event['title']}'")

                if created:
                    logger.info(f"Event '{event['title']}' created successfully")
                else:
                    logger.info(f"Event '{event['title']}' updated successfully")

            except Exception as e:
                logger.error(f"Error saving event '{event['title']}': {e}")
    print("------------fandango end----------------")