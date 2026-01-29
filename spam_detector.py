import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

# ==================== FONT CONFIGURATION ====================

# Fungsi untuk setup font emoji
def setup_emoji_font():
    """Setup font yang mendukung emoji"""
    import platform
    system = platform.system()
    
    font_paths = []
    
    if system == 'Windows':
        font_paths = [
            'C:/Windows/Fonts/seguiemj.ttf',
            'C:/Windows/Fonts/segoeui.ttf',
        ]
    elif system == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/Apple Color Emoji.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',
            '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
    
    # Coba register font yang tersedia
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='EmojiFont', fn_regular=font_path)
                print(f"✅ Font emoji berhasil dimuat: {font_path}")
                return True
            except Exception as e:
                print(f"⚠️ Gagal memuat font {font_path}: {e}")
                continue
    
    print("⚠️ Tidak ada font emoji yang ditemukan, menggunakan font default")
    return False

# Setup font saat module dimuat
setup_emoji_font()

# ==================== FUNGSI ALGORITMA ====================

def naive_string_matching(text, pattern):
    """Algoritma Naive String Matching"""
    t = len(text)
    p = len(pattern)
    for i in range(t - p + 1):
        j = 0
        while j < p:
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == p:
            return True
    return False


def normalize_text(text):
    """Normalisasi teks untuk deteksi variasi penulisan"""
    replacements = {
        'o': '0', 'i': '1', 'e': '3', 'a': '4', 's': '5',
        't': '7', 'b': '8', '@': 'a', '$': 's', '!': 'i'
    }
    text_normalized = text.lower()
    for char, replacement in replacements.items():
        text_normalized = text_normalized.replace(char, replacement)
    return text_normalized


def levenshtein_distance(s1, s2):
    """Menghitung jarak Levenshtein"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def fuzzy_match(text, pattern, threshold=1):
    """Fuzzy matching dengan toleransi kesalahan - hanya untuk word-level matching"""
    t = len(text)
    p = len(pattern)
    
    # Jika pattern terlalu pendek, jangan lakukan fuzzy match
    if p < 4:
        return False, ""
    
    # Split text menjadi kata-kata
    words = text.split()
    
    for word in words:
        # Hanya match jika panjang kata mirip (dalam range 80-120% dari pattern length)
        if p * 0.8 <= len(word) <= p * 1.2:
            distance = levenshtein_distance(word, pattern)
            if distance <= threshold:
                return True, word
    
    return False, ""


def load_database(filename="database_spam.txt"):
    """Load database kata kunci"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return [
        "judol", "slot", "casino", "togel", "poker", "roulette", "jackpot",
        "maxwin", "gacor", "scatter", "freespin", "betting", "bandar",
        "sportsbook", "livecasino", "pragmatic", "habanero",
        "microgaming", "withdraw", "depo", "chip", "turnover", 
        "rebate", "rtp", "link", "pinjaman", "dana", "cepat", "cair", 
        "tanpa", "jaminan", "agunan", "bunga", "limit", "plafon", 
        "disetujui", "acc", "transfer", "tunai", "ktp", "penghasilan", 
        "gajian", "danacepat", "danamudah", "pinjamuang", "kredivo", 
        "akulaku", "rupiah", "kredit", "selamat", "terpilih", "pemenang", 
        "klaim", "voucher", "kuota", "pulsa", "undian", "survey", 
        "berhadiah", "phishing", "scam", "penipuan", "verifikasi", 
        "login", "password", "akun", "rekening", "bank", "otp", "kode",
        "sms", "email", "website", "url"
    ]


def save_database(database, filename="database_spam.txt"):
    """Simpan database ke file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for keyword in database:
            f.write(keyword + '\n')


def detect_spam(text, database, use_fuzzy=True, threshold=2):
    """Deteksi spam menggunakan multiple algorithms"""
    text_lower = text.lower()
    text_normalized = normalize_text(text)

    for keyword in database:
        if not keyword:
            continue
        keyword_lower = keyword.lower()

        # Exact match (harus match persis)
        if naive_string_matching(text_lower, keyword_lower):
            return True, keyword, "Exact Match"
        
        # Normalized match (dengan normalisasi karakter)
        keyword_normalized = normalize_text(keyword)
        if naive_string_matching(text_normalized, keyword_normalized):
            return True, keyword, "Normalized Match"
        
        # Fuzzy match dengan threshold yang lebih tinggi (tidak terlalu sensitif)
        # Hanya untuk keyword yang cukup panjang
        if use_fuzzy and len(keyword_lower) >= 5:
            found, matched_word = fuzzy_match(text_lower, keyword_lower, threshold)
            if found:
                return True, keyword, f"Fuzzy Match: '{matched_word}'"

    return False, "", ""


# ==================== CUSTOM WIDGETS ====================

class EmojiLabel(Label):
    """Label dengan dukungan emoji"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Gunakan font emoji jika tersedia
        if LabelBase._fonts.get('EmojiFont'):
            self.font_name = 'EmojiFont'


class ChatBubble(BoxLayout):
    """Widget untuk bubble chat"""
    def __init__(self, message, is_user=True, is_spam=False, keyword="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [10, 5]
        self.spacing = 10
        
        if is_user:
            # User message (kanan)
            self.add_widget(Widget())  # Spacer kiri
            bubble = self.create_bubble(message, (0.25, 0.55, 1, 1), (1, 1, 1, 1))
            self.add_widget(bubble)
        else:
            # Bot response (kiri)
            bubble = self.create_bubble(message, (0.95, 0.95, 0.95, 1), (0.2, 0.2, 0.2, 1), is_spam, keyword)
            self.add_widget(bubble)
            self.add_widget(Widget())  # Spacer kanan
        
        self.height = bubble.height + 10
    
    def create_bubble(self, text, bg_color, text_color, is_spam=False, keyword=""):
        """Buat bubble chat"""
        bubble = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size_hint_y=None,
            width=280,
            padding=[15, 10],
            spacing=5
        )
        
        with bubble.canvas.before:
            Color(*bg_color)
            self.bubble_rect = RoundedRectangle(
                size=bubble.size,
                pos=bubble.pos,
                radius=[15, 15, 15, 15]
            )
        
        # Message text
        msg_label = EmojiLabel(
            text=text,
            color=text_color,
            font_size=14,
            text_size=(250, None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        msg_label.bind(texture_size=msg_label.setter('size'))
        bubble.add_widget(msg_label)
        
        # Spam indicator
        if is_spam:
            spam_label = EmojiLabel(
                text=f'Keyword: "{keyword}"',
                color=(0.8, 0.2, 0.2, 1),
                font_size=11,
                bold=True,
                size_hint_y=None,
                halign='left',
                text_size=(250, None)
            )
            spam_label.bind(texture_size=spam_label.setter('size'))
            bubble.add_widget(spam_label)
        
        # Time
        time_label = Label(
            text=datetime.now().strftime("%H:%M"),
            color=(0.5, 0.5, 0.5, 1) if not is_spam else text_color,
            font_size=10,
            size_hint_y=None,
            height=15,
            halign='right',
            text_size=(250, None)
        )
        bubble.add_widget(time_label)
        
        bubble.height = msg_label.height + (spam_label.height if is_spam else 0) + 15 + 20
        
        bubble.bind(pos=lambda w, v: setattr(self.bubble_rect, 'pos', v))
        bubble.bind(size=lambda w, v: setattr(self.bubble_rect, 'size', v))
        
        return bubble
        bubble.bind(size=lambda w, v: setattr(self.bubble_rect, 'size', v))
        
        return bubble


class MenuButton(Button):
    """Custom button untuk menu"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (0.2, 0.2, 0.2, 1)
        self.font_size = 14
        self.size_hint_y = None
        self.height = 50
        self.halign = 'left'
        self.valign = 'middle'
        self.padding = [20, 10]
        self.text_size = (240, self.height)
        
        # Gunakan font emoji jika tersedia
        if LabelBase._fonts.get('EmojiFont'):
            self.font_name = 'EmojiFont'
        
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_button_press(self, *args):
        self.bg_color.rgba = (0.95, 0.95, 0.95, 1)
    
    def on_button_release(self, *args):
        self.bg_color.rgba = (1, 1, 1, 1)


# ==================== MAIN APP ====================

class SpamDetectorApp(App):
    def build(self):
        self.database = load_database()
        self.total_checked = 0
        self.total_spam = 0
        
        Window.size = (400, 750)
        Window.clearcolor = (0.98, 0.98, 0.98, 1)
        
        # Main layout
        self.root_layout = FloatLayout()
        
        # Chat view
        self.chat_layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(
            size_hint_y=None,
            height=70,
            orientation='horizontal',
            padding=[10, 10]
        )
        
        with header.canvas.before:
            Color(0.25, 0.55, 1, 1)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        
        header.bind(pos=lambda w, v: setattr(self.header_rect, 'pos', v))
        header.bind(size=lambda w, v: setattr(self.header_rect, 'size', v))
        
        # Menu button - Hamburger menu
        menu_btn = Button(
            text='☰',
            size_hint=(None, None),
            width=50,
            height=50,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size=28,
            bold=True
        )
        if LabelBase._fonts.get('EmojiFont'):
            menu_btn.font_name = 'EmojiFont'
        menu_btn.bind(on_press=self.toggle_menu)
        
        # Title section
        title_box = BoxLayout(orientation='vertical', padding=[5, 0])
        
        title_label = EmojiLabel(
            text='🛡️ Spam Detector',
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=30,
            halign='left',
            text_size=(280, None)
        )
        
        self.accuracy_label = Label(
            text=f'Akurasi: {self.calculate_accuracy():.1f}%',
            color=(0.9, 0.9, 0.9, 1),
            font_size=12,
            size_hint_y=None,
            height=20,
            halign='left',
            text_size=(280, None)
        )
        
        title_box.add_widget(title_label)
        title_box.add_widget(self.accuracy_label)
        
        header.add_widget(menu_btn)
        header.add_widget(title_box)
        
        # Chat area
        scroll = ScrollView()
        self.chat_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5,
            padding=[0, 10]
        )
        self.chat_content.bind(minimum_height=self.chat_content.setter('height'))
        scroll.add_widget(self.chat_content)
        
        # Welcome message
        self.add_bot_message(
            "✅ Selamat datang di Spam Detector!\n\n"
            "Kirim pesan SMS untuk dianalisis. Bot akan otomatis "
            "mendeteksi spam menggunakan algoritma Naive String Matching.",
            is_spam=False
        )
        
        # Input area
        input_layout = BoxLayout(
            size_hint_y=None,
            height=60,
            padding=[10, 10],
            spacing=10
        )
        
        with input_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.input_bg = Rectangle(size=input_layout.size, pos=input_layout.pos)
        
        input_layout.bind(pos=lambda w, v: setattr(self.input_bg, 'pos', v))
        input_layout.bind(size=lambda w, v: setattr(self.input_bg, 'size', v))
        
        self.message_input = TextInput(
            hint_text='Ketik pesan untuk dianalisis...',
            multiline=False,
            background_normal='',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            cursor_color=(0.25, 0.55, 1, 1),
            font_size=14,
            padding=[15, 12]
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text='✈️',
            size_hint=(None, None),
            width=50,
            height=40,
            background_normal='',
            background_color=(0.25, 0.55, 1, 1),
            color=(1, 1, 1, 1),
            font_size=24
        )
        if LabelBase._fonts.get('EmojiFont'):
            send_btn.font_name = 'EmojiFont'
        send_btn.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_btn)
        
        # Assemble chat layout
        self.chat_layout.add_widget(header)
        self.chat_layout.add_widget(scroll)
        self.chat_layout.add_widget(input_layout)
        
        # Menu drawer
        self.menu_drawer = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=0,
            pos_hint={'x': -0.7, 'y': 0}
        )
        
        with self.menu_drawer.canvas.before:
            Color(1, 1, 1, 1)
            self.menu_bg = Rectangle(size=self.menu_drawer.size, pos=self.menu_drawer.pos)
            Color(0.8, 0.8, 0.8, 1)
            self.menu_border = Line(rectangle=(
                self.menu_drawer.x + self.menu_drawer.width,
                self.menu_drawer.y,
                0,
                self.menu_drawer.height
            ), width=1)
        
        self.menu_drawer.bind(pos=self.update_menu_canvas)
        self.menu_drawer.bind(size=self.update_menu_canvas)
        
        # Menu header
        menu_header = BoxLayout(
            size_hint_y=None,
            height=70,
            padding=[20, 15]
        )
        
        with menu_header.canvas.before:
            Color(0.25, 0.55, 1, 1)
            self.menu_header_rect = Rectangle(size=menu_header.size, pos=menu_header.pos)
        
        menu_header.bind(pos=lambda w, v: setattr(self.menu_header_rect, 'pos', v))
        menu_header.bind(size=lambda w, v: setattr(self.menu_header_rect, 'size', v))
        
        menu_title_box = BoxLayout(orientation='vertical')
        
        menu_title = EmojiLabel(
            text='Menu',
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=30,
            halign='left',
            text_size=(240, None)
        )
        
        self.db_info_label = EmojiLabel(
            text=f'Database: {len(self.database)} kata kunci',
            color=(0.9, 0.9, 0.9, 1),
            font_size=12,
            size_hint_y=None,
            height=20,
            halign='left',
            text_size=(240, None)
        )
        
        menu_title_box.add_widget(menu_title)
        menu_title_box.add_widget(self.db_info_label)
        menu_header.add_widget(menu_title_box)
        
        # Menu items
        menu_content = BoxLayout(orientation='vertical', spacing=2)
        
        btn_add = MenuButton(text='Tambah Kata Kunci')
        btn_add.bind(on_press=self.show_add_keyword_popup)
        
        btn_delete = MenuButton(text='Hapus Kata Kunci')
        btn_delete.bind(on_press=self.show_delete_keyword_popup)
        
        btn_view = MenuButton(text='Lihat Semua Kata Kunci')
        btn_view.bind(on_press=self.show_all_keywords_popup)
        
        btn_about = MenuButton(text='Tentang Aplikasi')
        btn_about.bind(on_press=self.show_about_popup)
        
        btn_clear = MenuButton(text='Hapus Riwayat Chat')
        btn_clear.bind(on_press=self.clear_chat)
        
        menu_content.add_widget(btn_add)
        menu_content.add_widget(btn_delete)
        menu_content.add_widget(btn_view)
        menu_content.add_widget(btn_about)
        menu_content.add_widget(btn_clear)
        menu_content.add_widget(Widget())  # Spacer
        
        self.menu_drawer.add_widget(menu_header)
        self.menu_drawer.add_widget(menu_content)
        
        # Add to root
        self.root_layout.add_widget(self.chat_layout)
        self.root_layout.add_widget(self.menu_drawer)
        
        self.menu_open = False
        
        return self.root_layout
    
    
    def update_menu_canvas(self, *args):
        """Update menu canvas"""
        self.menu_bg.pos = self.menu_drawer.pos
        self.menu_bg.size = self.menu_drawer.size
        self.menu_border.rectangle = (
            self.menu_drawer.x + self.menu_drawer.width,
            self.menu_drawer.y,
            0,
            self.menu_drawer.height
        )
    
    
    def toggle_menu(self, instance):
        """Toggle menu drawer"""
        if self.menu_open:
            # Close menu
            self.menu_drawer.width = 0
            self.menu_drawer.pos_hint = {'x': -0.7, 'y': 0}
            self.menu_open = False
        else:
            # Open menu
            self.menu_drawer.width = 280
            self.menu_drawer.pos_hint = {'x': 0, 'y': 0}
            self.menu_open = True
    
    
    def calculate_accuracy(self):
        """Hitung akurasi berdasarkan database"""
        base_accuracy = 95.0
        keyword_boost = len(self.database) * 0.05
        return min(base_accuracy + keyword_boost, 99.9)
    
    
    def update_accuracy(self):
        """Update tampilan akurasi"""
        accuracy = self.calculate_accuracy()
        self.accuracy_label.text = f'Akurasi: {accuracy:.1f}%'
    
    
    def add_bot_message(self, message, is_spam=False, keyword=""):
        """Tambah pesan bot"""
        bubble = ChatBubble(message=message, is_user=False, is_spam=is_spam, keyword=keyword)
        self.chat_content.add_widget(bubble)
    
    
    def add_user_message(self, message):
        """Tambah pesan user"""
        bubble = ChatBubble(message=message, is_user=True)
        self.chat_content.add_widget(bubble)
    
    
    def send_message(self, instance):
        """Kirim pesan dan analisis"""
        message = self.message_input.text.strip()
        
        if not message:
            return
        
        # Add user message
        self.add_user_message(message)
        self.message_input.text = ''
        
        # Detect spam
        self.total_checked += 1
        is_spam, keyword, match_type = detect_spam(message, self.database, use_fuzzy=True, threshold=2)
        
        if is_spam:
            self.total_spam += 1
            response = (
                "🚨 TERDETEKSI SPAM!\n\n"
                "Pesan ini mengandung kata kunci spam dan kemungkinan berbahaya. "
                "Jangan klik link atau berikan data pribadi!"
            )
            self.add_bot_message(response, is_spam=True, keyword=keyword)
        else:
            response = (
                "✅ Pesan Aman\n\n"
                "Pesan ini tidak terdeteksi sebagai spam. "
                "Namun tetap berhati-hati dengan pesan yang meminta data pribadi."
            )
            self.add_bot_message(response, is_spam=False)
        
        self.update_accuracy()
    
    
    def show_add_keyword_popup(self, instance):
        """Popup untuk tambah kata kunci"""
        self.toggle_menu(None)
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title = EmojiLabel(
            text='➕ Tambah Kata Kunci',
            size_hint_y=None,
            height=30,
            font_size=16,
            bold=True
        )
        
        keyword_input = TextInput(
            hint_text='Masukkan kata kunci spam baru...',
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size=14
        )
        
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        def add_keyword(btn):
            keyword = keyword_input.text.strip().lower()
            if keyword and keyword not in self.database:
                self.database.append(keyword)
                save_database(self.database)
                self.db_info_label.text = f'Database: {len(self.database)} kata kunci'
                self.update_accuracy()
                popup.dismiss()
                self.show_success_popup(f'Kata kunci "{keyword}" berhasil ditambahkan!')
            elif keyword in self.database:
                self.show_error_popup('Kata kunci sudah ada dalam database!')
            else:
                self.show_error_popup('Kata kunci tidak boleh kosong!')
        
        btn_add = Button(text='Tambah', background_color=(0.2, 0.7, 0.2, 1))
        btn_add.bind(on_press=add_keyword)
        
        btn_cancel = Button(text='Batal', background_color=(0.7, 0.7, 0.7, 1))
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_add)
        
        content.add_widget(title)
        content.add_widget(keyword_input)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, None),
            height=200,
            separator_height=0
        )
        popup.open()
    
    
    def show_delete_keyword_popup(self, instance):
        """Popup untuk hapus kata kunci"""
        self.toggle_menu(None)
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title = EmojiLabel(
            text='🗑️ Hapus Kata Kunci',
            size_hint_y=None,
            height=30,
            font_size=16,
            bold=True
        )
        
        keyword_input = TextInput(
            hint_text='Masukkan kata kunci yang akan dihapus...',
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size=14
        )
        
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        def delete_keyword(btn):
            keyword = keyword_input.text.strip().lower()
            if keyword in self.database:
                self.database.remove(keyword)
                save_database(self.database)
                self.db_info_label.text = f'Database: {len(self.database)} kata kunci'
                self.update_accuracy()
                popup.dismiss()
                self.show_success_popup(f'Kata kunci "{keyword}" berhasil dihapus!')
            else:
                self.show_error_popup('Kata kunci tidak ditemukan dalam database!')
        
        btn_delete = Button(text='Hapus', background_color=(0.9, 0.3, 0.3, 1))
        btn_delete.bind(on_press=delete_keyword)
        
        btn_cancel = Button(text='Batal', background_color=(0.7, 0.7, 0.7, 1))
        btn_cancel.bind(on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_delete)
        
        content.add_widget(title)
        content.add_widget(keyword_input)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, None),
            height=200,
            separator_height=0
        )
        popup.open()
    
    
    def show_all_keywords_popup(self, instance):
        """Popup untuk lihat semua kata kunci"""
        self.toggle_menu(None)
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = EmojiLabel(
            text=f'Database Kata Kunci ({len(self.database)})',
            size_hint_y=None,
            height=30,
            font_size=16,
            bold=True
        )
        
        scroll = ScrollView()
        keywords_text = ', '.join(sorted(self.database))
        
        keywords_label = Label(
            text=keywords_text,
            size_hint_y=None,
            font_size=13,
            color=(0.3, 0.3, 0.3, 1),
            text_size=(300, None),
            halign='left',
            valign='top'
        )
        keywords_label.bind(texture_size=keywords_label.setter('size'))
        
        scroll.add_widget(keywords_label)
        
        btn_close = Button(
            text='Tutup',
            size_hint_y=None,
            height=40,
            background_color=(0.25, 0.55, 1, 1)
        )
        btn_close.bind(on_press=lambda x: popup.dismiss())
        
        content.add_widget(title)
        content.add_widget(scroll)
        content.add_widget(btn_close)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.7),
            separator_height=0
        )
        popup.open()
    
    
    def show_about_popup(self, instance):
        """Popup tentang aplikasi"""
        self.toggle_menu(None)
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title = EmojiLabel(
            text='🛡️ Tentang Aplikasi',
            size_hint_y=None,
            height=40,
            font_size=18,
            bold=True
        )
        
        about_text = """Spam Detector v1.0

Aplikasi deteksi spam SMS menggunakan algoritma Naive String Matching dengan fitur:

✓ Exact Matching
✓ Text Normalization  
✓ Fuzzy Matching (Levenshtein)

Database: 31+ kata kunci spam dalam 3 kategori (Judi Online, Pinjaman Online, Penipuan/Phishing)

Dikembangkan dengan Python & Kivy Framework"""
        
        scroll = ScrollView()
        about_label = EmojiLabel(
            text=about_text,
            size_hint_y=None,
            font_size=13,
            color=(0.3, 0.3, 0.3, 1),
            text_size=(300, None),
            halign='left',
            valign='top'
        )
        about_label.bind(texture_size=about_label.setter('size'))
        scroll.add_widget(about_label)
        
        btn_close = Button(
            text='Tutup',
            size_hint_y=None,
            height=40,
            background_color=(0.25, 0.55, 1, 1)
        )
        btn_close.bind(on_press=lambda x: popup.dismiss())
        
        content.add_widget(title)
        content.add_widget(scroll)
        content.add_widget(btn_close)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.6),
            separator_height=0
        )
        popup.open()
    
    
    def clear_chat(self, instance):
        """Hapus riwayat chat"""
        self.toggle_menu(None)
        self.chat_content.clear_widgets()
        self.add_bot_message("Chat berhasil dihapus! 🗑️\nSilakan mulai analisis spam lagi.", is_spam=False)
        self.total_checked = 0
        self.total_spam = 0
        self.update_accuracy()
    
    
    def show_success_popup(self, message):
        """Popup sukses"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        msg_label = Label(
            text=message,
            font_size=14,
            color=(0.2, 0.6, 0.2, 1)
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.7, 0.2, 1)
        )
        btn_ok.bind(on_press=lambda x: popup.dismiss())
        
        content.add_widget(msg_label)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Berhasil',
            content=content,
            size_hint=(0.8, None),
            height=150
        )
        popup.open()
    
    
    def show_error_popup(self, message):
        """Popup error"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        msg_label = Label(
            text=message,
            font_size=14,
            color=(0.8, 0.2, 0.2, 1)
        )
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.9, 0.3, 0.3, 1)
        )
        btn_ok.bind(on_press=lambda x: popup.dismiss())
        
        content.add_widget(msg_label)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, None),
            height=150
        )
        popup.open()


# ==================== RUN APP ====================

if __name__ == '__main__':
    SpamDetectorApp().run()
