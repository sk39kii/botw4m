# -*- coding: utf-8 -*-

import base64
from DatabaseUtil import DatabaseUtil
import hmac
import hashlib
import os
from ReceivingEventObject import ReceivingEventObject
from SendingEventObject import SendingEventObject
import sys
import time
import tornado.httpclient
import tornado.httpserver
from tornado.httputil import url_concat
import tornado.ioloop
import tornado.gen
import tornado.options
from tornado.options import define, options
from tornado.queues import Queue
import tornado.web
from tornado.web import url

class ReceiveQueue():
    u"""LINEからの受信メッセージキュー
    """
    # BOT定義
    Content_Type = "application/json"
    X_Line_ChannelID = "ChannelID"
    X_Line_ChannelSecret = "ChannelSecret"
    X_Line_Trusted_User_With_ACL = "MID"
    # リクエストヘッダ
    REQUEST_HEADER = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Line-ChannelID": X_Line_ChannelID,
        "X-Line-ChannelSecret": X_Line_ChannelSecret,
        "X-Line-Trusted-User-With-ACL": X_Line_Trusted_User_With_ACL
    }
    # POST EVENT APIのURL
    POST_EVENT_API = "https://trialbot-api.line.me/v1/events"
    # Profiles APIのURL(GET)
    PROFILES_API = "https://trialbot-api.line.me/v1/profiles"

    def __init__(self):
        self.queued_items = Queue()
        self.db = DatabaseUtil("db/database.db")
        if not self.db.checkDuplicate("MessageObjects"):
            sql = ReceivingEventObject().getQuery_MessageObjects("create")
            self.db.execute(sql)
        if not self.db.checkDuplicate("OperationObjects"):
            sql = ReceivingEventObject().getQuery_OperationObjects("create")
            self.db.execute(sql)

    @tornado.gen.coroutine
    def watch_queue(self):
        while True:
            items = yield self.queued_items.get()
            self.parse_receiving_event(items[0], items[1])

    def parse_receiving_event(self, req_head, req_body):
        u"""LINEServerからのイベント通知を解析
        """
        # リクエストの署名検証
        if not self.validate_signature(req_head['X-LINE-ChannelSignature'], req_body):
            print("Signature NG")
            return

        # リクエストの解析
        # １回の通知でresultが複数含まれている場合もある
        # 以下の処理は１リクエストずつ処理
        json_dic = tornado.escape.json_decode(req_body)
        for result in json_dic["result"]:
            print(result)
            result_jsonstr = tornado.escape.json_encode(result)
            reo = ReceivingEventObject(result)

            if reo.isEventTypeMessage():
                print("MessageObject")
                # メッセージ通知(MessageObject)
                mo = reo.content
                # DBに格納
                sql = reo.getQuery_MessageObjects('insert')
                d = {
                    'id': mo.id, 'contentType': mo.contentType, 'from': mo._from,
                    'createdTime': mo.createdTime, 'to': mo.to, 'toType': mo.toType,
                    'text': mo.text, 'json_data': result_jsonstr
                }
                self.db.execute(sql, d)
                # イベント通知に対する送信
                self.toPOSTEventAPI(
                    tornado.escape.json_encode(
                        SendingEventObject(reo).createRequestBody()
                    )
                )
            elif reo.isEventTypeOperation():
                # ユーザ操作(OperationObject)
                oo = reo.content
                # DBに格納
                sql = reo.getQuery_OperationObjects('insert')

                d = {
                    'revision': oo.revision, 'opType': oo.opType,
                    'params0': oo.params[0], 'params1': '', 'params2': '',
                    'json_data': result_jsonstr
                }
                self.db.execute(sql, d)
                # ユーザーによる友だち追加（ブロック解除を含む）
                if reo.content.isFriendsAdd():
                    print("User Operation Add    ",reo.content.params[0])
                    # プロフィールの取得
                    result = self.toProfilesAPI(reo.content.params[0])
                    for v in result:
                        name = v["displayName"]
                    # ありがとうメッセージの送信
                    seo = SendingEventObject(reo)
                    seo.createSendContent_Thanks(name)
                    res = self.toPOSTEventAPI(
                        tornado.escape.json_encode(
                            seo.createRequestBody()
                        )
                    )
                elif reo.content.isFriendsBlock():
                    # ユーザーによるブロック
                    print("User Operation Block    ",reo.content.params[0])

    @tornado.gen.coroutine
    def toPOSTEventAPI(self, send_body):
        u"""LINEServerへ送信
        ※LINEServerへ送信する際はこちらがクライアント
        """
        # リクエストボディ(Sending Event ObjectのJSONデータ)
        # ※リクエストボディは8Kib以下であること(LINEの仕様)
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = None
        try:
            response = yield http_client.fetch(
                self.POST_EVENT_API,
                method='POST',
                headers=self.REQUEST_HEADER,
                body=send_body
            )
        except http_client.HTTPError as e:
            # HTTPError is raised for non-200 responses
            print("Error: " + str(e))
        except Exception as e:
            # Other errors
            print("Error: " + str(e))
        http_client.close()
        return response

    def toProfilesAPI(self, mid):
        u"""PROFILES APIでLINEServerにプロフィールを問い合わせ
        ※Contact Response ObjectのJSONデータが返却されてくる
        ※TODO:複数一括リクエストは未対応
        """
        # リクエストはGetでユーザーの識別子 (複数時はカンマ区切り)を渡す
        http_client = tornado.httpclient.HTTPClient()
        url = url_concat(self.PROFILES_API, {"mids": mid})
        print(url)
        result = None
        try:
            response = http_client.fetch(
                url,
                method='GET',
                headers=self.REQUEST_HEADER,
                body=None
            )
            json_dic = tornado.escape.json_decode(response.body)
            result = json_dic["contacts"]
        except http_client.HTTPError as e:
            # HTTPError is raised for non-200 responses
            print("Error: " + str(e))
        except Exception as e:
            # Other errors
            print("Error: " + str(e))
        http_client.close()
        return result

    def validate_signature(self, signature, content):
        u"""LINEServerからのリクエストかを署名検証する
        [検証内容]
        1. ChannelSecretを秘密鍵としHMAC-SHA256でリクエストボディのダイジェスト値を取得
        2. ダイジェスト値をBase64化した値がリクエストヘッダのChannelSignatureと合致するか検証
        ※LINE BOT SDK for Python(https://github.com/studio3104/line-bot-sdk-python)から借用
        """
        return hmac.compare_digest(
            signature.encode('utf-8'),
            base64.b64encode(
                hmac.new(
                    self.X_Line_ChannelSecret.encode('utf-8'),
                    msg=content,
                    digestmod=hashlib.sha256
                ).digest()
            )
        )


class IndexHandler(tornado.web.RequestHandler):
    u"""DocumentRootアクセスハンドラ(特に何もしない)
    """
    @tornado.gen.coroutine
    def get(self):
        # yield receiveQueue.queued_items.put("%f" % time.time())
        self.write("OK")


class CallBackHandler(tornado.web.RequestHandler):
    u"""LINEからの通知(コールバック)用ハンドラ
    """
    @tornado.gen.coroutine
    def post(self):
        req_head = self.request.headers
        req_body = self.request.body
        yield receiveQueue.queued_items.put([req_head, req_body])
        self.write("OK")


class Application(tornado.web.Application):
    u"""Webアプリ初期化クラス
    """
    def __init__(self):
        # ルーティングの設定
        routes_handlers = [
            url(r'/', IndexHandler, name='index'),
            url(r'/callback/', CallBackHandler, name='callback'),
        ]
        # 読み込みファイル(テンプレートと静的ファイル)の設定
        settings = dict(
            template_path = os.path.join(os.getcwd(), "templates"),
            static_path = os.path.join(os.getcwd(), "static"),
            debug=True
        )
        tornado.web.Application.__init__(self, routes_handlers, **settings)

if __name__ == "__main__":

    # LINEからの受信用キュー
    receiveQueue = ReceiveQueue()
    # コールバックに受信用キューを追加
    tornado.ioloop.IOLoop.instance().add_callback(receiveQueue.watch_queue)

    # Webサーバー設定
    config_path = os.path.join(os.path.dirname(__file__), "config")
    tornado.options.parse_config_file(os.path.join(config_path, 'server.conf'))
    tornado.options.parse_command_line()
    # SSL証明書、秘密鍵、CA証明書
    SSLCertificateFile = os.path.join(config_path, "2_bot.crt")
    SSLCertificateKeyFile = os.path.join(config_path, "bot.key")
    SSLCertificateChainFile = os.path.join(config_path, "1_root_bundle.crt")
    # Webアプリ設定
    application = Application()
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": SSLCertificateFile,
        "keyfile": SSLCertificateKeyFile,
        "ca_certs" : SSLCertificateChainFile,
    })

    # ポートはserver.confで設定
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()
