# -*- coding: utf-8 -*-

__version__ = '0.0.1'
__status__ = 'development'
__date__ = '18 July 2016'

class OperationObject(object):
    u"""ユーザからBotに対して行われたユーザ操作を表すオブジェクトクラス
    """
    # ユーザ操作の種別
    OPTYPE_FRIENDADD = 4    # ユーザによる友だち追加（ブロック解除を含む）
    OPTYPE_FRIENDBLOCK = 8  # ユーザによるブロック

    def __init__(self,reo_content):
        # 連番
        self.revision = reo_content["revision"]
        # ユーザ操作の種別
        self.opType = reo_content["opType"]
        # ユーザー操作の詳細情報
        self.params = reo_content["params"]

    def isFriendsAdd(self):
        u"""ユーザ操作がユーザによる友だち追加？
        """
        if self.opType == self.OPTYPE_FRIENDADD:
            return True
        else:
            return False

    def isFriendsBlock(self):
        u"""ユーザ操作がユーザによるブロック？
        """
        if self.opType == self.OPTYPE_FRIENDBLOCK:
            return True
        else:
            return False

def main():
    return

if __name__ == '__main__':
    main()
