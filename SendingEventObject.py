# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__status__ = 'development'
__date__ = '18 July 2016'

from ContentObject import ContentObject
from DatabaseUtil import DatabaseUtil
from MessageObject import MessageObject
from OperationObject import OperationObject
import random
import re

class SendingEventObject(object):
    u"""BOTからPOST EVENT APIを使って送信するイベント(Sending Event Object)
    """
    # コンテンツの種別
    CONTENTTYPE_TEXT = 1
    CONTENTTYPE_IMAGE = 2
    CONTENTTYPE_VIDEO = 3
    CONTENTTYPE_AUDIO = 4
    CONTENTTYPE_LOCATION = 7
    CONTENTTYPE_STICKER = 8
    CONTENTTYPE_CONTACT = 10
    CONTENTTYPE_RICHMESSAGE = 12
    # 定数
    TOCHANNEL = "1383378250"
    EVENTTYPE = "138311608800106203"

    # カウントゲーム関連
    COUNTGAME_ANSER0 = ["先攻", "後攻"]
    COUNTGAME_ANSER1 = ["1", "2", "3"]
    COUNTGAME_ANSER9 = ["ゲームやめる"]
    COUNTGAME_ANSER = COUNTGAME_ANSER0 + COUNTGAME_ANSER1 + COUNTGAME_ANSER9
    STATUS_COUNTGAME_NO = -1        # カウントゲームしてない
    STATUS_COUNTGAME_SELECT = 0     # カウントゲーム先攻後攻回答待ち
    STATUS_COUNTGAME_YES = 1        # カウントゲーム中

    def __init__(self,reo):
        self.db = None

        # 以下、メッセージ関連
        # 送信先のChannel ID
        self.toChannel = self.TOCHANNEL
        # イベントタイプ
        self.eventType = self.EVENTTYPE
        self.to = None
        self.content = None
        # 受信イベントによって返却内容を決定
        if reo.isEventTypeMessage():
            # イベント通知
            # 送信先ユーザーの識別子を指定
            # ※Array of Strings（配列 (最大150)）だが配列にしなくてもよさげ？
            # MessageObjectsの_fromはString
            self.to = reo.content._from
            # 種別に合わせて送信用コンテンツの作成
            if reo.content.iscontentTypeText():
                self.content = self.createSendContent_Text(reo.content)
                # self.createSendContent_Text(reo.content)
            elif reo.content.iscontentTypeImage():
                self.content = self.createSendContent_Image(reo.content)
            elif reo.content.iscontentTypeVideo():
                self.content = self.createSendContent_Video(reo.content)
            elif reo.content.iscontentTypeAudio():
                self.content = self.createSendContent_Audio(reo.content)
            elif reo.content.iscontentTypeLocation():
                self.content = self.createSendContent_Location(reo.content)
            elif reo.content.iscontentTypeSticker():
                self.content = self.createSendContent_Sticker(reo.content)
            elif reo.content.iscontentTypeContact():
                self.content = self.createSendContent_RichMessage(reo.content)

        elif reo.isEventTypeOperation():
            # ユーザ操作
            # 送信先ユーザーの識別子を指定
            self.to = reo.content.params[0]

    def createSendContent_Text(self, reo_content):
        u"""送信用コンテンツオブジェクト(Text)の作成
        ※イベント通知の返信で使用
        """
        # 事前定義
        commands = self.createCommand()
        responseMsg = "ご用でしょうか？"

        # ユーザがゲーム中か判定
        status, currentCounter = self.getCountGameStatus(reo_content)
        if status == self.STATUS_COUNTGAME_NO:
            # 通常モード(ゲームしてない)通知内容とマッチングした返却内容
            for mach, func in commands:
                if mach.search(reo_content.text):
                    responseMsg = func(reo_content)
                    break
        elif status == self.STATUS_COUNTGAME_SELECT:
            # ゲーム中(先攻後攻回答待ち)
            if reo_content.text in self.COUNTGAME_ANSER0:
                responseMsg = self.resAnser_game0(reo_content, currentCounter)
            elif reo_content.text in self.COUNTGAME_ANSER9:
                responseMsg = self.resAnser_gameend(reo_content)
            else:
                responseMsg = "ゲーム中は以下の回答しか受け付けません。\n"
                responseMsg += "「先攻」、「後攻」、「ゲームやめる」"
        elif status == self.STATUS_COUNTGAME_YES:
            # ゲーム中
            if reo_content.text in self.COUNTGAME_ANSER1:
                responseMsg = self.resAnser_game1(reo_content, currentCounter)
            elif reo_content.text in self.COUNTGAME_ANSER9:
                responseMsg = self.resAnser_gameend(reo_content)
            else:
                responseMsg = "ゲーム中は以下の回答しか受け付けません。\n"
                responseMsg += "「1」、「2」、「3」、「ゲームやめる」"
        else:
            # イレギュラー
            # 通常モード扱い
            for mach, func in commands:
                if mach.search(reo_content.text):
                    responseMsg = func(reo_content)
                    break

        return ContentObject().setContent_Text(responseMsg)

    def getCountGameStatus(self, reo_content):
        u"""ユーザがゲーム中かどうかステータス取得
        ※ついでにカウンター値も取得
        """
        status = self.STATUS_COUNTGAME_NO
        counter = 0
        try:
            # テーブルは事前に作成しておく
            if not db.checkDuplicate("CountGameRoomTbl"):
                # Table Create
                self.execQuery_CountGameRoomTbl('create', None)

            result = self.execQuery_CountGameRoomTbl(
                'select', {"player": reo_content._from}
            )
            for rec in result:
                status = rec[2]
                counter = rec[3]
        except Exception as e:
            print("Error: " + str(e))
        finally:
            pass
        if isinstance(status, str):
            status = int(status)
        if isinstance(counter, str):
            counter = int(status)
        return status, counter

    def execQuery_CountGameRoomTbl(self, s, d=None):
        u"""テーブル操作(CountGameRoomTbl)
        """
        sql = ""
        if s == 'create':
            sql = """
            create table CountGameRoomTbl(
              id TEXT
            , player TEXT
            , status INTEGER
            , counter INTEGER
            , time_stamp DEFAULT CURRENT_TIMESTAMP
            , PRIMARY KEY(id, player));
            """
        elif s == 'insert':
            sql = """
            insert into CountGameRoomTbl(id, player, status, counter)
            values (:id, :player, :status, :counter);
            """
        elif s == 'update':
            sql = """
            update CountGameRoomTbl
               set status = :status, counter = :counter
             where id = :id and player = :player;
            """
        elif s == 'select':
            sql = "select * from CountGameRoomTbl where player = :player"
        elif s == 'delete':
            sql = "delete from CountGameRoomTbl where id = 0 and player = :player"
        return self.execQuery(sql, d)

    def execQuery(self, sql, d):
        u"""テーブル操作
        """
        result = None
        try:
            db = DatabaseUtil("db/game.db")
            result = db.execute(sql, d)
        except Exception as e:
            print("Error: " + str(e))
        finally:
            db.close()
        return result

    def createSendContent_Image(self, reo_content):
        u"""送信用コンテンツオブジェクト(Image)の作成
        ※イベント通知の返信で使用
        """
        return ContentObject().setContent_Image(
            "originalContentUrl", "previewImageUrl"
        )

    def createSendContent_Video(self, reo_content):
        u"""送信用コンテンツオブジェクト(Video)の作成
        ※イベント通知の返信で使用
        """
        return ContentObject().setContent_Video(
            "originalContentUrl", "previewImageUrl"
        )

    def createSendContent_Audio(self, reo_content):
        u"""送信用コンテンツオブジェクト(Audio)の作成
        ※イベント通知の返信で使用
        """
        return ContentObject().setContent_Audio("originalContentUrl", 0)

    def createSendContent_Location(self, reo_content):
        u"""送信用コンテンツオブジェクト(Location)の作成
        ※イベント通知の返信で使用
        """
        location = {
            "title": "位置情報の説明（タイトル）",
            "latitude": 35.359556,
            "longitude": 138.731037,
            "address": "住所（任意）"
        }
        return ContentObject().setContent_Location(
            "位置情報の説明（タイトル）",
            "location"
        )

    def createSendContent_Sticker(self, reo_content):
        u"""送信用コンテンツオブジェクト(Sticker)の作成
        ※イベント通知の返信で使用
        """
        contentMetadata = {
            "STKID": "Stickerの識別子",
            "STKPKGID": "Stickerのパッケージ識別子",
            "STKVER": "Stickerのバージョン"
        }
        return ContentObject().setContent_Sticker(
            "contentMetadata"
        )

    def createSendContent_RichMessage(self, reo_content):
        u"""送信用コンテンツオブジェクト(RichMessage)の作成
        ※イベント通知の返信で使用
        """
        contentMetadata = {
            "DOWNLOAD_URL": "画像のベースURL",
            "SPEC_REV": "1",
            "ALT_TEXT": "代替テキスト",
            "MARKUP_JSON": "Rich Message Objectをエンコードした文字列"
        }
        return ContentObject().setContent_RichMessage(
            "contentMetadata"
        )

    def createSendContent_Thanks(self, name):
        u"""ユーザ操作（友だち追加）に対してのサンクス通知
        ※ユーザ操作の返信で使用
        """
        self.content = ContentObject().setContent_Text(
            self.createThanksMsg(name)
        )

    def createThanksMsg(self, name):
        u"""ありがとうメッセージ
        """
        displayName = "" if name is None else "{}さん ".format(name.strip())
        return "{}\n友だち追加ありがとうございます。".format(displayName)

    def createRequestBody(self):
        u"""送信用コンテンツのリクエストボディを作成
        """
        content = "" if self.content is None else self.content
        return {
            "to": ["{}".format(self.to)],
            "toChannel": self.toChannel,
            "eventType": self.eventType,
            "content": self.content
        }

    def createCommand(self):
        u"""送信内容(返信内容)の定義作成
        """
        return (
            (re.compile("会社の名前", 0), lambda x: self.resAnser_kaisya(x, 1)),
            (re.compile("どんな会社", 0), lambda x: self.resAnser_kaisya(x, 2)),
            (re.compile("業種は", 0), lambda x: self.resAnser_kaisya(x, 3)),
            (re.compile("どんな仕事", 0), lambda x: self.resAnser_kaisya(x, 4)),
            (re.compile("支店は", 0), lambda x: self.resAnser_kaisya(x, 5)),
            (re.compile("ホームページ", 0), lambda x: self.resAnser_kaisya(x, 6)),
            (re.compile("プログラムとは", 0), lambda x: self.resAnser_pg(x, 1)),
            (re.compile("プログラミングとは", 0), lambda x: self.resAnser_pg(x, 2)),
            (re.compile("プログラミング言語とは", 0), lambda x: self.resAnser_pg(x, 3)),
            (re.compile("プログラミング言語の種類", 0), lambda x: self.resAnser_pg(x, 4)),
            (re.compile("プログラミング言語の歴史", 0), lambda x: self.resAnser_pg(x, 5)),
            (re.compile("会話力", 0), lambda x: self.resAnser_other(x)),
            (re.compile("お願い", 0), lambda x: "かしこまりました。"),
            (re.compile("好きな", 0), lambda x: self.resAnser_ilike(x)),
            (re.compile("聞いてる", 0), lambda x: "聞いてません。"),
            (re.compile("将来の夢", 0), lambda x: "賢くなることです。"),
            (re.compile("ヤッホー", 0), lambda x: "(ヤッホー(ヤッホー(ヤッホー)))"),
            (re.compile("趣味", 0), lambda x: "ポケモンGo\n(今のレベルは4)"),
            (re.compile("ゲームしよう", 0), lambda x: self.resAnser_game(x)),
        )

    def resAnser_gameend(self, reo_content):
        u"""カウントゲーム辞める
        """
        # DB(CountGameRoomTbl)からユーザ削除
        self.execQuery_CountGameRoomTbl(
            'delete', {"player": reo_content._from}
        )
        return "お疲れ様でした。"

    def countGameAlg(self, currentCounter):
        u"""カウントゲーム(必勝サーチ)
        """
        # ターゲット
        targetNo = 31
        # カウントできる範囲
        countRange = 3
        # 必勝Noを算出
        victoryNo = targetNo - 1
        flaglist = []
        while victoryNo > 0:
            flaglist.append(victoryNo)
            victoryNo = victoryNo - 1 - countRange

        # 現在のカウンター値からカウント範囲分全てカウントしてみる
        anscnt = 0
        for i in range(1, countRange+1):
            anscnt = currentCounter + i
            if anscnt in flaglist:
                break
        else:
            anscnt = 0
            ansers = [1, 2, 3]
            anscnt = currentCounter + random.choice(ansers)
        return anscnt, (anscnt - currentCounter)
        # カウンター値をanscntでUPDATE
        # anscnt - currentCounter = n個カウント

    def countGameUpd(self, player, status, counter):
        u"""ステータス、カウンターの更新
        """
        self.execQuery_CountGameRoomTbl(
            'update',
            {'id': 0, 'player': player, 'status': status, 'counter': counter}
        )

    def resAnser_game1(self, reo_content, counter):
        u"""カウントゲーム(ゲーム中:相手の回答を受ける)
        """
        ans = ""
        newcounter = counter + int(reo_content.text)

        if newcounter >= 31:
            ans += "私の勝ちです。\n\n"
            ans += "一緒に遊んでくれて\nありがとうございました。"
            self.execQuery_CountGameRoomTbl(
                'delete', {"player": reo_content._from}
            )
        else:
            ans = "{}ですね。\n".format(reo_content.text)
            ans += "{}つカウントします。\n".format(reo_content.text)
            ans += "カウンター値：{} -> {}\n\n".format(
                counter, newcounter
            )
            # statusを1のまま、カウンター値を書き込み
            self.countGameUpd(reo_content._from, 1, newcounter)

            counter = newcounter

            ans += "では、私の番です。\n"
            newcounter, cnt = self.countGameAlg(counter)
            ans += "{}つカウントします。\n".format(cnt)
            ans += "カウンター値：{} -> {}\n".format(counter, newcounter)
            if newcounter >= 31:
                ans += "あなたの勝ちです。\n\nおめでとうございます。\n"
                ans += "一緒に遊んでくれて\nありがとうございました。"
                self.execQuery_CountGameRoomTbl(
                    'delete', {"player": reo_content._from}
                )
            else:
                ans += "あなたの番です。\n"
                ans += "現在のカウンター値：{}\n".format(newcounter)
                # statusを1のまま、カウンター値を書き込み
                self.countGameUpd(reo_content._from, 1, newcounter)

        return ans

    def resAnser_game0(self, reo_content, counter):
        u"""カウントゲーム(先攻後攻待ち -> ゲーム中)
        """
        ans = ""
        newcounter = counter
        if reo_content.text == "先攻":
            ans = "では、あなたからです。\n"
            ans += "現在のカウンター値：{}\n".format(counter)
            ans += "1つ～3つの範囲でいくつカウントしますか？\n"
        elif reo_content.text == "後攻":
            ans = "では、私から始めます。\n"
            ans += "現在のカウンター値：{}\n\n".format(counter)
            newcounter, cnt = self.countGameAlg(counter)
            ans += "{}つカウントします。\n".format(cnt)
            ans += "カウンター値：{} -> {}\n\n".format(counter, newcounter)
            ans += "あなたの番です。\n"
            ans += "現在のカウンター値：{}\n".format(newcounter)
            ans += "1つ～3つの範囲でいくつカウントしますか？"

        # statusを1にupdate、カウンター値を書き込み
        self.countGameUpd(reo_content._from, 1, newcounter)
        return ans

    def resAnser_game(self, reo_content):
        u"""カウントゲーム(ルール説明 -> 先攻後攻待ち)
        """
        # ルール説明
        ans = ""
        ans += "では「31ゲーム」をしましょう！\n\n"
        ans += "【ルール説明】\n"
        ans += "①まず、先攻後攻を決めます。\n"
        ans += "②交互に1～31までカウントアップ。\n"
        ans += "③31をカウントした方が負け。\n\n"
        ans += "※1回のターンでカウントアップできる数は3つまでとします。\n\n"
        ans += "例えば、私が3つ分カウントするとカウンタが「3」になります。\n次にあなたは、4～6までカウントアップできることになります。\n"
        ans += "・1つ分のカウントだと、カウンタが「4」\n"
        ans += "・2つ分のカウントだと、カウンタが「5」\n"
        ans += "・3つ分のカウントだと、カウンタが「6」\nになります。\n"
        ans += "ここであなたが2つ分のカウントをしたい場合、数字の「2」を入力してください。\n"
        ans += "するとカウンタは「5」になります。\n今度は私が1つ分カウントするとカウンタは「6」になります。\n"
        ans += "これを交互に続けていき、最終的に31をカウントしたほうが負けになります。\n"
        ans += "では、始めましょう！\n\n先攻か後攻どちらにしますか？\n"
        ans += "「先攻」か「後攻」のどちらかを送信してください。\n"

        # status0でinsert
        self.execQuery_CountGameRoomTbl(
            'insert',
            {'id': 0, 'player': reo_content._from, 'status': 0, 'counter': 0}
        )
        return ans

    def resAnser_ilike(self, reo_content):
        u"""好きなシリーズ(今のところ適当に回答)
        """
        ansers = ["1","白ごはん！","みかん！","あなた","鳥","魚","桜","東京"]
        ans = random.choice(ansers)
        print(ans)
        return ans

    def resAnser_other(self, reo_content):
        u"""返答：その他
        """
        ans = "私の会話力は以下の通りです。\n\n"
        ans += "【会社関連】\n"
        ans += "会社の名前は？\n"
        ans += "どんな会社？\n"
        ans += "業種は？\n"
        ans += "どんな仕事？\n"
        ans += "支店は？\n"
        ans += "ホームページ\n\n"
        ans += "【プログラム】\n"
        ans += "プログラムとは？\n"
        ans += "プログラミングとは？\n"
        ans += "プログラミング言語とは？\n"
        ans += "プログラミング言語の種類は？\n"
        ans += "プログラミング言語の歴史は？\n\n"
        ans += "【その他(あそび)】\n"
        ans += "会話力\n"
        ans += "お願い\n"
        ans += "好きな●●\n"
        ans += "聞いてる？\n"
        ans += "将来の夢\n"
        ans += "ヤッホー\n"
        ans += "趣味\n"
        ans += "ゲームしよう\n"
        return ans

    def resAnser_pg(self, reo_content, no):
        u"""返答：プログラム
        """
        ans = "{}？？".format(reo_content.text)
        if no == 1:
            # プログラムとは？
            ans = "コンピュータに出す命令文のことです。\n"
            ans += "コンピュータは命令(プログラム)されたとおりの動作をします。\n"
            ans += "つまりコンピュータのあるところ、日常のいたるところでプログラムが動いています。"
        elif no == 2:
            # プログラミングとは？
            ans = "プログラムを作る（書く）ことです。\n"
            ans += "プログラムを作る人や職業をプログラマーと呼んだりします。"
        elif no == 3:
            # プログラミング言語とは？
            ans += "コンピュータが理解できる言葉は「機械語」と呼ばれます。「機械語」は0と1からなる言葉です。\n"
            ans += "人が機械語でコンピュータに命令を出すのは難しい為、命令を出しやすいように形式的な言葉が作られました。それがプログラミング言語です"
        elif no == 4:
            # プログラミング言語の種類は？
            ans = "プログラム言語にも種類があります。\n"
            ans += "COBOL、C言語、Java、C#、Perl、Ruby、Python...\n"
            ans += "たくさんあります。"
        elif no == 5:
            # プログラミング言語の歴史は？
            ans = "長くなるので以下を参照してください\n"
            ans += "https://ja.wikipedia.org/wiki/%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E8%A8%80%E8%AA%9E%E5%B9%B4%E8%A1%A8"

        return ans

    def resAnser_kaisya(self, reo_content, no):
        u"""返答：会社説明
        """
        ans = "{}？？".format(reo_content.text)
        if no == 1:
            # 会社の名前は？
            ans = "○○（株）です。"
        elif no == 2:
            # どんな会社？
            ans = "ITを生業にしている中小IT企業です。"
        elif no == 3:
            # 業種は？
            ans = "システムの開発です。"
        elif no == 4:
            # どんな仕事？
            ans = "お客さんが悩んでいることをITを使って解決します。\n"
            ans += "具体的には、お客様専用のシステムを作ったり、そのシステムをより良く作り変えたりしています。"
        elif no == 5:
            # 支店は？
            ans = "○○に拠点があります。"
        elif no == 6:
            # ホームページ
            ans = "こちらになります。\nhttp://○○○.com/"
        return ans

def main():
    return

if __name__ == '__main__':
    main()
