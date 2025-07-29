import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ...models import Tora  # あなたのモデルに合わせて調整

def tora_scraper():
    print("------------tora api start----------------")
    
    API_URL = "https://live-tora.com/wp-json/wp/v2/posts"
    today = datetime.today().date()
    page = 1

    while True:
        # 投稿一覧を _embed 付きで取得（画像情報を含める）
        response = requests.get(
            f"{API_URL}?per_page=100&page={page}&_embed&_fields=id,date,title,content,_embedded"
        )

        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            break

        posts = response.json()
        if not posts:
            break  # データがなければ終了

        for post in posts:
            try:
                # イベント日付（datetime型 → date型）
                event_date = datetime.fromisoformat(post["date"]).date()
                if event_date <= today:
                    continue  # 過去の日付はスキップ

                # タイトル
                title = post["title"]["rendered"].strip()

                # 本文（HTMLをプレーンテキストに変換）
                content_html = post["content"]["rendered"]
                soup = BeautifulSoup(content_html, "html.parser")
                content = soup.get_text(separator="\n", strip=True)

                # アイキャッチ画像のURL取得（_embedded経由）
                image_url = None
                embedded = post.get("_embedded", {})
                media = embedded.get("wp:featuredmedia", [])
                if media:
                    image_url = media[0].get("source_url")
                else:
                    # fallback: 本文内の画像を使う
                    img_tag = soup.find("img")
                    if img_tag and img_tag.get("src"):
                        image_url = img_tag["src"]
                    else:
                        print(f"No featured image or inline image for post ID {post['id']}")
                # 保存（imageはURLとして保存する前提。Djangoモデルで image_url フィールドを使ってください）
                event, created = Tora.objects.update_or_create(
                    date=event_date,
                    defaults={
                        "title": title,
                        "content": content,
                        "image_url": image_url,  # URLFieldを使用すること
                    }
                )

                print(f"{'Created' if created else 'Updated'}: {title} ({event_date})")

            except Exception as e:
                print(f"Error processing post: {e}")

        page += 1  # 次のページへ

    print("------------tora api end----------------")
