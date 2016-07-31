# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__status__ = 'development'
__date__ = '18 July 2016'

class ContentObject(object):
    u"""イベントのコンテンツを表すオブジェクトクラス(BOTから送信時に使用)
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

    def __init__(self):
        # 定数
        self.toType = 1

    def setContent_Text(self, text):
        u"""ContentObjectにTextをセット
        text:送信するテキスト (最大1024文字)
        """
        return {
            "contentType": self.CONTENTTYPE_TEXT,
            "toType": self.toType,
            "text": text
        }

    def setContent_Image(self, originalContentUrl, previewImageUrl):
        u"""ContentObjectにImageをセット
        originalContentUrl:画像のURL (JPEG限定。縦横最大1024px)
        previewImageUrl:プレビュー画像のURL (JPEG限定。縦横最大240px)
        """
        return {
            "contentType": self.CONTENTTYPE_IMAGE,
            "toType": self.toType,
            "originalContentUrl": originalContentUrl,
            "previewImageUrl": previewImageUrl
        }

    def setContent_Video(self, originalContentUrl, previewImageUrl):
        u"""ContentObjectにVideoをセット
        originalContentUrl:動画ファイルのURL (mp4推奨)
        previewImageUrl:プレビュー用の画像のURL (JPEG限定。縦横最大240px)
        """
        return {
            "contentType": self.CONTENTTYPE_VIDEO,
            "toType": self.toType,
            "originalContentUrl": originalContentUrl,
            "previewImageUrl": previewImageUrl
        }

    def setContent_Audio(self, originalContentUrl, audlen):
        u"""ContentObjectにAudioをセット
        originalContentUrl:音声ファイルのURL (m4a推奨)
        audlen:音声ファイルの時間長さ(ミリ秒)
        """
        return {
            "contentType": self.CONTENTTYPE_AUDIO,
            "toType": self.toType,
            "originalContentUrl": originalContentUrl,
            "contentMetadata": audlen
        }

    def setContent_Location(self, text, location):
        u"""ContentObjectにLocationをセット
        text:位置情報の説明
        location.title:位置情報の説明(textと同じ内容)
        location.latitude:Decimal
        location.longitude:Decimal
        location.address:住所（任意）
        """
        return {
            "contentType": self.CONTENTTYPE_LOCATION,
            "toType": self.toType,
            "text": text,
            "location": location
        }

    def setContent_Sticker(self, contentMetadata):
        u"""ContentObjectにStickerをセット
        contentMetadata.STKID:Stickerの識別子
        contentMetadata.STKPKGID:Stickerのパッケージ識別子
        contentMetadata.STKVER:tickerのバージョン
        """
        return {
            "contentType": self.CONTENTTYPE_STICKER,
            "toType": self.toType,
            "contentMetadata": contentMetadata
        }

    def setContent_RichMessage(self, contentMetadata):
        u"""ContentObjectにRichMessageをセット
        contentMetadata.DOWNLOAD_URL:Stickerの識別子
        contentMetadata.SPEC_REV:"1"(定数)
        contentMetadata.ALT_TEXT:代替テキスト
        contentMetadata.MARKUP_JSON:Rich Message Objectをエンコードした文字列
        """
        return {
            "contentType": self.CONTENTTYPE_RICHMESSAGE,
            "toType": self.toType,
            "contentMetadata": contentMetadata
        }


def main():
    return

if __name__ == '__main__':
    main()
