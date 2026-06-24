import sys
import os
import shutil
import exifread
import json
from PIL import Image, ImageQt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTextEdit, QGraphicsView, 
                             QGraphicsScene, QFrame, QMessageBox, QGroupBox, QFormLayout,
                             QDialog, QKeySequenceEdit, QDialogButtonBox, QTabWidget,
                             QCheckBox)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QColor, QKeySequence

# --- MODERN MINIMALIST UI STYLESHEET ---
STYLESHEET = """
QMainWindow, QDialog { background-color: #121212; }
QWidget { background-color: #121212; color: #A0A0A0; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 13px; }
QLabel#CreditLabel { color: #404040; font-size: 11px; }
QLabel#Header { font-size: 22px; font-weight: 700; color: #00A3FF; letter-spacing: 1px; }

/* Styling Tab agar sesuai tema */
QTabWidget::pane { border: 1px solid #252525; background: #121212; top: -1px; }
QTabBar::tab { background: #1E1E1E; color: #808080; border: 1px solid #252525; padding: 10px 25px; margin-right: 2px; font-weight: 600; }
QTabBar::tab:selected { background: #121212; color: #00A3FF; border-bottom: 2px solid #00A3FF; }
QTabBar::tab:hover { background: #252525; }

QGroupBox { border: none; border-top: 1px solid #252525; margin-top: 20px; padding-top: 15px; font-weight: 600; color: #FFFFFF; }
QGroupBox::title { subcontrol-origin: margin; left: 0px; padding: 0 5px; }

QTextEdit, QKeySequenceEdit { background-color: #1A1A1A; border: 1px solid #252525; color: #FFFFFF; border-radius: 6px; padding: 8px; }
QPushButton { background-color: #1E1E1E; border: 1px solid #252525; color: #E0E0E0; padding: 10px; border-radius: 6px; font-weight: 500; }
QPushButton:hover { background-color: #252525; border: 1px solid #353535; }

/* Tombol Khusus */
QPushButton#btnSelect { background-color: #1B2B21; color: #4ADE80; border: 1px solid #2D4A37; }
QPushButton#btnSelect:hover { background-color: #24382B; }
QPushButton#btnMaybe { background-color: #2B261B; color: #FACC15; border: 1px solid #4A412D; }
QPushButton#btnMaybe:hover { background-color: #383121; }
QPushButton#btnReject { background-color: #2B1B1B; color: #F87171; border: 1px solid #4A2D2D; }
QPushButton#btnReject:hover { background-color: #382121; }

QPushButton#btnSettings { background-color: transparent; border: none; color: #606060; font-size: 18px; }
QPushButton#btnSettings:hover { color: #00A3FF; }
QLabel#DetailVal { color: #FFFFFF; font-weight: 600; }

/* Font khusus ExtraBold untuk Progress */
QLabel#Judul { 
    font-family: 'Plus Jakarta Sans';
    font-size: 40px;
    font-weight: 800;
    color: #00a3ff;
}
"""

# --- DIALOG SETTINGS (SHORTCUTS) ---
class SettingsDialog(QDialog):
    def __init__(self, current_shortcuts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shortcut Settings")
        self.resize(350, 300)
        self.new_shortcuts = current_shortcuts.copy()
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.edits = {}
        for key in ['select', 'maybe', 'reject', 'next', 'prev']:
            edit = QKeySequenceEdit(QKeySequence(self.new_shortcuts[key]))
            form_layout.addRow(key.capitalize(), edit)
            self.edits[key] = edit
        layout.addLayout(form_layout)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.validate_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def validate_and_accept(self):
        for key, edit in self.edits.items():
            seq = edit.keySequence()
            if not seq.isEmpty(): self.new_shortcuts[key] = seq[0]
        self.accept()

# --- DIALOG HELP / TUTORIAL ---
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selamat Datang di BendolSort")
        self.resize(700, 400)
        layout = QVBoxLayout(self)

        # Tab Tutorial
        tabs = QTabWidget()
        tabs.addTab(self.create_tab("Pengenalan", 
            "<h2>Halo!</h2><p>BendolSort adalah aplikasi manajemen foto all-in-one.</p>"
            "<ul><li><b>Sorter:</b> Pilah ribuan foto dengan cepat menggunakan shortcut keyboard.</li></ul>"), "Intro")
        
        tabs.addTab(self.create_tab("Cara Sortir", 
            "<h3>⌨️ Shortcut Default:</h3>"
            "<ul><li><b>Angka 1:</b> Pindahkan ke folder SELECT</li>"
            "<li><b>Angka 2:</b> Pindahkan ke folder MAYBE</li>"
            "<li><b>Angka 3:</b> Pindahkan ke folder REJECT</li>"
            "<li><b>Panah Kanan/Kiri:</b> Next / Prev Foto</li></ul>"
            "<p><i>Anda bisa mengubah shortcut ini di menu Settings (Ikon Gear).</i></p>"), "Sorter")
        
        layout.addWidget(tabs)

        # Checkbox "Jangan Tampilkan Lagi"
        self.chk_dont_show = QCheckBox("Jangan tampilkan ini lagi saat memulai aplikasi")
        layout.addWidget(self.chk_dont_show)

        btn_ok = QPushButton("Mulai Aplikasi")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setStyleSheet("background-color: #00A3FF; color: white; font-weight: bold;")
        layout.addWidget(btn_ok)

    def create_tab(self, title, content):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel(content)
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.RichText)
        lbl.setStyleSheet("font-size: 14px; line-height: 1.4;")
        lbl.setAlignment(Qt.AlignTop)
        l.addWidget(lbl)
        return w

# --- CUSTOM GRAPHICS VIEW ---
class PhotoViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QColor("#0F0F0F"))
        self.setFrameShape(QFrame.NoFrame)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._pixmap_item = None
    
    def set_image(self, pixmap):
        self.scene.clear()
        self._pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self._pixmap_item.boundingRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            z = 1.25 if event.angleDelta().y() > 0 else 1/1.25
            self.scale(z, z)
        else: super().wheelEvent(event)

# --- TAB 1: SORTER WIDGET ---
class SorterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.current_folder = ""
        self.image_files = []
        self.current_index = 0
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- LEFT PANEL ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(320)

        # Header
        h_lay = QHBoxLayout()
        lbl_title = QLabel("BendolSort")
        lbl_title.setObjectName("Header")
        btn_set = QPushButton("⚙")
        btn_set.setObjectName("btnSettings")
        btn_set.clicked.connect(self.main.open_settings)
        h_lay.addWidget(lbl_title); h_lay.addStretch(); h_lay.addWidget(btn_set)
        left_layout.addLayout(h_lay)
        lbl_title.setObjectName("Judul")

        # Folders
        grp_folders = QGroupBox("DIRECTORIES")
        f_layout = QVBoxLayout()
        self.btn_src = QPushButton(">  Source Folder"); self.btn_src.clicked.connect(self.select_source)
        self.btn_s1 = QPushButton(">  Set Folder Accept"); self.btn_s1.clicked.connect(lambda: self.set_target('select'))
        self.btn_s2 = QPushButton(">  Set Folder Maybe"); self.btn_s2.clicked.connect(lambda: self.set_target('maybe'))
        self.btn_s3 = QPushButton(">  Set Folder Reject"); self.btn_s3.clicked.connect(lambda: self.set_target('reject'))
        for b in [self.btn_src, self.btn_s1, self.btn_s2, self.btn_s3]: f_layout.addWidget(b)
        grp_folders.setLayout(f_layout); left_layout.addWidget(grp_folders)

        # Info
        grp_info = QGroupBox("INFORMASI FOTO")
        info_l = QFormLayout()
        self.l_count = QLabel("-"); self.l_count.setObjectName("TeksProgress")
        self.l_name = QLabel("-"); self.l_name.setObjectName("DetailVal")
        self.l_cam = QLabel("-"); self.l_cam.setObjectName("DetailVal")
        info_l.addRow("Progress", self.l_count); info_l.addRow("File", self.l_name); info_l.addRow("Camera", self.l_cam)
        grp_info.setLayout(info_l); left_layout.addWidget(grp_info)

        # Client Auto Sort
        grp_client = QGroupBox("AUTO SORT")
        c_layout = QVBoxLayout()
        self.txt_client = QTextEdit(); self.txt_client.setPlaceholderText("Paste filenames...")
        btn_run = QPushButton("Run Selection"); btn_run.clicked.connect(self.process_client)
        c_layout.addWidget(self.txt_client); c_layout.addWidget(btn_run)
        grp_client.setLayout(c_layout); left_layout.addWidget(grp_client)
        left_layout.addStretch()

        # Credit
        lbl_credit = QLabel("Credit @calvinbendol"); lbl_credit.setObjectName("CreditLabel"); lbl_credit.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(lbl_credit)

        # --- RIGHT PANEL ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        top_bar = QHBoxLayout()
        self.btn_p = QPushButton("  PREV  "); self.btn_p.clicked.connect(self.prev_image)
        self.btn_n = QPushButton("  NEXT  "); self.btn_n.clicked.connect(self.next_image)
        top_bar.addWidget(self.btn_p); top_bar.addWidget(self.btn_n); top_bar.addStretch()
        right_layout.addLayout(top_bar)

        self.viewer = PhotoViewer(); right_layout.addWidget(self.viewer)

        action_layout = QHBoxLayout(); action_layout.setSpacing(15)
        self.btn_sel = QPushButton("SELECT"); self.btn_sel.setObjectName("btnSelect")
        self.btn_may = QPushButton("MAYBE"); self.btn_may.setObjectName("btnMaybe")
        self.btn_rej = QPushButton("REJECT"); self.btn_rej.setObjectName("btnReject")
        for b in [self.btn_sel, self.btn_may, self.btn_rej]: 
            b.setFixedHeight(50); b.clicked.connect(self.handle_sort_btn)
            action_layout.addWidget(b)
        right_layout.addLayout(action_layout)

        layout.addWidget(left_panel); layout.addWidget(right_panel)
        self.update_shortcut_labels()

    # --- Logic Sorter ---
    def handle_sort_btn(self):
        sender = self.sender().text().split(' ')[0].lower()
        self.sort_current(sender)

    def update_shortcut_labels(self):
        sc = self.main.shortcuts
        self.btn_sel.setText(f"SELECT ({QKeySequence(sc['select']).toString()})")
        self.btn_may.setText(f"MAYBE ({QKeySequence(sc['maybe']).toString()})")
        self.btn_rej.setText(f"REJECT ({QKeySequence(sc['reject']).toString()})")

    def select_source(self):
        f = QFileDialog.getExistingDirectory(self, "Source")
        if f: self.current_folder = f; self.load_images()

    def set_target(self, t):
        f = QFileDialog.getExistingDirectory(self, t)
        if f:
            if t == 'select': self.main.path_select = f
            elif t == 'maybe': self.main.path_maybe = f
            elif t == 'reject': self.main.path_reject = f
            self.main.save_settings()

    def load_images(self):
        exts = ('.jpg', '.jpeg', '.png', '.arw', '.cr2', '.cr3', '.nef', '.dng', '.raf')
        self.image_files = sorted([f for f in os.listdir(self.current_folder) if f.lower().endswith(exts)])
        if self.image_files: self.current_index = 0; self.show_image()

    def show_image(self):
        if not self.image_files: return
        path = os.path.join(self.current_folder, self.image_files[self.current_index])
        self.l_count.setText(f"{self.current_index+1}/{len(self.image_files)}"); self.l_name.setText(self.image_files[self.current_index])
        
        pix = QPixmap(path)
        if pix.isNull():
            try:
                img = Image.open(path); img.thumbnail((1600, 1600))
                if img.mode != "RGBA": img = img.convert("RGBA")
                pix = QPixmap.fromImage(ImageQt.ImageQt(img))
            except: return
        self.viewer.set_image(pix)
        try:
            with open(path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                self.l_cam.setText(f"{tags.get('Image Make','')} {tags.get('Image Model','')}"[:25])
        except: self.l_cam.setText("-")

    def sort_current(self, action):
        target = {'select':self.main.path_select, 'maybe':self.main.path_maybe, 'reject':self.main.path_reject}.get(action)
        if not target: QMessageBox.warning(self, "Error", "Folder tujuan belum diset!"); return
        try:
            shutil.copy2(os.path.join(self.current_folder, self.image_files[self.current_index]), os.path.join(target, self.image_files[self.current_index]))
            self.next_image()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def process_client(self):
        names = [l.strip().lower() for l in self.txt_client.toPlainText().split('\n') if l.strip()]
        if not names or not self.main.path_select: return
        all_f = {f.lower(): f for f in os.listdir(self.current_folder)}
        c = 0
        for n in names:
            found = all_f.get(n) or next((f for fl, f in all_f.items() if fl.startswith(n+".")), None)
            if found: shutil.copy2(os.path.join(self.current_folder, found), os.path.join(self.main.path_select, found)); c += 1
        QMessageBox.information(self, "Done", f"Sorted {c} files.")

    def next_image(self):
        if self.current_index < len(self.image_files)-1: self.current_index += 1; self.show_image()
    def prev_image(self):
        if self.current_index > 0: self.current_index -= 1; self.show_image()

# --- MAIN APP ---
class SorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BendolSort")
        self.resize(1300, 850)
        self.setStyleSheet(STYLESHEET)
        self.settings_file = "settings.json"
        
        # State & Settings
        self.default_shortcuts = {'select': Qt.Key_1, 'maybe': Qt.Key_2, 'reject': Qt.Key_3, 'next': Qt.Key_Right, 'prev': Qt.Key_Left}
        self.shortcuts = self.default_shortcuts.copy()
        self.path_select = ""; self.path_maybe = ""; self.path_reject = ""; self.show_help = True
        self.load_settings()

        # UI Initialization
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.tab_sorter = SorterTab(self)
        
        # Menggunakan TabWidget agar konsisten dengan stylesheet, meski hanya 1 tab
        self.tabs.addTab(self.tab_sorter, "Photo Sorter")

        # Show Help on Startup if enabled
        if self.show_help:
            self.show_tutorial()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.shortcuts = data.get('shortcuts', self.default_shortcuts.copy())
                    self.path_select = data.get('path_select', "")
                    self.path_maybe = data.get('path_maybe', "")
                    self.path_reject = data.get('path_reject', "")
                    self.show_help = data.get('show_help', True)
            except: pass

    def save_settings(self):
        data = {'shortcuts': self.shortcuts, 'path_select': self.path_select, 
                'path_maybe': self.path_maybe, 'path_reject': self.path_reject, 
                'show_help': self.show_help}
        with open(self.settings_file, 'w') as f: json.dump(data, f)

    def open_settings(self):
        d = SettingsDialog(self.shortcuts, self)
        if d.exec_():
            self.shortcuts = d.new_shortcuts; self.save_settings()
            self.tab_sorter.update_shortcut_labels()

    def show_tutorial(self):
        d = HelpDialog(self)
        if d.exec_():
            if d.chk_dont_show.isChecked():
                self.show_help = False
                self.save_settings()

    def keyPressEvent(self, event):
        # Hanya jalankan shortcut jika sedang di Tab Sorter
        if self.tabs.currentIndex() == 0:
            if self.tab_sorter.txt_client.hasFocus(): super().keyPressEvent(event); return
            k = event.key()
            sc = self.shortcuts
            if k == sc['select']: self.tab_sorter.sort_current('select')
            elif k == sc['maybe']: self.tab_sorter.sort_current('maybe')
            elif k == sc['reject']: self.tab_sorter.sort_current('reject')
            elif k == sc['next']: self.tab_sorter.next_image()
            elif k == sc['prev']: self.tab_sorter.prev_image()
            elif k in [Qt.Key_Plus, Qt.Key_Equal]: self.tab_sorter.viewer.scale(1.2, 1.2)
            elif k == Qt.Key_Minus: self.tab_sorter.viewer.scale(0.8, 0.8)

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv); w = SorterApp(); w.show(); sys.exit(app.exec_())
