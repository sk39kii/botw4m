# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__status__ = 'development'
__date__ = '18 July 2016'

from MessageObject import MessageObject
from OperationObject import OperationObject

class ReceivingEventObject(object):
    u"""LINEからの受信イベント(Receiving Event Object)
    """
    # イベントタイプ
    EVENTTYPE_MESSAGE = "138311609000106303"
    EVENTTYPE_OPERATION = "138311609100106403"

    def __init__(self,result=None):
        if not result is None:
            # イベント識別子
            self.id = result["id"]
            # イベントタイプ
            self.eventType = result["eventType"]
            # 送信先ユーザ識別子
            self.to = result["to"]
            # 送信先のChannel ID
            self.toChannel = result["toChannel"]
            # このイベントのコンテンツ(Message Objectか、Operation Object)
            self.content = None
            if self.isEventTypeMessage():
                self.content = MessageObject(result["content"])
            elif self.isEventTypeOperation():
                self.content = OperationObject(result["content"])


    def isEventTypeMessage(self):
        u"""イベントタイプがメッセージ（ユーザからのイベント通知）？
        """
        if self.eventType == self.EVENTTYPE_MESSAGE:
            return True
        else:
            return False

    def isEventTypeOperation(self):
        u"""イベントタイプがユーザ操作？
        """
        if self.eventType == self.EVENTTYPE_OPERATION:
            return True
        else:
            return False

    def getQuery_OperationObjects(self, s):
        u"""OperationObjectsテーブルのクエリ
        """
        if s == 'create':
            return """
            create table OperationObjects(
              revision INTEGER
            , opType INTEGER
            , params0 TEXT
            , params1 TEXT
            , params2 TEXT
            , json_data TEXT
            , time_stamp DEFAULT CURRENT_TIMESTAMP
            , PRIMARY KEY(params0, time_stamp));
            """
        elif s == 'insert':
            return """
            insert into OperationObjects(
                revision, opType, params0, params1, params2, json_data
            ) values (
                :revision, :opType, :params0, :params1, :params2, :json_data
            );
            """

    def getQuery_MessageObjects(self, s):
        u"""MessageObjectsテーブルのクエリ
        """
        if s == 'create':
            return """
            create table MessageObjects(
              id TEXT
            , contentType INTEGER
            , _from TEXT
            , createdTime INTEGER
            , _to TEXT
            , toType INTEGER
            , _text TEXT
            , json_data TEXT
            , time_stamp DEFAULT CURRENT_TIMESTAMP
            , PRIMARY KEY(_from, contentType, time_stamp));
            """
        elif s == 'insert':
            return """
            insert into MessageObjects(
                id, contentType, _from, createdTime, _to, toType, _text,
                json_data
            ) values (
                :id, :contentType, :from, :createdTime, :to, :toType, :text,
                :json_data
            );
            """

def main():
    return

if __name__ == '__main__':
    main()
