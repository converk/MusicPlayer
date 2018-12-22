# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _toUtf8 = QString.toUtf8
except AttributeError:
    def _toUtf8(s):
        return s


class MusicTableView(QTableView):
    def __init__(self, type, parent=None):
        QTableView.__init__(self, parent)

        #设定初始背景颜色,以及被选中的时候的背景颜色
        self.setStyleSheet(
            '''
            MusicTableView
            {background-color: rgba(230, 230, 240, 0);
            selection-background-color: rgba(100, 100, 255, 55)}
            '''
        )

        self._playingIndex = -1
        self._parent = parent
        self.type = type
        self.model = QStandardItemModel()
        self._musicList = parent.musicList
        self._favList = parent.favList
        #self.tipRow = -1
        #self.list = self._musicList if self.type == 'all' else self._favList

        self.model.setColumnCount(3)

        self.setFixedWidth(300)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setMouseTracking(True)

        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setClickable(False)

        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setClickable(False)
        self.horizontalHeader().hide()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setModel(self.model)

        # 添加右键菜单
        self.contextMenu = QMenu(self)
        self.playAction = QAction(u'播放', self)
        self.deleteAction = QAction(u'移除', self)
        self.favAction = QAction(u'收藏', self)
        self.openFolderAction = QAction(u'打开文件', self)

        # signals
        # QObject.SIGNAL.connect(slot)
        self.playAction.triggered.connect(self.playSelections)  #播放选中的音乐
        self.deleteAction.triggered.connect(self.deleteSelections)  #删除选中的音乐
        self.favAction.triggered.connect(self.collectSelections)  #收藏音乐
        self.openFolderAction.triggered.connect(self.addMusics)  #添加音乐

        # 如果是 播放列表界面
        if self.type == 'all':
            self.setAcceptDrops(True)   #允许拖拽
            # menu
            self.contextMenu.addAction(self.playAction)
            self.contextMenu.addSeparator()   #两个选项之间增加分割线
            self.contextMenu.addAction(self.deleteAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.favAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.openFolderAction)

        # 如果是 我的收藏界面
        elif self.type == 'fav':
            # menu
            self.contextMenu.addAction(self.playAction)
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.deleteAction)

    # 播放选定曲目
    def playSelections(self):
        selectedRows = self.selectionModel().selectedRows()
        if len(selectedRows):
            #获取选中的歌曲在列表中的行数
            index = selectedRows[0]
            music = self.model.itemFromIndex(index).row()
            self.playMusic(music)

    # 删除选定曲目
    def deleteSelections(self):
        #被选中的行数
        selectedRows = self.selectionModel().selectedRows()
        #存储要删除的音乐
        musicDelList = []
        #播放列表
        if self.type == 'all':
            for index in selectedRows:
                i = self.model.itemFromIndex(index).row()
                #如果删除的歌曲是正在播放的,那么停止播放
                if self._parent.playingIndex == i:
                    self._parent.stop()
                musicDelList.append(self._musicList[i])
            for music in musicDelList:
                #从当前歌单移除音乐
                self._musicList.remove(music)
        #收藏列表
        elif self.type == 'fav':
            for index in selectedRows:
                i = self.model.itemFromIndex(index).row()
                if self._parent.playingIndex == i:
                    self._parent.stop()
                musicDelList.append(self._favList[i])
            for music in musicDelList:
                self._favList.remove(music)
        #删除完之后要更新列表
        self.update()  
        

    # 添加选定曲目到 我的收藏
    def collectSelections(self):
        selectedRows = self.selectionModel().selectedRows()
        for index in selectedRows:
            i = self.model.itemFromIndex(index).row()
            if all(music.absolutePath() != self._musicList[i].absolutePath() for music in self._favList):
                self._favList.append(self._musicList[i])
        self.update()

    # emit(SIGNAL)，关联对应信号槽（slot）
    def addMusics(self):
        self.emit(SIGNAL("addMusics()"))

    def update(self):
        self.emit(SIGNAL("update()"))

    def playMusic(self, row):
        self.emit(SIGNAL("playMusic(int)"), row)

    #两个tabview的右键菜单
    def contextMenuEvent(self, event):
        pos = event.pos()
        index = self.indexAt(pos)


        #如果选中的是音乐,那么这三个选项可用,如果右击空白区,那么这三个选项不可用
        self.playAction.setEnabled(self.model.itemFromIndex(index) is not None)
        self.deleteAction.setEnabled(self.model.itemFromIndex(index) is not None)
        self.favAction.setEnabled(self.model.itemFromIndex(index) is not None)

        if self.type == 'all' and self.model.itemFromIndex(index):
            if self._parent.musicList[self.model.itemFromIndex(index).row()] in self._parent.favList:
                self.favAction.setText(u"取消收藏")
            else:
                self.favAction.setText(u"收藏")

        self.contextMenu.exec_(event.globalPos())

    #鼠标双击播放
    def mouseDoubleClickEvent(self, event):
        QTableView.mouseDoubleClickEvent(self, event)
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            index = self.indexAt(pos)
            if self.model.itemFromIndex(index):
                i = self.model.itemFromIndex(index).row()
                self.playMusic(i)

    # def dragEnterEvent(self, event):
    #     for url in event.mimeData().urls():
    #         if url.path().toLower().contains('.mp3') or url.path().toLower().contains('.wma'):
    #             event.accept()
    #             break
    #         else:
    #             super(QTableView, self).dragMoveEvent(event)

    # def dragMoveEvent(self, event):
    #     for url in event.mimeData().urls():
    #         if url.path().toLower().contains('.mp3') or url.path().toLower().contains('.wma'):
    #             event.accept()
    #             break
    #         else:
    #             super(QTableView, self).dragMoveEvent(event)

    # def dropEvent(self, event):
    #     paths = []
    #     for url in event.mimeData().urls():
    #         if url.path().toLower().contains('.mp3') or url.path().toLower().contains('.wma'):
    #             s = url.path().remove(0, 1)
    #             paths.append(s)
    #     self._parent.addMusics(paths)

    #更新播放曲目的颜色的特征
    def updatePlayingItem(self):
        if self._playingIndex != self._parent.playingIndex:
            if self._playingIndex != -1 and self.model.rowCount() > self._playingIndex:
                self.model.item(self._playingIndex, 0).setForeground(QBrush(QColor(0, 0, 0)))
                self.model.item(self._playingIndex, 1).setForeground(QBrush(QColor(0, 0, 0)))
                self.model.item(self._playingIndex, 2).setForeground(QBrush(QColor(0, 0, 0)))
            self._playingIndex = self._parent.playingIndex
            if self._playingIndex != -1 and self.model.rowCount() > self._playingIndex:
                self.model.item(self._playingIndex, 0).setForeground(QBrush(QColor(255, 100, 100)))
                self.model.item(self._playingIndex, 1).setForeground(QBrush(QColor(255, 100, 100)))
                self.model.item(self._playingIndex, 2).setForeground(QBrush(QColor(255, 100, 100)))
