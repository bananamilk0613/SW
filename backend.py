import kivy

import pyrebase # 파이어베이스 연동을 위해 pyrebase 임포트

import os # 파일 경로를 위해 os 모듈 임포트

# Kivy 기본 위젯 및 레이아웃 모듈 임포트

import time

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

# RelativeLayout 추가 (하단 고정 버튼을 위해)

from kivy.uix.relativelayout import RelativeLayout 

from kivy.graphics import Color, Rectangle, RoundedRectangle, Line # 배경색 및 둥근 모서리를 위한 import 추가

from kivy.metrics import dp # dp 단위를 사용하기 위해 import

from kivy.properties import ObjectProperty, StringProperty # 위젯 참조 및 속성 사용을 위해 import

from kivy.uix.behaviors import ButtonBehavior # 커스텀 버튼 위젯을 위해 import

# Kivy 앱의 기본 이미지 경로를 사용하기 위해 Kivy 경로 라이브러리 임포트

from kivy.resources import resource_find

# 날짜 및 시간 처리를 위해 datetime 임포트
from datetime import datetime

# SpinnerOption 추가 (Spinner 옵션 커스터마이징을 위해)
from kivy.uix.spinner import SpinnerOption

# 비동기 이미지 로딩을 위해 AsyncImage 임포트
from kivy.uix.image import AsyncImage

# 스마트폰 기능 접근을 위한 plyer 임포트 (PC 환경 예외 처리 포함)

try:

    from plyer import filechooser

except ImportError:

    # plyer가 설치되지 않은 PC 환경을 위한 mock(가짜) 객체

    class MockFileChooser:

        def open_file(self, *args, **kwargs):

            Popup(title='알림', content=Label(text='이 기능은 모바일 환경에서만\n사용할 수 있습니다.', font_name='NanumFont'), size_hint=(0.8, 0.3)).open()

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

    FONT_NAME = None # 폰트 로드 실패 시 기본 폰트 사용

# --------------------------------------------------------

# 파이어 베이스 적용 코드

# --------------------------------------------------------

config = {

    "apiKey": "AIzaSyB5LXKty5tRMB3PB4CEgiP6Cb2eXlO5xxo",

    "authDomain": "campus-life-management.firebaseapp.com",

    "databaseURL": "https://campus-life-management-default-rtdb.firebaseio.com",

    "projectId": "campus-life-management",

    "storageBucket": "campus-life-management.firebasestorage.app",

    "messagingSenderId": "1037667609371",

    "appId": "1:1037667609371:web:73e90d9997406289cf81be",

    "measurementId": "G-LBN08ZY8Y3",

}

try:

    firebase = pyrebase.initialize_app(config)

    # 인증 서비스 가져오기

    auth = firebase.auth()

    # Realtime Database 서비스 가져오기

    db = firebase.database()

    print("Firebase 초기화 성공")

except Exception as e:

    print(f"Firebase 초기화 실패: {e}")

    firebase = None

    auth = None

    db = None

# --------------------------------------------------------

# 공통 UI 스타일 함수

# --------------------------------------------------------

# 로컬 이미지 플레이스홀더 경로 설정 (Kivy 기본 아이콘 사용)

DEFAULT_IMAGE = resource_find('data/logo/kivy-icon-256.png')





def get_rounded_textinput(hint_text, password=False, input_type='text'):

    """둥근 모서리가 적용된 텍스트 입력 필드를 반환합니다."""

    return TextInput(

        hint_text=hint_text,

        multiline=False,

        password=password,

        font_size='18sp',

        font_name=FONT_NAME,

        padding=[dp(15), dp(10), dp(15), dp(10)], # 좌, 상, 우, 하

        size_hint_y=None,

        height=dp(55),

        background_normal='',

        background_color=[1, 1, 1, 1],

        foreground_color=[0, 0, 0, 1],

        input_type=input_type # 'number', 'text', 'mail' 등

    )



class RoundedButton(Button):

    """둥근 모서리 배경을 가진 커스텀 버튼 클래스"""

    def __init__(self, **kwargs):

        super(RoundedButton, self).__init__(**kwargs)

        self.bind(pos=self.update_canvas, size=self.update_canvas)

        self.background_normal = ''

        self.background_color = (0, 0, 0, 0) # 투명하게 설정

        self.radius = [dp(10)] # 둥근 모서리 반지름



    def update_canvas(self, *args):

        self.canvas.before.clear()

        with self.canvas.before:

            Color(*self.bg_color)

            # 둥근 모서리를 가진 사각형을 배경으로 그립니다.

            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)



def get_styled_button(text, bg_color, text_color, font_size='22sp'):

    """스타일이 적용된 둥근 버튼 인스턴스를 반환합니다."""

    btn = RoundedButton(

        text=text,

        font_size=font_size,

        font_name=FONT_NAME,

        color=text_color,

        size_hint_y=None,

        height=dp(60)

    )

    btn.bg_color = bg_color # 배경색을 커스텀 속성에 저장

    return btn



class ClubListItem(ButtonBehavior, BoxLayout):

    """클릭 가능한 동아리 목록 아이템 위젯"""

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

    """클릭 가능한 분실물 목록 아이템 위젯"""

    def __init__(self, **kwargs):

        super(LostItemListItem, self).__init__(**kwargs)

        with self.canvas.before:

            Color(0.95, 0.95, 0.8, 1) # 항목 배경색 (연한 노란색)

            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])

        self.bind(pos=self._update_bg, size=self._update_bg)



    def _update_bg(self, instance, value):

        self.bg_rect.pos = instance.pos

        self.bg_rect.size = instance.size



# --------------------------------------------------------

# 화면 기본 클래스 (흰색 배경 공통 적용)

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

#  메인 화면 (로그인 성공 후 진입)

# --------------------------------------------------------

class MainScreen(WhiteBgScreen):

    # ... (__init__ 메소드의 상단 부분은 기존과 동일) ...

    

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



        # 기능별 버튼 - 색상 변경

        nav_layout.add_widget(create_nav_button("동아리 게시판", 'club', [0.0, 0.2, 0.6, 1])) # 남색

        nav_layout.add_widget(create_nav_button("분실물 게시판", 'lost_found', [0.2, 0.6, 1, 1])) # 파란색



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

        # (on_enter 메소드는 기존과 동일)

        app = App.get_running_app()

        self.welcome_label.text = f"환영합니다, {app.current_user_nickname}님! 어떤 정보가 필요하신가요?"



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



        # 팝업 전체를 담을 컨테이너 

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

            # "닉네임 (아이디)" 형식으로 표시

            text=f"[b]Campus Link 계정[/b]\n\n{app.current_user_nickname}님 ({app.current_user})\n\n앱 설정 및 정보",

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

            

        # "내 등록 관리" 버튼 추가 (분실물/습득물)

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




        content_layout.add_widget(Label()) # 스페이서



        # 2-2. 로그아웃 버튼 (둥근 스타일 적용)

        logout_button = get_styled_button("로그아웃", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])

        logout_button.height = dp(50)

        content_layout.add_widget(logout_button)



        full_popup_content.add_widget(content_layout)



        # 팝업 content 설정

        popup.content = full_popup_content



        def perform_logout(btn_instance):

            # ... (로그아웃 로직은 기존과 동일) ...

            app = App.get_running_app()

            app.current_user = 'guest'

            app.current_user_nickname = 'Guest'

            app.current_user_role = 'guest'

            

            # 로그인 화면으로 이동

            self.manager.current = 'login'

            login_screen = self.manager.get_screen('login')

            if login_screen:

                login_screen.username_input.text = ''

                login_screen.password_input.text = ''

            popup.dismiss()



        logout_button.bind(on_press=perform_logout)



        popup.open()





# --------------------------------------------------------

# 관리자 기능 관련 화면들

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



        item_approval_button = get_styled_button("분실물 등록 관리", [1, 0.5, 0.3, 1], [1, 1, 1, 1])

        item_approval_button.bind(on_press=lambda *args: self.go_to_screen('item_approval'))

        main_layout.add_widget(item_approval_button)



        # 관리자 교차 검증 메뉴 버튼 

        claim_approval_button = get_styled_button("물품 신청(소유권) 관리", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])

        claim_approval_button.bind(on_press=lambda *args: self.go_to_screen('admin_claim_approval'))

        main_layout.add_widget(claim_approval_button)

    



        main_layout.add_widget(Label()) # Spacer



        back_button = get_styled_button("메인 화면으로", [0.5, 0.5, 0.5, 1], [1, 1, 1, 1])

        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))

        main_layout.add_widget(back_button)



        self.add_widget(main_layout)





# --------------------------------------------------------

# 관리자 물품 신청(소유권) 관리

# --------------------------------------------------------

class AdminClaimApprovalScreen(WhiteBgScreen):
    """관리자가 사용자의 물품 신청(소유권)을 승인/거절하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]물품 신청 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        # 스크롤 뷰
        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))

        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        """(수정) Firebase에서 claims와 all_items를 직접 읽어와서 표시"""
        self.grid.clear_widgets()
        app = App.get_running_app()
        
        if not app.user_token:
             self.grid.add_widget(Label(text="로그인 정보가 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
             return

        # 헬퍼 함수
        def create_wrapping_label(text_content, **kwargs):
            label = Label(
                text=text_content, size_hint_y=None, font_name=FONT_NAME,
                markup=True, halign='left', **kwargs
            )
            label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            return label

        try:
            # 1. 모든 신청서(claims) 가져오기
            claims_node = db.child("claims").get(app.user_token)
            claims_dict = claims_node.val()
            
            if not claims_dict:
                self.grid.add_widget(Label(text="접수된 신청이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
                return

            # 2. 물건 정보(all_items)도 가져와야 함 (물품명을 보여주기 위해)
            items_node = db.child("all_items").get(app.user_token)
            items_dict = items_node.val() or {} # 없으면 빈 딕셔너리

            # 3. 'status'가 없는(pending) 신청만 필터링
            pending_claims = [c for c in claims_dict.values() if 'status' not in c]

            if not pending_claims:
                self.grid.add_widget(Label(text="검토 대기 중인 신청이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
                return

            for claim in pending_claims:
                item_id = claim.get('item_id')
                
                # items_dict에서 해당 아이템 정보 찾기
                item = items_dict.get(item_id)
                
                if not item:
                    continue # 물건 정보가 없으면 스킵

                # (UI 그리기)
                item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
                item_box.bind(minimum_height=item_box.setter('height'))

                with item_box.canvas.before:
                    Color(0.95, 0.95, 0.8, 1) 
                    self.bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
                
                item_box.bind(
                    pos=lambda instance, value, r=self.bg_rect: setattr(r, 'pos', value), # 람다 캡처 주의
                    size=lambda instance, value, r=self.bg_rect: setattr(r, 'size', value)
                )
                # (주의: 위 람다에서 self.bg_rect를 직접 쓰면 마지막 rect만 참조될 수 있으므로
                #  객체 생성 시점에 캡처하거나, 매번 새로 생성되는 위젯이므로 큰 문제 없을 수 있음.
                #  더 안전하게 하려면 헬퍼 클래스로 빼는 게 좋지만 일단 진행)

                # 기본 정보
                item_box.add_widget(create_wrapping_label(
                    text_content=f"[b]물품명:[/b] {item['name']}", color=[0,0,0,1]
                ))
                item_box.add_widget(create_wrapping_label(
                    text_content=f"[b]신청자:[/b] {claim.get('claimer_nickname', '알 수 없음')}", color=[0,0,0,1]
                ))
                
                item_box.add_widget(Label(size_hint_y=None, height=dp(10))) 

                # 등록자 정보
                item_box.add_widget(create_wrapping_label(
                    text_content=f"[b]등록자(Finder)가 올린 정보:[/b]", color=[0.1, 0.4, 0.7, 1]
                ))
                item_box.add_widget(create_wrapping_label(
                    text_content=f"  - (장소): {item['loc']}", color=[0.1, 0.4, 0.7, 1]
                ))
                item_box.add_widget(create_wrapping_label(
                    text_content=f"  - (상세): {item.get('desc', '없음')}", color=[0.1, 0.4, 0.7, 1]
                ))

                item_box.add_widget(Label(size_hint_y=None, height=dp(10)))

                # 신청자 검증 정보
                item_box.add_widget(create_wrapping_label(
                    text_content=f"[b]신청자(Claimer)가 입력한 [상세 특징]:[/b]", color=[0.8, 0.2, 0.2, 1]
                ))
                item_box.add_widget(create_wrapping_label(
                    text_content=f"{claim.get('verification_details', 'N/A')}", color=[0.8, 0.2, 0.2, 1]
                ))

                item_box.add_widget(Label(size_hint_y=None, height=dp(15))) 

                # 버튼
                button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
                
                approve_btn = Button(text="전달 완료 (승인)", font_name=FONT_NAME, background_color=[0.2, 0.8, 0.2, 1])
                approve_btn.item_id = item_id 
                approve_btn.claim = claim 
                approve_btn.bind(on_press=self.approve_claim) 
                
                reject_btn = Button(text="신청 거절", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1])
                reject_btn.item_id = item_id 
                reject_btn.claim = claim 
                reject_btn.bind(on_press=self.reject_claim)
                
                button_layout.add_widget(approve_btn)
                button_layout.add_widget(reject_btn)
                
                item_box.add_widget(button_layout)
                self.grid.add_widget(item_box)

        except Exception as e:
            self.grid.add_widget(Label(text=f"데이터 로딩 실패: {e}", font_name=FONT_NAME, color=[1,0,0,1], size_hint_y=None, height=dp(100)))


    def approve_claim(self, instance):
        """(관리자) 신청을 승인 -> '학생복지처' 인계를 안내합니다."""
        app = App.get_running_app()
        if not app.user_token: return

        item_id = instance.item_id
        claim_id = instance.claim.get('claim_id') # claim 객체 안에 ID가 있어야 함
        claim_data = instance.claim
        
        try:
            pickup_location = "학생복지처"
            
            # 1. 아이템 상태 변경
            db.child("all_items").child(item_id).update({'status': 'found_returned'}, app.user_token)
            
            # 2. 신청서 상태 변경 (DB 경로: claims/{claim_id})
            # claim 객체에 id가 없다면... key를 찾아야 하는데, 
            # 위 refresh_list에서 dict.values()로만 가져와서 key를 잃어버렸을 수 있음.
            if claim_id:
                db.child("claims").child(claim_id).update({
                    'status': 'approved',
                    'finder_contact': pickup_location
                }, app.user_token)
            else:
                 # (만약 ID가 없다면 비상용으로 전체 덮어쓰기 시도 - 권장 안함)
                 print("Error: Claim ID not found")

            popup_message = (
                f"승인이 완료되었습니다.\n\n"
                f"신청자('{claim_data.get('claimer_nickname')}')에게\n"
                f"'{pickup_location}' 수령이 안내됩니다."
            )
                            
            popup = Popup(title='[b]승인 완료[/b]',
                          title_font=FONT_NAME,
                          content=Label(text=popup_message, font_name=FONT_NAME, markup=True, padding=dp(10)),
                          size_hint=(0.9, 0.4))
            
            popup.bind(on_dismiss=self.refresh_list)
            popup.open()
            
        except Exception as e:
             Popup(title='오류', content=Label(text=f"승인 처리 실패: {e}", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()


    def reject_claim(self, instance):
        """(관리자) 신청을 거절"""
        app = App.get_running_app()
        if not app.user_token: return

        item_id = instance.item_id
        claim_id = instance.claim.get('claim_id')
        
        try:
            # 1. 아이템 상태 복구
            db.child("all_items").child(item_id).update({'status': 'found_available'}, app.user_token)
            
            # 2. 신청서 상태 거절로 변경
            if claim_id:
                db.child("claims").child(claim_id).update({'status': 'rejected'}, app.user_token)
            
            self.refresh_list()
            
        except Exception as e:
             Popup(title='오류', content=Label(text=f"거절 처리 실패: {e}", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

   



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
        
        if not app.user_token:
            self.update_approval_list([]) # 토큰 없으면 빈 리스트로
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            #  로컬 app.pending_clubs 대신 Firebase DB에서 직접 가져옵니다.
            pending_node = db.child("pending_clubs").get(app.user_token)
            
            pending_clubs_dict = pending_node.val() # 딕셔너리 형태로 받음
            
            if pending_clubs_dict:
                # 딕셔너리의 값들(value)만 리스트로 변환
                pending_list = list(pending_clubs_dict.values())
                self.update_approval_list(pending_list)
            else:
                # DB에 아무것도 없으면 빈 리스트로
                self.update_approval_list([])

        except Exception as e:
            self.update_approval_list([]) # 오류 시 빈 리스트
            Popup(title='DB 오류', content=Label(text=f'데이터 읽기 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()




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

        if not app.user_token:
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        club_id = approved_club.get('club_id')
        if not club_id:
            Popup(title='오류', content=Label(text='클럽 ID가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            
            # 1. 'all_clubs' 경로에 동아리 추가
            db.child("all_clubs").child(club_id).set(approved_club, app.user_token)
            
            # 2. 'pending_clubs' 경로에서 해당 동아리 삭제
            db.child("pending_clubs").child(club_id).remove(app.user_token)

            # 3. 목록 새로고침 (DB를 다시 읽어옴)
            self.refresh_approval_list()

        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'승인 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()



    def reject_club(self, instance):

        rejected_club = instance.club_data

        app = App.get_running_app()

        if rejected_club in app.pending_clubs:

            app.pending_clubs.remove(rejected_club)

        self.refresh_approval_list()





class ItemApprovalScreen(WhiteBgScreen):
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
        
        if not app.user_token:
            self.update_approval_list([])
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            pending_node = db.child("pending_items").get(app.user_token)
            pending_items_dict = pending_node.val()
            
            if pending_items_dict:
                pending_list = list(pending_items_dict.values())
                self.update_approval_list(pending_list)
            else:
                self.update_approval_list([])

        except Exception as e:
            self.update_approval_list([])
            Popup(title='DB 오류', content=Label(text=f'데이터 읽기 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def update_approval_list(self, pending_items):
        self.approval_grid.clear_widgets()
        if not pending_items:
            self.approval_grid.add_widget(Label(text="승인 대기 중인 게시물이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
        else:
            for item_request in pending_items:
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100), padding=dp(10), spacing=dp(10))

                # AsyncImage 적용
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
        
        if not app.user_token:
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        item_id = approved_item.get('item_id')
        if not item_id:
            Popup(title='오류', content=Label(text='아이템 ID가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            db.child("all_items").child(item_id).set(approved_item, app.user_token)
            db.child("pending_items").child(item_id).remove(app.user_token)
            self.check_keyword_notification(approved_item)
            self.refresh_approval_list()

        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'승인 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def reject_item(self, instance):
        rejected_item = instance.item_data
        app = App.get_running_app()
        
        if not app.user_token:
             return

        try:
            item_id = rejected_item.get('item_id')
            db.child("pending_items").child(item_id).remove(app.user_token)
            self.refresh_approval_list()
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'거절 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def check_keyword_notification(self, new_item):
        app = App.get_running_app()
        item_text = f"{new_item['name']} {new_item['desc']} {new_item['loc']} {new_item.get('time', '')}".lower()
        for keyword in app.notification_keywords:
            if keyword.lower() in item_text:
                Popup(title='키워드 알림',
                        content=Label(text=f"등록하신 키워드 '{keyword}'가 포함된\n'{new_item['name']}' 게시물이 등록되었습니다.", font_name=FONT_NAME),
                        size_hint=(0.8, 0.4)).open()
                break

# --------------------------------------------------------

#  분실물 신청 관리 (교차 검증)

# --------------------------------------------------------

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
            all_items_dict = db.child("all_items").get(app.user_token).val()
            my_items = []
            if all_items_dict:
                for item in all_items_dict.values():
                    # UID 비교를 우선하되, 없으면 ID로도 비교 (호환성 강화)
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

        def create_wrapping_label(text_content, **kwargs):
            label = Label(
                text=text_content, size_hint_y=None, font_name=FONT_NAME,
                markup=True, halign='left', **kwargs
            )
            label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            return label

        for item in my_items:
            item_id = item.get('item_id')
            item_status = item.get('status', 'unknown') #status가 없어도 죽지 않게 처리
            
            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            item_box.bind(minimum_height=item_box.setter('height')) 

            with item_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                self.bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
            
            item_box.bind(
                pos=lambda instance, value: setattr(self.bg_rect, 'pos', value),
                size=lambda instance, value: setattr(self.bg_rect, 'size', value)
            )

            item_box.add_widget(create_wrapping_label(
                text_content=f"[b]{item.get('name', '이름 없음')}[/b]", 
                color=[0,0,0,1]
            ))
            
            status_text = ""
            
            if item_status == 'found_pending':
                try:
                    claims_node = db.child("claims").get(app.user_token)
                    claims_dict = claims_node.val()
                    claim = None
                    if claims_dict:
                        for c in claims_dict.values():
                            if c.get('item_id') == item_id:
                                claim = c
                                break
                    
                    if claim:
                        status_text = f"[color=A01010]관리자 검토 중[/color]\n신청자: {claim.get('claimer_nickname', '알 수 없음')}"
                        item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0,0,0,1]))
                    else:
                        status_text = "[color=1010A0]신청 가능[/color]"
                        item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0,0,0,1]))
                except:
                    pass

            elif item_status == 'found_available':
                status_text = "[color=1010A0]신청 가능[/color] (대기중인 신청 없음)"
                item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0.3,0.3,0.3,1]))
            
            elif item_status == 'found_returned':
                # 습득자 안내 문구
                status_text = "[color=008000][b]교차 검증 승인됨[/b][/color]\n(학생복지처에 물품을 인계해주세요)"
                item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0.2,0.2,0.2,1]))

            elif item_status == 'lost':
                status_text = "내가 등록한 분실물"
                item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0.5,0.5,0.5,1]))
            
            else:
                # 알 수 없는 상태일 때도 표시
                status_text = f"상태: {item_status}"
                item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0.5,0.5,0.5,1]))

            self.grid.add_widget(item_box)
   

# --------------------------------------------------------

# 동아리 기능 관련 화면들

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
        
        if not app.user_token:
            self.update_club_list([]) 
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            clubs_node = db.child("all_clubs").get(app.user_token)
            clubs_dict = clubs_node.val() 
            
            if clubs_dict:
                clubs_list = list(clubs_dict.values())
                
                # 인기도 점수 기준 내림차순 정렬
                sorted_list = sorted(
                    clubs_list, 
                    key=lambda club: club.get("popularity_score", 0), 
                    reverse=True
                )
                self.update_club_list(sorted_list)
            else:
                self.update_club_list([])

        except Exception as e:
            self.update_club_list([]) 
            Popup(title='DB 오류', content=Label(text=f'데이터 읽기 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
        
        self.search_input.text = "" 

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
        detail_screen = self.manager.get_screen('club_detail')
        detail_screen.club_data = instance.club_data 
        self.go_to_screen('club_detail')

    def search_clubs(self, instance):
        app = App.get_running_app()
        search_term = self.search_input.text.lower()
        
        try:
            clubs_node = db.child("all_clubs").get(app.user_token)
            clubs_dict = clubs_node.val()
            
            if clubs_dict:
                all_clubs = list(clubs_dict.values())
                if not search_term:
                    results = all_clubs
                else:
                    results = [club for club in all_clubs if search_term in club['name'].lower()]
                
                # 검색 결과도 인기도 순 정렬
                sorted_results = sorted(
                    results, 
                    key=lambda club: club.get("popularity_score", 0), 
                    reverse=True
                )
                self.update_club_list(sorted_results)
            else:
                self.update_club_list([])
                
        except Exception:
            pass




class ClubDetailScreen(WhiteBgScreen):
    """동아리 상세 정보를 보여주는 화면"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 수직 BoxLayout 사용
        self.main_layout = BoxLayout(orientation='vertical')
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        """화면에 들어올 때마다 위젯을 다시 그림"""
        
        # 1. 기존 위젯 모두 제거
        self.main_layout.clear_widgets() 

        if self.club_data:
            app = App.get_running_app()
            
            # (알고리즘) 클릭 로그 저장 & 점수 갱신
            if app.user_token:
                 club_id = self.club_data.get('club_id')
                 self.update_popularity_score(club_id)

            is_president = app.current_user_uid == self.club_data.get('president')
            is_member = app.current_user_uid in self.club_data.get('members', {})

            
            # ---------------------------------------------------------
            # [A] 헤더 생성 (아직 main_layout에 붙이지 않음!)
            # ---------------------------------------------------------
            header = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height=dp(60), 
                spacing=dp(10)
            )
            
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


            # ---------------------------------------------------------
            # [B] 하단 버튼바 생성 (아직 붙이지 않음!)
            # ---------------------------------------------------------
            bottom_bar = BoxLayout(
                size_hint_y=None, 
                height=dp(80), 
                padding=dp(10), 
                spacing=dp(10)
            )
            with bottom_bar.canvas.before:
                Color(0.95, 0.95, 0.95, 1) 
                self.bottom_rect = Rectangle(size=bottom_bar.size, pos=bottom_bar.pos)
            bottom_bar.bind(size=self._update_rect_cb(self.bottom_rect), 
                            pos=self._update_rect_cb(self.bottom_rect))

            if is_president or is_member:
                pass # 회원은 하단바 비움
            else:
                apply_button = get_styled_button("신청하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
                apply_button.bind(on_press=self.go_to_application) 
                bottom_bar.add_widget(apply_button)

            # ---------------------------------------------------------
            # [C] 중간 스크롤 영역 생성
            # ---------------------------------------------------------
            scroll_view = ScrollView(
                size_hint=(1, 1) 
            )
            
            content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
            content_layout.bind(minimum_height=content_layout.setter('height'))
            scroll_view.add_widget(content_layout)

            
            # [동아리 소개 박스]
            intro_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(5))
            intro_box.bind(minimum_height=intro_box.setter('height')) 
            with intro_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1) 
                self.intro_bg_rect = RoundedRectangle(pos=intro_box.pos, size=intro_box.size, radius=[dp(5)])
            intro_box.bind(pos=lambda i, v: setattr(self.intro_bg_rect, 'pos', v),
                             size=lambda i, v: setattr(self.intro_bg_rect, 'size', v))
                             
            title_intro = Label(text="[b]동아리 소개[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, size_hint_y=None, height=dp(40), font_size='20sp', halign='left')
            title_intro.bind(size=title_intro.setter('text_size'))
            intro_box.add_widget(title_intro)
            
            long_desc_label = Label(text=self.club_data['long_desc'], font_name=FONT_NAME, color=[0.2,0.2,0.2,1], size_hint_y=None, halign='left')
            long_desc_label.bind(width=lambda *x: long_desc_label.setter('text_size')(long_desc_label, (long_desc_label.width, None)),
                                 texture_size=lambda *x: long_desc_label.setter('height')(long_desc_label, long_desc_label.texture_size[1]))
            intro_box.add_widget(long_desc_label)
            
            content_layout.add_widget(intro_box)


            # [섹션 루프]
            for section_title, data_key in [
                ("[b]공지사항[/b]", "announcements"), 
                ("[b]활동 내역[/b]", "activities"), 
                ("[b]자유게시판[/b]", "free_board"), 
                ("[b]후기[/b]", "reviews")
            ]:
                section_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(5))
                section_box.bind(minimum_height=section_box.setter('height'))
                with section_box.canvas.before:
                    Color(0.95, 0.95, 0.95, 1) 
                    bg_rect = RoundedRectangle(pos=section_box.pos, size=section_box.size, radius=[dp(5)])
                section_box.bind(pos=lambda i, v, r=bg_rect: setattr(r, 'pos', v),
                                 size=lambda i, v, r=bg_rect: setattr(r, 'size', v))

                # 소제목
                title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                title_label = Label(text=section_title, font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='20sp', halign='left')
                title_label.bind(size=title_label.setter('text_size'))
                title_layout.add_widget(title_label)
                
                # '자유게시판' 소제목 옆 글쓰기 버튼
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
                    # 데이터 리스트 변환 및 정렬
                    items_list = []
                    for item in section_data.values():
                        if isinstance(item, dict) and 'content' in item:
                            items_list.append(item)
                        else:
                            items_list.append({'content': str(item), 'timestamp': 0})
                    
                    # 최신순 정렬
                    items_list.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                    
                    # 자유게시판은 최대 4개까지만 표시
                    if data_key == 'free_board':
                        display_list = items_list[:4]
                    else:
                        display_list = items_list

                    for item in display_list:
                        text_to_show = item['content']
                        item_label = Label(text=f"- {text_to_show}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], size_hint_y=None, halign='left')
                        item_label.bind(width=lambda *x: item_label.setter('text_size')(item_label, (item_label.width, None)),
                                        texture_size=lambda *x: item_label.setter('height')(item_label, item_label.texture_size[1]))
                        section_box.add_widget(item_label)
                    
                    # '더보기' 버튼 (자유게시판 && 4개 초과 시)
                    if data_key == 'free_board' and len(items_list) > 4:
                        more_button = Button(
                            text="더보기...", 
                            font_name=FONT_NAME, 
                            color=[0.5, 0.5, 0.5, 1], 
                            background_color=[0,0,0,0], 
                            background_normal='',
                            size_hint_y=None, 
                            height=dp(30)
                        )
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
    
    
    def update_popularity_score(self, club_id):
        """활동(0.5), 자유(0.3), 클릭(0.01) 가중치 및 4학기 시간 반감 적용 알고리즘"""
        app = App.get_running_app()
        if not app.user_token: return

        try:
            club_data = db.child(f"all_clubs/{club_id}").get(app.user_token).val()
            if not club_data: return

            current_time = int(time.time())
            
            def get_semester_index(timestamp):
                dt = datetime.fromtimestamp(timestamp)
                year = dt.year
                month = dt.month
                if 3 <= month <= 8:
                    return year * 2 + 1 
                elif month >= 9:
                    return year * 2 + 2
                else:
                    return (year - 1) * 2 + 2

            current_semester_idx = get_semester_index(time.time())
            total_score = 0.0

            def calculate_decayed_score(items, base_weight):
                sub_total = 0.0
                if not items: return 0.0
                
                if isinstance(items, dict):
                    values = items.values()
                else:
                    return 0.0

                for item in values:
                    if isinstance(item, dict) and 'timestamp' in item:
                        ts = item['timestamp']
                    elif isinstance(item, int) or isinstance(item, float):
                        ts = item
                    else:
                        continue 
                    
                    content_semester_idx = get_semester_index(ts)
                    elapsed_semesters = current_semester_idx - content_semester_idx

                    if elapsed_semesters < 0: elapsed_semesters = 0

                    if elapsed_semesters >= 4:
                        continue 
                    
                    decay_factor = 0.5 ** elapsed_semesters
                    sub_total += base_weight * decay_factor
                
                return sub_total

            # 클릭 점수는 제외
            score_activity = calculate_decayed_score(club_data.get('activities'), 0.5)
            score_free = calculate_decayed_score(club_data.get('free_board'), 0.3)
            
            total_score = score_activity + score_free

            db.child(f"all_clubs/{club_id}/popularity_score").set(round(total_score, 2), app.user_token)

        except Exception as e:
            print(f"점수 계산 오류: {e}")

    def _update_rect_cb(self, rect):
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        return update_rect

    def show_club_menu_popup(self, instance):
        app = App.get_running_app()
        popup = Popup(
            title="", separator_height=0, size_hint=(0.6, 1.0),
            pos_hint={'right': 1, 'y': 0}, 
            auto_dismiss=True, background=''
        )

        full_popup_content = BoxLayout(orientation='vertical')
        with full_popup_content.canvas.before:
            Color(1, 1, 1, 1) 
            content_bg = Rectangle(size=full_popup_content.size, pos=full_popup_content.pos)
        full_popup_content.bind(size=lambda i, v: setattr(content_bg, 'size', v),
                                pos=lambda i, v: setattr(content_bg, 'pos', v))

        BLUE_STRIPE_COLOR = [0.1, 0.4, 0.7, 1]
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[dp(10), 0, dp(10), 0])
        with header.canvas.before:
            Color(*BLUE_STRIPE_COLOR)
            header_bg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda i, v: setattr(header_bg, 'size', v),
                    pos=lambda i, v: setattr(header_bg, 'pos', v))

        header.add_widget(Label(text="[b]동아리 메뉴[/b]", font_name=FONT_NAME, color=[1, 1, 1, 1], markup=True, font_size='22sp'))
        close_button = Button(
            text="X", font_size='22sp', size_hint=(None, 1), width=dp(40),
            color=[1, 1, 1, 1], background_normal='', background_color=[0, 0, 0, 0]
        )
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
            
        else: # 비회원
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
        
        popup = Popup(
            title="[b]동아리 탈퇴 확인[/b]", title_font=FONT_NAME, title_color=[0,0,0,1],
            content=popup_content, size_hint=(0.9, 0.4),
            separator_height=0, background=''
        )
        
        no_button.bind(on_press=popup.dismiss)
        yes_button.bind(on_press=lambda *args: self.perform_withdraw(popup))
        popup.open()

    def perform_withdraw(self, popup_to_dismiss):
        app = App.get_running_app()
        
        if not self.club_data or not app.user_token:
            Popup(title='오류', content=Label(text='로그인 정보 또는 동아리 정보가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        club_id = self.club_data.get('club_id')
        member_uid = app.current_user_uid 
        
        if not club_id or not member_uid:
            Popup(title='오류', content=Label(text='ID를 찾을 수 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        try:
            path = f"all_clubs/{club_id}/members/{member_uid}"
            db.child(path).remove(app.user_token)

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
        """전체보기 화면으로 이동"""
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


class ClubFreeBoardScreen(WhiteBgScreen):
    """자유게시판의 모든 글을 보여주는 전체보기 화면"""
    club_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        if self.club_data:
            # --- 헤더 ---
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
            
            back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
            back_button.height = dp(50)
            back_button.size_hint_x = None
            back_button.width = dp(60)
            back_button.bind(on_press=lambda *args: self.go_to_screen('club_detail'))
            header.add_widget(back_button)
            
            header.add_widget(Label(text=f"[b]{self.club_data['name']} 자유게시판[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='24sp'))
            self.main_layout.add_widget(header)

            # --- 게시글 목록 스크롤 ---
            scroll_view = ScrollView()
            content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
            content_layout.bind(minimum_height=content_layout.setter('height'))
            scroll_view.add_widget(content_layout)
            self.main_layout.add_widget(scroll_view)

            # 데이터 가져오기 및 정렬 (최신순)
            free_board_data = self.club_data.get('free_board', {})
            posts_list = []
            
            if free_board_data:
                for item in free_board_data.values():
                    if isinstance(item, dict) and 'content' in item:
                        posts_list.append(item)
                    else:
                        # 구형 데이터 호환용
                        posts_list.append({'content': str(item), 'timestamp': 0})
                
                # 타임스탬프 기준 내림차순 정렬 (최신글이 위로)
                posts_list.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

            if posts_list:
                for post in posts_list:
                    # 각 게시글을 박스 형태로 예쁘게 표시
                    post_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
                    post_box.bind(minimum_height=post_box.setter('height'))
                    
                    with post_box.canvas.before:
                        Color(0.95, 0.95, 0.95, 1)
                        RoundedRectangle(pos=post_box.pos, size=post_box.size, radius=[dp(5)])
                    
                    # (배경 업데이트 바인딩)
                    def update_bg(instance, value, box=post_box):
                         box.canvas.before.clear()
                         with box.canvas.before:
                             Color(0.95, 0.95, 0.95, 1)
                             RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(5)])
                    post_box.bind(pos=update_bg, size=update_bg)

                    # 내용 표시
                    content_label = Label(text=post['content'], font_name=FONT_NAME, color=[0.2,0.2,0.2,1], size_hint_y=None, halign='left')
                    content_label.bind(width=lambda *x: content_label.setter('text_size')(content_label, (content_label.width, None)),
                                       texture_size=lambda *x: content_label.setter('height')(content_label, content_label.texture_size[1]))
                    post_box.add_widget(content_label)
                    
                    # 날짜 표시 (선택 사항)
                    if post.get('timestamp'):
                        ts_date = datetime.fromtimestamp(post['timestamp']).strftime('%Y-%m-%d %H:%M')
                        date_label = Label(text=ts_date, font_name=FONT_NAME, color=[0.6,0.6,0.6,1], font_size='12sp', size_hint_y=None, height=dp(15), halign='right')
                        date_label.bind(size=date_label.setter('text_size'))
                        post_box.add_widget(date_label)

                    content_layout.add_widget(post_box)
            else:
                content_layout.add_widget(Label(text="작성된 글이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(50)))

    def go_to_screen(self, screen_name):
        if screen_name == 'club_detail':
            detail_screen = self.manager.get_screen(screen_name)
            detail_screen.club_data = self.club_data
        self.manager.current = screen_name


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
            Popup(title='오류', content=Label(text='모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return

        app = App.get_running_app()
        
        # (로그인 토큰 및 UID 확인)
        if not app.user_token or not app.current_user_uid:
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        # (고유한 동아리 ID 생성)
        club_id = f"club_{int(time.time())}_{app.current_user}"

        new_club_request = {
            'club_id': club_id, 
            'name': name,
            'short_desc': s_desc,
            'long_desc': l_desc,
            
            # (중요) '동아리장'으로 '아이디' 대신 'Firebase UID'를 저장합니다.
            'president': app.current_user_uid, 
            
            'members': { app.current_user_uid: True },
            
            'applications': {}, # (리스트 대신 딕셔너리로)
            'announcements': {},
            'activities': {},
            'reviews': {}
        }

        try:
            
            # Firebase DB 'pending_clubs' 경로에 club_id를 키로 하여 저장
            db.child("pending_clubs").child(club_id).set(new_club_request, app.user_token)

            # 필드 초기화
            self.club_name.text = ""
            self.short_desc.text = ""
            self.long_desc.text = ""

            popup = Popup(title='알림', content=Label(text='동아리 개설 신청이 완료되었습니다.\n관리자 승인 후 등록됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('club'))
            popup.open()

        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'데이터 저장 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()




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
            Popup(title='오류', content=Label(text='자기소개를 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return

        app = App.get_running_app()
        
        if not app.user_token or not self.club_data:
            Popup(title='오류', content=Label(text='로그인 정보 또는 동아리 정보가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        club_id = self.club_data.get('club_id')
        if not club_id:
            Popup(title='오류', content=Label(text='동아리 ID를 찾을 수 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        application_data = {
            'user_uid': app.current_user_uid, # 신청자 'UID'
            'user_nickname': app.current_user_nickname, # 신청자 '닉네임' (표시용)
            'intro': self.intro.text
        }

        try:
            # 신청자의 'UID'를 키(key)로 하여 신청 정보를 저장 (중복 신청 방지)
            path = f"all_clubs/{club_id}/applications/{app.current_user_uid}"
            db.child(path).set(application_data, app.user_token)

            popup = Popup(title='신청 완료', content=Label(text='가입 신청이 완료되었습니다.\n회장 승인 후 가입됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('club_detail'))
            popup.open()
            
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'신청 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()





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
            
            # (6.9.2) '멤버 관리(추방)' 버튼 추가
            member_manage_button = get_styled_button("멤버 관리 (추방)", [0.8, 0.5, 0.2, 1], [1, 1, 1, 1])
            member_manage_button.bind(on_press=self.go_to_member_management) 
            self.main_layout.add_widget(member_manage_button)

            post_announcement_button = get_styled_button("공지사항 작성", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
            post_announcement_button.bind(on_press=lambda *args: self.go_to_post('announcement'))
            self.main_layout.add_widget(post_announcement_button)

            post_activity_button = get_styled_button("활동내역 작성", [0.5, 0.5, 0.8, 1], [1, 1, 1, 1])
            post_activity_button.bind(on_press=lambda *args: self.go_to_post('activity'))
            self.main_layout.add_widget(post_activity_button)
            
            # (6.5) '자유게시판' 버튼은 여기서 삭제됨

            self.main_layout.add_widget(Label()) # Spacer

    def go_to_member_approval(self, instance):
        approval_screen = self.manager.get_screen('member_approval')
        approval_screen.club_data = self.club_data
        self.go_to_screen('member_approval')
        
    def go_to_member_management(self, instance):
        """ 멤버 관리 화면으로 이동"""
        management_screen = self.manager.get_screen('member_management')
        management_screen.club_data = self.club_data
        self.go_to_screen('member_management')

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
        
        app = App.get_running_app()
        if not self.club_data or not app.user_token:
            self.grid.add_widget(Label(text="동아리 정보 또는 로그인 정보가 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
            return
            
        club_id = self.club_data.get('club_id')
        self.header_title.text = f"[b]{self.club_data.get('name', '동아리')} 신청 관리[/b]"

        try:
            # Firebase DB의 해당 동아리 applications 경로에서 신청 목록을 읽어옴
            path = f"all_clubs/{club_id}/applications"
            applications_node = db.child(path).get(app.user_token)
            
            applications_dict = applications_node.val()

            if not applications_dict:
                self.grid.add_widget(Label(text="가입 신청이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
            else:
                # 딕셔너리의 값들(value)을 리스트로 변환하여 표시
                for app_data in applications_dict.values():
                    item_layout = BoxLayout(size_hint_y=None, height=dp(120), padding=dp(10), spacing=dp(10))
                    info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
                    
                    # (UID 대신 닉네임과 아이디(DB에 있다면)를 표시)
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

        if not self.club_data or not app.user_token:
            Popup(title='오류', content=Label(text='로그인 정보 또는 동아리 정보가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        club_id = self.club_data.get('club_id')
        applicant_uid = app_data.get('user_uid') # 신청자의 UID
        
        if not club_id or not applicant_uid:
            Popup(title='오류', content=Label(text='신청자 ID 또는 동아리 ID를 찾을 수 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            # 1. Firebase DB의 members 경로에 신청자 UID 추가
            path_members = f"all_clubs/{club_id}/members/{applicant_uid}"
            db.child(path_members).set(True, app.user_token)

            # 2. Firebase DB의 applications 경로에서 신청자 정보 삭제
            path_applications = f"all_clubs/{club_id}/applications/{applicant_uid}"
            db.child(path_applications).remove(app.user_token)

            self.refresh_list() # 목록 새로고침
        
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'멤버 승인 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()



    def reject_member(self, instance):
        app_data = instance.app_data
        app = App.get_running_app()
        
        if not self.club_data or not app.user_token:
            Popup(title='오류', content=Label(text='로그인 정보 또는 동아리 정보가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        club_id = self.club_data.get('club_id')
        applicant_uid = app_data.get('user_uid') # 신청자의 UID
        
        if not club_id or not applicant_uid:
            Popup(title='오류', content=Label(text='신청자 ID 또는 동아리 ID를 찾을 수 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        try:
            #  Firebase DB의 applications 경로에서 신청자 정보 삭제
            path_applications = f"all_clubs/{club_id}/applications/{applicant_uid}"
            db.child(path_applications).remove(app.user_token)
            
            self.refresh_list() # 목록 새로고침

        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'멤버 거절 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()


# --------------------------------------------------------
#  동아리장 - 멤버 관리 (추방) 화면
# --------------------------------------------------------
class MemberManagementScreen(WhiteBgScreen):
    """동아리 회장이 멤버를 관리(추방)하는 화면"""
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
        self.header_title = Label(text="[b]멤버 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp')
        header.add_widget(self.header_title)
        main_layout.add_widget(header)

        # 멤버 목록
        scroll_view = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)
        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        """ DB에서 멤버 목록을 불러와 닉네임과 함께 표시"""
        self.grid.clear_widgets()
        app = App.get_running_app()
        
        if not self.club_data or not app.user_token:
            self.grid.add_widget(Label(text="동아리 정보 또는 로그인 정보가 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
            return
            
        club_id = self.club_data.get('club_id')
        president_uid = self.club_data.get('president')
        self.header_title.text = f"[b]{self.club_data.get('name', '동아리')} 멤버 관리[/b]"

        try:
            # 1. DB에서 'members' 딕셔너리({uid1: True, uid2: True})를 가져옴
            path = f"all_clubs/{club_id}/members"
            members_dict = db.child(path).get(app.user_token).val()

            if not members_dict:
                self.grid.add_widget(Label(text="동아리장이 없습니다.", font_name=FONT_NAME, color=[0.5,0.5,0.5,1], size_hint_y=None, height=dp(100)))
                return

            # 2. 각 멤버의 UID로 'users' 경로에서 닉네임을 다시 조회
            for member_uid in members_dict.keys():
                
                # (동아리장 본인은 목록에 표시 안 함)
                if member_uid == president_uid:
                    continue
                
                item_layout = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(10))
                
                # 3. 닉네임 가져오기
                try:
                    nickname = db.child(f"users/{member_uid}/nickname").get(app.user_token).val()
                    if not nickname:
                        nickname = f"알 수 없는 멤버 ({member_uid[:5]}...)"
                except Exception:
                    nickname = f"멤버 정보 로드 실패 ({member_uid[:5]}...)"
                
                info_label = Label(text=nickname, font_name=FONT_NAME, color=[0,0,0,1], halign='left')
                info_label.bind(size=info_label.setter('text_size'))
                
                kick_btn = Button(
                    text="추방", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1],
                    size_hint_x=0.3
                )
                kick_btn.member_uid = member_uid # 버튼에 UID 정보 저장
                kick_btn.member_nickname = nickname
                kick_btn.bind(on_press=self.confirm_kick)

                item_layout.add_widget(info_label)
                item_layout.add_widget(kick_btn)
                self.grid.add_widget(item_layout)

        except Exception as e:
            self.grid.add_widget(Label(text=f"멤버 목록 로딩 실패: {e}", font_name=FONT_NAME, color=[0.8,0,0,1], size_hint_y=None, height=dp(100)))

    def confirm_kick(self, instance):
        """ 멤버 추방 확인 팝업"""
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
        
        popup = Popup(
            title="멤버 추방 확인", title_font=FONT_NAME, title_color=[0,0,0,1],
            content=popup_content, size_hint=(0.9, 0.4),
            separator_height=0, background=''
        )
        
        no_button.bind(on_press=popup.dismiss)
        yes_button.bind(on_press=lambda *args: self.perform_kick(member_uid, popup))
        popup.open()

    def perform_kick(self, member_uid, popup_to_dismiss):
        """ Firebase DB에서 멤버 삭제 (추방)"""
        app = App.get_running_app()
        club_id = self.club_data.get('club_id')
        
        if not club_id or not app.user_token:
            Popup(title='오류', content=Label(text='오류: ID 정보가 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        try:
            # Firebase DB의 members 경로에서 해당 멤버의 UID를 삭제
            path = f"all_clubs/{club_id}/members/{member_uid}"
            db.child(path).remove(app.user_token)

            popup_to_dismiss.dismiss() # 확인 팝업 닫기
            self.refresh_list() # 멤버 목록 새로고침

        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'추방 처리 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()





class PostScreen(WhiteBgScreen):
    """공지사항, 활동내역, 후기 등을 작성하는 화면"""
    club_data = ObjectProperty(None)
    post_type = StringProperty('') 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        type_map = {
            'announcement': '공지사항',
            'activity': '활동내역',
            'review': '후기',
            'free_board': '자유게시판' 
        }
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
        if not content:
            Popup(title='오류', content=Label(text='내용을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return
            
        app = App.get_running_app()
        
        if self.post_type == 'review' or self.post_type == 'free_board':
            content = f"({app.current_user_nickname}님) {content}"

        key_map = {
            'announcement': 'announcements',
            'activity': 'activities',
            'review': 'reviews',
            'free_board': 'free_board' 
        }
        data_key = key_map.get(self.post_type)

        if self.club_data and data_key and app.user_token:
            try:
                club_id = self.club_data.get('club_id')
                if not club_id:
                    Popup(title='오류', content=Label(text='동아리 ID가 없습니다.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
                    return
                
                # 내용과 함께 타임스탬프 저장 (알고리즘용)
                post_data = {
                    'content': content,
                    'timestamp': int(time.time())
                }
                
                path = f"all_clubs/{club_id}/{data_key}"
                db.child(path).push(post_data, app.user_token) 
                
                if data_key not in self.club_data:
                    self.club_data[data_key] = {}
                self.club_data[data_key][content[:10]] = post_data 
                
                popup = Popup(title='성공', content=Label(text='등록이 완료되었습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
                popup.bind(on_dismiss=lambda *args: self.go_to_screen('club_detail'))
                popup.open()
                
            except Exception as e:
                Popup(title='DB 오류', content=Label(text=f'데이터 저장 실패: {e}', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
        else:
            Popup(title='오류', content=Label(text='데이터 저장에 실패했습니다. (정보 부족)', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()


    def go_to_screen(self, screen_name):
        if screen_name == 'club_detail':
            detail_screen = self.manager.get_screen(screen_name)
            detail_screen.club_data = self.club_data
        self.manager.current = screen_name


# --- 안드로이드 권한 확인/요청을 위한 import  ---

from kivy.utils import platform  # 1. 플랫폼 확인을 위해 import



# 이 import는 'android' 플랫폼에서만 성공합니다.

try:

    from android.permissions import request_permissions, Permission

except ImportError:

    # PC나 iOS에서는 이 모듈이 없으므로, 테스트를 위한 가짜(Mock) 객체를 만듭니다.

    class MockPermission:

        READ_EXTERNAL_STORAGE = "READ_EXTERNAL_STORAGE"

        WRITE_EXTERNAL_STORAGE = "WRITE_EXTERNAL_STORAGE"

    Permission = MockPermission()

    

    def request_permissions(permissions_list, callback=None):

        print("권한 요청 시뮬레이션 (PC/iOS):", permissions_list)

        # PC에서는 즉시 권한이 승인된 것처럼 콜백 호출

        if callback:

            # grants = [True, True, ...]

            callback(permissions_list, [True] * len(permissions_list))



# --------------------------------------------------------

# 분실물 등록 페이지 (AddItemScreen)

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
        
        self.content_layout = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=[0, dp(10), 0, 0])
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))


        # 입력 필드
        self.name_input = get_rounded_textinput('물건 이름 (예: 에어팟 프로)')
        self.desc_input = get_rounded_textinput('자세한 설명 (공개됨, 예: 검은색 케이스)')
        self.loc_input = get_rounded_textinput('발견/분실 장소 (예: 중앙도서관 1층)')
        self.time_input = get_rounded_textinput('발견/분실 시간 (예: 14:30)')
        self.contact_input = get_rounded_textinput('연락처 (예: 010-1234-5678)')

        self.verification_desc_input = TextInput(
            hint_text='[신원 확인용 정보 (비공개)]\n(예: 배경화면 사진, 지갑 속 특정 카드, 케이스 안쪽 스티커 등)', 
            font_name=FONT_NAME, 
            size_hint_y=None, 
            height=dp(100), 
            padding=dp(15),
            background_normal='', 
            background_color=[0.95, 0.95, 0.8, 1] 
        )
        
        class KoreanSpinnerOption(SpinnerOption):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.font_name = FONT_NAME 
                self.background_normal = ''
                self.background_color = [1, 1, 1, 1] 
                self.color = [0, 0, 0, 1]            
                self.height = dp(50)

        self.category_spinner = Spinner(
            text='카테고리 선택 (종류)',
            values=('전자기기', '서적', '의류', '지갑/카드', '기타'),
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(55),
            background_normal='',             
            background_color=[1, 1, 1, 1],  
            color=[0, 0, 0, 1],
            option_cls=KoreanSpinnerOption 
        )

        self.content_layout.add_widget(self.name_input)
        self.content_layout.add_widget(self.desc_input)
        
        self.content_layout.add_widget(self.verification_desc_input)
        
        self.content_layout.add_widget(self.loc_input)
        self.content_layout.add_widget(self.time_input)
        self.content_layout.add_widget(self.contact_input)
        self.content_layout.add_widget(self.category_spinner)

        # 사진 등록 부분
        self.image_path = "" 
        photo_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), spacing=dp(10))
        self.photo_label = Label(text="사진이 선택되지 않았습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_x=0.7)
        photo_button = get_styled_button("사진 선택", [0.5, 0.7, 0.9, 1], [1, 1, 1, 1], font_size='18sp')
        photo_button.height = dp(55)
        photo_button.size_hint_x = 0.3
        photo_button.bind(on_press=self.select_photo)

        photo_layout.add_widget(self.photo_label)
        photo_layout.add_widget(photo_button)
        self.content_layout.add_widget(photo_layout)

        # 이미지 미리보기
        self.image_preview = Image(source=DEFAULT_IMAGE, size_hint_y=None, height=dp(150), fit_mode='contain')
        self.content_layout.add_widget(self.image_preview)

        self.content_layout.add_widget(Label(size_hint_y=None, height=dp(15))) 

        # 등록하기 버튼
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
                    index = self.content_layout.children.index(self.desc_input)
                    self.content_layout.add_widget(self.verification_desc_input, index=index)
                except:
                    self.content_layout.add_widget(self.verification_desc_input)

        self.name_input.text = ""
        self.desc_input.text = ""
        self.loc_input.text = ""
        self.time_input.text = ""
        self.contact_input.text = ""
        self.image_path = ""
        self.photo_label.text = "사진이 선택되지 않았습니다."
        self.image_preview.source = DEFAULT_IMAGE
        self.category_spinner.text = '카테고리 선택 (종류)'
        self.verification_desc_input.text = ""

    def select_photo(self, instance):
        if platform == 'android':
            permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
            request_permissions(permissions, self.on_permission_callback)
        else:
            self.open_file_chooser()

    def on_permission_callback(self, permissions, grants):
        if all(grants):
            self.open_file_chooser()
        else:
            Popup(title='권한 필요', content=Label(text='사진을 첨부하려면\n파일 접근 권한이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def open_file_chooser(self):
        filechooser.open_file(on_selection=self.on_file_selection)

    def on_file_selection(self, selection):
        if selection:
            self.image_path = selection[0]
            self.photo_label.text = os.path.basename(self.image_path)
            self.image_preview.source = self.image_path
            self.image_preview.reload()

    def register_item(self, instance):
        name = self.name_input.text
        desc = self.desc_input.text 
        loc = self.loc_input.text
        time_val = self.time_input.text
        contact = self.contact_input.text
        category = self.category_spinner.text
        verification_desc = self.verification_desc_input.text 

        if not name or not loc or not time_val or not contact or category == '카테고리 선택 (종류)':
            Popup(title='오류', content=Label(text='기본 정보를 모두 입력해주세요.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        if not self.is_lost and not verification_desc:
            Popup(title='오류', content=Label(text='[신원 확인용 정보]는\n습득물 등록 시 필수 항목입니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        app = App.get_running_app()
        item_id = f"item_{int(time.time())}_{app.current_user_uid}" 
        
        if not app.user_token:
            Popup(title='오류', content=Label(text='로그인이 필요합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        # 사진 업로드 처리
        image_url = ""
        if self.image_path:
            try:
                # 파일 확장자 추출 (없으면 jpg 기본)
                ext = os.path.splitext(self.image_path)[1]
                if not ext: ext = ".jpg"
                
                # Storage에 저장될 경로: images/아이템ID.확장자
                cloud_filename = f"images/{item_id}{ext}"
                
                # Firebase Storage에 파일 업로드
                storage.child(cloud_filename).put(self.image_path, app.user_token)
                
                # 업로드된 파일의 다운로드 URL 획득
                image_url = storage.child(cloud_filename).get_url(None)
                
            except Exception as e:
                print(f"이미지 업로드 실패: {e}")
                # 실패 시에도 글은 등록되도록 함 (이미지 없이)

        if self.is_lost:
            status = 'lost'
            verification_desc = "" 
        else:
            status = 'found_available'

        new_item = {
            'item_id': item_id,
            'name': name, 
            'desc': desc, 
            'loc': loc, 
            'time': time_val, 
            'contact': contact,
            'image': image_url, # 로컬 경로 대신 URL 저장
            'category': category,
            'status': status,
            'registered_by_id': app.current_user, 
            'registered_by_uid': app.current_user_uid, 
            'registered_by_nickname': app.current_user_nickname,
            'verification_desc': verification_desc 
        }
        
        try:
            db.child("pending_items").child(item_id).set(new_item, app.user_token)
            popup = Popup(title='알림', content=Label(text='등록 신청이 완료되었습니다.\n관리자 승인 후 게시됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('lost_found'))
            popup.open()
            
        except Exception as e:
            Popup(title='DB 오류', content=Label(text=f'데이터 저장 실패: {e}', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()


# --------------------------------------------------------

#  분실물 상세 정보 페이지 (ItemDetailScreen)

# --------------------------------------------------------



class ItemDetailScreen(WhiteBgScreen):
    item_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = RelativeLayout()
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.main_layout.clear_widgets()

        if not self.item_data:
            return

        app = App.get_running_app()
        
        # --- 1. 하단 고정 바 ---
        bottom_bar = BoxLayout(
            size_hint=(1, None), height=dp(80), 
            pos_hint={'bottom': 0}, padding=dp(10), spacing=dp(10)
        )
        with bottom_bar.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bottom_rect = Rectangle(size=bottom_bar.size, pos=bottom_bar.pos)
        bottom_bar.bind(size=self._update_rect_cb(self.bottom_rect), 
                        pos=self._update_rect_cb(self.bottom_rect))
        
        is_my_post = self.item_data.get('registered_by_uid') == app.current_user_uid
        item_status = self.item_data.get('status')
        
        if is_my_post:
            if item_status == 'found_pending':
                status_label_text = "다른 사용자가 신청하여 관리자가 검토 중입니다."
            elif item_status == 'found_returned':
                status_label_text = "물품 전달이 완료되었습니다."
            else:
                status_label_text = "내가 등록한 게시물입니다."
            status_label = Label(text=status_label_text, font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1])
            bottom_bar.add_widget(status_label)
        elif item_status == 'lost':
            contact_text = f"연락처: {self.item_data.get('contact', '비공개')}"
            contact_button = get_styled_button(contact_text, [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='20sp')
            bottom_bar.add_widget(contact_button)
        else: 
            if item_status == 'found_available':
                claim_button = get_styled_button("이 물건 주인입니다 (신청하기)", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1], font_size='20sp')
                claim_button.bind(on_press=self.show_claim_verification_popup)
                bottom_bar.add_widget(claim_button)
            elif item_status == 'found_pending':
                status_label = Label(text="관리자가 다른 사용자의 신청을 검토 중입니다.", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1])
                bottom_bar.add_widget(status_label)
            elif item_status == 'found_returned':
                status_label = Label(text="물품 전달이 완료되었습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1])
                bottom_bar.add_widget(status_label)

        
        # --- 2. 메인 컨텐츠 영역 ---
        main_content_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=[0, 0, 0, dp(80)] 
        )

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('lost_found'))
        header.add_widget(back_button)
        
        status_text_val = "분실물 정보" if self.item_data.get('status') == 'lost' else "습득물 정보"
        header.add_widget(Label(text=f"[b]{status_text_val}[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_content_container.add_widget(header)

        # --- 3. 스크롤 가능한 컨텐츠 ---
        scroll_view = ScrollView(size_hint=(1, 1))
        
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15), padding=dp(10))
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        # 3-1. 이미지 (AsyncImage 적용)
        image = AsyncImage(
            source=self.item_data.get('image') if self.item_data.get('image') else DEFAULT_IMAGE,
            size_hint_y=None,
            height=dp(300),
            fit_mode='contain'
        )
        scroll_content.add_widget(image)

        # 3-2. 등록자 정보
        registrant_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), padding=[dp(10), 0])
        registrant = self.item_data.get('registered_by_nickname', self.item_data.get('registered_by_id', '알 수 없음'))
        
        profile_icon = Image(source=DEFAULT_IMAGE, size_hint=(None, None), size=(dp(40), dp(40)))
        registrant_box.add_widget(profile_icon)
        registrant_box.add_widget(Label(size_hint_x=None, width=dp(10))) 
        
        registrant_label = Label(
            text=f"[b]등록자: {registrant}[/b]",
            font_name=FONT_NAME, color=[0,0,0,1], markup=True,
            font_size='18sp', halign='left'
        )
        registrant_label.bind(size=registrant_label.setter('text_size'))
        registrant_box.add_widget(registrant_label)
        scroll_content.add_widget(registrant_box)

        # 3-3. 구분선
        separator = Label(size_hint_y=None, height=dp(1))
        with separator.canvas.before:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=separator.pos, size=(self.width - dp(40), dp(1)))
        scroll_content.add_widget(separator)

        # 3-4. 상세 정보
        info_section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8), padding=[dp(10), dp(15)])
        info_section.bind(minimum_height=info_section.setter('height'))

        item_name_label = Label(
            text=f"[b]{self.item_data.get('name')}[/b]",
            font_name=FONT_NAME, color=[0,0,0,1], markup=True,
            font_size='24sp', size_hint_y=None, halign='left'
        )
        item_name_label.bind(width=lambda *x: item_name_label.setter('text_size')(item_name_label, (item_name_label.width, None)),
                                texture_size=lambda *x: item_name_label.setter('height')(item_name_label, item_name_label.texture_size[1]))
        info_section.add_widget(item_name_label)

        status_val = self.item_data.get('status')
        status_color = "[color=A01010]" if status_val == 'lost' else "[color=1010A0]"
        status_display_text = "분실" if status_val == 'lost' else "습득"
        
        category_label = Label(
            text=f"{status_color}[b]{status_display_text}[/b][/color] · {self.item_data.get('category', '기타')}",
            font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True,
            font_size='16sp', size_hint_y=None, height=dp(25), halign='left'
        )
        category_label.bind(size=category_label.setter('text_size'))
        info_section.add_widget(category_label)

        loc_time_label = Label(
            text=f"장소: {self.item_data.get('loc')}  ·  시간: {self.item_data.get('time', 'N/A')}",
            font_name=FONT_NAME, color=[0.3,0.3,0.3,1],
            font_size='16sp', size_hint_y=None, height=dp(25), halign='left'
        )
        loc_time_label.bind(size=loc_time_label.setter('text_size'))
        info_section.add_widget(loc_time_label)
        
        info_section.add_widget(Label(size_hint_y=None, height=dp(15))) 
        
        desc_title_label = Label(
            text="[b]상세 설명[/b]",
            font_name=FONT_NAME, color=[0,0,0,1], markup=True,
            font_size='20sp', size_hint_y=None, height=dp(40), halign='left'
        )
        desc_title_label.bind(size=desc_title_label.setter('text_size'))
        info_section.add_widget(desc_title_label)

        desc_content_label = Label(
            text=self.item_data.get('desc', '없음'),
            font_name=FONT_NAME, color=[0.2,0.2,0.2,1],
            font_size='16sp', size_hint_y=None, halign='left'
        )
        desc_content_label.bind(width=lambda *x: desc_content_label.setter('text_size')(desc_content_label, (desc_content_label.width, None)),
                                texture_size=lambda *x: desc_content_label.setter('height')(desc_content_label, desc_content_label.texture_size[1]))
        info_section.add_widget(desc_content_label)

        scroll_content.add_widget(info_section)
        scroll_view.add_widget(scroll_content)
        
        main_content_container.add_widget(scroll_view)
        
        self.main_layout.add_widget(main_content_container)
        self.main_layout.add_widget(bottom_bar)


    def show_claim_verification_popup(self, instance):
        app = App.get_running_app()
        item_id = self.item_data.get('item_id')

        try:
            claims_node = db.child("claims").get(app.user_token)
            claims_dict = claims_node.val()
            
            if claims_dict:
                for c in claims_dict.values():
                    if c.get('item_id') == item_id and c.get('claimer_id') == app.current_user_uid:
                         Popup(title='알림', content=Label(text='이미 신청한 물품입니다.\n관리자가 검토 중입니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
                         return
        except Exception:
            pass

        # 팝업 컨텐츠 레이아웃
        content_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        with content_layout.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect_bg = RoundedRectangle(pos=content_layout.pos, size=content_layout.size, radius=[dp(10)])
        
        content_layout.bind(pos=self._update_popup_rect_cb(self.rect_bg), 
                            size=self._update_popup_rect_cb(self.rect_bg))

        content_layout.add_widget(Label(
            text="[b]물품 주인 확인[/b]\n\n관리자가 확인할 수 있도록\n본인 소유임을 증명할 수 있는\n[b]상세 특징[/b]을 입력해주세요.",
            font_name=FONT_NAME, markup=True, halign='center', color=[0,0,0,1]
        ))
        
        detail_input = TextInput(
            hint_text='물품의 상세 특징 (예: 케이스 색상, 스티커, 배경화면, 내용물 등)', 
            font_name=FONT_NAME, multiline=True, size_hint_y=None, height=dp(100),
            background_normal='', background_color=[0.95, 0.95, 0.95, 1],
            foreground_color=[0,0,0,1],
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        content_layout.add_widget(detail_input)
        
        submit_button = get_styled_button("신청서 제출", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])
        
        popup = Popup(
            title="", 
            content=content_layout,
            size_hint=(0.9, 0.6),
            auto_dismiss=False,
            separator_height=0,  
            background=""  
        )
        
        submit_button.bind(on_press=lambda *args: self.submit_verification_claim(
            popup, item_id, detail_input.text
        ))
        
        content_layout.add_widget(submit_button)
        
        close_button = get_styled_button("취소", [0.5, 0.5, 0.5, 1], [1,1,1,1]) 
        close_button.bind(on_press=popup.dismiss)
        content_layout.add_widget(close_button)

        popup.open()

    def submit_verification_claim(self, popup, item_id, details):
        if not details:
            print("상세 내용을 입력해주세요.") 
            return

        app = App.get_running_app()
        
        if not app.user_token:
             popup.dismiss()
             return

        claim_id = f"claim_{int(time.time())}_{app.current_user_uid}"
        
        claim_data = {
            'claim_id': claim_id,
            'item_id': item_id,
            'claimer_id': app.current_user_uid,
            'claimer_nickname': app.current_user_nickname,
            'verification_details': details,
        }

        try:
            db.child("claims").child(claim_id).set(claim_data, app.user_token)
            db.child("all_items").child(item_id).update({'status': 'found_pending'}, app.user_token)
            
            popup.dismiss()
            
            success_popup = Popup(title='신청 완료', content=Label(text='주인 확인 신청이 완료되었습니다.\n관리자 검토 후 승인되면 연락처가 공개됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.4))
            success_popup.bind(on_dismiss=lambda *args: self.go_to_screen('lost_found'))
            success_popup.open()

        except Exception as e:
            print(f"신청 실패: {e}")
            popup.dismiss()


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

# --------------------------------------------------------

# 내 신청 현황 (신청자용)

# --------------------------------------------------------

class MyClaimsScreen(WhiteBgScreen):
    """내가 신청한 물품의 '상태'와 '연락처'를 확인하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main')) # 메인으로 돌아가기
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]내 신청 현황[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        # 스크롤 뷰
        scroll_view = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.grid.bind(minimum_height=self.grid.setter('height'))

        scroll_view.add_widget(self.grid)
        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        self.bind(on_enter=self.refresh_list)

    # 텍스트 겹침 방지 헬퍼 함수
    def create_wrapping_label(self, text_content, **kwargs):
        label = Label(
            text=text_content, size_hint_y=None, font_name=FONT_NAME,
            markup=True, halign='left', **kwargs
        )
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        return label

    def refresh_list(self, *args):
        self.grid.clear_widgets()
        app = App.get_running_app()
        
        if not app.user_token:
             return

        try:
            # 내 신청 내역(claims) 가져오기
            claims_node = db.child("claims").get(app.user_token)
            claims_dict = claims_node.val()
            my_claims = []
            
            if claims_dict:
                for c in claims_dict.values():
                    if c.get('claimer_id') == app.current_user_uid:
                        my_claims.append(c)
        except Exception:
            my_claims = []

        if not my_claims:
            self.grid.add_widget(Label(text="신청한 내역이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        for claim in my_claims:
            item_id = claim.get('item_id')
            
            # 물품 정보 가져오기
            item_name = "알 수 없는 물품"
            try:
                item_data = db.child(f"all_items/{item_id}").get(app.user_token).val()
                if item_data:
                    item_name = item_data.get('name', "알 수 없는 물품")
            except:
                pass
            
            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            item_box.bind(minimum_height=item_box.setter('height')) 

            with item_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
            item_box.bind(
                pos=lambda instance, value, r=bg_rect: setattr(r, 'pos', value),
                size=lambda instance, value, r=bg_rect: setattr(r, 'size', value)
            )

            # 1. 물품명 표시
            item_box.add_widget(self.create_wrapping_label(
                text_content=f"[b]물품명: {item_name}[/b]", 
                color=[0,0,0,1]
            ))
            
            item_box.add_widget(Label(size_hint_y=None, height=dp(5)))

            # 2. 신청 상태(status)에 따라 분기
            claim_status = claim.get('status')
            
            if claim_status == 'approved':
                # (관리자가 승인 시 finder_contact에 '학생복지처'라고 저장됨)
                location_info = claim.get('finder_contact', '학생복지처')
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=008000][b]승인 완료[/b][/color]\n" \
                                 f"수령 장소: [b]{location_info}[/b]\n" \
                                 "(학생복지처에 방문하여 물품을 수령하세요)", 
                    color=[0.2, 0.2, 0.2, 1]
                ))
                
            elif claim_status == 'rejected':
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=A01010][b]신청 거절[/b][/color]\n" \
                                 "(관리자가 신청을 거절했습니다)", 
                    color=[0.2, 0.2, 0.2, 1]
                ))
            
            else:
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=F08000][b]관리자 검토 중[/b][/color]\n" \
                                 "(관리자가 신청 내역을 확인하고 있습니다)", 
                    color=[0.2, 0.2, 0.2, 1]
                ))
            
            self.grid.add_widget(item_box)



# --------------------------------------------------------

#  분실물 페이지 (LostAndFoundScreen)

# --------------------------------------------------------

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
        self.category_spinner = Spinner(
            text='전체',
            values=('전체', '전자기기', '서적', '의류', '지갑/카드', '기타'),
            font_name=FONT_NAME,
            size_hint_x=0.7,
            background_normal='',             
            background_color=[1, 1, 1, 1],  
            color=[0, 0, 0, 1]                
        )
        
        self.category_spinner.option_cls_args = {
            'font_name': FONT_NAME,           
            'background_normal': '',        
            'background_color': [1, 1, 1, 1], 
            'color': [0, 0, 0, 1],            
            'height': dp(50)                  
        }
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
        
        popup_content.bind(pos=self._update_popup_rect_cb(self.rect_bg),
                           size=self._update_popup_rect_cb(self.rect_bg))

        popup = Popup(
            title='등록 종류 선택',
            title_font=FONT_NAME,
            title_color=[0, 0, 0, 1], 
            content=popup_content,
            size_hint=(0.8, 0.4),
            separator_height=0,      
            background=''            
        )
        
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
        if not app.user_token: return

        keyword = self.search_input.text.lower()
        category = self.category_spinner.text
        
        try:
            items_node = db.child("all_items").get(app.user_token)
            items_dict = items_node.val()
            
            all_items_list = []
            if items_dict:
                all_items_list = list(items_dict.values())

            base_list = [
                item for item in all_items_list 
                if item.get('status') == 'lost' or item.get('status') == 'found_available'
            ]
            
            filtered_list = base_list

            if category != '전체':
                filtered_list = [item for item in filtered_list if item.get('category') == category]

            if keyword:
                filtered_list = [
                    item for item in filtered_list
                    if keyword in item['name'].lower() 
                    or keyword in item.get('desc', '').lower()
                    or keyword in item.get('loc', '').lower()
                ]
            
            filtered_list.sort(key=lambda x: x.get('item_id', ''), reverse=True)

            self.update_item_list(filtered_list)
            
        except Exception as e:
            print(f"검색 실패: {e}")
            self.update_item_list([])


    def register_keyword(self, instance):
        app = App.get_running_app()
        keyword = self.keyword_input.text.strip()
        if keyword and keyword not in app.notification_keywords:
            app.notification_keywords.append(keyword)
            Popup(title='알림', content=Label(text=f"키워드 '{keyword}'가 등록되었습니다.", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            self.keyword_input.text = ""
        elif not keyword:
            Popup(title='오류', content=Label(text="키워드를 입력해주세요.", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
        else:
            Popup(title='알림', content=Label(text=f"이미 등록된 키워드입니다.", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def refresh_list(self, *args):
        self.search_input.text = ""
        self.category_spinner.text = '전체'
        self.search_items()

    def update_item_list(self, items):
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
                    height=dp(120),
                    spacing=dp(10),
                    padding=dp(5)
                )
                
                item_layout.item_data = item_data
                item_layout.bind(on_press=self.view_item_details)

                # AsyncImage 적용
                image = AsyncImage(
                    source=item_data.get('image') if item_data.get('image') else DEFAULT_IMAGE,
                    size_hint_x=None,
                    width=dp(90),
                    fit_mode='contain'
                )
                item_layout.add_widget(image)

                text_layout = BoxLayout(orientation='vertical', spacing=dp(5))

                status_val = item_data.get('status')
                status_text = ""
                if status_val == 'lost':
                    status_text = "[b][color=A01010]분실[/color][/b]"
                elif status_val == 'found_available':
                    status_text = "[b][color=1010A0]습득[/color][/b]"
                else:
                    status_text = "[b][color=505050]완료[/color][/b]" 
                
                name_label = Label(
                    text=f"{status_text} {item_data['name']}", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(25)
                )
                loc_label = Label(
                    text=f"[b]장소:[/b] {item_data['loc']}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )
                
                time_label = Label(
                    text=f"[b]시간:[/b] {item_data.get('time', 'N/A')}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )

                text_layout.add_widget(name_label)
                text_layout.add_widget(loc_label)
                text_layout.add_widget(time_label)

                for label in [name_label, loc_label, time_label]:
                    label.bind(size=label.setter('text_size'))

                item_layout.add_widget(text_layout)
                self.items_grid.add_widget(item_layout)

    def view_item_details(self, instance):
        detail_screen = self.manager.get_screen('item_detail')
        detail_screen.item_data = instance.item_data
        self.go_to_screen('item_detail')

    def _update_popup_rect_cb(self, rect):
        def update_rect(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size
        return update_rect




# --------------------------------------------------------

#  회원가입 페이지 (2단계)

# --------------------------------------------------------

class SignupScreen(WhiteBgScreen):

    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.current_step = 'step1'

        # Step 1과 Step 2 컨텐츠를 담을 메인 컨테이너
        self.main_container = BoxLayout(
            orientation='vertical',
        )
        self.add_widget(self.main_container)

        self.setup_step1()
        self.setup_step2()
        self.update_view() # 초기 화면은 Step 1



    def setup_step1(self):
        """회원가입 1단계 (기본 정보) 레이아웃 설정"""
        
        # 1.스크롤 뷰의 '내용물'이 될 레이아웃
        step1_content_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(15), 
            size_hint_y=None,  
            padding=[dp(50), dp(80), dp(50), dp(80)] 
        )
        # 내용물의 최소 높이에 따라 레이아웃의 실제 높이를 조절
        step1_content_layout.bind(minimum_height=step1_content_layout.setter('height'))

        step1_content_layout.add_widget(Label(
            text="[b]Campus Link 회원가입 (1/2)[/b]",
            font_size='32sp',
            font_name=FONT_NAME,
            color=[0.1, 0.4, 0.7, 1],
            markup=True,
            size_hint_y=None,
            height=dp(60)
        ))
        step1_content_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        # 입력 필드: 학번, 이름, 학과, 학년
        self.student_id_input = get_rounded_textinput('학번 (예: 20240001)', input_type='number')
        self.name_input = get_rounded_textinput('이름')
        self.department_input = get_rounded_textinput('학과')
        self.grade_input = get_rounded_textinput('학년 (예: 3)', input_type='number')

        step1_content_layout.add_widget(self.student_id_input)
        step1_content_layout.add_widget(self.name_input)
        step1_content_layout.add_widget(self.department_input)
        step1_content_layout.add_widget(self.grade_input)

        # 다음 버튼 (1/2)
        next_button = get_styled_button(
            "다음 (1/2)",
            [0.2, 0.6, 1, 1],
            [1, 1, 1, 1]
        )
        next_button.bind(on_press=self.go_to_step2)
        step1_content_layout.add_widget(next_button)

        # 취소 버튼
        cancel_button = get_styled_button(
            "취소 (로그인 화면으로)",
            [0.5, 0.5, 0.5, 1],
            [1, 1, 1, 1],
            font_size='18sp'
        )
        cancel_button.height = dp(50)
        cancel_button.bind(on_press=self.go_to_login)
        step1_content_layout.add_widget(cancel_button)

        step1_content_layout.add_widget(Label()) # 스페이서
        
        # 2. ScrollView 생성 및 '내용물' 레이아웃 탑재
        step1_scrollview = ScrollView(size_hint=(1, 1))
        step1_scrollview.add_widget(step1_content_layout) # 스크롤 뷰에 내용물 레이아웃 추가

        # 3. update_view가 사용할 self.step1_layout에 최종 스크롤 뷰를 할당
        self.step1_layout = step1_scrollview


    def setup_step2(self):
        """회원가입 2단계 (계정 정보) 레이아웃 설정"""
        
        # 1.스크롤 뷰의 '내용물'이 될 레이아웃
        step2_content_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(15), 
            size_hint_y=None,  
            padding=[dp(50), dp(80), dp(50), dp(80)] 
        )
        # 내용물의 최소 높이에 따라 레이아웃의 실제 높이를 조절
        step2_content_layout.bind(minimum_height=step2_content_layout.setter('height'))

        step2_content_layout.add_widget(Label(
            text="[b]Campus Link 회원가입 (2/2)[/b]",
            font_size='32sp',
            font_name=FONT_NAME,
            color=[0.1, 0.4, 0.7, 1],
            markup=True,
            size_hint_y=None,
            height=dp(60)
        ))
        step2_content_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        # --- 1. 위젯 인스턴스 생성 ---
        self.email_input = get_rounded_textinput('이메일 주소', input_type='mail')
        
        self.login_id_input = get_rounded_textinput('아이디 (로그인용)') 
        self.nickname_input = get_rounded_textinput('닉네임 (표시용)') 
        self.password_input = get_rounded_textinput('비밀번호 (최소 6자)', password=True)
        self.confirm_password_input = get_rounded_textinput('비밀번호 확인', password=True)

        # --- 2. 위젯을 '내용물' 레이아웃에 올바른 순서로 추가 ---
        step2_content_layout.add_widget(self.email_input)
        step2_content_layout.add_widget(self.login_id_input) 
        step2_content_layout.add_widget(self.nickname_input)
        step2_content_layout.add_widget(self.password_input)
        step2_content_layout.add_widget(self.confirm_password_input)

        # 최종 회원가입 버튼
        signup_button = get_styled_button(
            "회원가입 완료",
            [0.2, 0.6, 1, 1],
            [1, 1, 1, 1]
        )
        signup_button.bind(on_press=self.do_signup)
        step2_content_layout.add_widget(signup_button)

        # 이전 버튼
        prev_button = get_styled_button(
            "이전",
            [0.5, 0.5, 0.5, 1],
            [1, 1, 1, 1],
            font_size='18sp'
        )
        prev_button.height = dp(50)
        prev_button.bind(on_press=self.go_to_step1)
        step2_content_layout.add_widget(prev_button)

        step2_content_layout.add_widget(Label()) # 스페이서
        
        # 3. ScrollView 생성 및 '내용물' 레이아웃 탑재
        step2_scrollview = ScrollView(size_hint=(1, 1))
        step2_scrollview.add_widget(step2_content_layout) # 스크롤 뷰에 내용물 레이아웃 추가

        # 4.update_view가 사용할 self.step2_layout에 최종 스크롤 뷰를 할당
        self.step2_layout = step2_scrollview



    def update_view(self):

        """현재 단계에 맞춰 화면을 갱신합니다."""

        self.main_container.clear_widgets()

        if self.current_step == 'step1':

            self.main_container.add_widget(self.step1_layout)

        else:

            self.main_container.add_widget(self.step2_layout)



    def go_to_step1(self, instance):

        """Step 2에서 Step 1로 돌아갑니다."""

        self.current_step = 'step1'

        self.update_view()



    def go_to_step2(self, instance):

        """Step 1에서 Step 2로 진행합니다. (1단계 유효성 검사 포함)"""

        # Step 1 유효성 검사 (간단화)

        if not self.student_id_input.text or not self.name_input.text:

            self.show_popup("오류", "학번과 이름을 입력해주세요.")

            return



        self.current_step = 'step2'

        self.update_view()



    def go_to_login(self, instance):

        """로그인 화면으로 전환하고 모든 입력 필드를 초기화합니다."""

        self.student_id_input.text = ''

        self.name_input.text = ''

        self.department_input.text = ''

        self.grade_input.text = ''



        self.email_input.text = ''

        self.login_id_input.text = '' # <-- 아이디 필드 초기화

        self.nickname_input.text = ''

        self.password_input.text = ''

        self.confirm_password_input.text = ''



        self.current_step = 'step1' # 단계 초기화

        self.update_view() # 화면 초기화

        self.manager.current = 'login'



    

    def do_signup(self, instance):
        """최종 회원가입 버튼 클릭 시 실행되는 함수 (2단계 유효성 검사 포함)"""
        # --- (1단계 정보 가져오기) ---
        student_id = self.student_id_input.text
        name = self.name_input.text
        department = self.department_input.text
        grade = self.grade_input.text
        
        # --- (2단계 정보 가져오기) ---
        email = self.email_input.text
        login_id = self.login_id_input.text # DB 매핑에 사용될 키
        nickname = self.nickname_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        
        # 2단계 유효성 검사
        if not email or not login_id or not nickname or not password or not confirm_password:
            self.show_popup("오류", "모든 계정 정보를 채워주세요.")
            return
        if password != confirm_password:
            self.show_popup("오류", "비밀번호가 일치하지 않습니다.")
            return
        if len(password) < 6: # (Firebase 기본값은 6자입니다.)
            self.show_popup("오류", "비밀번호는 6자 이상이어야 합니다.")
            return

        # Firebase 객체 확인
        if auth is None or db is None:
             self.show_popup("오류", "Firebase가 초기화되지 않았습니다.")
             return
             
        try:
            mapping_node = db.child("id_to_email_mapping").child(login_id).get()
            if mapping_node.val() is not None:
                self.show_popup("오류", "이미 사용 중인 아이디입니다.")
                return
        except Exception as e:
            self.show_popup("오류", f"DB 검사 실패: {e}")
            return
        
        # --------------------------------------------------------
        # Firebase 연동 시작
        # --------------------------------------------------------
        try:
            # 1. Firebase Authentication에 '이메일'로 사용자 생성
            user = auth.create_user_with_email_and_password(email, password)
            
            uid = user['localId']
            id_token = user['idToken'] # 인증 토큰

            try:
                auth.send_email_verification(id_token)
            except Exception as email_error:
                # (이메일 발송이 실패해도 회원가입은 계속 진행되도록 함)
                print(f"경고: 인증 이메일 발송 실패 - {email_error}")

            # 3. Realtime Database에 '비공개' 프로필 정보 저장
            user_profile_data = {
                'login_id': login_id,
                'nickname': nickname,
                'email': email,
                'role': 'user',
                'student_id': student_id,
                'name': name,
                'department': department,
                'grade': grade
                # emailVerified 플래그는 Auth에만 있고, DB에는 굳이 저장 안 해도 됨
            }
            db.child("users").child(uid).set(user_profile_data, id_token)

            # 4. Realtime Database에 '공개용' 아이디-이메일 매핑 저장
            db.child("id_to_email_mapping").child(login_id).set(email, id_token)

            self.show_popup("성공", f"회원가입 신청이 완료되었습니다.\n\n'{email}'로 발송된\n인증 링크를 클릭하여 계정을 활성화해주세요.", after_dismiss_callback=self.go_to_login)

        except Exception as e:
            error_text = str(e)
            if "EMAIL_EXISTS" in error_text:
                self.show_popup("오류", "이미 사용 중인 이메일입니다.")
            elif "WEAK_PASSWORD" in error_text:
                self.show_popup("오류", "비밀번호는 6자 이상이어야 합니다.")
            elif "INVALID_EMAIL" in error_text:
                 self.show_popup("오류", "유효하지 않은 이메일 형식입니다.")
            else:
                self.show_popup("오류", "Firebase 연결에 실패했습니다.\n(네트워크 또는 규칙 확인)")


    def show_popup(self, title, message, after_dismiss_callback=None):

        """결과 메시지를 팝업으로 표시하는 도우미 함수"""

        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))



        # (핵심) 1. 흰색 배경 그리기

        with content_layout.canvas.before:

            Color(1, 1, 1, 1) # 흰색

            self.rect_popup_bg = Rectangle(size=content_layout.size, pos=content_layout.pos)

        

        # (핵심) 2. 팝업 크기/위치 변경 시 배경도 같이 변경되도록 바인딩

        def update_popup_rect(instance, value):

            self.rect_popup_bg.pos = instance.pos

            self.rect_popup_bg.size = instance.size

            

        content_layout.bind(pos=update_popup_rect, size=update_popup_rect)





        popup_content = Label(text=message, font_size='18sp', font_name=FONT_NAME, color=[0, 0, 0, 1])

        content_layout.add_widget(popup_content)



        confirm_button = get_styled_button("확인", [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='20sp')

        confirm_button.height = dp(50)



        popup = Popup(

            title=title,

            title_font=FONT_NAME,

            title_color=[0, 0, 0, 1], # 제목 색상

            content=content_layout,

            size_hint=(0.8, 0.4),

            auto_dismiss=False,

            separator_height=0,         # (핵심) 3. 기본 제목 표시줄(회색) 제거

            background=''               # (핵심) 4. 기본 팝업 배경(회색) 투명하게

        )



        def on_confirm(btn_instance):

            popup.dismiss()

            if after_dismiss_callback:

                after_dismiss_callback(None)



        confirm_button.bind(on_press=on_confirm)

        content_layout.add_widget(confirm_button)

        popup.open()





# --------------------------------------------------------

# 기존 로그인 화면

# --------------------------------------------------------

# --------------------------------------------------------

# 기존 로그인 화면

# --------------------------------------------------------

# --------------------------------------------------------
# 기존 로그인 화면
# --------------------------------------------------------
class LoginScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        # 모든 위젯을 담을 메인 레이아웃 (수직 배치)
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(50), dp(80), dp(50), dp(80)],
            spacing=dp(18)
        )

        # 1. 앱 이름 표시 (Label)
        app_name_label = Label(
            text="[b]Campus Link[/b]",
            font_size='48sp', # 크기 키움
            color=[0.1, 0.4, 0.7, 1], # 진한 파란색
            font_name=FONT_NAME,
            markup=True,
            size_hint_y=None,
            height=dp(90)
        )
        main_layout.add_widget(app_name_label)

        # 빈 공간 추가 (스페이서)
        main_layout.add_widget(Label(size_hint_y=None, height=dp(20)))

        # --- '아이디' ---
        self.username_input = get_rounded_textinput('아이디') 
        main_layout.add_widget(self.username_input)
        # --- ---

        # 비밀번호 입력 필드 (커스텀 스타일 적용)
        self.password_input = get_rounded_textinput('비밀번호', password=True)
        main_layout.add_widget(self.password_input)

        # 로그인 버튼 (둥근 스타일 적용)
        login_button = get_styled_button(
            "로그인",
            [0.2, 0.6, 1, 1], # 파란색
            [1, 1, 1, 1]
        )
        login_button.bind(on_press=self.do_login)
        main_layout.add_widget(login_button)

        # 회원가입 버튼 (둥근 스타일 적용)
        signup_button = get_styled_button(
            "회원가입",
            [0.5, 0.7, 0.9, 1], # 밝은 파란색
            [1, 1, 1, 1]
        )
        signup_button.bind(on_press=self.go_to_signup)
        main_layout.add_widget(signup_button)

        # 하단에 빈 공간 추가
        main_layout.add_widget(Label())

        # Screen에 메인 레이아웃 추가
        self.add_widget(main_layout)

    def go_to_signup(self, instance):
        """회원가입 화면으로 전환합니다."""
        self.manager.current = 'signup'

    def show_popup(self, title, message, show_retry_button=False):
        """결과 메시지를 팝업으로 표시하는 도우미 함수"""

        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        with content_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.rect_popup = Rectangle(size=content_layout.size, pos=content_layout.pos)

        def update_popup_rect(instance, value):
            self.rect_popup.pos = instance.pos
            self.rect_popup.size = instance.size

        content_layout.bind(pos=update_popup_rect, size=update_popup_rect)

        popup_content = Label(
            text=message,
            font_size='18sp',
            font_name=FONT_NAME,
            color=[0, 0, 0, 1]
        )
        content_layout.add_widget(popup_content)

        if show_retry_button:
            retry_button = get_styled_button("다시 시도", [0.9, 0.2, 0.2, 1], [1, 1, 1, 1], font_size='20sp')
            retry_button.height = dp(50)

            popup = Popup(
                title=title,
                title_font=FONT_NAME,
                title_color=[0, 0, 0, 1],
                content=content_layout,
                size_hint=(0.8, 0.4),
                auto_dismiss=False,
                separator_height=0,
                background=''
            )
            # 버튼을 누르면 팝업만 닫습니다.
            retry_button.bind(on_press=lambda x: popup.dismiss())
            content_layout.add_widget(retry_button)
        else:
            popup = Popup(
                title=title,
                title_font=FONT_NAME,
                title_color=[0, 0, 0, 1],
                content=content_layout,
                size_hint=(0.8, 0.4),
                auto_dismiss=True,
                separator_height=0,
                background=''
            )

        popup.open()

    def do_login(self, instance):
        """로그인 버튼 클릭 시 실행되는 함수"""
        username = self.username_input.text # 'username'은 사용자가 입력한 '아이디'입니다.
        password = self.password_input.text
        app = App.get_running_app()
        
        if not username or not password:
            self.show_popup("로그인 실패", "아이디와 비밀번호를 입력하세요.", show_retry_button=True)
            return
        
        if auth is None or db is None:
             self.show_popup("로그인 실패", "Firebase가 초기화되지 않았습니다.", show_retry_button=True)
             return

        try:
            # 1. (DB 조회) 아이디로 이메일 찾기
            email_node = db.child("id_to_email_mapping").child(username).get()
            email = email_node.val() 

            if email is None:
                self.show_popup("로그인 실패", "존재하지 않는 아이디입니다.", show_retry_button=True)
                return

            # 2. (인증) 찾은 이메일로 실제 로그인 시도
            user = auth.sign_in_with_email_and_password(email, password)
            
            uid = user['localId']
            id_token = user['idToken']

            # 3. 사용자 정보 새로고침 및 이메일 인증 확인
            refreshed_user_info = auth.get_account_info(id_token)
            email_verified = refreshed_user_info['users'][0]['emailVerified'] # True 또는 False

            if not email_verified:
                # show_popup을 호출하고, 'return'으로 함수를 종료합니다.
                self.show_popup("로그인 실패", "이메일 인증이 완료되지 않았습니다.\n\n메일함에서 인증 링크를 클릭해주세요.", show_retry_button=True)
                return 
            
            # 4. 인증 토큰과 UID를 App 객체에 저장
            app.user_token = id_token 
            app.current_user_uid = uid 

            # 5. (DB 조회) 프로필 정보 가져오기
            user_profile = db.child("users").child(uid).get(id_token).val()

            if user_profile:
                app.current_user_nickname = user_profile.get('nickname', '사용자')
                app.current_user_role = user_profile.get('role', 'user')
                app.current_user = user_profile.get('login_id', username)
            else:
                app.current_user_nickname = "사용자"
                app.current_user_role = "user"
                app.current_user = username

            # 6. 메인 화면으로 이동
            self.manager.current = 'main'

        except Exception as e:
            error_text = str(e)
            if "INVALID_LOGIN_CREDENTIALS" in error_text:
                self.show_popup("로그인 실패", "비밀번호가 올바르지 않습니다.", show_retry_button=True)
            elif "INVALID_EMAIL" in error_text:
                self.show_popup("로그인 실패", "유효하지 않은 이메일 형식입니다.", show_retry_button=True)
            else:
                self.show_popup("로그인 실패", "DB 연결 또는 인증에 실패했습니다.", show_retry_button=True)






class MyApp(App):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # (더미 데이터) 실제 앱에서는 이 데이터를 데이터베이스나 서버에서 가져와야 합니다.



        self.current_user = 'guest' # 로그인 아이디 저장

        self.current_user_nickname = 'Guest' # 표시용 닉네임 저장

        self.current_user_role = 'guest'

        


        self.user_token = None # Firebase 인증 토큰 (로그인 시 저장됨)

        self.current_user_uid = None # Firebase 고유 UID (로그인 시 저장됨)




        # --- ---


        self.notification_keywords = ['지갑'] # 알림 테스트용


    def build(self):
        global firebase, auth, db, storage 
        
        try:
            firebase = pyrebase.initialize_app(config)
            auth = firebase.auth()
            db = firebase.database()
            storage = firebase.storage() # 스토리지 객체 초기화
            print("Firebase 초기화 성공")
        except Exception as e:
            print(f"Firebase 초기화 실패: {e}")
        

        self.title = "Campus Link"

        sm = ScreenManager()

        # 화면 
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(MainScreen(name='main'))
        
        # 동아리 관련 화면들 
        sm.add_widget(ClubScreen(name='club'))
        sm.add_widget(ClubDetailScreen(name='club_detail'))
        sm.add_widget(ClubFreeBoardScreen(name='club_free_board'))
        sm.add_widget(ClubCreateScreen(name='club_create'))
        sm.add_widget(ClubApplicationScreen(name='club_apply'))
        sm.add_widget(ClubManagementScreen(name='club_management'))
        sm.add_widget(MemberApprovalScreen(name='member_approval'))
        sm.add_widget(MemberManagementScreen(name='member_management'))
        sm.add_widget(PostScreen(name='post_screen'))

        #분실물 관련 화면들
        sm.add_widget(LostAndFoundScreen(name='lost_found'))
        sm.add_widget(AddItemScreen(name='add_item'))
        sm.add_widget(ItemDetailScreen(name='item_detail'))

        # 관리자 화면 
        sm.add_widget(AdminMainScreen(name='admin_main'))
        sm.add_widget(ClubApprovalScreen(name='club_approval'))
        sm.add_widget(ItemApprovalScreen(name='item_approval'))
        sm.add_widget(AdminClaimApprovalScreen(name='admin_claim_approval'))

        # (finder용) 내 등록 물품 관리
        sm.add_widget(ClaimManagementScreen(name='claim_management'))

        # (claimer용) 내 신청 현황
        sm.add_widget(MyClaimsScreen(name='my_claims'))
        
        return sm





#--------------------------------------------------------

if __name__ == '__main__':

    # 앱 실행

    MyApp().run()