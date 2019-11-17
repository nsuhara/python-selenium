# Heroku + Selenium + ChromeでWEBプロセスを自動化する

- [Heroku + Selenium + ChromeでWEBプロセスを自動化する](#heroku--selenium--chrome%e3%81%a7web%e3%83%97%e3%83%ad%e3%82%bb%e3%82%b9%e3%82%92%e8%87%aa%e5%8b%95%e5%8c%96%e3%81%99%e3%82%8b)
  - [はじめに](#%e3%81%af%e3%81%98%e3%82%81%e3%81%ab)
    - [目的](#%e7%9b%ae%e7%9a%84)
    - [関連する記事](#%e9%96%a2%e9%80%a3%e3%81%99%e3%82%8b%e8%a8%98%e4%ba%8b)
    - [実行環境](#%e5%ae%9f%e8%a1%8c%e7%92%b0%e5%a2%83)
    - [ソースコード](#%e3%82%bd%e3%83%bc%e3%82%b9%e3%82%b3%e3%83%bc%e3%83%89)
  - [シナリオと前提条件](#%e3%82%b7%e3%83%8a%e3%83%aa%e3%82%aa%e3%81%a8%e5%89%8d%e6%8f%90%e6%9d%a1%e4%bb%b6)
  - [自動プロセスの作成](#%e8%87%aa%e5%8b%95%e3%83%97%e3%83%ad%e3%82%bb%e3%82%b9%e3%81%ae%e4%bd%9c%e6%88%90)
    - [Python API構成](#python-api%e6%a7%8b%e6%88%90)
    - [APIメインフレーム](#api%e3%83%a1%e3%82%a4%e3%83%b3%e3%83%95%e3%83%ac%e3%83%bc%e3%83%a0)
    - [FXレート取得](#fx%e3%83%ac%e3%83%bc%e3%83%88%e5%8f%96%e5%be%97)
  - [Herokuの設定](#heroku%e3%81%ae%e8%a8%ad%e5%ae%9a)
    - [ChromeとDriverの設定](#chrome%e3%81%a8driver%e3%81%ae%e8%a8%ad%e5%ae%9a)
    - [Driverバージョンの設定](#driver%e3%83%90%e3%83%bc%e3%82%b8%e3%83%a7%e3%83%b3%e3%81%ae%e8%a8%ad%e5%ae%9a)

## はじめに

Mac環境の記事ですが、Windows環境も同じ手順になります。環境依存の部分は読み替えてお試しください。

### 目的

この記事を最後まで読むと、次のことができるようになります。

- SeleniumとChromeDriverを使ってWEBプロセスを自動化する
- HerokuにChromeとDriverを設定する

`WEBプロセスの自動化`

Yahoo!ファイナンスのFXチャート・レートから**米ドル/円**を取得して表示する。

| ブラウザから手動で表示                                                                                                                                                               | 自動で取得したデータを表示                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <img width="400" alt="スクリーンショット 2019-11-17 16.21.49.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/6ad5419b-a901-06d9-a985-376ebae40f9b.png"> | <img width="400" alt="スクリーンショット 2019-11-17 0.33.50.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/8094825c-7ad6-d6de-bb98-2e48e08dd740.png"> |

### 関連する記事

- [Selenium](https://pypi.org/project/selenium/)
- [heroku-buildpack-chromedriver.git](https://github.com/heroku/heroku-buildpack-chromedriver.git)
- [heroku-buildpack-google-chrome.git](https://github.com/heroku/heroku-buildpack-google-chrome.git)

### 実行環境

| 環境          | Ver.         |
| ------------- | ------------ |
| macOS Mojave  | 10.14.6      |
| Python        | 3.7.3        |
| Flask         | 1.1.1        |
| selenium      | 3.141.0      |
| chromedrive   | 78.0.3904.70 |
| google-chrome | 78.0.3904.97 |

### ソースコード

実際に実装内容やソースコードを追いながら読むとより理解が深まるかと思います。是非ご活用ください。

[GitHub](https://github.com/nsuhara/python-selenium.git)

## シナリオと前提条件

1. Yahoo!ファイナンスのFXチャート・レートから**米ドル/円**を取得して表示する。
2. MySQLやPostgreSQLに保存することを想定していますが、自動化の説明を目的としますのでDB関連はスコープ外とします。
3. APIフレームワークはFlaskを採用します。

## 自動プロセスの作成

### Python API構成

```tree.sh
python-selenium
  ├── fx_rate
  │   ├── __init__.py
  │   └── utility.py
  └── main.py
```

### APIメインフレーム

```main.py
import datetime
import logging
import os

from flask import Flask

from fx_rate.utility import get_fx_rate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/fx-rate', methods=['GET'])
def get():
    usd_jpy = get_fx_rate()
    res = 'timestamp={}, USDJPY={}'.format(
        datetime.datetime.utcnow() + datetime.timedelta(hours=9), usd_jpy)
    logger.info(res)
    return res, 200


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)
```

### FXレート取得

```utility.py
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_fx_rate():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://info.finance.yahoo.co.jp/fx/')
    usd_jpy = driver.find_element(By.ID, 'USDJPY_top_bid').text
    driver.quit()
    return usd_jpy


if __name__ == '__main__':
    usd_jpy = get_fx_rate()
    print('timestamp={}, USDJPY={}'.format(datetime.datetime.utcnow() +
                                           datetime.timedelta(hours=9), usd_jpy))
```

## Herokuの設定

### ChromeとDriverの設定

Settings > Buildpacksセクションの**Add buildpack**から以下を追加します。

<img width="700" alt="スクリーンショット 2019-11-16 21.12.36.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/3767f0ec-f523-69e3-9be2-0879dce1bb78.png">

| Buildpack     | URL                                                          |
| ------------- | ------------------------------------------------------------ |
| chromedrive   | https://github.com/heroku/heroku-buildpack-chromedriver.git  |
| google-chrome | https://github.com/heroku/heroku-buildpack-google-chrome.git |

`Herokuへデプロイすると自動でインストールされます。事前にご登録ください。すでにデプロイ済みやソースコードを変更せずに再デプロイする場合は、以下の空コミットをお試しください。`

```allow_empty.sh
~$ git commit --allow-empty -m "allow empty commit"
~$ git push heroku master
```

### Driverバージョンの設定

通常は設定不要です。Chromeがバージョンアップしたときなど、**chromedrive**と**google-chrome**でバージョンが異なる場合は、**chromedrive**のバージョンを指定する必要があります。

1. Settings > Config Varsセクションの**Reveal Config Vars**をクリックします。
2. **KEY**と**VALUE**を入力して**Add**をクリックします。

<img width="700" alt="スクリーンショット 2019-11-16 21.12.25.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/07ab69cc-b1fd-85a4-c114-aa0308e6fea3.png">

| KEY                  | VALUE                                 |
| -------------------- | ------------------------------------- |
| CHROMEDRIVER_VERSION | サポートバージョン (例: 78.0.3904.70) |
