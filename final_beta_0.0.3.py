import kivy
import requests
import json
import os
import io
import time
from datetime import datetime
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.resources import resource_find
from kivy.utils import platform
from jnius import autoclass
if platform == 'android':
    try:
        import android
        from android.permissions import request_permissions, Permission
    except ImportError:
        print("Android 모듈 로딩 실패 (PC 환경일 수 있음)")
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Uri = autoclass('android.net.Uri')
    File = autoclass('java.io.File')
    FileInputStream = autoclass('java.io.FileInputStream')
    ContentResolver = autoclass('android.content.ContentResolver')
    FileOutputStream = autoclass('java.io.FileOutputStream')
    FileDescriptor = autoclass('java.io.FileDescriptor') 
    Intent = autoclass('android.content.Intent')
    activity = PythonActivity.mActivity
    activity = PythonActivity.mActivity

try:
    from plyer import filechooser
except ImportError:
    class MockFileChooser:
        def open_file(self, *args, **kwargs):
            Popup(title='알림', content=Label(text='PC에서는 지원되지 않는 기능입니다.', font_name='NanumFont'), size_hint=(0.8, 0.3)).open()
        def on_selection(self, *args): pass
    filechooser = MockFileChooser()

if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from android.os import Build
    except ImportError:
        class MockPermission:
            READ_EXTERNAL_STORAGE = "READ_EXTERNAL_STORAGE"
            WRITE_EXTERNAL_STORAGE = "WRITE_EXTERNAL_STORAGE"
            READ_MEDIA_IMAGES = "READ_MEDIA_IMAGES"
        Permission = MockPermission()
        Build = type('Build', (object,), {'VERSION': type('VERSION', (object,), {'SDK_INT': 21})}) 
        def request_permissions(permissions_list, callback=None):
            if callback: callback(permissions_list, [True] * len(permissions_list))
else:
    class MockPermission:
        READ_EXTERNAL_STORAGE = "READ_EXTERNAL_STORAGE"
        WRITE_EXTERNAL_STORAGE = "WRITE_EXTERNAL_STORAGE"
        READ_MEDIA_IMAGES = "READ_MEDIA_IMAGES"
    Permission = MockPermission()
    Build = type('Build', (object,), {'VERSION': type('VERSION', (object,), {'SDK_INT': 21})}) 
    def request_permissions(permissions_list, callback=None):
        if callback: callback(permissions_list, [True] * len(permissions_list))

kivy.require('1.11.1')

FB_API_KEY = "AIzaSyB5LXKty5tRMB3PB4CEgiP6Cb2eXlO5xxo"
FB_DB_URL = "https://campus-life-management-default-rtdb.firebaseio.com"
FB_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
FB_STORAGE_BUCKET = "campus-life-management.firebasestorage.app"

FONT_NAME = 'NanumFont'
FONT_PATH = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')

try:
    LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
except Exception as e:
    print(f"폰트 등록 오류: {e}")
    FONT_NAME = None

temp_image = resource_find('data/logo/kivy-icon-256.png')
DEFAULT_IMAGE = temp_image if temp_image else ''


class WrappedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.halign = 'left'
        self.valign = 'middle'
        self.color = [0, 0, 0, 1]
        
        self.bind(width=self.update_text_size)
        self.bind(texture_size=self.update_height)

    def update_text_size(self, *args):
        self.text_size = (self.width, None)

    def update_height(self, *args):
        self.height = self.texture_size[1]


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.radius = [dp(10)]
        self.halign = 'center'
        self.valign = 'middle'
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width - dp(20), None)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color) if hasattr(self, 'bg_color') else Color(0.5, 0.5, 0.5, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

def get_styled_button(text, bg_color, text_color, font_size='22sp'):
    btn = RoundedButton(
        text=text,
        font_size=font_size,
        font_name=FONT_NAME,
        color=text_color,
        size_hint_y=None,
        height=dp(60)
    )
    btn.bg_color = bg_color
    return btn

class ClubListItem(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(ClubListItem, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(15)
        self.spacing = dp(5)
        
        self.height = dp(80)
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(minimum_height=self.setter('height'))

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        

class FirebaseREST:
    @staticmethod
    def login(email, password):
        url = f"{FB_AUTH_URL}:signInWithPassword?key={FB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code != 200:
                try: return {"error": res.json().get("error", {"message": f"HTTP {res.status_code}"})}
                except: return {"error": {"message": f"HTTP {res.status_code}"}}
            return res.json()
        except Exception as e:
            return {"error": {"message": str(e)}}

    @staticmethod
    def signup(email, password):
        url = f"{FB_AUTH_URL}:signUp?key={FB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code != 200:
                 try: return {"error": res.json().get("error", {"message": f"HTTP {res.status_code}"})}
                 except: return {"error": {"message": f"HTTP {res.status_code}"}}
            return res.json()
        except Exception as e:
            return {"error": {"message": str(e)}}

    @staticmethod
    def send_email_verification(id_token):
        url = f"{FB_AUTH_URL}:sendOobCode?key={FB_API_KEY}"
        payload = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
        try: 
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code != 200:
                return {"error": {"message": f"전송 실패({res.status_code}): {res.text}"}}
            return {"success": True}
        except Exception as e:
            return {"error": {"message": f"통신 오류: {str(e)}"}}

    @staticmethod
    def get_user_info(id_token):
        url = f"{FB_AUTH_URL}:lookup?key={FB_API_KEY}"
        payload = {"idToken": id_token}
        try:
            res = requests.post(url, json=payload, timeout=10)
            return res.json() if res.status_code == 200 else {}
        except: return {}

    @staticmethod
    def db_get(path, token=None):
        url = f"{FB_DB_URL}/{path}.json"
        if token: url += f"?auth={token}"
        try:
            res = requests.get(url, timeout=10)
            return res.json() if res.status_code == 200 else None
        except: return None

    @staticmethod
    def db_put(path, data, token):
        url = f"{FB_DB_URL}/{path}.json?auth={token}"
        try:
            res = requests.put(url, json=data, timeout=10)
            return res.json() if res.status_code == 200 else {}
        except: return {}

    @staticmethod
    def db_post(path, data, token):
        url = f"{FB_DB_URL}/{path}.json?auth={token}"
        try:
            res = requests.post(url, json=data, timeout=10)
            return res.json() if res.status_code == 200 else {}
        except: return {}

    @staticmethod
    def db_delete(path, token):
        url = f"{FB_DB_URL}/{path}.json?auth={token}"
        try: requests.delete(url, timeout=10)
        except: pass
    
    @staticmethod
    def db_update(path, data, token):
        url = f"{FB_DB_URL}/{path}.json?auth={token}"
        try:
            res = requests.patch(url, json=data, timeout=10)
            return res.json() if res.status_code == 200 else {}
        except: return {}
    
    # Content URI에서 바이트를 읽어와 업로드하는 함수 (pyjnius 및 os.read 사용)
    @staticmethod
    def upload_image_from_uri(content_uri, filename_base):
        """
        PC: 일반 파일 경로를 사용하여 업로드
        Android: Content URI와 ParcelFileDescriptor를 사용하여 업로드
        """
        
        # ---------------------------------------------------------
        #  PC 환경 - 테스트용
        # ---------------------------------------------------------
        if platform != 'android':
            print(f"[PC] 파일 업로드 시도: {content_uri}")

            # 확장자 추출 (기본값 .jpg)
            ext = os.path.splitext(content_uri)[1]
            if not ext: ext = ".jpg"
            
            full_filename = f"{filename_base}_{int(time.time())}{ext}"
            
            # 기존에 정의된 일반 파일 업로드 함수(upload_image) 호출
            return FirebaseREST.upload_image(content_uri, full_filename)

        # ---------------------------------------------------------
        # Android 환경 - 실전용
        # ---------------------------------------------------------
        if platform == 'android':
            try:
                # Java 클래스 로딩
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                Uri = autoclass('android.net.Uri')
                activity = PythonActivity.mActivity
                
                # ContentResolver로 데이터 읽기
                uri = Uri.parse(content_uri)
                content_resolver = activity.getContentResolver()
                mime_type = content_resolver.getType(uri) or 'image/jpeg'
                
                # 확장자 결정
                ext = '.jpeg'
                if 'png' in mime_type: ext = '.png'
                elif 'gif' in mime_type: ext = '.gif'
                
                full_filename = f"{filename_base}_{int(time.time())}{ext}"
                cloud_path = f"images/{full_filename}"
                
                input_stream = content_resolver.openInputStream(uri)
                ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
                buffer_stream = ByteArrayOutputStream()
                
                # 버퍼 읽기 (Java 방식)
                byte_array = bytearray(4096)
                pfd = content_resolver.openFileDescriptor(uri, "r")
                fd = pfd.getFd()
                import os
                stream_fd = os.dup(fd)
                
                image_data = b""
                while True:
                    chunk = os.read(stream_fd, 1024 * 8)
                    if not chunk: break
                    image_data += chunk
                
                os.close(stream_fd)

                # Firebase Storage 업로드 요청
                upload_url = f"https://firebasestorage.googleapis.com/v0/b/{FB_STORAGE_BUCKET}/o?name={cloud_path}"
                headers = {"Content-Type": mime_type}
                
                res = requests.post(upload_url, data=image_data, headers=headers, timeout=30)
                
                if res.status_code == 200:
                    data = res.json()
                    token = data.get('downloadTokens')
                    import urllib.parse
                    encoded_path = urllib.parse.quote(cloud_path, safe='')
                    return f"https://firebasestorage.googleapis.com/v0/b/{FB_STORAGE_BUCKET}/o/{encoded_path}?alt=media&token={token}"
                else:
                    print(f"업로드 실패: {res.text}")
                    return ""
            except Exception as e:
                print(f"Android 업로드 에러: {e}")
                return ""
        else:
            # PC 등 Android가 아닐 때
            return FirebaseREST.upload_image(content_uri, filename_base + ".jpg")

    @staticmethod
    def upload_image(local_path, filename):
        """일반 파일 경로에서 읽어와 Firebase Storage에 업로드"""
        url = f"https://firebasestorage.googleapis.com/v0/b/{FB_STORAGE_BUCKET}/o?name=images%2F{filename}"
        try:
            with open(local_path, 'rb') as f: image_data = f.read()
            headers = {"Content-Type": "image/jpeg"}
            res = requests.post(url, data=image_data, headers=headers, timeout=20)
            if res.status_code == 200:
                data = res.json()
                token = data.get('downloadTokens')
                return f"https://firebasestorage.googleapis.com/v0/b/{FB_STORAGE_BUCKET}/o/images%2F{filename}?alt=media&token={token}"
            return ""
        except: return ""
        

def get_rounded_textinput(hint_text, password=False, input_type='text'):
    return TextInput(
        hint_text=hint_text,
        multiline=False,
        password=password,
        font_size='18sp',
        font_name=FONT_NAME,
        padding=[dp(15), dp(10), dp(15), dp(10)],
        size_hint_y=None,
        height=dp(55),
        background_normal='',
        background_color=[1, 1, 1, 1],
        foreground_color=[0, 0, 0, 1],
        input_type=input_type
    )



class LostItemListItem(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(LostItemListItem, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = dp(10)
        self.spacing = dp(10)
        self.height = dp(120)

        with self.canvas.before:
            Color(0.95, 0.95, 0.8, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(minimum_height=self.update_height)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_height(self, *args):
        self.height = max(self.minimum_height, dp(120))

class WhiteBgScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name

class MainScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        root_float = FloatLayout()
        main_content = BoxLayout(orientation='vertical', padding=[dp(20), dp(100), dp(20), dp(80)], spacing=dp(25))

        main_content.add_widget(WrappedLabel(
            text="[b]Campus Link 메인[/b]", 
            font_size='38sp', 
            color=[0.1, 0.4, 0.7, 1],
            font_name=FONT_NAME, 
            markup=True, 
            halign='center'
        ))

        self.welcome_label = WrappedLabel(
            text="환영합니다! 어떤 정보가 필요하신가요?", 
            font_size='18sp',
            font_name=FONT_NAME, 
            color=[0.5, 0.5, 0.5, 1], 
            halign='center'
        )
        main_content.add_widget(self.welcome_label)
        
        main_content.add_widget(Label(size_hint_y=None, height=dp(10)))

        nav_layout = BoxLayout(orientation='vertical', spacing=dp(15))

        def create_nav_button(text, screen_name, bg_color):
            btn = get_styled_button(text, bg_color, [1, 1, 1, 1], font_size='24sp')
            btn.bind(on_press=lambda *args: self.go_to_screen(screen_name))
            return btn

        nav_layout.add_widget(create_nav_button("동아리 게시판", 'club', [0.0, 0.2, 0.6, 1]))
        nav_layout.add_widget(create_nav_button("분실물 게시판", 'lost_found', [0.2, 0.6, 1, 1]))

        main_content.add_widget(nav_layout)
        main_content.add_widget(Label())
        root_float.add_widget(main_content)

        settings_button = Button(
            text="설정", font_size='18sp', font_name=FONT_NAME, background_normal='',
            background_color=[0, 0, 0, 0], color=[0.1, 0.4, 0.7, 1],
            size_hint=(None, None), size=(dp(90), dp(50)), pos_hint={'right': 1, 'top': 1},
        )
        settings_button.bind(on_press=self.show_settings_popup)
        root_float.add_widget(settings_button)
        self.add_widget(root_float)

    def on_enter(self, *args):
        app = App.get_running_app()
        self.welcome_label.text = f"환영합니다, {app.current_user_nickname}님! 어떤 정보가 필요하신가요?"

    def show_settings_popup(self, instance):
        app = App.get_running_app()
        popup = Popup(title="", separator_height=0, size_hint=(0.85, 0.7), 
                      pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                      auto_dismiss=True, background='')
        
        full_popup_content = BoxLayout(orientation='vertical')
        with full_popup_content.canvas.before:
            Color(1, 1, 1, 1)
            content_bg = Rectangle(size=full_popup_content.size, pos=full_popup_content.pos)
        full_popup_content.bind(size=lambda i, v: setattr(content_bg, 'size', v), pos=lambda i, v: setattr(content_bg, 'pos', v))

        BLUE_STRIPE_COLOR = [0.1, 0.4, 0.7, 1]
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[dp(10), 0, dp(10), 0])
        with header.canvas.before:
            Color(*BLUE_STRIPE_COLOR)
            header_bg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda i, v: setattr(header_bg, 'size', v), pos=lambda i, v: setattr(header_bg, 'pos', v))

        close_button = Button(text="X", font_size='22sp', size_hint=(None, 1), width=dp(40), color=[1, 1, 1, 1], background_normal='', background_color=[0, 0, 0, 0])
        close_button.bind(on_press=popup.dismiss)
        header.add_widget(close_button)
        header.add_widget(Label(text="[b]앱 설정[/b]", font_name=FONT_NAME, color=[1, 1, 1, 1], markup=True, font_size='22sp'))
        full_popup_content.add_widget(header)

        content_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        info_label = WrappedLabel(
            text=f"[b]Campus Link 계정[/b]\n\n{app.current_user_nickname}님\n({app.current_user})\n\n앱 설정 및 정보",
            font_size='18sp', font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True,
            halign='center'
        )
        content_layout.add_widget(info_label)

        if app.current_user_role == 'admin':
            admin_button = get_styled_button("관리자 메뉴", [0.2, 0.4, 0.8, 1], [1, 1, 1, 1], font_size='18sp')
            admin_button.height = dp(50)
            def go_to_admin_menu(instance):
                self.manager.current = 'admin_main'
                popup.dismiss()
            admin_button.bind(on_press=go_to_admin_menu)
            content_layout.add_widget(admin_button)

        my_items_button = get_styled_button("내 등록 물품 관리", [0.5, 0.7, 0.9, 1], [1, 1, 1, 1], font_size='18sp')
        my_items_button.height = dp(50)
        def go_to_my_items(instance):
            self.manager.current = 'claim_management'
            popup.dismiss()
        my_items_button.bind(on_press=go_to_my_items)
        content_layout.add_widget(my_items_button)

        my_claims_button = get_styled_button("내 신청 현황", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1], font_size='18sp')
        my_claims_button.height = dp(50)
        def go_to_my_claims(instance):
            self.manager.current = 'my_claims'
            popup.dismiss()
        my_claims_button.bind(on_press=go_to_my_claims)
        content_layout.add_widget(my_claims_button)
        
        content_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        logout_button = get_styled_button("로그아웃", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])
        logout_button.height = dp(50)
        content_layout.add_widget(logout_button)
        
        full_popup_content.add_widget(content_layout)
        popup.content = full_popup_content

        def perform_logout(btn_instance):
            app = App.get_running_app()
            app.current_user = 'guest'
            app.current_user_nickname = 'Guest'
            app.current_user_role = 'guest'
            app.user_token = None
            app.current_user_uid = None
            self.manager.current = 'login'
            login_screen = self.manager.get_screen('login')
            if login_screen:
                login_screen.username_input.text = ''
                login_screen.password_input.text = ''
            popup.dismiss()
        
        logout_button.bind(on_press=perform_logout)
        popup.open()

class AdminMainScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        main_layout.add_widget(Label(
            text="[b]관리자 메뉴[/b]", font_size='38sp', color=[0.7, 0.1, 0.1, 1],
            font_name=FONT_NAME, markup=True, size_hint_y=None, height=dp(70)
        ))
        main_layout.add_widget(Label(size_hint_y=0.2))
        approval_button = get_styled_button("동아리 개설 관리", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        approval_button.bind(on_press=lambda *args: self.go_to_screen('club_approval'))
        main_layout.add_widget(approval_button)
        item_approval_button = get_styled_button("분실물 등록 관리", [1, 0.5, 0.3, 1], [1, 1, 1, 1])
        item_approval_button.bind(on_press=lambda *args: self.go_to_screen('item_approval'))
        main_layout.add_widget(item_approval_button)
        claim_approval_button = get_styled_button("물품 신청(소유권) 관리", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])
        claim_approval_button.bind(on_press=lambda *args: self.go_to_screen('admin_claim_approval'))
        main_layout.add_widget(claim_approval_button)
        main_layout.add_widget(Label())
        back_button = get_styled_button("메인 화면으로", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1])
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        main_layout.add_widget(back_button)
        self.add_widget(main_layout)

class AdminClaimApprovalScreen(WhiteBgScreen):
    """관리자가 사용자의 물품 신청(소유권)을 승인/거절하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]물품 신청 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        self.main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll_view.add_widget(self.grid)
        self.main_layout.add_widget(scroll_view)

        self.refresh_list()

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        app = App.get_running_app()
        if not app.user_token: return

        try:
            claims_dict = FirebaseREST.db_get("claims", app.user_token)
            all_claims = list(claims_dict.values()) if claims_dict else []
            items_dict = FirebaseREST.db_get("all_items", app.user_token)
            all_items = list(items_dict.values()) if items_dict else []
        except:
            all_claims = []
            all_items = []

        pending_claims = [c for c in all_claims if 'status' not in c or c['status'] == 'pending']

        if not pending_claims:
            self.grid.add_widget(Label(text="검토 대기 중인 신청이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        for claim in pending_claims:
            item_id = claim.get('item_id')
            item = next((i for i in all_items if i.get('item_id') == item_id), None)
            if not item: continue

            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            item_box.bind(minimum_height=item_box.setter('height'))
            with item_box.canvas.before:
                Color(0.95, 0.95, 0.8, 1)
                self.bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
            item_box.bind(pos=lambda i, v: setattr(self.bg_rect, 'pos', v), size=lambda i, v: setattr(self.bg_rect, 'size', v))

            item_box.add_widget(WrappedLabel(text=f"[b]물품명:[/b] {item['name']}", color=[0,0,0,1], markup=True))
            item_box.add_widget(WrappedLabel(text=f"[b]신청자:[/b] {claim.get('claimer_nickname', '알 수 없음')} ({claim.get('claimer_id')})", color=[0,0,0,1], markup=True))
            item_box.add_widget(Label(size_hint_y=None, height=dp(10)))
            
            item_box.add_widget(WrappedLabel(text=f"[b]등록자(Finder)가 올린 정보:[/b]", color=[0.1, 0.4, 0.7, 1], markup=True))
            item_box.add_widget(WrappedLabel(text=f"  - (장소): {item['loc']}", color=[0.1, 0.4, 0.7, 1]))
            item_box.add_widget(WrappedLabel(text=f"  - (상세): {item.get('desc', '없음')}", color=[0.1, 0.4, 0.7, 1]))
            item_box.add_widget(Label(size_hint_y=None, height=dp(10)))
            
            item_box.add_widget(WrappedLabel(text=f"[b]신청자(Claimer)가 입력한 [상세 특징]:[/b]", color=[0.8, 0.2, 0.2, 1], markup=True))
            item_box.add_widget(WrappedLabel(text=f"{claim.get('verification_details', 'N/A')}", color=[0.8, 0.2, 0.2, 1]))
            item_box.add_widget(Label(size_hint_y=None, height=dp(15)))

            button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            approve_btn = Button(text="전달 완료 (승인)", font_name=FONT_NAME, background_color=[0.2, 0.8, 0.2, 1])
            approve_btn.claim = claim
            approve_btn.item = item
            approve_btn.bind(on_press=self.approve_claim)
            reject_btn = Button(text="신청 거절", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1])
            reject_btn.claim = claim
            reject_btn.item = item
            reject_btn.bind(on_press=self.reject_claim)
            button_layout.add_widget(approve_btn)
            button_layout.add_widget(reject_btn)
            item_box.add_widget(button_layout)
            self.grid.add_widget(item_box)

    def approve_claim(self, instance):
        app = App.get_running_app()
        claim = instance.claim
        item = instance.item
        pickup_location = "학생복지처"
        item['status'] = 'found_returned'
        claim['status'] = 'approved'
        claim['finder_contact'] = pickup_location
        try:
            FirebaseREST.db_put(f"all_items/{item['item_id']}", item, app.user_token)
            FirebaseREST.db_put(f"claims/{claim['claim_id']}", claim, app.user_token)
            popup_message = f"승인이 완료되었습니다.\n\n신청자('{claim.get('claimer_nickname')}')에게\n'{pickup_location}' 수령이 안내됩니다."
            popup = Popup(title='[b]승인 완료[/b]', title_font=FONT_NAME, content=Label(text=popup_message, font_name=FONT_NAME, markup=True, padding=dp(10)), size_hint=(0.9, 0.4))
            popup.bind(on_dismiss=self.refresh_list)
            popup.open()
        except Exception as e:
             Popup(title='DB 오류', content=Label(text=f'승인 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def reject_claim(self, instance):
        app = App.get_running_app()
        claim = instance.claim
        item = instance.item
        item['status'] = 'found_available'
        claim['status'] = 'rejected'
        try:
            FirebaseREST.db_put(f"all_items/{item['item_id']}", item, app.user_token)
            FirebaseREST.db_put(f"claims/{claim['claim_id']}", claim, app.user_token)
            self.refresh_list()
        except Exception as e:
             Popup(title='DB 오류', content=Label(text=f'거절 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

class ClubApprovalScreen(WhiteBgScreen):
    """동아리 개설 신청을 관리하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        """화면에 들어올 때마다 UI를 새로 그림"""
        self.main_layout.clear_widgets()

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]동아리 개설 승인[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        self.main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.approval_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.approval_grid.bind(minimum_height=self.approval_grid.setter('height'))
        scroll_view.add_widget(self.approval_grid)
        self.main_layout.add_widget(scroll_view)

        self.refresh_approval_list()

    def refresh_approval_list(self, *args):
        app = App.get_running_app()
        if not app.user_token:
            self.update_approval_list([]) 
            return
            
        try:
            pending_node = FirebaseREST.db_get("pending_clubs", app.user_token)
            if pending_node:
                pending_list = list(pending_node.values())
                self.update_approval_list(pending_list)
            else:
                self.update_approval_list([])
        except Exception as e:
            self.update_approval_list([])

    def update_approval_list(self, pending_clubs):
        self.approval_grid.clear_widgets()
        if not pending_clubs:
            self.approval_grid.add_widget(Label(text="승인 대기 중인 동아리가 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
        else:
            for club_request in pending_clubs:
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100), padding=dp(10), spacing=dp(10))
                info_layout = BoxLayout(orientation='vertical')
                info_layout.add_widget(Label(text=f"[b]{club_request['name']}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, halign='left', valign='top'))
                info_layout.add_widget(Label(text=club_request['short_desc'], font_name=FONT_NAME, color=[0.3,0.3,0.3,1], halign='left', valign='top'))

                button_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
                approve_button = Button(text="수락", font_name=FONT_NAME, background_color=[0.2, 0.8, 0.2, 1])
                approve_button.club_data = club_request
                approve_button.bind(on_press=self.approve_club)

                reject_button = Button(text="거절", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1])
                reject_button.club_data = club_request
                reject_button.bind(on_press=self.reject_club)

                button_layout.add_widget(approve_button)
                button_layout.add_widget(reject_button)
                item_layout.add_widget(info_layout)
                item_layout.add_widget(button_layout)
                self.approval_grid.add_widget(item_layout)

    def approve_club(self, instance):
        approved_club = instance.club_data
        app = App.get_running_app()
        if not app.user_token: return
        club_id = approved_club.get('club_id')
        if not club_id: return
        try:
            FirebaseREST.db_put(f"all_clubs/{club_id}", approved_club, app.user_token)
            FirebaseREST.db_delete(f"pending_clubs/{club_id}", app.user_token)
            self.refresh_approval_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'승인 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def reject_club(self, instance):
        rejected_club = instance.club_data
        app = App.get_running_app()
        club_id = rejected_club.get('club_id')
        if not club_id: return
        try:
            FirebaseREST.db_delete(f"pending_clubs/{club_id}", app.user_token)
            self.refresh_approval_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'거절 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

class ItemApprovalScreen(WhiteBgScreen):
    """분실물 등록 신청을 관리하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]분실물 등록 승인[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        self.main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.approval_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.approval_grid.bind(minimum_height=self.approval_grid.setter('height'))
        scroll_view.add_widget(self.approval_grid)
        self.main_layout.add_widget(scroll_view)

        self.refresh_approval_list()

    def refresh_approval_list(self, *args):
        app = App.get_running_app()
        if not app.user_token:
            self.update_approval_list([])
            return
        try:
            pending = FirebaseREST.db_get("pending_items", app.user_token)
            items = list(pending.values()) if pending else []
            self.update_approval_list(items)
        except:
            self.update_approval_list([])

    def update_approval_list(self, pending_items):
        self.approval_grid.clear_widgets()
        if not pending_items:
            self.approval_grid.add_widget(Label(text="승인 대기 중인 게시물이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
        else:
            for item_request in pending_items:
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100), padding=dp(10), spacing=dp(10))

                img = AsyncImage(source=item_request.get('image', DEFAULT_IMAGE), size_hint_x=0.3, allow_stretch=True)
                info_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
                info_layout.add_widget(Label(text=f"[b]{item_request['name']}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, halign='left', valign='top'))
                info_layout.add_widget(Label(text=f"장소: {item_request['loc']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], halign='left', valign='top'))
                info_layout.add_widget(Label(text=f"시간: {item_request.get('time', 'N/A')}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], halign='left', valign='top'))

                button_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
                approve_button = Button(text="수락", font_name=FONT_NAME, background_color=[0.2, 0.8, 0.2, 1])
                approve_button.item_data = item_request
                approve_button.bind(on_press=self.approve_item)

                reject_button = Button(text="거절", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1])
                reject_button.item_data = item_request
                reject_button.bind(on_press=self.reject_item)

                button_layout.add_widget(approve_button)
                button_layout.add_widget(reject_button)

                item_layout.add_widget(img)
                item_layout.add_widget(info_layout)
                item_layout.add_widget(button_layout)
                self.approval_grid.add_widget(item_layout)

    def approve_item(self, instance):
        approved_item = instance.item_data
        app = App.get_running_app()
        if not app.user_token: return
        item_id = approved_item.get('item_id')
        if not item_id: return
        try:
            FirebaseREST.db_put(f"all_items/{item_id}", approved_item, app.user_token)
            FirebaseREST.db_delete(f"pending_items/{item_id}", app.user_token)
            self.check_keyword_notification(approved_item)
            self.refresh_approval_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'승인 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def reject_item(self, instance):
        rejected_item = instance.item_data
        app = App.get_running_app()
        if not app.user_token: return
        try:
            item_id = rejected_item.get('item_id')
            FirebaseREST.db_delete(f"pending_items/{item['item_id']}", app.user_token)
            self.refresh_approval_list()
        except: pass

    def check_keyword_notification(self, new_item):
        app = App.get_running_app()
        item_text = f"{new_item['name']} {new_item['desc']} {new_item['loc']} {new_item.get('time', '')}".lower()
        for keyword in app.notification_keywords:
            if keyword.lower() in item_text:
                Popup(title='키워드 알림', content=Label(text=f"키워드 '{keyword}' 포함\n'{new_item['name']}' 등록됨.", font_name=FONT_NAME), size_hint=(0.8, 0.4)).open()
                break


class ClaimManagementScreen(WhiteBgScreen):
    """ 내가 등록한 분실/습득물의 '상태'를 확인하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]내 등록 물품 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))

        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        app = App.get_running_app()
        if not app.user_token: return

        try:
            all_items_dict = FirebaseREST.db_get("all_items", app.user_token)
            my_items = []
            
            if all_items_dict:
                for item in all_items_dict.values():
                    reg_uid = item.get('registered_by_uid')
                    reg_id = item.get('registered_by_id')
                    
                    if reg_uid and reg_uid == app.current_user_uid:
                        my_items.append(item)
                    elif not reg_uid and reg_id == app.current_user:
                        my_items.append(item)
        except Exception:
             my_items = []

        if not my_items:
            self.grid.add_widget(Label(text="내가 등록한 물품이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        for item in my_items:
            item_id = item.get('item_id')
            item_status = item.get('status', 'unknown')
            
            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            item_box.bind(minimum_height=item_box.setter('height')) 

            with item_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
            
            item_box.bind(
                pos=lambda instance, value, r=bg_rect: setattr(r, 'pos', value),
                size=lambda instance, value, r=bg_rect: setattr(r, 'size', value)
            )

            item_box.add_widget(WrappedLabel(
                text=f"[b]{item.get('name', '이름 없음')}[/b]", 
                color=[0,0,0,1], markup=True, font_size='16sp'
            ))
            
            status_text = ""
            
            if item_status == 'found_pending':
                try:
                    claims_node = FirebaseREST.db_get("claims", app.user_token)
                    claims_dict = claims_node if claims_node else {}
                    claim = None
                    
                    for c in claims_dict.values():
                        if c.get('item_id') == item_id:
                            claim = c
                            break
                    
                    if claim:
                        status_text = f"[color=A01010]관리자 검토 중[/color]\n신청자: {claim.get('claimer_nickname', '알 수 없음')}"
                        item_box.add_widget(WrappedLabel(text=status_text, color=[0,0,0,1], markup=True))
                    else:
                        status_text = "[color=1010A0]신청 가능[/color]"
                        item_box.add_widget(WrappedLabel(text=status_text, color=[0,0,0,1], markup=True))
                except:
                    pass

            elif item_status == 'found_available':
                status_text = "[color=1010A0]신청 가능[/color] (대기중인 신청 없음)"
                item_box.add_widget(WrappedLabel(text=status_text, color=[0.3,0.3,0.3,1], markup=True))
            
            elif item_status == 'found_returned':
                item_box.add_widget(WrappedLabel(
                    text="[color=008000][b]교차 검증 승인됨[/b][/color]", 
                    color=[1, 1, 1, 1], markup=True
                ))
                item_box.add_widget(WrappedLabel(
                    text="(학생복지처에 물품을 인계해주세요)", 
                    color=[0.4, 0.4, 0.4, 1],
                    font_size='14sp'
                ))

            elif item_status == 'lost':
                status_text = "내가 등록한 분실물"
                item_box.add_widget(WrappedLabel(text=status_text, color=[0.5,0.5,0.5,1]))
            
            else:
                status_text = f"상태: {item_status}"
                item_box.add_widget(WrappedLabel(text=status_text, color=[0.5,0.5,0.5,1]))

            self.grid.add_widget(item_box)


class SignupScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.current_step = 'step1'
        self.main_container = BoxLayout(orientation='vertical')
        self.add_widget(self.main_container)
        self.setup_step1()
        self.setup_step2()
        self.update_view()

    def setup_step1(self):
        step1_content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=[dp(50), dp(80), dp(50), dp(80)])
        step1_content_layout.bind(minimum_height=step1_content_layout.setter('height'))
        step1_content_layout.add_widget(Label(text="[b]Campus Link 회원가입 (1/2)[/b]", font_size='32sp', font_name=FONT_NAME, color=[0.1, 0.4, 0.7, 1], markup=True, size_hint_y=None, height=dp(60)))
        step1_content_layout.add_widget(Label(size_hint_y=None, height=dp(10)))
        self.student_id_input = get_rounded_textinput('학번 (예: 20240001)', input_type='number')
        self.name_input = get_rounded_textinput('이름')
        self.department_input = get_rounded_textinput('학과')
        self.grade_input = get_rounded_textinput('학년 (예: 3)', input_type='number')
        step1_content_layout.add_widget(self.student_id_input)
        step1_content_layout.add_widget(self.name_input)
        step1_content_layout.add_widget(self.department_input)
        step1_content_layout.add_widget(self.grade_input)
        next_button = get_styled_button("다음 (1/2)", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        next_button.bind(on_press=self.go_to_step2)
        step1_content_layout.add_widget(next_button)
        cancel_button = get_styled_button("취소 (로그인 화면으로)", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1], font_size='18sp')
        cancel_button.height = dp(50)
        cancel_button.bind(on_press=self.go_to_login)
        step1_content_layout.add_widget(cancel_button)
        step1_content_layout.add_widget(Label())
        step1_scrollview = ScrollView(size_hint=(1, 1))
        step1_scrollview.add_widget(step1_content_layout)
        self.step1_layout = step1_scrollview

    def setup_step2(self):
        step2_content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=[dp(50), dp(80), dp(50), dp(80)])
        step2_content_layout.bind(minimum_height=step2_content_layout.setter('height'))
        step2_content_layout.add_widget(Label(text="[b]Campus Link 회원가입 (2/2)[/b]", font_size='32sp', font_name=FONT_NAME, color=[0.1, 0.4, 0.7, 1], markup=True, size_hint_y=None, height=dp(60)))
        step2_content_layout.add_widget(Label(size_hint_y=None, height=dp(10)))
        self.email_input = get_rounded_textinput('이메일 주소', input_type='mail')
        self.login_id_input = get_rounded_textinput('아이디 (로그인용)')
        self.nickname_input = get_rounded_textinput('닉네임 (표시용)')
        self.password_input = get_rounded_textinput('비밀번호 (최소 6자)', password=True)
        self.confirm_password_input = get_rounded_textinput('비밀번호 확인', password=True)
        step2_content_layout.add_widget(self.email_input)
        step2_content_layout.add_widget(self.login_id_input)
        step2_content_layout.add_widget(self.nickname_input)
        step2_content_layout.add_widget(self.password_input)
        step2_content_layout.add_widget(self.confirm_password_input)
        signup_button = get_styled_button("회원가입 완료", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        signup_button.bind(on_press=self.do_signup)
        step2_content_layout.add_widget(signup_button)
        prev_button = get_styled_button("이전", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1], font_size='18sp')
        prev_button.height = dp(50)
        prev_button.bind(on_press=self.go_to_step1)
        step2_content_layout.add_widget(prev_button)
        step2_content_layout.add_widget(Label())
        step2_scrollview = ScrollView(size_hint=(1, 1))
        step2_scrollview.add_widget(step2_content_layout)
        self.step2_layout = step2_scrollview

    def update_view(self):
        self.main_container.clear_widgets()
        if self.current_step == 'step1':
            self.main_container.add_widget(self.step1_layout)
        else:
            self.main_container.add_widget(self.step2_layout)

    def go_to_step1(self, instance):
        self.current_step = 'step1'
        self.update_view()

    def go_to_step2(self, instance):
        if not self.student_id_input.text or not self.name_input.text:
            self.show_popup("오류", "학번과 이름을 입력해주세요.")
            return
        self.current_step = 'step2'
        self.update_view()

    def go_to_login(self, instance):
        self.student_id_input.text = ''
        self.name_input.text = ''
        self.department_input.text = ''
        self.grade_input.text = ''
        self.email_input.text = ''
        self.login_id_input.text = ''
        self.nickname_input.text = ''
        self.password_input.text = ''
        self.confirm_password_input.text = ''
        self.current_step = 'step1'
        self.update_view()
        self.manager.current = 'login'

    def do_signup(self, instance):
        student_id = self.student_id_input.text
        name = self.name_input.text
        department = self.department_input.text
        grade = self.grade_input.text
        email = self.email_input.text
        login_id = self.login_id_input.text
        nickname = self.nickname_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text

        if not email or not login_id or not nickname or not password or not confirm_password:
            self.show_popup("오류", "모든 계정 정보를 채워주세요.")
            return
        if password != confirm_password:
            self.show_popup("오류", "비밀번호가 일치하지 않습니다.")
            return
        if len(password) < 6:
            self.show_popup("오류", "비밀번호는 6자 이상이어야 합니다.")
            return

        try:
            existing_email = FirebaseREST.db_get(f"id_to_email_mapping/{login_id}")
            if isinstance(existing_email, dict) and "error" in existing_email:
                 self.show_popup("오류", "네트워크 상태를 확인해주세요.")
                 return
            if existing_email:
                self.show_popup("오류", "이미 사용 중인 아이디입니다.")
                return

            result = FirebaseREST.signup(email, password)
            if "error" in result:
                error_msg = result["error"].get("message", "")
                if "EMAIL_EXISTS" in error_msg:
                    self.show_popup("오류", "이미 사용 중인 이메일입니다.")
                else:
                    self.show_popup("오류", f"회원가입 실패: {error_msg}")
                return

            uid = result.get('localId')
            id_token = result.get('idToken')

            if not uid or not id_token:
                 self.show_popup("오류", "가입 처리 중 문제가 발생했습니다.")
                 return

            FirebaseREST.send_email_verification(id_token)

            user_profile_data = {
                'login_id': login_id, 'nickname': nickname, 'email': email, 'role': 'user',
                'student_id': student_id, 'name': name, 'department': department, 'grade': grade
            }
            
            FirebaseREST.db_put(f"users/{uid}", user_profile_data, id_token)
            FirebaseREST.db_put(f"id_to_email_mapping/{login_id}", email, id_token)
            self.show_popup("성공", f"회원가입 신청이 완료되었습니다.\n\n'{email}'로 발송된\n인증 링크를 클릭하여 계정을 활성화해주세요.", after_dismiss_callback=self.go_to_login)
        except Exception as e:
            self.show_popup("오류", f"데이터 저장 실패: {e}")

    def show_popup(self, title, message, after_dismiss_callback=None):
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        with content_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect_popup_bg = Rectangle(size=content_layout.size, pos=content_layout.pos)

        def update_popup_rect(instance, value):
            self.rect_popup_bg.pos = instance.pos
            self.rect_popup_bg.size = instance.size
        content_layout.bind(pos=update_popup_rect, size=update_popup_rect)
        popup_content = WrappedLabel(
            text=message, 
            font_size='16sp', 
            font_name=FONT_NAME, 
            color=[0, 0, 0, 1],
            halign='center' 
        )
        content_layout.add_widget(popup_content)

        confirm_button = get_styled_button("확인", [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='20sp')
        confirm_button.height = dp(50)
        
        popup = Popup(title=title, title_font=FONT_NAME, title_color=[0, 0, 0, 1], 
                      content=content_layout, size_hint=(0.85, 0.5), 
                      auto_dismiss=False, separator_height=0, background='')
        
        def on_confirm(btn_instance):
            popup.dismiss()
            if after_dismiss_callback:
                after_dismiss_callback(None)
        confirm_button.bind(on_press=on_confirm)
        content_layout.add_widget(confirm_button)
        popup.open()

class LoginScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=[dp(50), dp(80), dp(50), dp(80)], spacing=dp(18))
        app_name_label = Label(text="[b]Campus Link[/b]", font_size='48sp', color=[0.1, 0.4, 0.7, 1], font_name=FONT_NAME, markup=True, size_hint_y=None, height=dp(90))
        main_layout.add_widget(app_name_label)
        main_layout.add_widget(Label(size_hint_y=None, height=dp(20)))
        self.username_input = get_rounded_textinput('아이디')
        main_layout.add_widget(self.username_input)
        self.password_input = get_rounded_textinput('비밀번호', password=True)
        main_layout.add_widget(self.password_input)
        login_button = get_styled_button("로그인", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        login_button.bind(on_press=self.do_login)
        main_layout.add_widget(login_button)
        signup_button = get_styled_button("회원가입", [0.5, 0.7, 0.9, 1], [1, 1, 1, 1])
        signup_button.bind(on_press=self.go_to_signup)
        main_layout.add_widget(signup_button)
        main_layout.add_widget(Label())
        self.add_widget(main_layout)

    def go_to_signup(self, instance):
        self.manager.current = 'signup'

    def show_popup(self, title, message, show_retry_button=False):
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        with content_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect_popup = Rectangle(size=content_layout.size, pos=content_layout.pos)
        def update_popup_rect(instance, value):
            self.rect_popup.pos = instance.pos
            self.rect_popup.size = instance.size
        content_layout.bind(pos=update_popup_rect, size=update_popup_rect)
        
        popup_content = WrappedLabel(
            text=message, 
            font_size='16sp', 
            font_name=FONT_NAME, 
            color=[0, 0, 0, 1],
            halign='center'
        )
        content_layout.add_widget(popup_content)

        popup = Popup(title=title, title_font=FONT_NAME, title_color=[0, 0, 0, 1], 
                      content=content_layout, size_hint=(0.85, 0.45),
                      auto_dismiss=not show_retry_button, separator_height=0, background='')

        if show_retry_button:
            retry_button = get_styled_button("다시 시도", [0.9, 0.2, 0.2, 1], [1, 1, 1, 1], font_size='18sp')
            retry_button.height = dp(50)
            retry_button.bind(on_press=lambda x: popup.dismiss())
            content_layout.add_widget(retry_button)
            
        popup.open()

    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        app = App.get_running_app()

        if not username or not password:
            self.show_popup("로그인 실패", "아이디와 비밀번호를 입력하세요.", show_retry_button=True)
            return

        try:
            email = FirebaseREST.db_get(f"id_to_email_mapping/{username}")
            if not email:
                self.show_popup("로그인 실패", "존재하지 않는 아이디입니다.", show_retry_button=True)
                return

            result = FirebaseREST.login(email, password)
            if "error" in result:
                error_msg = result["error"].get("message", "")
                if "INVALID_PASSWORD" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
                    self.show_popup("로그인 실패", "비밀번호가 올바르지 않습니다.", show_retry_button=True)
                else:
                    self.show_popup("로그인 실패", f"오류: {error_msg}", show_retry_button=True)
                return

            id_token = result.get('idToken')
            uid = result.get('localId')

            if not id_token or not uid:
                self.show_popup("로그인 실패", "인증 정보를 받아오지 못했습니다.", show_retry_button=True)
                return

            user_info_res = FirebaseREST.get_user_info(id_token)
            users_list = user_info_res.get('users', [])
            if not users_list or not users_list[0].get('emailVerified', False):
                self.show_popup("로그인 실패", "이메일 인증이 완료되지 않았습니다.\n\n메일함에서 인증 링크를 클릭해주세요.", show_retry_button=True)
                return

            app.user_token = id_token
            app.current_user_uid = uid

            user_profile = FirebaseREST.db_get(f"users/{uid}", id_token)
            if user_profile:
                app.current_user_nickname = user_profile.get('nickname', '사용자')
                app.current_user_role = user_profile.get('role', 'user')
                app.current_user = user_profile.get('login_id', username)
            else:
                app.current_user_nickname = "사용자"
                app.current_user_role = "user"
                app.current_user = username

            self.manager.current = 'main'

        except Exception as e:
            self.show_popup("로그인 실패", f"시스템 오류: {e}", show_retry_button=True)


class ClubScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]동아리 게시판[/b]", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True, font_size='26sp'))
        create_button = get_styled_button("개설 신청", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1], font_size='18sp')
        create_button.height = dp(50)
        create_button.size_hint_x = None
        create_button.width = dp(120)
        create_button.bind(on_press=lambda *args: self.go_to_screen('club_create'))
        header.add_widget(create_button)
        main_layout.add_widget(header)

        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(10), 0, dp(10), 0])
        self.search_input = TextInput(hint_text='동아리 이름 검색', font_name=FONT_NAME, size_hint_x=0.8, multiline=False)
        search_button = get_styled_button("검색", [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='18sp')
        search_button.size_hint_x = 0.2
        search_button.height = dp(50)
        search_button.bind(on_press=self.search_clubs)
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_button)
        main_layout.add_widget(search_layout)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.results_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        scroll_view.add_widget(self.results_grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        app = App.get_running_app()
        if not app.user_token:
            self.update_club_list([]) 
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            clubs_dict = FirebaseREST.db_get("all_clubs", app.user_token)
            
            if clubs_dict and isinstance(clubs_dict, dict) and "error" not in clubs_dict:
                clubs_list = list(clubs_dict.values())
                sorted_list = sorted(
                    clubs_list, 
                    key=lambda club: club.get("popularity_score", 0) if isinstance(club, dict) else 0, 
                    reverse=True
                )
                self.update_club_list(sorted_list)
                app.all_clubs = sorted_list
            else:
                self.update_club_list([])
                app.all_clubs = []

        except Exception as e:
            self.update_club_list([]) 
            Popup(title='DB 오류', content=Label(text=f'데이터 읽기 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
        
        self.search_input.text = "" 

    def update_club_list(self, clubs):
        self.results_grid.clear_widgets()
        if not clubs:
            self.results_grid.add_widget(Label(text="표시할 동아리가 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return
            
        for club in clubs:
            if not isinstance(club, dict): continue

            item = ClubListItem()
            item.club_data = club
            item.bind(on_press=self.view_club_details)

            name_label = WrappedLabel(
                text=f"[b]{club.get('name', '이름 없음')}[/b]", 
                font_name=FONT_NAME, 
                markup=True, 
                font_size='18sp'
            )
            
            score = club.get('popularity_score', 0)
            desc_text = club.get('short_desc', '')
            if score > 0: desc_text += f" (인기도: {score})"

            desc_label = WrappedLabel(
                text=desc_text, 
                font_name=FONT_NAME, 
                color=[0.3, 0.3, 0.3, 1],
                font_size='14sp'
            )

            item.add_widget(name_label)
            item.add_widget(desc_label)
            self.results_grid.add_widget(item)

    def view_club_details(self, instance):
        detail_screen = self.manager.get_screen('club_detail')
        detail_screen.club_data = instance.club_data 
        self.go_to_screen('club_detail')

    def search_clubs(self, instance):
        app = App.get_running_app()
        search_term = self.search_input.text.lower()
        try:
            if not app.all_clubs:
                 clubs_dict = FirebaseREST.db_get("all_clubs", app.user_token)
                 if clubs_dict and isinstance(clubs_dict, dict) and "error" not in clubs_dict: 
                     app.all_clubs = list(clubs_dict.values())
            
            if app.all_clubs:
                if not search_term:
                    results = app.all_clubs
                else:
                    results = [club for club in app.all_clubs if isinstance(club, dict) and search_term in club.get('name', '').lower()]
                
                sorted_results = sorted(results, key=lambda club: club.get("popularity_score", 0), reverse=True)
                self.update_club_list(sorted_results)
            else:
                self.update_club_list([])
        except Exception:
            pass

class ClubDetailScreen(WhiteBgScreen):
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()
        if self.club_data:
            app = App.get_running_app()
            
            if app.user_token:
                 club_id = self.club_data.get('club_id')
                 try:
                     self.update_popularity_score(club_id)
                 except:
                     pass

            is_president = app.current_user_uid == self.club_data.get('president')
            is_member = app.current_user_uid in self.club_data.get('members', {})

            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            menu_button = get_styled_button("메뉴", [0.1, 0.4, 0.7, 1], [1, 1, 1, 1], font_size='18sp')
            menu_button.height = dp(50)
            menu_button.size_hint_x = None
            menu_button.width = dp(90)
            menu_button.bind(on_press=self.show_club_menu_popup)
            header.add_widget(menu_button)

            bottom_bar = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10), spacing=dp(10))
            with bottom_bar.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                self.bottom_rect = Rectangle(size=bottom_bar.size, pos=bottom_bar.pos)
            bottom_bar.bind(size=self._update_rect_cb(self.bottom_rect), pos=self._update_rect_cb(self.bottom_rect))
            
            if not (is_president or is_member):
                apply_button = get_styled_button("신청하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
                apply_button.bind(on_press=self.go_to_application)
                bottom_bar.add_widget(apply_button)

            scroll_view = ScrollView(size_hint=(1, 1))
            content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
            content_layout.bind(minimum_height=content_layout.setter('height'))
            scroll_view.add_widget(content_layout)

            intro_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(5))
            intro_box.bind(minimum_height=intro_box.setter('height'))
            with intro_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                self.intro_bg_rect = RoundedRectangle(pos=intro_box.pos, size=intro_box.size, radius=[dp(5)])
            intro_box.bind(pos=lambda i, v: setattr(self.intro_bg_rect, 'pos', v), size=lambda i, v: setattr(self.intro_bg_rect, 'size', v))
            
            title_intro = Label(text="[b]동아리 소개[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, size_hint_y=None, height=dp(40), font_size='20sp', halign='left')
            title_intro.bind(size=title_intro.setter('text_size'))
            intro_box.add_widget(title_intro)
            
            long_desc_label = WrappedLabel(text=self.club_data['long_desc'], font_name=FONT_NAME, color=[0.2,0.2,0.2,1], font_size='15sp')
            intro_box.add_widget(long_desc_label)
            content_layout.add_widget(intro_box)

            for section_title, data_key in [("[b]공지사항[/b]", "announcements"), ("[b]활동 내역[/b]", "activities"), ("[b]자유게시판[/b]", "free_board"), ("[b]후기[/b]", "reviews")]:
                section_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(5))
                section_box.bind(minimum_height=section_box.setter('height'))
                with section_box.canvas.before:
                    Color(0.95, 0.95, 0.95, 1)
                    bg_rect = RoundedRectangle(pos=section_box.pos, size=section_box.size, radius=[dp(5)])
                section_box.bind(pos=lambda i, v, r=bg_rect: setattr(r, 'pos', v), size=lambda i, v, r=bg_rect: setattr(r, 'size', v))

                title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                title_label = Label(text=section_title, font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='20sp', halign='left')
                title_label.bind(size=title_label.setter('text_size'))
                title_layout.add_widget(title_label)
                
                if data_key == 'free_board' and (is_president or is_member):
                    write_button_small = get_styled_button("글쓰기", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='16sp')
                    write_button_small.height = dp(40)
                    write_button_small.size_hint_x = None
                    write_button_small.width = dp(90)
                    write_button_small.bind(on_press=self.go_to_free_board_post)
                    title_layout.add_widget(write_button_small)
                section_box.add_widget(title_layout)

                section_data = self.club_data.get(data_key)
                if section_data:
                    items_list = []
                    for item in section_data.values():
                        if isinstance(item, dict) and 'content' in item:
                            items_list.append(item)
                        else:
                            items_list.append({'content': str(item), 'timestamp': 0})
                    items_list.sort(key=lambda x: int(x.get('timestamp', 0)), reverse=True)
                    
                    if data_key == 'free_board': display_list = items_list[:4]
                    else: display_list = items_list

                    for item in display_list:
                        text_to_show = item['content']
                        item_label = WrappedLabel(text=f"- {text_to_show}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], font_size='14sp')
                        section_box.add_widget(item_label)
                    
                    if data_key == 'free_board' and len(items_list) > 4:
                        more_button = Button(text="더보기...", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], background_color=[0,0,0,0], background_normal='', size_hint_y=None, height=dp(30))
                        more_button.bind(on_press=self.go_to_all_free_board)
                        section_box.add_widget(more_button)
                else:
                    empty_label = Label(text="아직 내용이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(30), halign='left')
                    empty_label.bind(size=empty_label.setter('text_size'))
                    section_box.add_widget(empty_label)
                content_layout.add_widget(section_box)

            self.main_layout.add_widget(header)
            self.main_layout.add_widget(scroll_view)
            self.main_layout.add_widget(bottom_bar)

    # 인기도 알고리즘 (REST 방식 적용)
    def update_popularity_score(self, club_id):
        app = App.get_running_app()
        if not app.user_token: return

        try:
            club_data = FirebaseREST.db_get(f"all_clubs/{club_id}", app.user_token)
            if not club_data: return

            current_time = int(time.time())
            
            def get_semester_index(timestamp):
                dt = datetime.fromtimestamp(timestamp)
                year = dt.year
                month = dt.month
                if 3 <= month <= 8: return year * 2 + 1 
                elif month >= 9: return year * 2 + 2
                else: return (year - 1) * 2 + 2

            current_semester_idx = get_semester_index(time.time())
            
            def calculate_decayed_score(items, base_weight):
                sub_total = 0.0
                if not items: return 0.0
                if isinstance(items, dict): values = items.values()
                else: return 0.0
                
                for item in values:
                    if isinstance(item, dict) and 'timestamp' in item:
                        ts = int(item['timestamp'])
                    elif isinstance(item, int) or isinstance(item, float):
                        ts = item
                    else: continue 
                    
                    content_semester_idx = get_semester_index(ts)
                    elapsed_semesters = current_semester_idx - content_semester_idx
                    if elapsed_semesters < 0: elapsed_semesters = 0
                    if elapsed_semesters >= 4: continue 
                    
                    decay_factor = 0.5 ** elapsed_semesters
                    sub_total += base_weight * decay_factor
                return sub_total

            score_activity = calculate_decayed_score(club_data.get('activities'), 0.5)
            score_free = calculate_decayed_score(club_data.get('free_board'), 0.3)
            total_score = score_activity + score_free

            FirebaseREST.db_put(f"all_clubs/{club_id}/popularity_score", round(total_score, 2), app.user_token)
        except Exception as e:
            print(f"점수 계산 오류: {e}")

    def _update_rect_cb(self, rect):
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        return update_rect

    def show_club_menu_popup(self, instance):
        app = App.get_running_app()
        popup = Popup(title="", separator_height=0, size_hint=(0.6, 1.0), pos_hint={'right': 1, 'y': 0}, auto_dismiss=True, background='')
        full_popup_content = BoxLayout(orientation='vertical')
        with full_popup_content.canvas.before:
            Color(1, 1, 1, 1)
            content_bg = Rectangle(size=full_popup_content.size, pos=full_popup_content.pos)
        full_popup_content.bind(size=lambda i, v: setattr(content_bg, 'size', v), pos=lambda i, v: setattr(content_bg, 'pos', v))
        BLUE_STRIPE_COLOR = [0.1, 0.4, 0.7, 1]
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[dp(10), 0, dp(10), 0])
        with header.canvas.before:
            Color(*BLUE_STRIPE_COLOR)
            header_bg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda i, v: setattr(header_bg, 'size', v), pos=lambda i, v: setattr(header_bg, 'pos', v))
        header.add_widget(Label(text="[b]동아리 메뉴[/b]", font_name=FONT_NAME, color=[1, 1, 1, 1], markup=True, font_size='22sp'))
        close_button = Button(text="X", font_size='22sp', size_hint=(None, 1), width=dp(40), color=[1, 1, 1, 1], background_normal='', background_color=[0, 0, 0, 0])
        close_button.bind(on_press=popup.dismiss)
        header.add_widget(close_button)
        full_popup_content.add_widget(header)
        content_layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(30))
        
        is_president = app.current_user_uid == self.club_data.get('president')
        is_member = app.current_user_uid in self.club_data.get('members', {})

        if is_president:
            manage_button = get_styled_button("동아리 관리", [0.8, 0.1, 0.1, 1], [1, 1, 1, 1])
            manage_button.bind(on_press=lambda *args: (popup.dismiss(), self.go_to_club_management(None)))
            content_layout.add_widget(manage_button)
        elif is_member:
            review_button = get_styled_button("후기 작성", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
            review_button.bind(on_press=lambda *args: (popup.dismiss(), self.go_to_post_screen(None)))
            content_layout.add_widget(review_button)
            withdraw_button = get_styled_button("동아리 탈퇴", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1], font_size='18sp')
            withdraw_button.bind(on_press=lambda *args: (popup.dismiss(), self.withdraw_from_club(None)))
            content_layout.add_widget(withdraw_button)
        else:
            content_layout.add_widget(Label(text="비회원입니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1]))
        content_layout.add_widget(Label())
        full_popup_content.add_widget(content_layout)
        popup.content = full_popup_content
        popup.open()

    def withdraw_from_club(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        popup_content.add_widget(Label(text='정말 동아리를 탈퇴하시겠습니까?', font_name=FONT_NAME, color=[0,0,0,1]))
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        yes_button = get_styled_button("예, 탈퇴합니다", [0.8, 0.2, 0.2, 1], [1,1,1,1])
        no_button = get_styled_button("아니요", [0.5, 0.5, 0.5, 1], [1,1,1,1])
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        popup_content.add_widget(button_layout)
        popup = Popup(title="[b]동아리 탈퇴 확인[/b]", title_font=FONT_NAME, title_color=[0,0,0,1], content=popup_content, size_hint=(0.9, 0.4), separator_height=0, background='')
        no_button.bind(on_press=popup.dismiss)
        yes_button.bind(on_press=lambda *args: self.perform_withdraw(popup))
        popup.open()

    def perform_withdraw(self, popup_to_dismiss):
        app = App.get_running_app()
        club_id = self.club_data.get('club_id')
        member_uid = app.current_user_uid 
        if not club_id or not member_uid: return
        try:
            FirebaseREST.db_delete(f"all_clubs/{club_id}/members/{member_uid}", app.user_token)
            popup_to_dismiss.dismiss()
            success_popup = Popup(title='탈퇴 완료', content=Label(text='동아리에서 탈퇴되었습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            success_popup.bind(on_dismiss=lambda *args: self.go_to_screen('club'))
            success_popup.open()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'탈퇴 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def go_to_free_board_post(self, instance):
        post_screen = self.manager.get_screen('post_screen')
        post_screen.club_data = self.club_data
        post_screen.post_type = 'free_board' 
        self.go_to_screen('post_screen')

    def go_to_all_free_board(self, instance):
        free_board_screen = self.manager.get_screen('club_free_board')
        free_board_screen.club_data = self.club_data
        self.go_to_screen('club_free_board')
    
    def go_to_application(self, instance):
        app_screen = self.manager.get_screen('club_apply')
        app_screen.club_data = self.club_data 
        self.go_to_screen('club_apply')
    def go_to_club_management(self, instance):
        management_screen = self.manager.get_screen('club_management')
        management_screen.club_data = self.club_data
        self.go_to_screen('club_management')
    def go_to_post_screen(self, instance):
        post_screen = self.manager.get_screen('post_screen')
        post_screen.club_data = self.club_data
        post_screen.post_type = 'review'
        self.go_to_screen('post_screen')

class ClubCreateScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]동아리 개설 신청[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)
        self.club_name = get_rounded_textinput('동아리 이름')
        self.short_desc = get_rounded_textinput('한줄 소개 (목록에 표시됩니다)')
        self.long_desc = TextInput(hint_text='자세한 설명 (동아리 활동, 모집 대상 등)', font_name=FONT_NAME, size_hint_y=None, height=dp(150), padding=dp(15))
        main_layout.add_widget(self.club_name)
        main_layout.add_widget(self.short_desc)
        main_layout.add_widget(self.long_desc)
        main_layout.add_widget(Label())
        create_button = get_styled_button("신청하기", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
        create_button.bind(on_press=self.request_club_creation)
        main_layout.add_widget(create_button)
        self.add_widget(main_layout)

    def request_club_creation(self, instance):
        name = self.club_name.text
        s_desc = self.short_desc.text
        l_desc = self.long_desc.text
        if not name or not s_desc or not l_desc:
            Popup(title='오류', content=Label(text='모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return
        app = App.get_running_app()
        if not app.user_token or not app.current_user_uid:
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
        club_id = f"club_{int(time.time())}_{app.current_user}"
        new_club_request = {
            'club_id': club_id, 'name': name, 'short_desc': s_desc, 'long_desc': l_desc,
            'president': app.current_user_uid, 'members': { app.current_user_uid: True },
            'applications': {}, 'announcements': {}, 'activities': {}, 'reviews': {}
        }
        try:
            FirebaseREST.db_put(f"pending_clubs/{club_id}", new_club_request, app.user_token)
            self.club_name.text = ""
            self.short_desc.text = ""
            self.long_desc.text = ""
            popup = Popup(title='알림', content=Label(text='동아리 개설 신청이 완료되었습니다.\n관리자 승인 후 등록됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('club'))
            popup.open()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'데이터 저장 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

class ClubApplicationScreen(WhiteBgScreen):
    club_data = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()
        if self.club_data:
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']} 신청[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            self.main_layout.add_widget(header)
            self.intro = TextInput(hint_text='자기소개 및 지원 동기', font_name=FONT_NAME, size_hint_y=None, height=dp(150), padding=dp(15))
            self.main_layout.add_widget(Label(text="가입 신청서", font_name=FONT_NAME, size_hint_y=None, height=dp(30)))
            self.main_layout.add_widget(self.intro)
            self.main_layout.add_widget(Label())
            apply_button = get_styled_button("신청서 제출", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
            apply_button.bind(on_press=self.submit_application)
            self.main_layout.add_widget(apply_button)

    def submit_application(self, instance):
        if not self.intro.text:
            Popup(title='오류', content=Label(text='자기소개를 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return
        app = App.get_running_app()
        if not app.user_token or not self.club_data:
            Popup(title='오류', content=Label(text='로그인 정보 또는 동아리 정보가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
        club_id = self.club_data.get('club_id')
        if not club_id: return
        application_data = { 'user_uid': app.current_user_uid, 'user_nickname': app.current_user_nickname, 'intro': self.intro.text }
        try:
            FirebaseREST.db_put(f"all_clubs/{club_id}/applications/{app.current_user_uid}", application_data, app.user_token)
            popup = Popup(title='신청 완료', content=Label(text='가입 신청이 완료되었습니다.\n회장 승인 후 가입됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('club_detail'))
            popup.open()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'신청 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

class ClubManagementScreen(WhiteBgScreen):
    club_data = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()
        if self.club_data:
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']} 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            self.main_layout.add_widget(header)
            self.main_layout.add_widget(Label(size_hint_y=0.2))
            member_approval_button = get_styled_button("가입 신청 관리", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
            member_approval_button.bind(on_press=self.go_to_member_approval)
            self.main_layout.add_widget(member_approval_button)
            member_manage_button = get_styled_button("멤버 관리 (추방)", [0.8, 0.5, 0.2, 1], [1, 1, 1, 1])
            member_manage_button.bind(on_press=self.go_to_member_management)
            self.main_layout.add_widget(member_manage_button)
            post_announcement_button = get_styled_button("공지사항 작성", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
            post_announcement_button.bind(on_press=lambda *args: self.go_to_post('announcement'))
            self.main_layout.add_widget(post_announcement_button)
            post_activity_button = get_styled_button("활동내역 작성", [0.5, 0.5, 0.8, 1], [1, 1, 1, 1])
            post_activity_button.bind(on_press=lambda *args: self.go_to_post('activity'))
            self.main_layout.add_widget(post_activity_button)
            self.main_layout.add_widget(Label())

    def go_to_member_approval(self, instance):
        approval_screen = self.manager.get_screen('member_approval')
        approval_screen.club_data = self.club_data
        self.go_to_screen('member_approval')
    def go_to_member_management(self, instance):
        management_screen = self.manager.get_screen('member_management')
        management_screen.club_data = self.club_data
        self.go_to_screen('member_management')
    def go_to_post(self, post_type):
        post_screen = self.manager.get_screen('post_screen')
        post_screen.club_data = self.club_data
        post_screen.post_type = post_type
        self.go_to_screen('post_screen')

class MemberApprovalScreen(WhiteBgScreen):
    club_data = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club_management'))
        header.add_widget(back_button)
        self.header_title = Label(text="[b]가입 신청 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp')
        header.add_widget(self.header_title)
        main_layout.add_widget(header)
        scroll_view = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        app = App.get_running_app()
        if not self.club_data or not app.user_token: return
        club_id = self.club_data.get('club_id')
        self.header_title.text = f"[b]{self.club_data.get('name', '동아리')} 신청 관리[/b]"
        try:
            applications_dict = FirebaseREST.db_get(f"all_clubs/{club_id}/applications", app.user_token)
            if not applications_dict:
                self.grid.add_widget(Label(text="가입 신청이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
            else:
                for app_data in applications_dict.values():
                    item_layout = BoxLayout(size_hint_y=None, height=dp(120), padding=dp(10), spacing=dp(10))
                    info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
                    user_display = app_data.get('user_nickname', app_data.get('user_uid', '알수없음'))
                    info_layout.add_widget(Label(text=f"[b]신청자: {user_display}[/b]", font_name=FONT_NAME, markup=True, color=[0,0,0,1], halign='left'))
                    info_layout.add_widget(Label(text=f"자기소개: {app_data['intro']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], halign='left'))
                    button_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
                    approve_btn = Button(text="수락", font_name=FONT_NAME, background_color=[0.2, 0.8, 0.2, 1])
                    approve_btn.app_data = app_data
                    approve_btn.bind(on_press=self.approve_member)
                    reject_btn = Button(text="거절", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1])
                    reject_btn.app_data = app_data
                    reject_btn.bind(on_press=self.reject_member)
                    button_layout.add_widget(approve_btn)
                    button_layout.add_widget(reject_btn)
                    item_layout.add_widget(info_layout)
                    item_layout.add_widget(button_layout)
                    self.grid.add_widget(item_layout)
        except Exception as e:
            self.grid.add_widget(Label(text=f"신청 목록 로딩 실패: {e}", font_name=FONT_NAME, color=[0.8,0,0,1], size_hint_y=None, height=dp(100)))

    def approve_member(self, instance):
        app_data = instance.app_data
        app = App.get_running_app()
        club_id = self.club_data.get('club_id')
        applicant_uid = app_data.get('user_uid')
        try:
            FirebaseREST.db_put(f"all_clubs/{club_id}/members/{applicant_uid}", True, app.user_token)
            FirebaseREST.db_delete(f"all_clubs/{club_id}/applications/{applicant_uid}", app.user_token)
            self.refresh_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'멤버 승인 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def reject_member(self, instance):
        app_data = instance.app_data
        app = App.get_running_app()
        club_id = self.club_data.get('club_id')
        applicant_uid = app_data.get('user_uid')
        try:
            FirebaseREST.db_delete(f"all_clubs/{club_id}/applications/{applicant_uid}", app.user_token)
            self.refresh_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'멤버 거절 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

class MemberManagementScreen(WhiteBgScreen):
    club_data = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club_management'))
        header.add_widget(back_button)
        self.header_title = Label(text="[b]멤버 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp')
        header.add_widget(self.header_title)
        main_layout.add_widget(header)
        scroll_view = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        app = App.get_running_app()
        if not self.club_data or not app.user_token: return
        club_id = self.club_data.get('club_id')
        president_uid = self.club_data.get('president')
        self.header_title.text = f"[b]{self.club_data.get('name', '동아리')} 멤버 관리[/b]"
        try:
            members_dict = FirebaseREST.db_get(f"all_clubs/{club_id}/members", app.user_token)
            if not members_dict:
                self.grid.add_widget(Label(text="동아리장이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
                return
            for member_uid in members_dict.keys():
                if member_uid == president_uid: continue
                item_layout = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(10))
                try:
                    user_data = FirebaseREST.db_get(f"users/{member_uid}", app.user_token)
                    nickname = user_data.get('nickname') if user_data else f"알 수 없는 멤버 ({member_uid[:5]}...)"
                except Exception:
                    nickname = f"멤버 정보 로드 실패 ({member_uid[:5]}...)"
                info_label = Label(text=nickname, font_name=FONT_NAME, color=[0,0,0,1], halign='left')
                info_label.bind(size=info_label.setter('text_size'))
                kick_btn = Button(text="추방", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1], size_hint_x=0.3)
                kick_btn.member_uid = member_uid
                kick_btn.member_nickname = nickname
                kick_btn.bind(on_press=self.confirm_kick)
                item_layout.add_widget(info_label)
                item_layout.add_widget(kick_btn)
                self.grid.add_widget(item_layout)
        except Exception as e:
            self.grid.add_widget(Label(text=f"멤버 목록 로딩 실패: {e}", font_name=FONT_NAME, color=[0.8,0,0,1], size_hint_y=None, height=dp(100)))

    def confirm_kick(self, instance):
        member_uid = instance.member_uid
        nickname = instance.member_nickname
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        popup_content.add_widget(Label(text=f"'{nickname}' 님을\n정말 추방하시겠습니까?", font_name=FONT_NAME, color=[0,0,0,1], halign='center'))
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        yes_button = get_styled_button("예 (추방)", [0.8, 0.2, 0.2, 1], [1,1,1,1])
        no_button = get_styled_button("아니요", [0.5, 0.5, 0.5, 1], [1,1,1,1])
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        popup_content.add_widget(button_layout)
        popup = Popup(title="멤버 추방 확인", title_font=FONT_NAME, title_color=[0,0,0,1], content=popup_content, size_hint=(0.9, 0.4), separator_height=0, background='')
        no_button.bind(on_press=popup.dismiss)
        yes_button.bind(on_press=lambda *args: self.perform_kick(member_uid, popup))
        popup.open()

    def perform_kick(self, member_uid, popup_to_dismiss):
        app = App.get_running_app()
        club_id = self.club_data.get('club_id')
        try:
            FirebaseREST.db_delete(f"all_clubs/{club_id}/members/{member_uid}", app.user_token)
            popup_to_dismiss.dismiss()
            self.refresh_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'추방 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

class PostScreen(WhiteBgScreen):
    club_data = ObjectProperty(None)
    post_type = StringProperty('') 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()
        type_map = {'announcement': '공지사항', 'activity': '활동내역', 'review': '후기', 'free_board': '자유게시판'}
        title = type_map.get(self.post_type, '글')
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
        header.add_widget(back_button)
        header.add_widget(Label(text=f"[b]{title} 작성[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        self.main_layout.add_widget(header)
        self.content_input = TextInput(hint_text=f'{title} 내용을 입력하세요.', font_name=FONT_NAME, size_hint_y=0.8, padding=dp(15))
        self.main_layout.add_widget(self.content_input)
        submit_button = get_styled_button("등록하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        submit_button.bind(on_press=self.submit_post)
        self.main_layout.add_widget(submit_button)

    def submit_post(self, instance):
        content = self.content_input.text.strip()
        if not content: return
        app = App.get_running_app()
        if self.post_type == 'review' or self.post_type == 'free_board':
            content = f"({app.current_user_nickname}님) {content}"
        key_map = {'announcement': 'announcements', 'activity': 'activities', 'review': 'reviews', 'free_board': 'free_board'}
        data_key = key_map.get(self.post_type)
        if self.club_data and data_key and app.user_token:
            try:
                club_id = self.club_data.get('club_id')
                post_data = {
                    'content': content,
                    'timestamp': int(time.time())
                }
                FirebaseREST.db_post(f"all_clubs/{club_id}/{data_key}", post_data, app.user_token)
                
                if data_key not in self.club_data: self.club_data[data_key] = {}
                self.club_data[data_key][str(time.time())] = post_data 
                
                popup = Popup(title='성공', content=Label(text='등록이 완료되었습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
                popup.bind(on_dismiss=lambda *args: self.go_to_screen('club_detail'))
                popup.open()
            except Exception as e:
                Popup(title='DB 오류', content=Label(text=f'데이터 저장 실패: {e}', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()

    def go_to_screen(self, screen_name):
        if screen_name == 'club_detail':
            detail_screen = self.manager.get_screen(screen_name)
            detail_screen.club_data = self.club_data
        self.manager.current = screen_name



class ClubFreeBoardScreen(WhiteBgScreen):
    """자유게시판 전체보기 화면 (REST 방식 적용)"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        if self.club_data:
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']} 자유게시판[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='24sp'))
            self.main_layout.add_widget(header)

            scroll_view = ScrollView()
            content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
            content_layout.bind(minimum_height=content_layout.setter('height'))
            scroll_view.add_widget(content_layout)
            self.main_layout.add_widget(scroll_view)

            free_board_data = self.club_data.get('free_board', {})
            posts_list = []
            
            if free_board_data:
                for item in free_board_data.values():
                    if isinstance(item, dict) and 'content' in item:
                        posts_list.append(item)
                    else:
                        posts_list.append({'content': str(item), 'timestamp': 0})
                
                posts_list.sort(key=lambda x: int(x.get('timestamp', 0)), reverse=True)

            if posts_list:
                for post in posts_list:
                    post_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
                    post_box.bind(minimum_height=post_box.setter('height'))
                    with post_box.canvas.before:
                        Color(0.95, 0.95, 0.95, 1)
                        RoundedRectangle(pos=post_box.pos, size=post_box.size, radius=[dp(5)])
                    
                    def update_bg(instance, value, box=post_box):
                         box.canvas.before.clear()
                         with box.canvas.before:
                             Color(0.95, 0.95, 0.95, 1)
                             RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(5)])
                    post_box.bind(pos=update_bg, size=update_bg)

                    content_label = WrappedLabel(text=post['content'], font_name=FONT_NAME, color=[0.2,0.2,0.2,1])
                    post_box.add_widget(content_label)
                    
                    if post.get('timestamp'):
                        ts_date = datetime.fromtimestamp(int(post['timestamp'])).strftime('%Y-%m-%d %H:%M')
                        date_label = Label(text=ts_date, font_name=FONT_NAME, color=[0.6,0.6,0.6,1], font_size='12sp', size_hint_y=None, height=dp(15), halign='right')
                        date_label.bind(size=date_label.setter('text_size'))
                        post_box.add_widget(date_label)

                    content_layout.add_widget(post_box)
            else:
                content_layout.add_widget(Label(text="작성된 글이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(50)))


class LostAndFoundScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]분실물 게시판[/b]", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True, font_size='26sp', halign='center', valign='middle'))
        post_button = get_styled_button("+", [1, 0.5, 0.3, 1], [1, 1, 1, 1], font_size='24sp')
        post_button.height = dp(50)
        post_button.size_hint_x = None
        post_button.width = dp(60)
        post_button.bind(on_press=self.show_registration_choice_popup)
        header.add_widget(post_button)
        main_layout.add_widget(header)
        search_filter_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(10), padding=[dp(10), 0])
        keyword_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.search_input = TextInput(hint_text='물품 이름, 설명 등 키워드 검색', font_name=FONT_NAME, size_hint_x=0.7, multiline=False)
        search_button = get_styled_button("검색", [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='18sp')
        search_button.height = dp(50)
        search_button.size_hint_x = 0.3
        search_button.bind(on_press=self.search_items)
        keyword_layout.add_widget(self.search_input)
        keyword_layout.add_widget(search_button)
        category_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        category_label = Label(text='카테고리(종류):', font_name=FONT_NAME, size_hint_x=0.3)
        self.category_spinner = Spinner(text='전체', values=('전체', '전자기기', '서적', '의류', '지갑/카드', '기타'), font_name=FONT_NAME, size_hint_x=0.7, background_normal='', background_color=[1, 1, 1, 1], color=[0, 0, 0, 1])
        self.category_spinner.option_cls_args = {'font_name': FONT_NAME, 'background_normal': '', 'background_color': [1, 1, 1, 1], 'color': [0, 0, 0, 1], 'height': dp(50)}
        self.category_spinner.bind(text=self.search_items)
        category_layout.add_widget(category_label)
        category_layout.add_widget(self.category_spinner)
        search_filter_layout.add_widget(keyword_layout)
        search_filter_layout.add_widget(category_layout)
        main_layout.add_widget(search_filter_layout)
        scroll_view = ScrollView(size_hint=(1, 1))
        self.items_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))
        scroll_view.add_widget(self.items_grid)
        main_layout.add_widget(scroll_view)
        notification_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(10), 0])
        self.keyword_input = TextInput(hint_text='알림받을 키워드 (예: 지갑)', font_name=FONT_NAME, size_hint_x=0.7)
        keyword_button = get_styled_button("키워드 등록", [0.5, 0.5, 0.5, 1], [1,1,1,1], font_size='16sp')
        keyword_button.height=dp(50)
        keyword_button.size_hint_x = 0.3
        keyword_button.bind(on_press=self.register_keyword)
        notification_layout.add_widget(self.keyword_input)
        notification_layout.add_widget(keyword_button)
        main_layout.add_widget(notification_layout)
        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def show_registration_choice_popup(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        with popup_content.canvas.before:
            Color(1, 1, 1, 1)
            self.rect_bg = RoundedRectangle(pos=popup_content.pos, size=popup_content.size, radius=[dp(10)])
        popup_content.bind(pos=lambda i, v: setattr(self.rect_bg, 'pos', v), size=lambda i, v: setattr(self.rect_bg, 'size', v))
        popup = Popup(title='등록 종류 선택', title_font=FONT_NAME, title_color=[0, 0, 0, 1], content=popup_content, size_hint=(0.8, 0.4), separator_height=0, background='')
        def go_to_register(is_lost, *args):
            register_screen = self.manager.get_screen('add_item')
            register_screen.is_lost = is_lost
            self.manager.current = 'add_item'
            popup.dismiss()
        lost_button = get_styled_button("잃어버렸어요 (분실물 등록)", [0.8, 0.2, 0.2, 1], [1,1,1,1])
        found_button = get_styled_button("주웠어요 (습득물 등록)", [0.2, 0.6, 1, 1], [1,1,1,1])
        lost_button.bind(on_press=lambda *args: go_to_register(True))
        found_button.bind(on_press=lambda *args: go_to_register(False))
        popup_content.add_widget(lost_button)
        popup_content.add_widget(found_button)
        popup.open()

    def search_items(self, *args):
        app = App.get_running_app()
        keyword = self.search_input.text.lower()
        category = self.category_spinner.text
        if not app.all_items:
             base_list = []
        else:
             base_list = [item for item in app.all_items if isinstance(item, dict) and (item.get('status') == 'lost' or item.get('status') == 'found_available')]
        
        filtered_list = base_list
        if category != '전체':
            filtered_list = [item for item in filtered_list if item.get('category') == category]
        if keyword:
            filtered_list = [item for item in filtered_list if keyword in item.get('name', '').lower() or keyword in item.get('desc', '').lower() or keyword in item.get('loc', '').lower()]
        self.update_item_list(filtered_list)

    def register_keyword(self, instance):
        app = App.get_running_app()
        keyword = self.keyword_input.text.strip()
        if keyword and keyword not in app.notification_keywords:
            app.notification_keywords.append(keyword)
            Popup(title='알림', content=Label(text=f"키워드 '{keyword}'가 등록되었습니다.", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            self.keyword_input.text = ""

    def refresh_list(self, *args):
        app = App.get_running_app()
        if app.user_token:
            try:
                items_dict = FirebaseREST.db_get("all_items", app.user_token)
                if items_dict and isinstance(items_dict, dict) and "error" not in items_dict:
                    app.all_items = list(items_dict.values())
                else:
                    app.all_items = []
            except:
                app.all_items = []
        self.search_input.text = ""
        self.category_spinner.text = '전체'
        self.search_items()

    def update_item_list(self, items):
        self.items_grid.clear_widgets()
        if not items:
            self.items_grid.add_widget(Label(text="표시할 분실물이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        for item_data in items:
            if not isinstance(item_data, dict): continue

            item_layout = LostItemListItem()
            item_layout.item_data = item_data
            item_layout.bind(on_press=self.view_item_details)

            image = AsyncImage(source=item_data.get('image') if item_data.get('image') else DEFAULT_IMAGE, 
                               size_hint=(None, None), size=(dp(90), dp(90)), fit_mode='cover')
            image.pos_hint = {'top': 1}
            
            text_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=1)
            text_layout.size_hint_y = None
            text_layout.bind(minimum_height=text_layout.setter('height'))
            text_layout.pos_hint = {'top': 1}

            status_text = "[color=1010A0][습득][/color]" if item_data.get('status') == 'found_available' else "[color=A01010][분실][/color]"
            
            name_label = WrappedLabel(text=f"{status_text} {item_data.get('name', '')}", font_name=FONT_NAME, markup=True, font_size='16sp')
            loc_label = WrappedLabel(text=f"장소: {item_data.get('loc', '')}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], font_size='13sp')
            time_label = WrappedLabel(text=f"시간: {item_data.get('time', 'N/A')}", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], font_size='13sp')

            text_layout.add_widget(name_label)
            text_layout.add_widget(loc_label)
            text_layout.add_widget(time_label)
            
            item_layout.add_widget(image)
            item_layout.add_widget(text_layout)
            self.items_grid.add_widget(item_layout)

    def view_item_details(self, instance):
        detail_screen = self.manager.get_screen('item_detail')
        detail_screen.item_data = instance.item_data
        self.go_to_screen('item_detail')



class AddItemScreen(WhiteBgScreen):
    is_lost = ObjectProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if platform == 'android':
            try:
                from android.activity import bind as android_bind
                android_bind(on_activity_result=self.on_android_activity_result)
            except ImportError:
                pass

        root_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(20)])

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('lost_found'))
        header.add_widget(back_button)
        self.header_title = Label(text="[b]분실/습득물 등록[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp')
        header.add_widget(self.header_title)
        root_layout.add_widget(header)

        scroll_view = ScrollView()
        
        self.content_layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=[0, dp(10), 0, 0])
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        self.name_input = get_rounded_textinput('물건 이름 (예: 에어팟 프로)')
        self.desc_input = get_rounded_textinput('자세한 설명 (공개됨)')
        self.loc_input = get_rounded_textinput('발견/분실 장소')
        self.time_input = get_rounded_textinput('시간 (예: 14:30)')
        self.contact_input = get_rounded_textinput('연락처')

        self.verification_desc_input = TextInput(
            hint_text='[신원 확인용 정보 (비공개)]', font_name=FONT_NAME, 
            size_hint_y=None, height=dp(100), padding=dp(15),
            background_normal='', background_color=[0.95, 0.95, 0.8, 1] 
        )
        
        class KoreanSpinnerOption(SpinnerOption):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.font_name = FONT_NAME if FONT_NAME else 'Roboto'
                self.background_normal = ''
                self.background_color = [1, 1, 1, 1] 
                self.color = [0, 0, 0, 1]            
                self.height = dp(50)

        self.category_spinner = Spinner(
            text='카테고리 선택',
            values=('전자기기', '서적', '의류', '지갑/카드', '기타'),
            font_name=FONT_NAME if FONT_NAME else 'Roboto',
            size_hint_y=None, height=dp(55),
            background_normal='', background_color=[1, 1, 1, 1], color=[0, 0, 0, 1],
            option_cls=KoreanSpinnerOption
        )

        self.content_layout.add_widget(self.name_input)
        self.content_layout.add_widget(self.desc_input)
        self.content_layout.add_widget(self.verification_desc_input)
        self.content_layout.add_widget(self.loc_input)
        self.content_layout.add_widget(self.time_input)
        self.content_layout.add_widget(self.contact_input)
        self.content_layout.add_widget(self.category_spinner)

        self.image_path = "" 
        photo_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), spacing=dp(10))
        self.photo_label = Label(text="사진 없음", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_x=0.7)
        photo_button = get_styled_button("앨범에서 선택", [0.5, 0.7, 0.9, 1], [1, 1, 1, 1], font_size='18sp')
        photo_button.height = dp(55)
        photo_button.size_hint_x = 0.3
        photo_button.bind(on_press=self.check_permission_and_open_gallery)

        photo_layout.add_widget(self.photo_label)
        photo_layout.add_widget(photo_button)
        self.content_layout.add_widget(photo_layout)

        self.image_preview = AsyncImage(source=DEFAULT_IMAGE, size_hint_y=None, height=dp(200), fit_mode='contain')
        self.content_layout.add_widget(self.image_preview)
        
        self.content_layout.add_widget(Label(size_hint_y=None, height=dp(15))) 

        register_button = get_styled_button("등록 신청", [1, 0.5, 0.3, 1], [1, 1, 1, 1])
        register_button.bind(on_press=self.register_item)
        self.content_layout.add_widget(register_button)
        
        scroll_view.add_widget(self.content_layout)
        root_layout.add_widget(scroll_view)
        self.add_widget(root_layout)

    def on_enter(self, *args):
        if self.is_lost:
            self.header_title.text = "[b]분실물 등록[/b]"
            if self.verification_desc_input.parent:
                self.verification_desc_input.parent.remove_widget(self.verification_desc_input)
        else:
            self.header_title.text = "[b]습득물 등록[/b]"
            if not self.verification_desc_input.parent:
                try:
                    idx = self.content_layout.children.index(self.desc_input)
                    self.content_layout.add_widget(self.verification_desc_input, index=idx)
                except:
                    self.content_layout.add_widget(self.verification_desc_input)

        self.name_input.text = ""
        self.desc_input.text = ""
        self.loc_input.text = ""
        self.time_input.text = ""
        self.contact_input.text = ""
        self.image_path = ""
        self.photo_label.text = "사진 없음"
        self.image_preview.source = DEFAULT_IMAGE
        self.category_spinner.text = '카테고리 선택'
        self.verification_desc_input.text = ""

    def check_permission_and_open_gallery(self, instance):
        if platform != 'android':
            self.open_pc_file_chooser()
            return

        try:
            from jnius import autoclass
            from android.permissions import request_permissions, Permission
            from kivy.clock import Clock

            BuildVERSION = autoclass('android.os.Build$VERSION')
            
            if BuildVERSION.SDK_INT >= 33:
                perms = [Permission.READ_MEDIA_IMAGES]
            else:
                perms = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
            
            request_permissions(perms)
            Clock.schedule_once(lambda dt: self.open_android_gallery(), 0.2)

        except Exception as e:
            Popup(title='오류 발생', 
                  content=Label(text=f"버전 체크 실패:\n{str(e)}", font_name=FONT_NAME), 
                  size_hint=(0.9, 0.5)).open()

    def open_android_gallery(self):
        """createChooser에 Java String을 명시적으로 전달"""
        try:
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String') 
            
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            
            title_java = String("사진 선택")
            chooser = Intent.createChooser(intent, title_java)
            
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivityForResult(chooser, 999)
            
        except Exception as e:
            Popup(title='오류', content=Label(text=f'갤러리 앱 호출 실패.\n{e}', font_name=FONT_NAME), size_hint=(0.8, 0.4)).open()

    def open_pc_file_chooser(self):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.on_pc_selection, filters=[("Images", "*.png", "*.jpg", "*.jpeg")])
        except:
            Popup(title='알림', content=Label(text='PC 파일 탐색기 모듈 없음', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def on_pc_selection(self, selection):
        if selection:
            self.image_path = selection[0]
            self.image_preview.source = selection[0]
            self.photo_label.text = "사진 선택됨"

    def on_android_activity_result(self, request_code, result_code, intent):
        if request_code == 999 and result_code == -1:
            try:
                uri = intent.getData()
                if not uri: return
                
                self.image_path = uri.toString()
                self.photo_label.text = "사진 선택됨"
                
                cached = self.save_content_uri_to_cache(uri)
                if cached:
                    self.image_preview.source = cached
                    self.image_preview.reload()
            except Exception as e:
                print(f"사진 처리 실패: {e}")

    def save_content_uri_to_cache(self, android_uri):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            content_resolver = PythonActivity.mActivity.getContentResolver()
            
            cache_dir = PythonActivity.mActivity.getCacheDir().getAbsolutePath()
            temp_filename = f"temp_{int(time.time())}.jpg"
            output_path = os.path.join(cache_dir, temp_filename)
            
            inp = content_resolver.openInputStream(android_uri)
            with open(output_path, 'wb') as f:
                while True:
                    chunk = inp.read()
                    if not chunk: break 
                    break 
            return output_path 
        except:
            return None 

    def register_item(self, instance):
        name = self.name_input.text
        desc = self.desc_input.text 
        loc = self.loc_input.text
        time_val = self.time_input.text
        contact = self.contact_input.text
        category = self.category_spinner.text

        if not name or not loc or not contact or category == '카테고리 선택':
            Popup(title='오류', content=Label(text='필수 정보를 입력해주세요.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        app = App.get_running_app()
        if not app.user_token: return 

        item_id = f"item_{int(time.time())}_{app.current_user_uid}"
        image_url = ""

        if self.image_path:
            try:
                if self.image_path.startswith('content://'):
                    image_url = FirebaseREST.upload_image_from_uri(self.image_path, item_id)
                else:
                    ext = os.path.splitext(self.image_path)[1] or ".jpg"
                    image_url = FirebaseREST.upload_image(self.image_path, f"{item_id}{ext}")
            except Exception as e:
                print(f"업로드 에러: {e}")

        new_item = {
            'item_id': item_id, 'name': name, 'desc': desc, 'loc': loc, 'time': time_val, 'contact': contact,
            'image': image_url, 'category': category, 'status': 'lost' if self.is_lost else 'found_available',
            'registered_by_id': app.current_user, 'registered_by_uid': app.current_user_uid, 
            'registered_by_nickname': app.current_user_nickname, 
            'verification_desc': self.verification_desc_input.text if not self.is_lost else ""
        }
        
        try:
            FirebaseREST.db_put(f"pending_items/{item_id}", new_item, app.user_token)
            popup = Popup(title='성공', content=Label(text='등록 신청되었습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('lost_found'))
            popup.open()
        except:
            Popup(title='실패', content=Label(text='서버 저장 실패', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()



class ItemDetailScreen(WhiteBgScreen):
    item_data = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = RelativeLayout()
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()
        if not self.item_data: return
        app = App.get_running_app()
        
        bottom_bar = BoxLayout(size_hint=(1, None), height=dp(80), pos_hint={'bottom': 0}, padding=dp(10), spacing=dp(10))
        with bottom_bar.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bottom_rect = Rectangle(size=bottom_bar.size, pos=bottom_bar.pos)
        bottom_bar.bind(size=self._update_rect_cb(self.bottom_rect), pos=self._update_rect_cb(self.bottom_rect))
        
        is_my_post = self.item_data.get('registered_by_id') == app.current_user
        item_status = self.item_data.get('status')
        
        if is_my_post:
            if item_status == 'found_pending': status_label_text = "다른 사용자가 신청하여 관리자가 검토 중입니다."
            elif item_status == 'found_returned': status_label_text = "물품 전달이 완료되었습니다."
            else: status_label_text = "내가 등록한 게시물입니다."
            bottom_bar.add_widget(Label(text=status_label_text, font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1]))
        elif item_status == 'lost':
            contact_button = get_styled_button(f"연락처: {self.item_data['contact']}", [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='20sp')
            bottom_bar.add_widget(contact_button)
        else: 
            if item_status == 'found_available':
                claim_button = get_styled_button("이 물건 주인입니다 (신청하기)", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1], font_size='20sp')
                claim_button.bind(on_press=self.show_claim_verification_popup)
                bottom_bar.add_widget(claim_button)
            elif item_status == 'found_pending':
                bottom_bar.add_widget(Label(text="관리자가 다른 사용자의 신청을 검토 중입니다.", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1]))
            elif item_status == 'found_returned':
                bottom_bar.add_widget(Label(text="물품 전달이 완료되었습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1]))

        main_content_container = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=[0, 0, 0, dp(80)])
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('lost_found'))
        header.add_widget(back_button)
        status_text = "분실물 정보" if self.item_data['status'] == 'lost' else "습득물 정보"
        header.add_widget(Label(text=f"[b]{status_text}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_content_container.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15), padding=dp(10))
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        image = AsyncImage(source=self.item_data.get('image') if self.item_data.get('image') else DEFAULT_IMAGE, size_hint_y=None, height=dp(300), fit_mode='contain')
        scroll_content.add_widget(image)

        registrant_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), padding=[dp(10), 0])
        registrant = self.item_data.get('registered_by_nickname', self.item_data.get('registered_by_id', '알 수 없음'))
        registrant_box.add_widget(Image(source=DEFAULT_IMAGE, size_hint=(None, None), size=(dp(40), dp(40))))
        registrant_box.add_widget(Label(size_hint_x=None, width=dp(10)))
        registrant_label = Label(text=f"[b]등록자: {registrant}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='18sp', halign='left')
        registrant_label.bind(size=registrant_label.setter('text_size'))
        registrant_box.add_widget(registrant_label)
        
        separator = Label(size_hint_y=None, height=dp(1))
        with separator.canvas.before:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=separator.pos, size=(self.width - dp(40), dp(1)))
        scroll_content.add_widget(separator)

        info_section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8), padding=[dp(10), dp(15)])
        info_section.bind(minimum_height=info_section.setter('height'))
        item_name_label = WrappedLabel(text=f"[b]{self.item_data['name']}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='24sp')
        info_section.add_widget(item_name_label)

        status_color = "[color=A01010]" if self.item_data['status'] == 'lost' else "[color=1010A0]"
        status_display_text = "분실" if self.item_data['status'] == 'lost' else "습득"
        category_label = Label(text=f"{status_color}[b]{status_display_text}[/b][/color] · {self.item_data.get('category', '기타')}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True, font_size='16sp', size_hint_y=None, height=dp(25), halign='left')
        category_label.bind(size=category_label.setter('text_size'))
        info_section.add_widget(category_label)

        loc_time_label = Label(text=f"장소: {self.item_data['loc']}  ·  시간: {self.item_data.get('time', 'N/A')}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], font_size='16sp', size_hint_y=None, height=dp(25), halign='left')
        loc_time_label.bind(size=loc_time_label.setter('text_size'))
        info_section.add_widget(loc_time_label)
        
        info_section.add_widget(Label(size_hint_y=None, height=dp(15)))
        desc_title_label = Label(text="[b]상세 설명[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='20sp', size_hint_y=None, height=dp(40), halign='left')
        desc_title_label.bind(size=desc_title_label.setter('text_size'))
        info_section.add_widget(desc_title_label)
        
        desc_content_label = WrappedLabel(text=self.item_data.get('desc', '없음'), font_name=FONT_NAME, color=[0.2,0.2,0.2,1], font_size='16sp')
        info_section.add_widget(desc_content_label)
        
        scroll_content.add_widget(info_section)
        scroll_view.add_widget(scroll_content)
        main_content_container.add_widget(scroll_view)
        self.main_layout.add_widget(main_content_container)
        self.main_layout.add_widget(bottom_bar)

    def _update_rect_cb(self, rect):
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        return update_rect
    def _update_popup_rect_cb(self, rect):
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        return update_rect

    def show_claim_verification_popup(self, instance):
        app = App.get_running_app()
        item_id = self.item_data.get('item_id')

        if any(c['item_id'] == item_id and c['claimer_id'] == app.current_user for c in app.claims):
            Popup(title='알림', content=Label(text='이미 신청한 물품입니다.\n관리자가 검토 중입니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        with content_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect_bg = RoundedRectangle(pos=content_layout.pos, size=content_layout.size, radius=[dp(10)])
        content_layout.bind(pos=self._update_popup_rect_cb(self.rect_bg), size=self._update_popup_rect_cb(self.rect_bg))

        content_layout.add_widget(Label(text="[b]물품 주인 확인[/b]\n\n관리자가 확인할 수 있도록\n본인 소유임을 증명할 수 있는\n[b]상세 특징[/b]을 입력해주세요.", font_name=FONT_NAME, markup=True, halign='center', color=[0,0,0,1]))
        detail_input = TextInput(hint_text='물품의 상세 특징 (예: 케이스 색상, 스티커, 배경화면, 내용물 등)', font_name=FONT_NAME, multiline=True, size_hint_y=None, height=dp(100), background_normal='', background_color=[0.95, 0.95, 0.95, 1], foreground_color=[0,0,0,1], padding=[dp(10), dp(10), dp(10), dp(10)])
        content_layout.add_widget(detail_input)
        submit_button = get_styled_button("신청서 제출", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])
        popup = Popup(title="", content=content_layout, size_hint=(0.9, 0.6), auto_dismiss=False, separator_height=0, background="")
        submit_button.bind(on_press=lambda *args: self.submit_verification_claim(popup, item_id, detail_input.text))
        content_layout.add_widget(submit_button)
        close_button = get_styled_button("취소", [0.5, 0.5, 0.5, 1], [1,1,1,1]) 
        close_button.bind(on_press=popup.dismiss)
        content_layout.add_widget(close_button)
        popup.open()

    def submit_verification_claim(self, popup, item_id, details):
        if not details: return
        app = App.get_running_app()
        if not app.user_token:
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        claim_id = f"claim_{int(time.time())}_{app.current_user}"
        new_claim = {
            'claim_id': claim_id, 'item_id': item_id,
            'claimer_id': app.current_user, 'claimer_uid': app.current_user_uid, 'claimer_nickname': app.current_user_nickname,
            'verification_details': details,
            'status': 'pending', 'timestamp': str(time.time())
        }
        try:
            FirebaseREST.db_put(f"claims/{claim_id}", new_claim, app.user_token)
            FirebaseREST.db_update(f"all_items/{item_id}", {'status': 'found_pending'}, app.user_token)
            
            popup.dismiss()
            success_popup = Popup(title='신청 완료', content=Label(text='신청이 완료되었습니다.\n관리자 승인 후 연락처가 공개됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            success_popup.bind(on_dismiss=lambda *args: self.go_to_screen('lost_found'))
            success_popup.open()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'신청 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()


class MyClaimsScreen(WhiteBgScreen):
    """내가 신청한 물품의 '상태'와 '연락처'를 확인하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]내 신청 현황[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))

        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def create_wrapping_label(self, text_content, **kwargs):
        label = Label(text=text_content, size_hint_y=None, font_name=FONT_NAME, markup=True, halign='left', **kwargs)
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        return label

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        app = App.get_running_app()
        if not app.user_token: return

        try:
            claims_dict = FirebaseREST.db_get("claims", app.user_token)
            all_claims = list(claims_dict.values()) if claims_dict else []
            items_dict = FirebaseREST.db_get("all_items", app.user_token)
            all_items = list(items_dict.values()) if items_dict else []
        except:
            all_claims = []
            all_items = []

        my_claims = [c for c in all_claims if c['claimer_id'] == app.current_user]

        if not my_claims:
            self.grid.add_widget(Label(text="신청한 내역이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        for claim in my_claims:
            item_id = claim.get('item_id')
            item = next((i for i in all_items if i.get('item_id') == item_id), None)
            item_name = item['name'] if item else '알 수 없는 물품'
            
            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            item_box.bind(minimum_height=item_box.setter('height')) 
            
            with item_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
        
            item_box.bind(
                pos=lambda instance, value, r=bg_rect: setattr(r, 'pos', value),
                size=lambda instance, value, r=bg_rect: setattr(r, 'size', value)
            )

            item_box.add_widget(self.create_wrapping_label(text_content=f"[b]물품명: {item_name}[/b]", color=[0,0,0,1]))
            item_box.add_widget(Label(size_hint_y=None, height=dp(5)))

            claim_status = claim.get('status')
            if claim_status == 'approved':
                location_info = claim.get('finder_contact', '학생복지처')
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=008000][b]승인 완료[/b][/color]\n" \
                                 f"수령 장소: [b]{location_info}[/b]\n" \
                                 "(학생복지처에 방문하여 물품을 수령하세요)", color=[0.2, 0.2, 0.2, 1]))
            elif claim_status == 'rejected':
                item_box.add_widget(self.create_wrapping_label(text_content="[color=A01010][b]신청 거절[/b][/color]\n(관리자가 신청을 거절했습니다)", color=[0.2, 0.2, 0.2, 1]))
            else:
                item_box.add_widget(self.create_wrapping_label(text_content="[color=F08000][b]관리자 검토 중[/b][/color]\n(관리자가 신청 내역을 확인하고 있습니다)", color=[0.2, 0.2, 0.2, 1]))
            self.grid.add_widget(item_box)

class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = 'guest'
        self.current_user_nickname = 'Guest'
        self.current_user_role = 'guest'
        self.user_token = None
        self.current_user_uid = None
        self.all_items = []
        self.claims = []
        self.all_clubs = []
        self.notification_keywords = ['지갑']

    def build(self):
        self.title = "Campus Link"
        sm = ScreenManager()
        
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(MainScreen(name='main'))
        
        sm.add_widget(ClubScreen(name='club'))
        sm.add_widget(ClubDetailScreen(name='club_detail'))
        sm.add_widget(ClubCreateScreen(name='club_create'))
        sm.add_widget(ClubApplicationScreen(name='club_apply'))
        sm.add_widget(ClubManagementScreen(name='club_management'))
        sm.add_widget(MemberApprovalScreen(name='member_approval'))
        sm.add_widget(MemberManagementScreen(name='member_management'))
        sm.add_widget(PostScreen(name='post_screen'))
        sm.add_widget(ClubFreeBoardScreen(name='club_free_board'))

        sm.add_widget(LostAndFoundScreen(name='lost_found'))
        sm.add_widget(AddItemScreen(name='add_item'))
        sm.add_widget(ItemDetailScreen(name='item_detail'))

        sm.add_widget(AdminMainScreen(name='admin_main'))
        sm.add_widget(ClubApprovalScreen(name='club_approval'))
        sm.add_widget(ItemApprovalScreen(name='item_approval'))
        sm.add_widget(AdminClaimApprovalScreen(name='admin_claim_approval'))

        sm.add_widget(ClaimManagementScreen(name='claim_management'))
        sm.add_widget(MyClaimsScreen(name='my_claims'))
        
        return sm

if __name__ == '__main__':
    MyApp().run()
