import kivy
import os # 파일 경로를 위해 os 모듈 임포트
import requests # API 통신을 위해 requests 모듈 임포트
import json

# Kivy 기본 위젯 및 레이아웃 모듈 임포트
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner # 카테고리 선택을 위해 Spinner 추가
# 검색 기능 UI를 위해 ScrollView와 GridLayout 추가
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
# Kivy 코어 텍스트 모듈 임포트 및 ScreenManager, FloatLayout 추가
from kivy.core.text import LabelBase # 폰트 등록을 위해 필요
from kivy.uix.screenmanager import ScreenManager, Screen # 화면 관리를 위해 필요
from kivy.uix.floatlayout import FloatLayout # 우측 상단 버튼 배치를 위해 필요
from kivy.graphics import Color, Rectangle, RoundedRectangle # 배경색 및 둥근 모서리를 위한 import 추가
from kivy.metrics import dp # dp 단위를 사용하기 위해 import
from kivy.properties import ObjectProperty, StringProperty # 위젯 참조 및 속성 사용을 위해 import
from kivy.uix.behaviors import ButtonBehavior # 커스텀 버튼 위젯을 위해 import
# Kivy 앱의 기본 이미지 경로를 사용하기 위해 Kivy 경로 라이브러리 임포트
from kivy.resources import resource_find

# 스마트폰 기능 접근을 위한 plyer 임포트 (PC 환경 예외 처리 포함)
try:
    from plyer import filechooser
except ImportError:
    # plyer가 설치되지 않은 PC 환경을 위한 mock(가짜) 객체
    class MockFileChooser:
        def open_file(self, *args, **kwargs):
            show_info_popup('알림', '이 기능은 모바일 환경에서만\n사용할 수 있습니다.')
        def on_selection(self, *args):
            pass
    filechooser = MockFileChooser()


# Kivy 버전 명시
kivy.require('1.11.1')

# --------------------------------------------------------
# 폰트 설정 및 등록
# 중요: 'NanumGothic.ttf' 파일이 이 파이썬 파일과 같은 폴더에 있어야 합니다.
FONT_NAME = 'NanumFont' # Kivy 내부에서 사용할 폰트 이름
# 안드로이드 호환을 위해 절대 경로로 폰트 경로를 지정합니다.
FONT_PATH = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')

# Kivy에 사용할 폰트 등록
try:
    LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH)
except Exception as e:
    # 폰트 파일을 찾지 못하면 오류 메시지를 콘솔에 출력
    print(f"폰트 등록 오류: {e}. 'NanumGothic.ttf' 파일이 현재 폴더에 있는지, buildozer.spec에 ttf가 포함됐는지 확인하세요.")
# --------------------------------------------------------

# --------------------------------------------------------
# API 서버 연동 설정
# --------------------------------------------------------
# 사용자의 로컬 IP 주소로 API 서버 주소를 설정합니다.
BASE_URL = 'http://172.26.17.35:8000'
LOGIN_URL = f'{BASE_URL}/auth/login/'
SIGNUP_URL = f'{BASE_URL}/auth/register/' # 회원가입 URL 수정
POSTS_URL = f'{BASE_URL}/api/clubposts/'

def handle_login(username, password):
    """로그인 API를 호출하고 결과를 반환합니다."""
    payload = {
        'username': username,
        'password': password
    }
    try:
        response = requests.post(LOGIN_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        # 서버가 토큰, user_id, role을 반환한다고 가정
        return data.get('token'), data.get('user_id'), data.get('role', 'user')
    except requests.exceptions.RequestException as e:
        print(f"로그인 실패: {e}")
        # 서버로부터 응답(4xx, 5xx 에러)을 받은 경우
        if e.response is not None:
            try:
                error_data = e.response.json()
                message = error_data.get('non_field_errors', ['로그인 정보가 올바르지 않습니다.'])[0]
                return None, None, message
            except json.JSONDecodeError:
                return None, None, "서버에서 잘못된 응답을 받았습니다."
        # 서버에 연결조차 되지 않은 경우
        else:
            return None, None, "서버에 연결할 수 없습니다."


def handle_signup(payload):
    """회원가입 API를 호출하고 결과를 반환합니다."""
    try:
        response = requests.post(SIGNUP_URL, json=payload, timeout=5)
        response.raise_for_status() # 2xx 상태 코드가 아니면 예외 발생
        return True, "회원가입이 완료되었습니다."
    except requests.exceptions.RequestException as e:
        print(f"회원가입 실패: {e}")
        if e.response is not None:
            # 500 에러와 같이 JSON이 아닌 응답 처리
            if e.response.status_code == 500:
                return False, "서버 내부 오류가 발생했습니다.\n관리자에게 문의하세요."
            try:
                error_data = e.response.json()
                error_messages = []
                for key, value in error_data.items():
                    error_messages.append(f"{key}: {', '.join(value)}")
                return False, "\n".join(error_messages)
            except json.JSONDecodeError:
                return False, "서버에서 잘못된 응답을 받았습니다."
        else:
            return False, "서버에 연결할 수 없습니다."

def get_club_posts(auth_token):
    """헤더에 토큰을 포함하여 게시물 목록을 요청합니다."""
    if not auth_token:
        print("인증 토큰이 없어 게시물을 조회할 수 없습니다.")
        return None
    headers = {
        'Authorization': f'Token {auth_token}'
    }
    try:
        response = requests.get(POSTS_URL, headers=headers)
        response.raise_for_status()
        posts = response.json()
        print("게시물 목록:", posts)
        return posts
    except requests.exceptions.RequestException as e:
        print(f"게시물 조회 실패: {e}")
        return None

# --------------------------------------------------------
# 공통 UI 스타일 함수
# --------------------------------------------------------
DEFAULT_IMAGE = resource_find('data/logo/kivy-icon-256.png')

class WhitePopup(Popup):
    def __init__(self, **kwargs):
        custom_content = BoxLayout(orientation='vertical', padding=(dp(15), dp(10)))
        
        if 'title' in kwargs:
            title_label = Label(
                text=f"[b]{kwargs.get('title', '')}[/b]", 
                font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True,
                size_hint_y=None, height=dp(40), font_size='20sp'
            )
            custom_content.add_widget(title_label)

        if 'content' in kwargs:
            user_content = kwargs.pop('content')
            custom_content.add_widget(user_content)

        kwargs['content'] = custom_content
        kwargs['title'] = ''

        super().__init__(**kwargs)

        self.separator_height = 0
        self.background = ''

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(radius=[dp(10)])

        def update_rect(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
        
        custom_content.bind(pos=update_rect, size=update_rect)

def get_rounded_textinput(hint_text, password=False, input_type='text'):
    return TextInput(
        hint_text=hint_text, multiline=False, password=password, font_size='18sp',
        font_name=FONT_NAME, padding=[dp(15), dp(10), dp(15), dp(10)],
        size_hint_y=None, height=dp(55), background_normal='',
        background_color=[1, 1, 1, 1], foreground_color=[0, 0, 0, 1],
        input_type=input_type
    )

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.radius = [dp(10)]

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

def get_styled_button(text, bg_color, text_color, font_size='22sp'):
    btn = RoundedButton(
        text=text, font_size=font_size, font_name=FONT_NAME,
        color=text_color, size_hint_y=None, height=dp(60)
    )
    btn.bg_color = bg_color
    return btn

def show_info_popup(title, message, callback=None, button_text="확인", button_color=[0.2, 0.6, 1, 1], size_hint=(0.8, 0.4)):
    """정보/알림 팝업을 띄우는 헬퍼 함수"""
    content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=(dp(10)))
    
    msg_label = Label(text=message, font_name=FONT_NAME, color=[0, 0, 0, 1], halign='center')
    msg_label.bind(size=msg_label.setter('text_size'))
    content_layout.add_widget(msg_label)

    confirm_button = get_styled_button(button_text, button_color, [1, 1, 1, 1], font_size='20sp')
    confirm_button.height = dp(50)
    content_layout.add_widget(confirm_button)
    
    popup = WhitePopup(title=title, content=content_layout, size_hint=size_hint, auto_dismiss=False)
    
    def on_confirm(instance):
        popup.dismiss()
        if callback:
            callback()

    confirm_button.bind(on_press=on_confirm)
    popup.open()

class ClubListItem(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(ClubListItem, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class LostItemListItem(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(LostItemListItem, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.95, 0.95, 0.8, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

# --------------------------------------------------------
# 화면 기본 클래스
# --------------------------------------------------------
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

# --------------------------------------------------------
# 메인 화면
# --------------------------------------------------------
class MainScreen(WhiteBgScreen):
    # ... (기존 코드와 동일, 변경 없음)
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        root_float = FloatLayout()

        # 메인 컨텐츠 레이아웃
        main_content = BoxLayout(orientation='vertical', padding=[dp(40), dp(100), dp(40), dp(80)], spacing=dp(25))

        # 1. 메인 타이틀
        main_content.add_widget(Label(
            text="[b]Campus Link 메인[/b]",
            font_size='38sp',
            color=[0.1, 0.4, 0.7, 1], # 진한 파란색
            font_name=FONT_NAME,
            markup=True,
            size_hint_y=None, height=dp(70),
            halign='center', valign='middle'
        ))

        # 2. 환영 메시지
        self.welcome_label = Label(
            text="환영합니다! 어떤 정보가 필요하신가요?",
            font_size='18sp',
            font_name=FONT_NAME,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None, height=dp(50)
        )
        main_content.add_widget(self.welcome_label)

        main_content.add_widget(Label(size_hint_y=None, height=dp(10)))

        # 3. 네비게이션 버튼 레이아웃 (Grid 대신 BoxLayout 사용)
        nav_layout = BoxLayout(orientation='vertical', spacing=dp(15))

        # 네비게이션 버튼 생성 및 바인딩 헬퍼 함수
        def create_nav_button(text, screen_name, bg_color):
            btn = get_styled_button(text, bg_color, [1, 1, 1, 1], font_size='24sp')
            btn.bind(on_press=lambda *args: self.go_to_screen(screen_name))
            return btn

        # 기능별 버튼 (플로우 차트 구조 반영) - 색상 변경
        nav_layout.add_widget(create_nav_button("동아리 게시판", 'club', [0.0, 0.2, 0.6, 1])) # 남색
        nav_layout.add_widget(create_nav_button("분실물 게시판", 'lost_found', [0.2, 0.6, 1, 1])) # 파란색
        nav_layout.add_widget(create_nav_button("개인 시간표", 'timetable', [0.53, 0.81, 0.92, 1])) # 하늘색

        main_content.add_widget(nav_layout)

        # 스페이서
        main_content.add_widget(Label())

        root_float.add_widget(main_content)

        # 4. 설정 버튼 (우측 상단)
        settings_button = Button(
            text="설정",
            font_size='18sp',
            font_name=FONT_NAME,
            background_normal='',
            background_color=[0, 0, 0, 0], # 배경 투명
            color=[0.1, 0.4, 0.7, 1], # 텍스트 색상
            size_hint=(None, None),
            size=(dp(90), dp(50)),
            pos_hint={'right': 1, 'top': 1},
        )
        settings_button.bind(on_press=self.show_settings_popup)
        root_float.add_widget(settings_button)

        self.add_widget(root_float)

    def on_enter(self, *args):
        # 화면에 들어올 때마다 사용자 이름으로 환영 메시지 업데이트
        app = App.get_running_app()
        self.welcome_label.text = f"환영합니다, {app.current_user}님! 어떤 정보가 필요하신가요?"

    def show_settings_popup(self, instance):
        """설정 팝업을 표시합니다. (사이드 패널 스타일)"""
        app = App.get_running_app()
        # 팝업 인스턴스를 먼저 생성하여 닫기 버튼에 바인딩할 수 있게 합니다.
        popup = Popup(
            title="",
            separator_height=0,
            size_hint=(0.6, 1.0),
            pos_hint={'x': 0.4, 'y': 0},
            auto_dismiss=True,
            background='' # 팝업 기본 배경 투명하게 설정
        )

        # 팝업 전체를 담을 컨테이너 (여기에 흰색 배경을 그립니다)
        full_popup_content = BoxLayout(orientation='vertical')

        # 팝업 내용 배경을 흰색으로 설정
        with full_popup_content.canvas.before:
            Color(1, 1, 1, 1) # 흰색 배경
            content_bg = Rectangle(size=full_popup_content.size, pos=full_popup_content.pos)
        full_popup_content.bind(size=lambda i, v: setattr(content_bg, 'size', v),
                                pos=lambda i, v: setattr(content_bg, 'pos', v))

        BLUE_STRIPE_COLOR = [0.1, 0.4, 0.7, 1] # 진한 파란색

        # 1. 커스텀 헤더 (파란색 스트라이프 및 닫기 버튼)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[dp(10), 0, dp(10), 0])

        # 파란색 스트라이프 배경 그리기 (header 위젯에)
        with header.canvas.before:
            Color(*BLUE_STRIPE_COLOR)
            header_bg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda i, v: setattr(header_bg, 'size', v),
                    pos=lambda i, v: setattr(header_bg, 'pos', v))


        # 1-1. 닫기 버튼 (왼쪽)
        close_button = Button(
            text="X",
            font_size='22sp',
            size_hint=(None, 1), # 높이는 부모와 동일하게
            width=dp(40),
            color=[1, 1, 1, 1], # 흰색 텍스트
            background_normal='',
            background_color=[0, 0, 0, 0] # 투명
        )
        close_button.bind(on_press=popup.dismiss) # 닫기 기능 바인딩
        header.add_widget(close_button)

        # 1-2. 팝업 제목
        header.add_widget(Label(
            text="[b]앱 설정[/b]",
            font_name=FONT_NAME,
            color=[1, 1, 1, 1], # 흰색 텍스트
            markup=True,
            font_size='22sp'
        ))

        full_popup_content.add_widget(header)

        # 2. 메인 컨텐츠 (로그아웃 정보)
        content_layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(30))

        # 2-1. 로그인 정보 표시
        info_label = Label(
            text=f"[b]Campus Link 계정[/b]\n\n현재 사용자: {app.current_user}\n\n앱 설정 및 정보",
            font_size='18sp',
            font_name=FONT_NAME,
            color=[0, 0, 0, 1], # 검은색 텍스트
            markup=True,
            size_hint_y=None,
            height=dp(150),
            halign='center',
            valign='top'
        )
        content_layout.add_widget(info_label)

        # 관리자인 경우 '관리자 메뉴' 버튼 추가
        if app.current_user_role == 'admin':
            admin_button = get_styled_button("관리자 메뉴", [0.2, 0.4, 0.8, 1], [1, 1, 1, 1], font_size='18sp')
            admin_button.height = dp(50)
            def go_to_admin_menu(instance):
                self.manager.current = 'admin_main'
                popup.dismiss()
            admin_button.bind(on_press=go_to_admin_menu)
            content_layout.add_widget(admin_button)

        content_layout.add_widget(Label()) # 스페이서

        # 2-2. 로그아웃 버튼 (둥근 스타일 적용)
        logout_button = get_styled_button("로그아웃", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])
        logout_button.height = dp(50)
        content_layout.add_widget(logout_button)

        full_popup_content.add_widget(content_layout)

        # 팝업 content 설정
        popup.content = full_popup_content

        def perform_logout(btn_instance):
            self.manager.current = 'login'
            login_screen = self.manager.get_screen('login')
            if login_screen:
                login_screen.username_input.text = ''
                login_screen.password_input.text = ''
            popup.dismiss()

        logout_button.bind(on_press=perform_logout)

        popup.open()


# --------------------------------------------------------
# 관리자 화면들
# ... (기존 코드와 동일, 변경 없음)
# --------------------------------------------------------
class AdminMainScreen(WhiteBgScreen):
    """관리자 메인 메뉴 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))

        main_layout.add_widget(Label(
            text="[b]관리자 메뉴[/b]", font_size='38sp', color=[0.7, 0.1, 0.1, 1],
            font_name=FONT_NAME, markup=True, size_hint_y=None, height=dp(70)
        ))

        main_layout.add_widget(Label(size_hint_y=0.2)) # Spacer

        approval_button = get_styled_button("동아리 개설 관리", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        approval_button.bind(on_press=lambda *args: self.go_to_screen('club_approval'))
        main_layout.add_widget(approval_button)

        item_approval_button = get_styled_button("분실물 관리", [1, 0.5, 0.3, 1], [1, 1, 1, 1])
        item_approval_button.bind(on_press=lambda *args: self.go_to_screen('item_approval'))
        main_layout.add_widget(item_approval_button)

        main_layout.add_widget(Label()) # Spacer

        back_button = get_styled_button("메인 화면으로", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1])
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        main_layout.add_widget(back_button)

        self.add_widget(main_layout)


class ClubApprovalScreen(WhiteBgScreen):
    """동아리 개설 신청을 관리하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]동아리 개설 승인[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.approval_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.approval_grid.bind(minimum_height=self.approval_grid.setter('height'))

        scroll_view.add_widget(self.approval_grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        self.bind(on_enter=self.refresh_approval_list)

    def refresh_approval_list(self, *args):
        app = App.get_running_app()
        self.update_approval_list(app.pending_clubs)

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

        # 승인된 동아리를 all_clubs에 추가하고 pending_clubs에서 제거
        if approved_club in app.pending_clubs:
            app.all_clubs.append(approved_club)
            app.pending_clubs.remove(approved_club)

        # 목록 새로고침
        self.refresh_approval_list()

    def reject_club(self, instance):
        rejected_club = instance.club_data
        app = App.get_running_app()
        if rejected_club in app.pending_clubs:
            app.pending_clubs.remove(rejected_club)
        self.refresh_approval_list()


class ItemApprovalScreen(WhiteBgScreen):
    """분실물 등록 신청을 관리하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]분실물 등록 승인[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 1))
        self.approval_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.approval_grid.bind(minimum_height=self.approval_grid.setter('height'))

        scroll_view.add_widget(self.approval_grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        self.bind(on_enter=self.refresh_approval_list)

    def refresh_approval_list(self, *args):
        app = App.get_running_app()
        self.update_approval_list(app.pending_items)

    def update_approval_list(self, pending_items):
        self.approval_grid.clear_widgets()
        if not pending_items:
            self.approval_grid.add_widget(Label(text="승인 대기 중인 게시물이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
        else:
            for item_request in pending_items:
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100), padding=dp(10), spacing=dp(10))

                img = Image(source=item_request.get('image', DEFAULT_IMAGE), size_hint_x=0.3, allow_stretch=True)
                info_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
                info_layout.add_widget(Label(text=f"[b]{item_request['name']}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, halign='left', valign='top'))
                info_layout.add_widget(Label(text=f"장소: {item_request['loc']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], halign='left', valign='top'))

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
        if approved_item in app.pending_items:
            app.all_items.append(approved_item)
            app.pending_items.remove(approved_item)
            self.check_keyword_notification(approved_item) # 키워드 알림 체크
        self.refresh_approval_list()

    def reject_item(self, instance):
        rejected_item = instance.item_data
        app = App.get_running_app()
        if rejected_item in app.pending_items:
            app.pending_items.remove(rejected_item)
        self.refresh_approval_list()

    def check_keyword_notification(self, new_item):
        """새 아이템이 등록될 때 키워드와 일치하는지 확인하고 팝업을 띄웁니다."""
        app = App.get_running_app()
        item_text = f"{new_item['name']} {new_item['desc']}".lower()
        for keyword in app.notification_keywords:
            if keyword.lower() in item_text:
                show_info_popup('키워드 알림', f"등록하신 키워드 '{keyword}'가 포함된\n'{new_item['name']}' 게시물이 등록되었습니다.")
                break # 여러 키워드에 해당되더라도 한번만 알림


# --------------------------------------------------------
# 동아리 화면들
# ... (기존 코드와 동일, 변경 없음)
# --------------------------------------------------------
class ClubScreen(WhiteBgScreen):
    """동아리 목록을 보여주는 메인 화면"""
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
        self.update_club_list(app.all_clubs)
        self.search_input.text = "" # 검색창 초기화

    def update_club_list(self, clubs):
        self.results_grid.clear_widgets()
        if not clubs:
            self.results_grid.add_widget(Label(text="표시할 동아리가 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
        else:
            for club in clubs:
                item = ClubListItem(
                    orientation='vertical',
                    padding=dp(15),
                    spacing=dp(5),
                    size_hint_y=None,
                    height=dp(80)
                )

                item.club_data = club
                item.bind(on_press=self.view_club_details)

                name_label = Label(text=f"[b]{club['name']}[/b]", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True, halign='left', valign='middle', size_hint_y=None, height=dp(30))
                desc_label = Label(text=club['short_desc'], font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], halign='left', valign='middle', size_hint_y=None, height=dp(20))

                for label in [name_label, desc_label]:
                    label.bind(size=label.setter('text_size'))
                    item.add_widget(label)

                self.results_grid.add_widget(item)

    def view_club_details(self, instance):
        """ 동아리 상세 정보 화면으로 이동 """
        detail_screen = self.manager.get_screen('club_detail')
        detail_screen.club_data = instance.club_data # 선택된 동아리 정보 전달
        self.go_to_screen('club_detail')

    def search_clubs(self, instance):
        app = App.get_running_app()
        search_term = self.search_input.text.lower()
        if not search_term:
            results = app.all_clubs
        else:
            results = [club for club in app.all_clubs if search_term in club['name'].lower()]
        self.update_club_list(results)


class ClubDetailScreen(WhiteBgScreen):
    """동아리 상세 정보를 보여주는 화면"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        """화면에 들어올 때마다 위젯을 다시 그림"""
        self.main_layout.clear_widgets() # 이전 위젯들 제거

        if self.club_data:
            app = App.get_running_app()

            # 상단 헤더
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            self.main_layout.add_widget(header)

            scroll_view = ScrollView()
            content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
            content_layout.bind(minimum_height=content_layout.setter('height'))
            scroll_view.add_widget(content_layout)
            self.main_layout.add_widget(scroll_view)

            # --- UI 개선 부분 ---
            # 동아리 소개
            title_intro = Label(text="[b]동아리 소개[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, size_hint_y=None, height=dp(40), font_size='20sp', halign='left')
            title_intro.bind(size=title_intro.setter('text_size'))
            content_layout.add_widget(title_intro)
            
            long_desc_label = Label(text=self.club_data['long_desc'], font_name=FONT_NAME, color=[0.2,0.2,0.2,1], size_hint_y=None, halign='left')
            long_desc_label.bind(width=lambda *x: long_desc_label.setter('text_size')(long_desc_label, (long_desc_label.width, None)),
                                 texture_size=lambda *x: long_desc_label.setter('height')(long_desc_label, long_desc_label.texture_size[1]))
            content_layout.add_widget(long_desc_label)

            # 공지사항, 활동내역, 후기 등
            for section_title, data_key in [("[b]공지사항[/b]", "announcements"), ("[b]활동 내역[/b]", "activities"), ("[b]후기[/b]", "reviews")]:
                title_label = Label(text=section_title, font_name=FONT_NAME, color=[0,0,0,1], markup=True, size_hint_y=None, height=dp(40), font_size='20sp', halign='left')
                title_label.bind(size=title_label.setter('text_size'))
                content_layout.add_widget(title_label)
                
                if self.club_data[data_key]:
                    for item in self.club_data[data_key]:
                        item_label = Label(text=f"- {item}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], size_hint_y=None, halign='left')
                        item_label.bind(width=lambda *x: item_label.setter('text_size')(item_label, (item_label.width, None)),
                                        texture_size=lambda *x: item_label.setter('height')(item_label, item_label.texture_size[1]))
                        content_layout.add_widget(item_label)
                else:
                    empty_label = Label(text="아직 내용이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(30), halign='left')
                    empty_label.bind(size=empty_label.setter('text_size'))
                    content_layout.add_widget(empty_label)
            # --- UI 개선 끝 ---


            # 사용자 권한에 따라 다른 버튼 표시
            button_layout = BoxLayout(size_hint_y=None, height=dp(60), padding=[0, dp(10), 0, 0])
            is_president = app.current_user == self.club_data['president']
            is_member = app.current_user in self.club_data['members']

            if is_president:
                manage_button = get_styled_button("동아리 관리", [0.8, 0.1, 0.1, 1], [1, 1, 1, 1])
                manage_button.bind(on_press=self.go_to_club_management)
                button_layout.add_widget(manage_button)
            elif is_member:
                review_button = get_styled_button("후기 작성", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
                review_button.bind(on_press=self.go_to_post_screen)
                button_layout.add_widget(review_button)
            else: # 비회원
                apply_button = get_styled_button("신청하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
                apply_button.bind(on_press=self.go_to_application)
                button_layout.add_widget(apply_button)
            self.main_layout.add_widget(button_layout)


    def go_to_application(self, instance):
        app_screen = self.manager.get_screen('club_apply')
        app_screen.club_data = self.club_data # 신청할 동아리 정보 전달
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
    """새로운 동아리를 개설하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))

        # 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]동아리 개설 신청[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        # 입력 필드
        self.club_name = get_rounded_textinput('동아리 이름')
        self.short_desc = get_rounded_textinput('한줄 소개 (목록에 표시됩니다)')
        self.long_desc = TextInput(hint_text='자세한 설명 (동아리 활동, 모집 대상 등)', font_name=FONT_NAME, size_hint_y=None, height=dp(150), padding=dp(15))

        main_layout.add_widget(self.club_name)
        main_layout.add_widget(self.short_desc)
        main_layout.add_widget(self.long_desc)
        main_layout.add_widget(Label()) # Spacer

        # 개설하기 버튼
        create_button = get_styled_button("신청하기", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
        create_button.bind(on_press=self.request_club_creation)
        main_layout.add_widget(create_button)

        self.add_widget(main_layout)

    def request_club_creation(self, instance):
        name = self.club_name.text
        s_desc = self.short_desc.text
        l_desc = self.long_desc.text

        if not name or not s_desc or not l_desc:
            show_info_popup('오류', '모든 항목을 입력해주세요.', button_color=[0.8, 0.2, 0.2, 1])
            return

        app = App.get_running_app()
        new_club_request = {
            'name': name,
            'short_desc': s_desc,
            'long_desc': l_desc,
            'president': app.current_user,
            'members': [app.current_user], # 개설자는 자동으로 멤버
            'applications': [],
            'announcements': [],
            'activities': [],
            'reviews': []
        }

        # App의 pending_clubs 리스트에 신청 정보 추가
        app.pending_clubs.append(new_club_request)

        # 필드 초기화
        self.club_name.text = ""
        self.short_desc.text = ""
        self.long_desc.text = ""

        show_info_popup('알림', '동아리 개설 신청이 완료되었습니다.\n관리자 승인 후 등록됩니다.', callback=lambda: self.go_to_screen('club'))


class ClubApplicationScreen(WhiteBgScreen):
    """동아리 가입 신청 화면"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        if self.club_data:
            # 헤더
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']} 신청[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            self.main_layout.add_widget(header)

            # 입력 필드
            self.intro = TextInput(hint_text='자기소개 및 지원 동기', font_name=FONT_NAME, size_hint_y=None, height=dp(150), padding=dp(15))

            self.main_layout.add_widget(Label(text="가입 신청서", font_name=FONT_NAME, size_hint_y=None, height=dp(30)))
            self.main_layout.add_widget(self.intro)
            self.main_layout.add_widget(Label()) # Spacer

            # 신청하기 버튼
            apply_button = get_styled_button("신청서 제출", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
            apply_button.bind(on_press=self.submit_application)
            self.main_layout.add_widget(apply_button)

    def submit_application(self, instance):
        if not self.intro.text:
            show_info_popup('오류', '자기소개를 입력해주세요.', button_color=[0.8, 0.2, 0.2, 1])
            return

        app = App.get_running_app()
        application_data = {
            'user': app.current_user,
            'intro': self.intro.text
        }

        # 해당 동아리의 applications 리스트에 신청 정보 추가
        for club in app.all_clubs:
            if club['name'] == self.club_data['name']:
                # 중복 신청 방지
                if any(app['user'] == app.current_user for app in club['applications']):
                    show_info_popup('알림', '이미 가입을 신청했습니다.')
                    return

                club['applications'].append(application_data)
                break

        show_info_popup('신청 완료', '가입 신청이 완료되었습니다.\n회장 승인 후 가입됩니다.', callback=lambda: self.go_to_screen('club_detail'))


class ClubManagementScreen(WhiteBgScreen):
    """동아리 회장이 동아리를 관리하는 화면"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()
        if self.club_data:
            # 헤더
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
            header.add_widget(back_button)
            header.add_widget(Label(text=f"[b]{self.club_data['name']} 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            self.main_layout.add_widget(header)

            self.main_layout.add_widget(Label(size_hint_y=0.2)) # Spacer

            # 관리 메뉴 버튼
            member_approval_button = get_styled_button("가입 신청 관리", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
            member_approval_button.bind(on_press=self.go_to_member_approval)
            self.main_layout.add_widget(member_approval_button)

            post_announcement_button = get_styled_button("공지사항 작성", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
            post_announcement_button.bind(on_press=lambda *args: self.go_to_post('announcement'))
            self.main_layout.add_widget(post_announcement_button)

            post_activity_button = get_styled_button("활동내역 작성", [0.5, 0.5, 0.8, 1], [1, 1, 1, 1])
            post_activity_button.bind(on_press=lambda *args: self.go_to_post('activity'))
            self.main_layout.add_widget(post_activity_button)

            self.main_layout.add_widget(Label()) # Spacer

    def go_to_member_approval(self, instance):
        approval_screen = self.manager.get_screen('member_approval')
        approval_screen.club_data = self.club_data
        self.go_to_screen('member_approval')

    def go_to_post(self, post_type):
        post_screen = self.manager.get_screen('post_screen')
        post_screen.club_data = self.club_data
        post_screen.post_type = post_type
        self.go_to_screen('post_screen')


class MemberApprovalScreen(WhiteBgScreen):
    """동아리 가입 신청을 승인/거절하는 화면"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # 헤더
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

        # 신청 목록
        scroll_view = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        if self.club_data:
            self.header_title.text = f"[b]{self.club_data['name']} 신청 관리[/b]"
            applications = self.club_data.get('applications', [])
            if not applications:
                self.grid.add_widget(Label(text="가입 신청이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
            else:
                for app_data in applications:
                    item_layout = BoxLayout(size_hint_y=None, height=dp(120), padding=dp(10), spacing=dp(10))
                    info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
                    info_layout.add_widget(Label(text=f"[b]신청자: {app_data['user']}[/b]", font_name=FONT_NAME, markup=True, color=[0,0,0,1], halign='left'))
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

    def approve_member(self, instance):
        app_data = instance.app_data
        self.club_data['members'].append(app_data['user'])
        self.club_data['applications'].remove(app_data)
        self.refresh_list()

    def reject_member(self, instance):
        app_data = instance.app_data
        self.club_data['applications'].remove(app_data)
        self.refresh_list()


class PostScreen(WhiteBgScreen):
    """공지사항, 활동내역, 후기 등을 작성하는 화면"""
    club_data = ObjectProperty(None)
    post_type = StringProperty('') # 'announcement', 'activity', 'review'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        type_map = {
            'announcement': '공지사항',
            'activity': '활동내역',
            'review': '후기'
        }
        title = type_map.get(self.post_type, '글')

        # 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
        header.add_widget(back_button)
        header.add_widget(Label(text=f"[b]{title} 작성[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        self.main_layout.add_widget(header)

        # 입력 필드
        self.content_input = TextInput(hint_text=f'{title} 내용을 입력하세요.', font_name=FONT_NAME, size_hint_y=0.8, padding=dp(15))
        self.main_layout.add_widget(self.content_input)

        # 등록 버튼
        submit_button = get_styled_button("등록하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        submit_button.bind(on_press=self.submit_post)
        self.main_layout.add_widget(submit_button)

    def submit_post(self, instance):
        content = self.content_input.text.strip()
        if not content:
            show_info_popup('오류', '내용을 입력해주세요.', button_color=[0.8, 0.2, 0.2, 1])
            return

        key_map = {
            'announcement': 'announcements',
            'activity': 'activities',
            'review': 'reviews'
        }
        data_key = key_map.get(self.post_type)
        if self.club_data and data_key:
            self.club_data[data_key].append(content)
            show_info_popup('성공', '등록이 완료되었습니다.', callback=lambda: self.go_to_screen('club_detail'))
        else:
            show_info_popup('오류', '데이터 저장에 실패했습니다.', button_color=[0.8, 0.2, 0.2, 1])

    def go_to_screen(self, screen_name):
        # 상세 화면으로 돌아갈 때 데이터가 갱신되도록 club_data를 다시 전달
        if screen_name == 'club_detail':
            detail_screen = self.manager.get_screen(screen_name)
            detail_screen.club_data = self.club_data
        self.manager.current = screen_name

# --------------------------------------------------------
# 분실물 화면들
# --------------------------------------------------------
class AddItemScreen(WhiteBgScreen):
    is_lost = ObjectProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(20)])

        # 헤더
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

        # 스크롤 가능한 컨텐츠 영역
        scroll_view = ScrollView()
        content_layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=[0, dp(10), 0, 0])
        content_layout.bind(minimum_height=content_layout.setter('height'))


        # 입력 필드
        self.name_input = get_rounded_textinput('물건 이름 (예: 에어팟 프로)')
        self.desc_input = get_rounded_textinput('자세한 설명 (선택)')
        self.loc_input = get_rounded_textinput('발견/분실 장소 (예: 중앙도서관 1층)')
        self.contact_input = get_rounded_textinput('연락처 (예: 010-1234-5678)')

        self.category_spinner = Spinner(
            text='카테고리 선택',
            values=('전자기기', '서적', '의류', '지갑/카드', '기타'),
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(55)
        )

        content_layout.add_widget(self.name_input)
        content_layout.add_widget(self.desc_input)
        content_layout.add_widget(self.loc_input)
        content_layout.add_widget(self.contact_input)
        content_layout.add_widget(self.category_spinner)

        # 사진 등록 부분
        self.image_path = "" # 이미지 경로 저장 변수
        photo_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), spacing=dp(10))
        self.photo_label = Label(text="사진이 선택되지 않았습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_x=0.7)
        photo_button = get_styled_button("사진 선택", [0.5, 0.7, 0.9, 1], [1, 1, 1, 1], font_size='18sp')
        photo_button.height = dp(55)
        photo_button.size_hint_x = 0.3
        photo_button.bind(on_press=self.select_photo)

        photo_layout.add_widget(self.photo_label)
        photo_layout.add_widget(photo_button)
        content_layout.add_widget(photo_layout)

        # 이미지 미리보기
        self.image_preview = Image(source=DEFAULT_IMAGE, size_hint_y=None, height=dp(150), fit_mode='contain')
        content_layout.add_widget(self.image_preview)

        content_layout.add_widget(Label(size_hint_y=None, height=dp(15))) # Spacer

        # 등록하기 버튼
        register_button = get_styled_button("등록 신청", [1, 0.5, 0.3, 1], [1, 1, 1, 1])
        register_button.bind(on_press=self.register_item)
        content_layout.add_widget(register_button)
        
        scroll_view.add_widget(content_layout)
        root_layout.add_widget(scroll_view)

        self.add_widget(root_layout)

    def on_enter(self, *args):
        # 화면에 들어올 때마다 제목과 필수 항목 조정
        if self.is_lost:
            self.header_title.text = "[b]분실물 등록[/b]"
        else:
            self.header_title.text = "[b]습득물 등록[/b]"

        # 필드 초기화
        self.name_input.text = ""
        self.desc_input.text = ""
        self.loc_input.text = ""
        self.contact_input.text = ""
        self.image_path = ""
        self.photo_label.text = "사진이 선택되지 않았습니다."
        self.image_preview.source = DEFAULT_IMAGE
        self.category_spinner.text = '카테고리 선택'

    def select_photo(self, instance):
        """plyer를 사용하여 파일 선택 창을 엽니다."""
        filechooser.open_file(on_selection=self.on_file_selection)

    def on_file_selection(self, selection):
        """파일이 선택되었을 때 호출될 콜백 함수입니다."""
        if selection:
            self.image_path = selection[0]
            self.photo_label.text = os.path.basename(self.image_path)
            self.image_preview.source = self.image_path
            self.image_preview.reload() # 이미지를 다시 로드하여 갱신합니다.

    def register_item(self, instance):
        name = self.name_input.text
        desc = self.desc_input.text
        loc = self.loc_input.text
        contact = self.contact_input.text
        category = self.category_spinner.text

        if not name or not loc or not contact or category == '카테고리 선택':
            show_info_popup('오류', '사진을 제외한 모든 항목을 입력해주세요.', button_color=[0.8, 0.2, 0.2, 1])
            return

        # 습득물인 경우 사진 필수
        if not self.is_lost and not self.image_path:
            show_info_popup('오류', '습득물은 사진을 반드시 첨부해야 합니다.', button_color=[0.8, 0.2, 0.2, 1])
            return

        # 이미지 경로가 없으면 기본 이미지 사용
        image = self.image_path if self.image_path else ""

        new_item = {
            'name': name, 'desc': desc, 'loc': loc, 'contact': contact,
            'image': image, 'category': category,
            'status': 'lost' if self.is_lost else 'found'
        }

        # App의 pending_items 리스트에 새 아이템 추가
        app = App.get_running_app()
        app.pending_items.append(new_item)

        show_info_popup('알림', '등록 신청이 완료되었습니다.\n관리자 승인 후 게시됩니다.', callback=lambda: self.go_to_screen('lost_found'))


class ItemDetailScreen(WhiteBgScreen):
    item_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        """화면에 들어올 때마다 위젯을 다시 그림"""
        self.main_layout.clear_widgets()

        if self.item_data:
            # 상단 헤더
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('lost_found'))
            header.add_widget(back_button)
            header.add_widget(Label(text="[b]분실물 상세 정보[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
            self.main_layout.add_widget(header)

            # 이미지
            image = Image(
                source=self.item_data.get('image') if self.item_data.get('image') else DEFAULT_IMAGE,
                size_hint_y=None,
                height=dp(250),
                fit_mode='contain'
            )
            self.main_layout.add_widget(image)

            # 정보 레이블
            self.main_layout.add_widget(Label(text=f"[b]물건:[/b] {self.item_data['name']}", font_name=FONT_NAME, color=[0,0,0,1], markup=True, size_hint_y=None, height=dp(40)))
            self.main_layout.add_widget(Label(text=f"[b]상세 설명:[/b] {self.item_data.get('desc', '없음')}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True, size_hint_y=None, height=dp(40)))
            self.main_layout.add_widget(Label(text=f"[b]장소:[/b] {self.item_data['loc']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True, size_hint_y=None, height=dp(40)))
            self.main_layout.add_widget(Label(text=f"[b]연락처:[/b] {self.item_data['contact']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True, size_hint_y=None, height=dp(40)))

            self.main_layout.add_widget(Label()) # Spacer


class LostAndFoundScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # 상단 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])

        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)

        header.add_widget(Label(
            text="[b]분실물 게시판[/b]",
            font_name=FONT_NAME,
            color=[0, 0, 0, 1],
            markup=True,
            font_size='26sp',
            halign='center', valign='middle'
        ))

        post_button = get_styled_button("+", [1, 0.5, 0.3, 1], [1, 1, 1, 1], font_size='24sp')
        post_button.height = dp(50)
        post_button.size_hint_x = None
        post_button.width = dp(60)
        post_button.bind(on_press=self.show_registration_choice_popup)
        header.add_widget(post_button)

        main_layout.add_widget(header)

        # 검색 및 필터링 UI
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
        category_label = Label(text='카테고리:', font_name=FONT_NAME, size_hint_x=0.3)
        self.category_spinner = Spinner(
            text='전체',
            values=('전체', '전자기기', '서적', '의류', '지갑/카드', '기타'),
            font_name=FONT_NAME,
            size_hint_x=0.7
        )
        self.category_spinner.bind(text=self.search_items)
        category_layout.add_widget(category_label)
        category_layout.add_widget(self.category_spinner)

        search_filter_layout.add_widget(keyword_layout)
        search_filter_layout.add_widget(category_layout)
        main_layout.add_widget(search_filter_layout)

        # 분실물 목록을 표시할 스크롤 뷰
        scroll_view = ScrollView(size_hint=(1, 1))
        self.items_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))

        scroll_view.add_widget(self.items_grid)
        main_layout.add_widget(scroll_view)

        # 알림 키워드 등록 UI
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

        # 화면이 처음 보일 때 전체 목록을 표시
        self.bind(on_enter=self.refresh_list)

    def show_registration_choice_popup(self, instance):
        """분실/습득 등록 선택 팝업을 띄웁니다."""
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        popup = WhitePopup(
            title='등록 종류 선택',
            content=popup_content,
            size_hint=(0.8, 0.5) # 세로 크기 늘림
        )

        def go_to_register(is_lost, *args):
            register_screen = self.manager.get_screen('add_item')
            register_screen.is_lost = is_lost
            self.manager.current = 'add_item'
            popup.dismiss()

        lost_button = get_styled_button("잃어버렸어요 (분실물 등록)", [0.8, 0.2, 0.2, 1], [1,1,1,1])
        lost_button.bind(on_press=lambda *args: go_to_register(True))

        found_button = get_styled_button("주웠어요 (습득물 등록)", [0.2, 0.6, 1, 1], [1,1,1,1])
        found_button.bind(on_press=lambda *args: go_to_register(False))

        popup_content.add_widget(lost_button)
        popup_content.add_widget(found_button)

        popup.open()

    def search_items(self, *args):
        """키워드와 카테고리로 아이템을 검색합니다."""
        app = App.get_running_app()
        keyword = self.search_input.text.lower()
        category = self.category_spinner.text

        filtered_list = app.all_items

        # 카테고리 필터링
        if category != '전체':
            filtered_list = [item for item in filtered_list if item.get('category') == category]

        # 키워드 필터링
        if keyword:
            filtered_list = [
                item for item in filtered_list
                if keyword in item['name'].lower() or keyword in item.get('desc', '').lower()
            ]

        self.update_item_list(filtered_list)

    def register_keyword(self, instance):
        app = App.get_running_app()
        keyword = self.keyword_input.text.strip()
        if keyword and keyword not in app.notification_keywords:
            app.notification_keywords.append(keyword)
            show_info_popup('알림', f"키워드 '{keyword}'가 등록되었습니다.")
            self.keyword_input.text = ""
        elif not keyword:
            show_info_popup('오류', "키워드를 입력해주세요.", button_color=[0.8, 0.2, 0.2, 1])
        else:
            show_info_popup('알림', f"이미 등록된 키워드입니다.")

    def refresh_list(self, *args):
        self.search_input.text = ""
        self.category_spinner.text = '전체'
        self.search_items()

    def update_item_list(self, items):
        """ 주어진 분실물 목록으로 화면을 업데이트합니다. (이미지 포함) """
        self.items_grid.clear_widgets()
        if not items:
            no_items_label = Label(
                text="표시할 분실물이 없습니다.",
                font_name=FONT_NAME,
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(100)
            )
            self.items_grid.add_widget(no_items_label)
        else:
            for item_data in items:
                item_layout = LostItemListItem(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(100),
                    spacing=dp(10),
                    padding=dp(5)
                )
                item_layout.item_data = item_data
                item_layout.bind(on_press=self.view_item_details)

                image = Image(
                    source=item_data.get('image') if item_data.get('image') else DEFAULT_IMAGE,
                    size_hint_x=None,
                    width=dp(90),
                    fit_mode='contain'
                )
                item_layout.add_widget(image)

                text_layout = BoxLayout(orientation='vertical', spacing=dp(5))

                status_text = "[b][color=1010A0]습득[/color][/b]" if item_data['status'] == 'found' else "[b][color=A01010]분실[/color][/b]"
                name_label = Label(
                    text=f"{status_text} {item_data['name']}", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(25)
                )
                loc_label = Label(
                    text=f"[b]장소:[/b] {item_data['loc']}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )

                text_layout.add_widget(name_label)
                text_layout.add_widget(loc_label)

                for label in [name_label, loc_label]:
                    label.bind(size=label.setter('text_size'))

                item_layout.add_widget(text_layout)
                self.items_grid.add_widget(item_layout)

    def view_item_details(self, instance):
        """ 분실물 상세 정보 화면으로 이동 """
        detail_screen = self.manager.get_screen('item_detail')
        detail_screen.item_data = instance.item_data
        self.go_to_screen('item_detail')


# --------------------------------------------------------
# 시간표 화면
# ... (기존 코드와 동일, 변경 없음)
# --------------------------------------------------------
class TimetableScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # 상단 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])

        # 버튼에 둥근 스타일 적용
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)

        header.add_widget(Label(
            text="[b]개인 시간표[/b]",
            font_name=FONT_NAME,
            color=[0, 0, 0, 1],
            markup=True,
            font_size='26sp',
            halign='center', valign='middle'
        ))

        main_layout.add_widget(header)

        # 더미 시간표 (Grid Layout을 사용하여 시간표 모양 구현)
        timetable_grid = BoxLayout(orientation='vertical', spacing=1, size_hint_y=None, height=dp(400))
        # 배경색을 연한 회색으로 변경 (구분선 역할)
        with timetable_grid.canvas.before:
             Color(0.9, 0.9, 0.9, 1)
             self.grid_bg = Rectangle(size=timetable_grid.size, pos=timetable_grid.pos)

        def update_grid_bg(instance, value):
            self.grid_bg.pos = instance.pos
            self.grid_bg.size = instance.size
        timetable_grid.bind(pos=update_grid_bg, size=update_grid_bg)


        # 시간표 제목 행 (월, 화, 수, 목, 금)
        day_names = ["", "월", "화", "수", "목", "금"]
        day_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=1)
        for day in day_names:
            day_label = Label(text=day, font_name=FONT_NAME, color=[0.1, 0.1, 0.1, 1],
                                  size_hint_x=1)
            with day_label.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                day_label.bg_rect = Rectangle(size=day_label.size, pos=day_label.pos)
            day_label.bind(pos=self._update_cell_bg, size=self._update_cell_bg)
            day_row.add_widget(day_label)
        timetable_grid.add_widget(day_row)

        # 수업 시간 (데이터 초기화)
        for i in range(1, 5): # 1교시부터 4교시
            class_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80), spacing=1)
            # 시간 컬럼
            time_label = Label(text=f"[b]{i}교시[/b]", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                                     size_hint_x=1)
            with time_label.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                time_label.bg_rect = Rectangle(size=time_label.size, pos=time_label.pos)
            time_label.bind(pos=self._update_cell_bg, size=self._update_cell_bg)
            class_row.add_widget(time_label)

            # 요일별 셀
            for j in range(5): # 월~금
                text = ""
                bg_color = [1, 1, 1, 1]

                # 데이터 모두 제거됨

                class_cell = Label(text=text, font_name=FONT_NAME, color=[0.1, 0.1, 0.1, 1],
                                       size_hint_x=1)
                with class_cell.canvas.before:
                    Color(*bg_color)
                    class_cell.bg_rect = Rectangle(size=class_cell.size, pos=class_cell.pos)
                class_cell.bind(pos=self._update_cell_bg, size=self._update_cell_bg)
                class_row.add_widget(class_cell)

            timetable_grid.add_widget(class_row)

        main_layout.add_widget(timetable_grid)

        main_layout.add_widget(Label(text="[b]시간표는 설정에서 편집할 수 있습니다. (현재 데이터 없음)[/b]", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], markup=True, size_hint_y=None, height=dp(30)))
        main_layout.add_widget(Label()) # 스페이서

        self.add_widget(main_layout)

    def _update_cell_bg(self, instance, value):
        """ 시간표 셀의 배경을 업데이트하는 콜백 함수 """
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size


# --------------------------------------------------------
# 회원가입 및 로그인 화면
# --------------------------------------------------------
class SignupScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.current_step = 'step1'

        self.main_container = BoxLayout(
            orientation='vertical', padding=[dp(50), dp(80), dp(50), dp(80)], spacing=dp(18)
        )
        self.add_widget(self.main_container)

        self.setup_step1()
        self.setup_step2()
        self.update_view()

    def setup_step1(self):
        self.step1_layout = BoxLayout(orientation='vertical', spacing=dp(15))
        self.step1_layout.add_widget(Label(
            text="[b]Campus Link 회원가입 (1/2)[/b]", font_size='32sp', font_name=FONT_NAME,
            color=[0.1, 0.4, 0.7, 1], markup=True, size_hint_y=None, height=dp(60)
        ))
        self.step1_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        self.student_id_input = get_rounded_textinput('학번 (예: 20240001)', input_type='number')
        self.name_input = get_rounded_textinput('이름')
        self.department_input = get_rounded_textinput('학과')
        self.grade_input = get_rounded_textinput('학년 (예: 3)', input_type='number')

        auth_layout = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        self.simple_auth_input = get_rounded_textinput('간편 인증 코드', input_type='number')
        self.simple_auth_input.size_hint_x = 0.7
        auth_button = get_styled_button("인증", [0.5, 0.7, 0.9, 1], [1, 1, 1, 1], font_size='18sp')
        auth_button.height = dp(55)
        auth_button.size_hint_x = 0.3
        auth_layout.add_widget(self.simple_auth_input)
        auth_layout.add_widget(auth_button)

        self.step1_layout.add_widget(self.student_id_input)
        self.step1_layout.add_widget(self.name_input)
        self.step1_layout.add_widget(self.department_input)
        self.step1_layout.add_widget(self.grade_input)
        self.step1_layout.add_widget(auth_layout)

        next_button = get_styled_button("다음 (1/2)", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        next_button.bind(on_press=self.go_to_step2)
        self.step1_layout.add_widget(next_button)

        cancel_button = get_styled_button("취소 (로그인 화면으로)", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1], font_size='18sp')
        cancel_button.height = dp(50)
        cancel_button.bind(on_press=self.go_to_login)
        self.step1_layout.add_widget(cancel_button)
        self.step1_layout.add_widget(Label())

    def setup_step2(self):
        self.step2_layout = BoxLayout(orientation='vertical', spacing=dp(15))
        self.step2_layout.add_widget(Label(
            text="[b]Campus Link 회원가입 (2/2)[/b]", font_size='32sp', font_name=FONT_NAME,
            color=[0.1, 0.4, 0.7, 1], markup=True, size_hint_y=None, height=dp(60)
        ))
        self.step2_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        self.email_input = get_rounded_textinput('이메일 주소', input_type='mail')
        self.nickname_input = get_rounded_textinput('닉네임')
        self.password_input = get_rounded_textinput('비밀번호 (최소 4자)', password=True)
        self.confirm_password_input = get_rounded_textinput('비밀번호 확인', password=True)

        self.step2_layout.add_widget(self.email_input)
        self.step2_layout.add_widget(self.nickname_input)
        self.step2_layout.add_widget(self.password_input)
        self.step2_layout.add_widget(self.confirm_password_input)

        signup_button = get_styled_button("회원가입 완료", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
        signup_button.bind(on_press=self.do_signup)
        self.step2_layout.add_widget(signup_button)

        prev_button = get_styled_button("이전", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1], font_size='18sp')
        prev_button.height = dp(50)
        prev_button.bind(on_press=self.go_to_step1)
        self.step2_layout.add_widget(prev_button)
        self.step2_layout.add_widget(Label())

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

    def go_to_login(self, instance=None):
        # Clear all fields
        for widget in self.step1_layout.children:
            if isinstance(widget, TextInput): widget.text = ''
            if isinstance(widget, BoxLayout):
                 for child in widget.children:
                     if isinstance(child, TextInput): child.text = ''
        for widget in self.step2_layout.children:
            if isinstance(widget, TextInput): widget.text = ''

        self.current_step = 'step1'
        self.update_view()
        self.manager.current = 'login'

    def do_signup(self, instance):
        # 2단계 유효성 검사
        if not all([self.email_input.text, self.nickname_input.text, self.password_input.text, self.confirm_password_input.text]):
            self.show_popup("오류", "모든 계정 정보를 채워주세요.")
            return
        if self.password_input.text != self.confirm_password_input.text:
            self.show_popup("오류", "비밀번호가 일치하지 않습니다.")
            return
        if len(self.password_input.text) < 4:
            self.show_popup("오류", "비밀번호는 최소 4자 이상이어야 합니다.")
            return

        # API로 보낼 데이터 구성
        payload = {
            'username': self.nickname_input.text,
            'password': self.password_input.text,
            'email': self.email_input.text,
            'first_name': self.name_input.text, # 'name'을 first_name으로 매핑
            'student_id': self.student_id_input.text,
            'department': self.department_input.text,
            'grade': self.grade_input.text,
        }

        # API 호출
        success, message = handle_signup(payload)
        if success:
            self.show_popup("성공", message, after_dismiss_callback=self.go_to_login)
        else:
            self.show_popup("회원가입 실패", message)


    def show_popup(self, title, message, after_dismiss_callback=None):
        show_info_popup(title, message, callback=after_dismiss_callback, size_hint=(0.8, 0.45))


class LoginScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(
            orientation='vertical', padding=[dp(50), dp(80), dp(50), dp(80)], spacing=dp(18)
        )
        app_name_label = Label(
            text="[b]Campus Link[/b]", font_size='48sp', color=[0.1, 0.4, 0.7, 1],
            font_name=FONT_NAME, markup=True, size_hint_y=None, height=dp(90)
        )
        main_layout.add_widget(app_name_label)
        main_layout.add_widget(Label(size_hint_y=None, height=dp(20)))

        self.username_input = get_rounded_textinput('사용자 이름')
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

    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        app = App.get_running_app()

        token, user_id, role_or_error = handle_login(username, password)

        if token:
            app.auth_token = token
            app.user_id = user_id
            app.current_user = username
            app.current_user_role = role_or_error
            self.manager.current = 'main'
        else:
            self.show_popup("로그인 실패", role_or_error)

    def show_popup(self, title, message):
        show_info_popup(title, message, button_text="다시 시도", button_color=[0.9, 0.2, 0.2, 1])


class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 로컬 사용자 데이터를 제거하고, 서버 인증 정보를 저장할 변수 추가
        self.auth_token = None
        self.user_id = None
        self.current_user = 'guest'
        self.current_user_role = 'guest'

        self.all_clubs = [
            {'name': '축구 동아리 KickOff', 'short_desc': '축구를 사랑하는 사람들의 모임입니다.', 'long_desc': '매주 수요일 오후 4시에 대운동장에서 정기적으로 활동합니다. 축구를 좋아하거나 배우고 싶은 모든 학생을 환영합니다!', 'president': 'user', 'members': ['user', 'member'], 'applications': [{'user':'test_user', 'intro':'열심히 하겠습니다!'}], 'announcements': ["이번 주 활동은 쉽니다."], 'activities': ["지난 주 친선 경기 진행"], 'reviews': ["분위기 좋아요!"]},
            {'name': '코딩 스터디 CodeHive', 'short_desc': '파이썬, 자바 등 함께 공부하는 코딩 모임', 'long_desc': '알고리즘 스터디와 프로젝트 개발을 함께 진행합니다. 초보자도 대환영!', 'president': 'admin', 'members': ['admin'], 'applications': [], 'announcements': [], 'activities': [], 'reviews': []},
        ]
        self.pending_clubs = []
        self.all_items = []
        self.pending_items = []
        self.notification_keywords = []

    def build(self):
        self.title = "Campus Link"
        sm = ScreenManager()
        # 모든 화면 추가
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ClubScreen(name='club'))
        sm.add_widget(ClubDetailScreen(name='club_detail'))
        sm.add_widget(ClubCreateScreen(name='club_create'))
        sm.add_widget(ClubApplicationScreen(name='club_apply'))
        sm.add_widget(ClubManagementScreen(name='club_management'))
        sm.add_widget(MemberApprovalScreen(name='member_approval'))
        sm.add_widget(PostScreen(name='post_screen'))
        sm.add_widget(LostAndFoundScreen(name='lost_found'))
        sm.add_widget(AddItemScreen(name='add_item'))
        sm.add_widget(ItemDetailScreen(name='item_detail'))
        sm.add_widget(TimetableScreen(name='timetable'))
        sm.add_widget(AdminMainScreen(name='admin_main'))
        sm.add_widget(ClubApprovalScreen(name='club_approval'))
        sm.add_widget(ItemApprovalScreen(name='item_approval'))
        return sm

if __name__ == '__main__':
    MyApp().run()

