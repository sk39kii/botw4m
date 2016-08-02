# botw4m

LINE BOTをTornadoで動かしてみる。

## 概要
BOTが巷で流行っているので、LINEの「BOT API Trial Account」に申し込んだ。  
せっかくなのでWebサーバ側はノンブロッキングWebに興味があったのでTornadoを使ってみることにした。


## 前準備
### Botサーバ
PythonとTornadoをインストールしておく。
* Python 3.5.2
* Tornado 4.3  

※他の環境は未検証

```sh
pip install tornado
```

### LINE BOT
LINE BOTのチャンネル設定でコールバックURLを指定。
* Callback URL
```
https://<your bot server domain>:443/callback/
```

### 動かす前の準備

* LINE BOTのChannelID、ChannelSecret、MIDを実際の値に書き換える(server.py L26付近)
* Toronado内でSSL証明書の読み込みを辺りで行っている(server.py L245付近)。  
実物のSSL証明書をconfig配下に設置する。(今回はStartSSLを使用した)

## 使い方
### 起動と停止

起動
```sh
python server.py
```
停止
```
Ctrl + c
```

### ターミナルを閉じても動かしておきたい場合
起動
```sh
nohup ./start.sh > 標準出力ログ 2> エラーログ < /dev/null &

例：
nohup ./start.sh > log/out.log 2> log/err.log < /dev/null &
```

停止はプロセルをkillする


## その他
### 動かしてわかったこと
* BOTサーバが起動してなくてもクライアントからメッセージ送ると既読になる
* 人前で見せて使ってもらう場合は、一度PC版のLINEなどで操作デモを見せてから、使ってもらった方が伝わりやすい


### 課題・検討
* 複数人で一斉に使うと応答が返ってこない場合があるのでレスポンスを速くする  
(APIアクセスを減らす、DB周り、tornadoのマルチプロセス化など)
* イベント通知に複数件含まれている場合の応答
* ログ出力周りの整理(現在printデバッグ)
* Profiles APIへのアクセスが非同期になってない
* 現在はメッセージのやり取りのみ対応
* 応答内容を一つのPythonスクリプト内に書いている  
※別に分けた方が拡張しやすい。(それこそ別に分けてWebAPI化し、このBOTはその間の連携係にするなど)
* 応答機能(コンテンツ)の拡充
* カウントゲーム内の数字を送る時に全角数字の対応
