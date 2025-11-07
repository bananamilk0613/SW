import kivy
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
# 새 화면: 메인 화면 (로그인 성공 후 진입)
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
            self.manager.current = 'claim_management' # 새 화면으로 이동
            popup.dismiss()
        my_items_button.bind(on_press=go_to_my_items)
        content_layout.add_widget(my_items_button)

        # --- ▼▼▼ (신규) '내 신청 현황' 버튼 추가 ▼▼▼ ---
        my_claims_button = get_styled_button("내 신청 현황", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1], font_size='18sp')
        my_claims_button.height = dp(50)
        def go_to_my_claims(instance):
            self.manager.current = 'my_claims' # 새 화면으로 이동
            popup.dismiss()
        my_claims_button.bind(on_press=go_to_my_claims)
        content_layout.add_widget(my_claims_button)
        # --- ▲▲▲ (신규) ---

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
#  관리자 물품 신청(소유권) 관리
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
        back_button.bind(on_press=lambda *args: self.go_to_screen('admin_main')) # 관리자 메인으로
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
        self.grid.clear_widgets()
        app = App.get_running_app()

        
        # 1. 모든 신청(claims) 목록을 가져옵니다.
        all_claims = app.claims
        
        # 2. 'status'가 없는 (즉, 'pending' 상태인) 신청만 필터링합니다.
        pending_claims = [c for c in all_claims if 'status' not in c]
        

        if not pending_claims:
            self.grid.add_widget(Label(text="검토 대기 중인 신청이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        # 헬퍼 함수... (생략)
        def create_wrapping_label(text_content, **kwargs):
            label = Label(
                text=text_content, size_hint_y=None, font_name=FONT_NAME,
                markup=True, halign='left', **kwargs
            )
            label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            return label

        for claim in pending_claims:
            item_id = claim.get('item_id')
            
            # item_id를 이용해 원본 item 찾기
            item = next((i for i in app.all_items if i.get('item_id') == item_id), None)
            
            if not item:
                continue 
            
            # (1) 물품 기본 정보 표시
            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            item_box.bind(minimum_height=item_box.setter('height'))

            with item_box.canvas.before:
                Color(0.95, 0.95, 0.8, 1) # 연한 노란색 배경
                self.bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
            
            item_box.bind(
                pos=lambda instance, value: setattr(self.bg_rect, 'pos', value),
                size=lambda instance, value: setattr(self.bg_rect, 'size', value)
            )

            # (2) 물품 정보, 신청자 정보
            item_box.add_widget(create_wrapping_label(
                text_content=f"[b]물품명:[/b] {item['name']}", color=[0,0,0,1]
            ))
            item_box.add_widget(create_wrapping_label(
                text_content=f"[b]신청자:[/b] {claim.get('claimer_nickname', '알 수 없음')} ({claim.get('claimer_id')})", color=[0,0,0,1]
            ))
            
            item_box.add_widget(Label(size_hint_y=None, height=dp(10))) # 여백

            # (3) 교차 비교 UI
            
            item_box.add_widget(create_wrapping_label(
                text_content=f"[b]등록자(Finder)가 올린 정보:[/b]", color=[0.1, 0.4, 0.7, 1] # 파란색
            ))
            item_box.add_widget(create_wrapping_label(
                text_content=f"  - 장소: {item['loc']}", color=[0.1, 0.4, 0.7, 1]
            ))
            item_box.add_widget(create_wrapping_label(
                text_content=f"  - 상세: {item.get('desc', '없음')}", color=[0.1, 0.4, 0.7, 1]
            ))
            item_box.add_widget(Label(size_hint_y=None, height=dp(10))) # 여백

            # (3-2) 신청자가 입력한 검증 정보
            item_box.add_widget(create_wrapping_label(
                text_content=f"[b]신청자(Claimer)가 입력한 정보:[/b]", color=[0.8, 0.2, 0.2, 1] # 빨간색
            ))
            item_box.add_widget(create_wrapping_label(
                text_content=f"  - 장소: {claim.get('verification_location', 'N/A')}", color=[0.8, 0.2, 0.2, 1]
            ))
            item_box.add_widget(create_wrapping_label(
                text_content=f"  - 상세: {claim.get('verification_details', 'N/A')}", color=[0.8, 0.2, 0.2, 1]
            ))
            item_box.add_widget(Label(size_hint_y=None, height=dp(15))) # 버튼 전 여백

            # (4) 승인/거절 버튼 추가
            button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            
            approve_btn = Button(text="전달 완료 (승인)", font_name=FONT_NAME, background_color=[0.2, 0.8, 0.2, 1])
            approve_btn.item_id = item_id # item 객체 대신 id 전달
            approve_btn.claim = claim # claim 객체 전달
            approve_btn.bind(on_press=self.approve_claim) 
            
            reject_btn = Button(text="신청 거절", font_name=FONT_NAME, background_color=[0.8, 0.2, 0.2, 1])
            reject_btn.item_id = item_id # item 객체 대신 id 전달
            reject_btn.claim = claim # claim 객체 전달
            reject_btn.bind(on_press=self.reject_claim)
            
            button_layout.add_widget(approve_btn)
            button_layout.add_widget(reject_btn)
            
            item_box.add_widget(button_layout)
            
            self.grid.add_widget(item_box)
    

    # --- 연락처 공유' 로직 ---
    def approve_claim(self, instance):
        """(관리자) 신청을 승인 -> 신청(claim) 객체에 상태와 연락처를 기록합니다."""
        app = App.get_running_app()
        item_id = instance.item_id
        claim = instance.claim

        # 1. 원본 item 객체를 찾아 등록자(Finder)의 연락처를 확보합니다.
        item = next((i for i in app.all_items if i.get('item_id') == item_id), None)
        if not item:
            Popup(title='오류', content=Label(text='원본 아이템을 찾을 수 없습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        finder_contact = item.get('contact', '연락처 없음')
        
        # 2. 아이템 상태 변경
        item['status'] = 'found_returned'
        
        # 3. (중요) 신청(claim) 객체를 삭제하는 대신, '승인' 상태와 '연락처'를 추가합니다.
        claim['status'] = 'approved'
        claim['finder_contact'] = finder_contact
            
        # 4. 관리자에게 팝업 알림
        popup_message = f"승인이 완료되었습니다.\n\n" \
                        f"'{claim.get('claimer_nickname')}' 님에게\n" \
                        f"등록자 연락처 ({finder_contact})가 공유됩니다."
                        
        popup = Popup(title='[b]승인 완료[/b]',
                      title_font=FONT_NAME,
                      content=Label(text=popup_message, font_name=FONT_NAME, markup=True, padding=dp(10)),
                      size_hint=(0.9, 0.4))
        
        # 5. 팝업이 닫힌 '후에' 목록을 새로고침합니다.
        popup.bind(on_dismiss=self.refresh_list)
        popup.open()

    # --- 신청 거절' 로직 ---
    def reject_claim(self, instance):
        """(관리자) 신청을 거절 -> 신청(claim) 객체에 '거절' 상태를 기록합니다."""
        app = App.get_running_app()
        item_id = instance.item_id
        claim = instance.claim

        # 1. 아이템 상태를 'found_available'(신청 가능)으로 복구
        for item in app.all_items:
            if item.get('item_id') == item_id:
                item['status'] = 'found_available'
                break
        
        # 2. (중요) 신청(claim) 객체를 삭제하는 대신, '거절' 상태를 추가합니다.
        claim['status'] = 'rejected'
            
        # 3. 목록 새로고침
        self.refresh_list()
   

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
                
                # '시간' 정보도 표시 (선택 사항)
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
        # '시간' 정보도 알림 검색 대상에 포함
        item_text = f"{new_item['name']} {new_item['desc']} {new_item['loc']} {new_item.get('time', '')}".lower()
        for keyword in app.notification_keywords:
            if keyword.lower() in item_text:
                Popup(title='키워드 알림',
                        content=Label(text=f"등록하신 키워드 '{keyword}'가 포함된\n'{new_item['name']}' 게시물이 등록되었습니다.", font_name=FONT_NAME),
                        size_hint=(0.8, 0.4)).open()
                break # 여러 키워드에 해당되더라도 한번만 알림

# --------------------------------------------------------
# 새 화면: 분실물 신청 관리 (교차 검증)
# --------------------------------------------------------
class ClaimManagementScreen(WhiteBgScreen):
    """(수정) 내가 등록한 분실/습득물의 '상태'를 확인하는 화면"""
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
        header.add_widget(Label(text="[b]내 등록 물품 관리[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
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
        self.grid.clear_widgets()
        app = App.get_running_app()

        # 내가 등록한 아이템만 필터링
        my_items = [item for item in app.all_items if item.get('registered_by_id') == app.current_user]

        if not my_items:
            self.grid.add_widget(Label(text="내가 등록한 물품이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        # 헬퍼 함수: 자동 줄바꿈 및 높이 조절 라벨 생성
        def create_wrapping_label(text_content, **kwargs):
            label = Label(
                text=text_content,
                size_hint_y=None, # <- 높이를 텍스트에 맞춤
                font_name=FONT_NAME,
                markup=True,
                halign='left',
                **kwargs
            )
            label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            return label

        for item in my_items:
            item_id = item.get('item_id')
            
            # (1) 물품 기본 정보 표시
            item_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5))
            # (중요) item_box의 높이가 자식들의 높이 합(minimum_height)에 맞춰지도록 바인딩
            item_box.bind(minimum_height=item_box.setter('height')) 

            with item_box.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                self.bg_rect = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[dp(5)])
            
            # (중요) 배경 사각형도 item_box의 위치/크기에 맞춰 업데이트되도록 바인딩
            item_box.bind(
                pos=lambda instance, value: setattr(self.bg_rect, 'pos', value),
                size=lambda instance, value: setattr(self.bg_rect, 'size', value)
            )

            # (수정) 헬퍼 함수 사용
            item_box.add_widget(create_wrapping_label(
                text_content=f"[b]{item['name']}[/b]", 
                color=[0,0,0,1]
            ))
            
            status_text = ""
            
            # (2) 상태에 따른 분기
            if item['status'] == 'found_pending':
                claim = next((c for c in app.claims if c['item_id'] == item_id), None)
                if claim:
                    status_text = f"[color=A01010]관리자 검토 중[/color]\n신청자: {claim.get('claimer_nickname', '알 수 없음')}"
                    item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0,0,0,1]))
                else:
                    item['status'] = 'found_available' # 상태 복구
                    status_text = "[color=1010A0]신청 가능[/color]"
                    item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0,0,0,1]))
            
            elif item['status'] == 'found_available':
                status_text = "[color=1010A0]신청 가능[/color] (대기중인 신청 없음)"
                item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0.3,0.3,0.3,1]))
            
            elif item['status'] == 'found_returned':
                status_text = "전달 완료"
                item_box.add_widget(create_wrapping_label(text_content=status_text, color=[0.5,0.5,0.5,1]))

            elif item['status'] == 'lost':
                status_text = "내가 등록한 분실물"
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
            Popup(title='오류', content=Label(text='모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return

        app = App.get_running_app()
        new_club_request = {
            'name': name,
            'short_desc': s_desc,
            'long_desc': l_desc,
            'president': app.current_user, # 아이디를 회장으로 등록
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

        popup = Popup(title='알림', content=Label(text='동아리 개설 신청이 완료되었습니다.\n관리자 승인 후 등록됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
        popup.bind(on_dismiss=lambda *args: self.go_to_screen('club'))
        popup.open()


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
        application_data = {
            'user': app.current_user, # 신청자 '아이디'
            'user_nickname': app.current_user_nickname, # 신청자 '닉네임' (표시용)
            'intro': self.intro.text
        }

        # 해당 동아리의 applications 리스트에 신청 정보 추가
        for club in app.all_clubs:
            if club['name'] == self.club_data['name']:
                # 중복 신청 방지 (아이디 기준)
                if any(app_data['user'] == app.current_user for app_data in club['applications']):
                    Popup(title='알림', content=Label(text='이미 가입을 신청했습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
                    return

                club['applications'].append(application_data)
                break

        popup = Popup(title='신청 완료', content=Label(text='가입 신청이 완료되었습니다.\n회장 승인 후 가입됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
        popup.bind(on_dismiss=lambda *args: self.go_to_screen('club_detail'))
        popup.open()


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
                    
                    # 닉네임이 있으면 닉네임(아이디) 형식, 없으면 아이디만 표시
                    user_display = app_data.get('user_nickname', app_data['user'])
                    if 'user_nickname' in app_data:
                         user_display = f"{app_data['user_nickname']} ({app_data['user']})"
                    
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

    def approve_member(self, instance):
        app_data = instance.app_data
        self.club_data['members'].append(app_data['user']) # 아이디를 멤버로 추가
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
            Popup(title='오류', content=Label(text='내용을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return
            
        # 후기 작성 시 닉네임 정보 포함
        if self.post_type == 'review':
            app = App.get_running_app()
            content = f"({app.current_user_nickname}님) {content}"


        key_map = {
            'announcement': 'announcements',
            'activity': 'activities',
            'review': 'reviews'
        }
        data_key = key_map.get(self.post_type)
        if self.club_data and data_key:
            self.club_data[data_key].append(content)
            popup = Popup(title='성공', content=Label(text='등록이 완료되었습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
            popup.bind(on_dismiss=lambda *args: self.go_to_screen('club_detail'))
            popup.open()
        else:
            Popup(title='오류', content=Label(text='데이터 저장에 실패했습니다.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()

    def go_to_screen(self, screen_name):
        # 상세 화면으로 돌아갈 때 데이터가 갱신되도록 club_data를 다시 전달
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
# 새 화면: 분실물 등록 페이지 (AddItemScreen)
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
        
        # --- '시간' 입력 필드 추가 ---
        self.time_input = get_rounded_textinput('발견/분실 시간 (예: 14:30)')
        
        self.contact_input = get_rounded_textinput('연락처 (예: 010-1234-5678)')

        self.category_spinner = Spinner(
            text='카테고리 선택 (종류)',
            values=('전자기기', '서적', '의류', '지갑/카드', '기타'),
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(55),
            background_normal='',             # (스타일 수정) 스피너 버튼 자체 배경 흰색으로
            background_color=[1, 1, 1, 1],  # (스타일 수정)
            color=[0, 0, 0, 1]                # (스타일 수정) 스피너 버튼 텍스트 검은색으로
        )
        
        # 2. (핵심) 생성된 객체에 'option_cls_args' 속성을 별도로 설정합니다.
        self.category_spinner.option_cls_args = {
            'font_name': FONT_NAME,           # (1. 폰트 깨짐 해결)
            'background_normal': '',        # (2. 스타일 해결)
            'background_color': [1, 1, 1, 1], # (2. 흰색 배경)
            'color': [0, 0, 0, 1],            # (2. 검은색 텍스트)
            'height': dp(50)                  # (2. 옵션 높이 조절)
        }

        content_layout.add_widget(self.name_input)
        content_layout.add_widget(self.desc_input)
        content_layout.add_widget(self.loc_input)
        
        # --- '시간' 필드를 레이아웃에 추가 ---
        content_layout.add_widget(self.time_input)
        
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
        
        # --- '시간' 필드 초기화 추가 ---
        self.time_input.text = ""
        
        self.contact_input.text = ""
        self.image_path = ""
        self.photo_label.text = "사진이 선택되지 않았습니다."
        self.image_preview.source = DEFAULT_IMAGE
        self.category_spinner.text = '카테고리 선택 (종류)'

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
        
        # --- '시간' 값 가져오기 ---
        time_val = self.time_input.text # 변수명 변경 (time 모듈과 충돌 방지)
        
        contact = self.contact_input.text
        category = self.category_spinner.text

        # --- '시간'을 필수 항목으로 유효성 검사 추가 ---
        if not name or not loc or not time_val or not contact or category == '카테고리 선택 (종류)':
            Popup(title='오류', content=Label(text='사진을 제외한 모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        # ---  사진 필수 검사 비활성화  ---
        # 습득물인 경우 사진 필수 (플로우차트 일치)
        # if not self.is_lost and not self.image_path:
        #     Popup(title='오류', content=Label(text='습득물은 사진을 반드시 첨부해야 합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
        #     return
        # --- 주석 처리 ---

        # 이미지 경로가 없으면 기본 이미지 사용
        # (사진을 안 올리면 image 변수에 빈 문자열("")이 들어가게 됩니다)
        image = self.image_path if self.image_path else "" 
        
        app = App.get_running_app()

        
        # 고유 ID 생성 (간단하게 현재 시간 사용)
        item_id = f"item_{int(time.time())}_{app.current_user}"
        
        # 상태(status) 설정
        if self.is_lost:
            status = 'lost' # 내가 잃어버림
        else:
            status = 'found_available' # 내가 주웠고, 주인을 찾는 중

        new_item = {
            'item_id': item_id, # <-- 고유 ID 추가
            'name': name, 'desc': desc, 'loc': loc, 'time': time_val, 'contact': contact, # time_val 사용
            'image': image, # <-- 사진을 안 올렸으면 "" (빈 문자열)이 저장됨
            'category': category,
            'status': status, # <-- 'lost' 또는 'found_available'로 수정
            'registered_by_id': app.current_user, # 등록자 아이디
            'registered_by_nickname': app.current_user_nickname # 등록자 닉네임
        }

        # App의 pending_items 리스트에 새 아이템 추가
        app.pending_items.append(new_item)

        popup = Popup(title='알림', content=Label(text='등록 신청이 완료되었습니다.\n관리자 승인 후 게시됩니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
        popup.bind(on_dismiss=lambda *args: self.go_to_screen('lost_found'))
        popup.open()


# --------------------------------------------------------
# 새 화면: 분실물 상세 정보 페이지 (ItemDetailScreen)
# --------------------------------------------------------
class ItemDetailScreen(WhiteBgScreen):
    item_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 메인 레이아웃을 RelativeLayout으로 변경 (하단 고정 버튼을 위함)
        self.main_layout = RelativeLayout()
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        """화면에 들어올 때마다 위젯을 다시 그림"""
        self.main_layout.clear_widgets()

        if not self.item_data:
            return

        app = App.get_running_app()
        
        # --- 1. 하단 고정 바 (상태에 따라 다르게 표시) ---
        # (이 부분은 수정되지 않았습니다. 기존과 동일)
        bottom_bar = BoxLayout(
            size_hint=(1, None), height=dp(80), 
            pos_hint={'bottom': 0}, padding=dp(10), spacing=dp(10)
        )
        with bottom_bar.canvas.before:
            Color(0.95, 0.95, 0.95, 1) # 연한 회색 배경
            self.bottom_rect = Rectangle(size=bottom_bar.size, pos=bottom_bar.pos)
        bottom_bar.bind(size=self._update_rect_cb(self.bottom_rect), 
                        pos=self._update_rect_cb(self.bottom_rect))
        
        is_my_post = self.item_data.get('registered_by_id') == app.current_user
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
            contact_text = f"연락처: {self.item_data['contact']}"
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

        
        # --- 2. 메인 컨텐츠 영역 (하단 바 위) ---
        main_content_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=[0, 0, 0, dp(80)] 
        )

        # 상단 헤더 (뒤로가기 버튼 + 제목)
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

        # --- 3. 스크롤 가능한 컨텐츠 ---
        scroll_view = ScrollView(size_hint=(1, 1))
        
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15), padding=dp(10))
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        # 3-1. 이미지
        image = Image(
            source=self.item_data.get('image') if self.item_data.get('image') else DEFAULT_IMAGE,
            size_hint_y=None,
            height=dp(300),
            fit_mode='contain'
        )
        scroll_content.add_widget(image)

        # 3-2. 등록자 정보
        registrant_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), padding=[dp(10), 0])
        registrant = self.item_data.get('registered_by_nickname', self.item_data.get('registered_by_id', '알 수 없음'))
        
        profile_icon = Image(
            source=DEFAULT_IMAGE, 
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        registrant_box.add_widget(profile_icon)
        registrant_box.add_widget(Label(size_hint_x=None, width=dp(10))) # 여백
        
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

        # 3-4. 상세 정보 섹션
        info_section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8), padding=[dp(10), dp(15)])
        info_section.bind(minimum_height=info_section.setter('height'))

        # 물품명
        item_name_label = Label(
            text=f"[b]{self.item_data['name']}[/b]",
            font_name=FONT_NAME, color=[0,0,0,1], markup=True,
            font_size='24sp', size_hint_y=None, halign='left'
        )
        item_name_label.bind(width=lambda *x: item_name_label.setter('text_size')(item_name_label, (item_name_label.width, None)),
                                texture_size=lambda *x: item_name_label.setter('height')(item_name_label, item_name_label.texture_size[1]))
        info_section.add_widget(item_name_label)

        # 상태 및 카테고리
        status_color = "[color=A01010]" if self.item_data['status'] == 'lost' else "[color=1010A0]"
        status_display_text = "분실" if self.item_data['status'] == 'lost' else "습득"
        category_label = Label(
            text=f"{status_color}[b]{status_display_text}[/b][/color] · {self.item_data.get('category', '기타')}",
            font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True,
            font_size='16sp', size_hint_y=None, height=dp(25), halign='left'
        )
        category_label.bind(size=category_label.setter('text_size'))
        info_section.add_widget(category_label)

    
        # 시간 (한 줄에 표시)
        time_label = Label(
            # text=f"장소: {self.item_data['loc']}  ·  시간: {self.item_data.get('time', 'N/A')}", (이전 코드)
            text=f"시간: {self.item_data.get('time', 'N/A')}", # (수정된 코드)
            font_name=FONT_NAME, color=[0.3,0.3,0.3,1],
            font_size='16sp', size_hint_y=None, height=dp(25), halign='left'
        )
        time_label.bind(size=time_label.setter('text_size'))
        info_section.add_widget(time_label)

        # 스크롤 뷰에 컨텐츠 추가
        scroll_content.add_widget(info_section)
        scroll_view.add_widget(scroll_content)
        
        # 메인 컨테이너에 스크롤 뷰 추가
        main_content_container.add_widget(scroll_view)
        
        # --- 4. 최종 조립 ---
        self.main_layout.add_widget(main_content_container)
        self.main_layout.add_widget(bottom_bar)

    def show_claim_verification_popup(self, instance):
        """'이 물건 주인입니다' 클릭 시 교차 검증 팝업을 띄웁니다."""
        app = App.get_running_app()
        item_id = self.item_data.get('item_id')

        # 이미 이 물건에 대해 내가 신청한 내역이 있는지 확인
        if any(c['item_id'] == item_id and c['claimer_id'] == app.current_user for c in app.claims):
            Popup(title='알림', content=Label(text='이미 신청한 물품입니다.\n관리자가 검토 중입니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return
            
        # 팝업 컨텐츠
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        popup_content.add_widget(Label(
            text="[b]물품 주인 확인[/b]\n\n관리자가 확인할 수 있도록\n본인 소유임을 증명할 수 있는 정보를 입력해주세요.",
            font_name=FONT_NAME, markup=True, halign='center'
        ))
        
        # 1. 상세 특징 입력
        detail_input = TextInput(
            hint_text='물품의 상세 특징 (예: 케이스 색상, 스티커 등)', 
            font_name=FONT_NAME, multiline=True, size_hint_y=None, height=dp(100)
        )
        
        # 2. 분실 장소/시간 입력
        loc_input = TextInput(
            hint_text='잃어버린 장소 및 시간 (예: 제1공학관 3층, 어제 오후 2시경)', 
            font_name=FONT_NAME, multiline=True, size_hint_y=None, height=dp(100)
        )
        
        popup_content.add_widget(detail_input)
        popup_content.add_widget(loc_input)
        
        # 3. 신청 버튼
        submit_button = get_styled_button("신청서 제출", [0.8, 0.2, 0.2, 1], [1, 1, 1, 1])
        
        popup = Popup(
            title="소유권 주장 신청",
            title_font=FONT_NAME,
            content=popup_content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )
        
        # 신청 버튼에 콜백 함수 바인딩
        submit_button.bind(on_press=lambda *args: self.submit_verification_claim(
            popup, item_id, detail_input.text, loc_input.text
        ))
        
        popup_content.add_widget(submit_button)
        
        # 4. 닫기 버튼
        close_button = Button(text="취소", font_name=FONT_NAME, size_hint_y=None, height=dp(40))
        close_button.bind(on_press=popup.dismiss)
        popup_content.add_widget(close_button)

        popup.open()

    def submit_verification_claim(self, popup_to_dismiss, item_id, details, location):
        """팝업에서 '신청서 제출' 버튼 클릭 시 호출됩니다."""
        
        if not details or not location:
            Popup(title='오류', content=Label(text='두 항목 모두 입력해야 합니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()
            return

        app = App.get_running_app()

        # 1. 아이템 상태를 'found_pending'으로 변경
        for item in app.all_items:
            if item.get('item_id') == item_id:
                item['status'] = 'found_pending'
                break
                
        # 2. '신청(claim)' 객체 생성 (검증 정보 포함)
        new_claim = {
            'item_id': item_id,
            'claimer_id': app.current_user,
            'claimer_nickname': app.current_user_nickname,
            'verification_details': details,     # <-- 검증 정보 1 추가
            'verification_location': location  # <-- 검증 정보 2 추가
        }
        app.claims.append(new_claim)
        
        # 3. 팝업 닫기
        popup_to_dismiss.dismiss()
        
        # 4. 팝업 알림 후 목록으로 이동
        success_popup = Popup(title='신청 완료', content=Label(text='관리자에게 신청서가 전달되었습니다.\n검토 후 연락이 갈 것입니다.', font_name=FONT_NAME), size_hint=(0.8, 0.4))
        success_popup.bind(on_dismiss=lambda *args: self.go_to_screen('lost_found'))
        success_popup.open()

    def _update_rect_cb(self, rect):
        """하단 바 배경 업데이트를 위한 콜백 함수"""
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

        # 내가 신청한(claimer_id) 모든 'claims' 필터링
        my_claims = [c for c in app.claims if c['claimer_id'] == app.current_user]

        if not my_claims:
            self.grid.add_widget(Label(text="신청한 내역이 없습니다.", font_name=FONT_NAME, color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height=dp(100)))
            return

        for claim in my_claims:
            item_id = claim.get('item_id')
            
            # 아이템 원본 정보를 찾아 물품명 획득
            item = next((i for i in app.all_items if i.get('item_id') == item_id), None)
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

            # 1. 물품명 표시
            item_box.add_widget(self.create_wrapping_label(
                text_content=f"[b]물품명: {item_name}[/b]", 
                color=[0,0,0,1]
            ))
            
            item_box.add_widget(Label(size_hint_y=None, height=dp(5))) # 여백

            # 2. 신청 상태(status)에 따라 분기
            claim_status = claim.get('status')
            
            if claim_status == 'approved':
                # (핵심) 승인됨 -> 연락처 표시
                contact_info = claim.get('finder_contact', '연락처 정보 없음')
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=008000][b]승인 완료[/b][/color]\n" \
                                 f"등록자 연락처: [b]{contact_info}[/b]\n" \
                                 "(등록자에게 연락하여 물품을 수령하세요)", 
                    color=[0.2, 0.2, 0.2, 1]
                ))
                
            elif claim_status == 'rejected':
                # 거절됨
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=A01010][b]신청 거절[/b][/color]\n" \
                                 "(관리자가 신청을 거절했습니다)", 
                    color=[0.2, 0.2, 0.2, 1]
                ))
            
            else:
                # 'status' 필드가 없음 -> 'pending' (검토 중)
                item_box.add_widget(self.create_wrapping_label(
                    text_content="[color=F08000][b]관리자 검토 중[/b][/color]\n" \
                                 "(관리자가 신청 내역을 확인하고 있습니다)", 
                    color=[0.2, 0.2, 0.2, 1]
                ))
            
            self.grid.add_widget(item_box)

# --------------------------------------------------------
# 새 화면: 분실물 페이지 (LostAndFoundScreen)
# --------------------------------------------------------
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

        # 검색 및 필터링 UI (플로우차트 일치)
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
            background_normal='',             # (스타일 수정) 스피너 버튼 자체 배경 흰색으로
            background_color=[1, 1, 1, 1],  # (스타일 수정)
            color=[0, 0, 0, 1]                # (스타일 수정) 스피너 버튼 텍스트 검은색으로
        )
        
        # 2. (핵심) 생성된 객체에 'option_cls_args' 속성을 별도로 설정합니다.
        self.category_spinner.option_cls_args = {
            'font_name': FONT_NAME,           # (1. 폰트 깨짐 해결)
            'background_normal': '',        # (2. 스타일 해결)
            'background_color': [1, 1, 1, 1], # (2. 흰색 배경)
            'color': [0, 0, 0, 1],            # (2. 검은색 텍스트)
            'height': dp(50)                  # (2. 옵션 높이 조절)
        }
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

        # 알림 키워드 등록 UI (플로우차트 일치)
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

        popup = Popup(
            title='등록 종류 선택',
            title_font=FONT_NAME,
            content=popup_content,
            size_hint=(0.8, 0.4)
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

        
        
        # 1. '분실(lost)' 또는 '신청 가능(found_available)' 상태인 아이템만 기본 목록으로 함
        base_list = [
            item for item in app.all_items 
            if item.get('status') == 'lost' or item.get('status') == 'found_available'
        ]
        
        filtered_list = base_list
        

        # 카테고리 필터링
        if category != '전체':
            filtered_list = [item for item in filtered_list if item.get('category') == category]

        # 키워드 필터링
        if keyword:
            filtered_list = [
                item for item in filtered_list
                if keyword in item['name'].lower() 
                or keyword in item.get('desc', '').lower()
                or keyword in item.get('loc', '').lower() # 장소도 검색
            ]

        self.update_item_list(filtered_list)

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
                # --- 목록 아이템 높이 120dp로 증가 ---
                item_layout = LostItemListItem(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(120),
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
                
                # (수정) 습득물 중에서도 'found_available'만 목록에 보이므로, 'found'로 표시해도 무방.
                # 'lost'는 '분실'로 표시됩니다.
                if item_data['status'] == 'lost':
                    status_text = "[b][color=A01010]분실[/color][/b]"
                else: 
                    # item_data['status'] == 'found_available'
                    status_text = "[b][color=1010A0]습득[/color][/b]"
                
                name_label = Label(
                    text=f"{status_text} {item_data['name']}", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(25)
                )
                loc_label = Label(
                    text=f"[b]장소:[/b] {item_data['loc']}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )
                
                # --- '시간' 라벨 추가 ---
                time_label = Label(
                    text=f"[b]시간:[/b] {item_data.get('time', 'N/A')}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )

                text_layout.add_widget(name_label)
                text_layout.add_widget(loc_label)
                
                # --- '시간' 라벨을 text_layout에 추가 ---
                text_layout.add_widget(time_label)

                # --- time_label도 바인딩 대상에 포함 ---
                for label in [name_label, loc_label, time_label]:
                    label.bind(size=label.setter('text_size'))

                item_layout.add_widget(text_layout)
                self.items_grid.add_widget(item_layout)

    def view_item_details(self, instance):
        """ 분실물 상세 정보 화면으로 이동 """
        detail_screen = self.manager.get_screen('item_detail')
        detail_screen.item_data = instance.item_data
        self.go_to_screen('item_detail')

# --------------------------------------------------------
# 새 화면: 회원가입 페이지 (2단계)
# --------------------------------------------------------
class SignupScreen(WhiteBgScreen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.current_step = 'step1'

        # Step 1과 Step 2 컨텐츠를 담을 메인 컨테이너
        self.main_container = BoxLayout(
            orientation='vertical',
            padding=[dp(50), dp(80), dp(50), dp(80)],
            spacing=dp(18)
        )
        self.add_widget(self.main_container)

        self.setup_step1()
        self.setup_step2()
        self.update_view() # 초기 화면은 Step 1

    def setup_step1(self):
        """회원가입 1단계 (기본 정보) 레이아웃 설정"""
        self.step1_layout = BoxLayout(orientation='vertical', spacing=dp(15))

        self.step1_layout.add_widget(Label(
            text="[b]Campus Link 회원가입 (1/2)[/b]",
            font_size='32sp',
            font_name=FONT_NAME,
            color=[0.1, 0.4, 0.7, 1],
            markup=True,
            size_hint_y=None,
            height=dp(60)
        ))
        self.step1_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        # 입력 필드: 학번, 이름, 학과, 학년, 간편 인증
        self.student_id_input = get_rounded_textinput('학번 (예: 20240001)', input_type='number')
        self.name_input = get_rounded_textinput('이름')
        self.department_input = get_rounded_textinput('학과')
        self.grade_input = get_rounded_textinput('학년 (예: 3)', input_type='number')

        # 간편 인증 필드 (더미)
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

        # 다음 버튼 (1/2)
        next_button = get_styled_button(
            "다음 (1/2)",
            [0.2, 0.6, 1, 1],
            [1, 1, 1, 1]
        )
        next_button.bind(on_press=self.go_to_step2)
        self.step1_layout.add_widget(next_button)

        # 취소 버튼
        cancel_button = get_styled_button(
            "취소 (로그인 화면으로)",
            [0.5, 0.5, 0.5, 1],
            [1, 1, 1, 1],
            font_size='18sp'
        )
        cancel_button.height = dp(50)
        cancel_button.bind(on_press=self.go_to_login)
        self.step1_layout.add_widget(cancel_button)

        self.step1_layout.add_widget(Label()) # 스페이서

    def setup_step2(self):
        """회원가입 2단계 (계정 정보) 레이아웃 설정"""
        self.step2_layout = BoxLayout(orientation='vertical', spacing=dp(15))

        self.step2_layout.add_widget(Label(
            text="[b]Campus Link 회원가입 (2/2)[/b]",
            font_size='32sp',
            font_name=FONT_NAME,
            color=[0.1, 0.4, 0.7, 1],
            markup=True,
            size_hint_y=None,
            height=dp(60)
        ))
        self.step2_layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        # --- '아이디' / '닉네임' 분리 ---
        # 입력 필드: 이메일, 아이디(신규), 닉네임, 비밀번호, 비밀번호 확인
        self.email_input = get_rounded_textinput('이메일 주소', input_type='mail')
        self.login_id_input = get_rounded_textinput('아이디 (로그인용)') # 새로 추가
        self.nickname_input = get_rounded_textinput('닉네임 (표시용)') # 힌트 텍스트 변경
        self.password_input = get_rounded_textinput('비밀번호 (최소 4자)', password=True)
        self.confirm_password_input = get_rounded_textinput('비밀번호 확인', password=True)

        self.step2_layout.add_widget(self.email_input)
        self.step2_layout.add_widget(self.login_id_input) # 레이아웃에 추가
        self.step2_layout.add_widget(self.nickname_input)
        self.step2_layout.add_widget(self.password_input)
        self.step2_layout.add_widget(self.confirm_password_input)
        # --- ---

        # 최종 회원가입 버튼
        signup_button = get_styled_button(
            "회원가입 완료",
            [0.2, 0.6, 1, 1],
            [1, 1, 1, 1]
        )
        signup_button.bind(on_press=self.do_signup)
        self.step2_layout.add_widget(signup_button)

        # 이전 버튼
        prev_button = get_styled_button(
            "이전",
            [0.5, 0.5, 0.5, 1],
            [1, 1, 1, 1],
            font_size='18sp'
        )
        prev_button.height = dp(50)
        prev_button.bind(on_press=self.go_to_step1)
        self.step2_layout.add_widget(prev_button)

        self.step2_layout.add_widget(Label()) # 스페이서

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
        self.simple_auth_input.text = ''

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
        # --- '아이디' / '닉네임' 분리 ---
        email = self.email_input.text
        login_id = self.login_id_input.text # 값 가져오기
        nickname = self.nickname_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        app = App.get_running_app()

        # 2단계 유효성 검사
        if not email or not login_id or not nickname or not password or not confirm_password:
            self.show_popup("오류", "모든 계정 정보를 채워주세요.")
        elif login_id in app.users: # Key를 login_id로 검사
            self.show_popup("오류", "이미 사용 중인 아이디입니다.")
        elif password != confirm_password:
            self.show_popup("오류", "비밀번호가 일치하지 않습니다.")
        elif len(password) < 4:
            self.show_popup("오류", "비밀번호는 최소 4자 이상이어야 합니다.")
        else:
            # 회원가입 성공 처리
            # 닉네임 정보까지 포함하여 저장
            app.users[login_id] = {'password': password, 'role': 'user', 'nickname': nickname} 
            self.show_popup("성공", f"아이디 '{login_id}'님의 회원가입이 완료되었습니다!\n로그인 해주세요.", after_dismiss_callback=self.go_to_login)
        # --- ---

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

        # --- '아이디'로 수정 ---
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
        username = self.username_input.text # 'username'은 이제 '아이디'입니다.
        password = self.password_input.text
        app = App.get_running_app()

        # 사용자 DB에서 정보 확인
        if username in app.users and app.users[username]['password'] == password:
            user_data = app.users[username]
            
            # --- '아이디' / '닉네임' 분리 ---
            app.current_user = username # 아이디 저장
            app.current_user_nickname = user_data['nickname'] # 닉네임 저장
            app.current_user_role = user_data['role'] # 역할 저장
            # --- ---

            self.manager.current = 'main'
        else:
            title = "로그인 실패"
            message = "아이디 또는 비밀번호를 다시 확인하세요." # 메시지 수정
            self.show_popup(title, message, show_retry_button=True)


class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # (더미 데이터) 실제 앱에서는 이 데이터를 데이터베이스나 서버에서 가져와야 합니다.
        # --- '아이디' / '닉네임' 분리 및 속성 추가 ---
        self.users = {
            # '아이디': {'password': '비밀번호', 'role': '역할', 'nickname': '닉네임'}
            'admin': {'password': 'admin1234', 'role': 'admin', 'nickname': '관리자'},
            'user': {'password': '1234', 'role': 'user', 'nickname': '테스트유저'},
            'member': {'password': 'member123', 'role': 'user', 'nickname': '테스트멤버'}
        }
        self.current_user = 'guest' # 로그인 아이디 저장
        self.current_user_nickname = 'Guest' # 표시용 닉네임 저장
        self.current_user_role = 'guest'
        # --- ---

        self.all_clubs = [
            {'name': '축구 동아리 KickOff', 'short_desc': '축구를 사랑하는 사람들의 모임입니다.', 'long_desc': '매주 수요일 오후 4시에 대운동장에서 정기적으로 활동합니다. 축구를 좋아하거나 배우고 싶은 모든 학생을 환영합니다!', 
             'president': 'user', 'members': ['user', 'member'], 
             'applications': [{'user':'test_user_id', 'user_nickname': '신청자닉네임', 'intro':'열심히 하겠습니다!'}], 
             'announcements': ["이번 주 활동은 쉽니다."], 'activities': ["지난 주 친선 경기 진행"], 'reviews': ["(테스트멤버님) 분위기 좋아요!"]},
            {'name': '코딩 스터디 CodeHive', 'short_desc': '파이썬, 자바 등 함께 공부하는 코딩 모임', 'long_desc': '알고리즘 스터디와 프로젝트 개발을 함께 진행합니다. 초보자도 대환영!', 
             'president': 'admin', 'members': ['admin'], 'applications': [], 'announcements': [], 'activities': [], 'reviews': []},
        ]
        self.pending_clubs = []

        # --- ▼▼▼ 분실물 데이터 구조 변경 (검증 정보 반영) ▼▼▼ ---
        
        self.all_items = [
             {
                'item_id': 'item_1', 'name': '검은색 에어팟 프로', 'desc': '케이스에 스티커 붙어있음', 
                'loc': '중앙도서관 1층', 'time': '13:00', 'contact': '010-1111-2222',
                'image': '', 'category': '전자기기', 
                'status': 'lost', 
                'registered_by_id': 'user', 'registered_by_nickname': '테스트유저'
             },
             {
                'item_id': 'item_2', 'name': '파란색 학생증', 'desc': '컴퓨터공학과 2학년', 
                'loc': '제1공학관 3층', 'time': '09:10', 'contact': '010-3333-4444',
                'image': '', 'category': '지갑/카드', 
                'status': 'found_pending', # (claims 더미 데이터와 맞춤)
                'registered_by_id': 'member', 'registered_by_nickname': '테스트멤버'
             },
             {
                'item_id': 'item_4_returned', 'name': '갈색 장지갑', 'desc': '신분증 있음', 
                'loc': '학생회관 식당', 'time': '12:30', 'contact': '학생회관 분실물 센터',
                'image': '', 'category': '지갑/카드', 
                'status': 'found_returned', 
                'registered_by_id': 'admin', 'registered_by_nickname': '관리자'
             }
        ]
        self.pending_items = [
            {
                'item_id': 'item_3_pending', 'name': '주인을 찾습니다(아이패드)', 'desc': '실버 색상, 펜슬 포함', 
                'loc': '중앙도서관 2층', 'time': '15:00', 'contact': '010-5555-6666',
                'image': '', 'category': '전자기기', 
                'status': 'found_available', # (승인 대기중일때도 기본 상태는 found_available)
                'registered_by_id': 'user', 'registered_by_nickname': '테스트유저'
            }
        ]
        self.notification_keywords = ['지갑'] # 알림 테스트용
        
        # --- ▼▼▼ (수정) claims 더미 데이터 (관리자 승인 전 상태) ▼▼▼ ---
        self.claims = [
            {'item_id': 'item_2', 
             'claimer_id': 'user', 
             'claimer_nickname': '테스트유저',
             'verification_details': '파란색 학생증 케이스 뒷면에 노란색 스마일 스티커가 붙어있습니다.',
             'verification_location': '제1공학관 3층 302호 강의실에서 잃어버린 것 같습니다.'
            }
        ]
        # --- ▲▲▲ (수정) ▲▲▲ ---


    def build(self):
        self.title = "Campus Link"

        sm = ScreenManager()

        # 화면 추가
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(MainScreen(name='main'))
        
        # 동아리 관련 화면들 추가
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

        # 관리자 화면 추가
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
# 백엔드 연동 준비 코드 
#--------------------------------------------------------
import requests
import json
#  사용자님의 로컬 IP 주소로 API 서버 주소를 설정합니다.
BASE_URL = 'http://192.168.56.1:8000' 
LOGIN_URL = f'{BASE_URL}/auth/login/' 
def handle_login(username, password):
    # 1. Django 서버가 기대하는 형식의 데이터 (JSON)를 준비합니다.     
    payload = {
        'username': username,
        'password': password
    }    
    try:
        # 2. POST 요청을 서버로 보냅니다.
        response = requests.post(LOGIN_URL, json=payload)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        # 3. 서버 응답을 JSON 형식으로 변환합니다.
        data = response.json()
        auth_token = data.get('token')
        user_id = data.get('user_id')
        # 4. 로그인 성공! 토큰을 앱에 저장합니다.
        # 이 토큰은 앞으로 모든 로그인 필요 API 호출에 사용됩니다.
        print(f"로그인 성공! 유저 ID: {user_id}, 토큰: {auth_token}")
        return auth_token
    except requests.exceptions.RequestException as e:
        print(f"로그인 실패: {e}")
        return None
    
#  로그인 성공 후 얻은 토큰
AUTH_TOKEN = "로그인 성공 시 반환된 토큰 값"
#  API URL
POSTS_URL = 'http://192.168.56.1:8000/api/clubposts/'
def get_club_posts():
 # 1. 헤더에 토큰을 포함시킵니다.
 headers = {
 'Authorization': f'Token {AUTH_TOKEN}'
 }
 try:
        # 2. GET 요청을 보냅니다.
        response = requests.get(POSTS_URL, headers=headers)
        response.raise_for_status()
        # 3. 게시물 목록을 JSON 형식으로 받습니다.
        posts = response.json()
        print("게시물 목록:", posts)
        return posts

 except requests.exceptions.RequestException as e:
    print(f"게시물 조회 실패: {e}")
    return None

#--------------------------------------------------------
if __name__ == '__main__':
    # 앱 실행
    MyApp().run()