# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__status__ = 'development'
__date__ = '18 July 2016'

class MessageObject(object):
    u"""ユーザから送信されたメッセージを表すオブジェクトクラス
    """
    # コンテンツの種別
    CONTENTTYPE_TEXT = 1
    CONTENTTYPE_IMAGE = 2
    CONTENTTYPE_VIDEO = 3
    CONTENTTYPE_AUDIO = 4
    CONTENTTYPE_LOCATION = 7
    CONTENTTYPE_STICKER = 8
    CONTENTTYPE_CONTACT = 10
    # Message Content API
    MSGCONTENTAPI = "https://trialbot-api.line.me/v1/bot/message/{0}/content"
    # Message Content APIで取得するコンテンツ
    MSGCONTENTAPI_TARGET = {CONTENTTYPE_IMAGE, CONTENTTYPE_VIDEO, CONTENTTYPE_AUDIO}


    def __init__(self,reo_content):
        # Message Objectの共通フィールド
        # メッセージの識別子
        self.id = reo_content["id"]
        # コンテンツの種別
        self.contentType = reo_content["contentType"]
        # 送信元ユーザーの識別子
        self._from = reo_content["from"]
        # メッセージの生成時刻 (エポック時間のミリ秒)
        self.createdTime = reo_content["createdTime"]
        # 送信先ユーザー識別子の配列
        self.to = reo_content["to"][0]
        # 定数 1
        self.toType = reo_content["toType"]
        # テキスト(種別がTextの場合に値あり)
        self.text = reo_content["text"]

        # コンテンツの詳細情報(種別がStickerとContactの場合に値あり)
        self.contentMetadata = reo_content["contentMetadata"]
        # ロケーション(種別がLocationの場合に値あり)
        self.location = reo_content["location"]
        # Image, Video, AudioはAPIを使って内容取得
        if self.contentType in self.MSGCONTENTAPI_TARGET:
            # Image, Video, Audio
            self.getContent_MsgContentAPI(reo_content)

    def getContent_MsgContentAPI(self, content):
        u"""Message Content APIで取得するコンテンツ(未実装)
        """
        return

    def iscontentTypeText(self):
        u"""コンテンツの種別がText？
        """
        return True if self.contentType == self.CONTENTTYPE_TEXT else False

    def iscontentTypeImage(self):
        u"""コンテンツの種別がImage？
        """
        return True if self.contentType == self.CONTENTTYPE_IMAGE else False

    def iscontentTypeVideo(self):
        u"""コンテンツの種別がVideo？
        """
        return True if self.contentType == self.CONTENTTYPE_VIDEO else False

    def iscontentTypeVide(self):
        u"""コンテンツの種別がVideo？
        """
        return True if self.contentType == self.CONTENTTYPE_AUDIO else False

    def iscontentTypeLocation(self):
        u"""コンテンツの種別がLocation？
        """
        return True if self.contentType == self.CONTENTTYPE_LOCATION else False

    def iscontentTypeSticker(self):
        u"""コンテンツの種別がSticker？
        """
        return True if self.contentType == self.CONTENTTYPE_STICKER else False

    def iscontentTypeContact(self):
        u"""コンテンツの種別がContact？
        """
        return True if self.contentType == self.CONTENTTYPE_CONTACT else False

def main():
    return

if __name__ == '__main__':
    main()
