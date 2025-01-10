import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QMenuBar, QShortcut, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QKeySequence, QCursor, QIcon
from PyQt5.QtCore import Qt, QPoint

def resource_path(relative_path):
    """获取资源的绝对路径，支持开发环境和 PyInstaller 打包后的环境"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包环境，就使用当前文件的路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # 检查命令行参数
        args = sys.argv[1:]
        if args:
            # 如果有参数（图片路径），则打开该图片
            self.load_image(args[0])

    def initUI(self):
        # 设置程序图标
        icon_path = resource_path('icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        # 设置窗口标题和大小
        self.setWindowTitle('图片查看器')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea(self)
        self.setCentralWidget(self.scroll_area)
        
        # 创建图片显示标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        
        # 初始化拖动相关变量
        self.last_mouse_pos = None
        self.is_dragging = False
        
        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件(&F)')
        
        # 添加"打开文件"动作
        open_action = QAction('打开(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # 添加"保存文件"动作
        save_action = QAction('保存(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # 添加缩放动作
        view_menu = menubar.addMenu('查看(&V)')
        zoom_in_action = QAction('放大(&I)', self)
        zoom_in_action.setShortcuts([QKeySequence('Ctrl++'), QKeySequence('Ctrl+=')])
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('缩小(&O)', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # 在查看菜单中添加恢复原始大小选项
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction('恢复原始大小(&R)', self)
        reset_zoom_action.setShortcut('Ctrl+0')
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # 添加到"编辑"菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        paste_action = QAction('粘贴(&P)', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste_from_clipboard)
        edit_menu.addAction(paste_action)
        
        self.current_image = None
        self.scale_factor = 1.0
        
    def open_file(self):
        # 获取桌面路径
        desktop_path = os.path.expanduser("~/Desktop")
        
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            desktop_path,  # 设置默认路径为桌面
            "图片文件 (*.png *.jpg *.bmp *.gif)"
        )
        if file_name:
            self.load_image(file_name)
            
    def load_image(self, file_name):
        self.current_image = QPixmap(file_name)
        self.update_image()
            
    def update_image(self):
        if self.current_image:
            scaled_image = self.current_image.scaled(
                int(self.current_image.width() * self.scale_factor),
                int(self.current_image.height() * self.scale_factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_image)
            # 更新标签大小以适应图片
            self.image_label.setFixedSize(scaled_image.size())
            # 允许鼠标追踪
            self.image_label.setMouseTracking(True)
    
    # 添加鼠标事件处理方法
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.globalPos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseMoveEvent(self, event):
        if self.is_dragging and self.last_mouse_pos:
            delta = event.globalPos() - self.last_mouse_pos
            # 更新滚动条位置
            self.scroll_area.horizontalScrollBar().setValue(
                self.scroll_area.horizontalScrollBar().value() - delta.x()
            )
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().value() - delta.y()
            )
            self.last_mouse_pos = event.globalPos()

    def zoom_in(self):
        if self.current_image:
            self.scale_factor *= 1.25
            self.update_image()
            
    def zoom_out(self):
        if self.current_image:
            self.scale_factor *= 0.8
            self.update_image()
            
    # 添加新方法：从剪贴板粘贴图片
    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            self.current_image = QPixmap.fromImage(clipboard.image())
            self.scale_factor = 1.0
            self.update_image()
        elif mime_data.hasUrls():
            # 如果剪贴板包含文件URL（比如从文件管理器复制的图片）
            file_url = mime_data.urls()[0]
            if file_url.isLocalFile():
                self.load_image(file_url.toLocalFile())

    # 添加保存文件方法
    def save_file(self):
        if not self.current_image:
            return
        
        # 获取桌面路径
        desktop_path = os.path.expanduser("~/Desktop")
            
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "保存图片",
            desktop_path,  # 设置默认路径为桌面
            "PNG 图片 (*.png);;JPEG 图片 (*.jpg *.jpeg);;BMP 图片 (*.bmp);;所有文件 (*.*)"
        )
        
        if file_name:
            pixmap = self.image_label.pixmap()
            if pixmap:
                pixmap.save(file_name)

    # 添加恢复原始大小的方法
    def reset_zoom(self):
        if self.current_image:
            self.scale_factor = 1.0
            self.update_image()

def main():
    app = QApplication(sys.argv)
    # 设置应用程序图标（任务栏图标）
    icon_path = resource_path('icon.ico')
    app.setWindowIcon(QIcon(icon_path))
    
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
