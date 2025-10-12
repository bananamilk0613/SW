import kivy
import sys
import os # 파일 경로를 위해 os 모듈 임포트
# Kivy 기본 위젯 및 레이아웃 모듈 임포트
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
# 검색 기능 UI를 위해 ScrollView와 GridLayout 추가
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
# Kivy 코어 텍스트 모듈 임포트 및 ScreenManager, FloatLayout 추가
from kivy.core.text import LabelBase # 폰트 등록을 위해 필요
from kivy.uix.screenmanager import ScreenManager, Screen # 화면 관리를 위해 필요
from kivy.uix.floatlayout import FloatLayout # 우측 상단 버튼 배치를 위해 필요
from kivy.graphics import Color, Rectangle, RoundedRectangle # 배경색 및 둥근 모서리를 위한 import 추가
from kivy.metrics import dp # dp 단위를 사용하기 위해 import
from kivy.properties import ObjectProperty # 위젯 참조를 위해 import
from kivy.uix.behaviors import ButtonBehavior # 커스텀 버튼 위젯을 위해 import
# Kivy 앱의 기본 이미지 경로를 사용하기 위해 Kivy 경로 라이브러리 임포트
from kivy.resources import resource_find

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
# 공통 UI 스타일 함수
# --------------------------------------------------------
# 로컬 이미지 플레이스홀더 경로 설정 (Kivy 기본 아이콘 사용)
# 이 경로는 Kivy가 설치된 곳이면 어디서든 작동합니다.
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
        # Kivy TextInput에서 이메일은 'mail' 타입을 사용합니다.
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
# 새 화면: 메인 화면 (로그인 성공 후 진입)
# --------------------------------------------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.current_user = "guest" 
        
        # 배경색을 흰색으로 설정 (White Background)
        with self.canvas.before:
            Color(1, 1, 1, 1) # R, G, B, A (흰색)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
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
        welcome_label = Label(
            text="환영합니다! 어떤 정보가 필요하신가요?",
            font_size='18sp',
            font_name=FONT_NAME,
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None, height=dp(50)
        )
        main_content.add_widget(welcome_label)
        
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
    
    def _update_rect(self, instance, value):
        """화면 크기가 변경될 때 배경 사각형 크기를 업데이트합니다."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_screen(self, screen_name):
        """지정된 화면으로 전환합니다."""
        self.manager.current = screen_name

    def set_username(self, username):
        """로그인 화면에서 사용자 ID를 전달받아 저장합니다."""
        self.current_user = username
        
    def show_settings_popup(self, instance):
        """설정 팝업을 표시합니다. (사이드 패널 스타일)"""
        
        # 팝업 인스턴스를 먼저 생성하여 닫기 버튼에 바인딩할 수 있게 합니다.
        popup = Popup(
            title="", 
            separator_height=0, 
            size_hint=(0.6, 1.0), 
            pos_hint={'x': 0.4, 'y': 0}, 
            auto_dismiss=True
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
            text=f"[b]Campus Link 계정[/b]\n\n현재 사용자: {self.current_user}\n\n앱 설정 및 정보",
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
# 동아리 기능 관련 화면들
# --------------------------------------------------------

class ClubScreen(Screen):
    """동아리 목록을 보여주는 메인 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.all_clubs = [
            {'name': '축구 동아리 KickOff', 'short_desc': '축구를 사랑하는 사람들의 모임입니다.', 'long_desc': '매주 수요일 오후 4시에 대운동장에서 정기적으로 활동합니다. 축구를 좋아하거나 배우고 싶은 모든 학생을 환영합니다!'},
            {'name': '코딩 스터디 CodeHive', 'short_desc': '파이썬, 자바 등 함께 공부하는 코딩 모임', 'long_desc': '알고리즘 스터디와 프로젝트 개발을 함께 진행합니다. 초보자도 대환영!'},
            {'name': '영화 토론 동아리', 'short_desc': '매주 새로운 영화를 보고 토론합니다.', 'long_desc': '다양한 장르의 영화를 감상하고 깊이 있는 토론을 나누는 동아리입니다.'},
        ]
        
        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10), padding=[0, dp(10), 0, dp(10)])
        
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        header.add_widget(back_button)
        
        header.add_widget(Label(text="[b]동아리 게시판[/b]", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True, font_size='26sp'))
        
        create_button = get_styled_button("개설", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1], font_size='18sp')
        create_button.height = dp(50)
        create_button.size_hint_x = None
        create_button.width = dp(80)
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
        self.update_club_list(self.all_clubs)

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
        search_term = self.search_input.text.lower()
        if not search_term:
            results = self.all_clubs
        else:
            results = [club for club in self.all_clubs if search_term in club['name'].lower()]
        self.update_club_list(results)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


class ClubDetailScreen(Screen):
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

            # 동아리 소개
            self.main_layout.add_widget(Label(text="[b]동아리 소개[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, size_hint_y=None, height=dp(40)))
            self.main_layout.add_widget(Label(text=self.club_data['long_desc'], font_name=FONT_NAME, color=[0.2,0.2,0.2,1], size_hint_y=None, height=dp(100)))
            
            self.main_layout.add_widget(Label(size_hint_y=0.1)) # Spacer

            # 기능 버튼들 (공지사항, 게시글 등)
            btn_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
            btn_names = ["공지사항", "게시글", "사진첩", "회원 목록"]
            for name in btn_names:
                btn = get_styled_button(name, [0.8, 0.8, 0.8, 1], [0,0,0,1], font_size='18sp')
                btn.height=dp(50)
                btn.bind(on_press=self.show_placeholder_popup)
                btn_layout.add_widget(btn)
            self.main_layout.add_widget(btn_layout)
            
            self.main_layout.add_widget(Label()) # Spacer

            # 신청하기 버튼
            apply_button = get_styled_button("신청하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
            apply_button.bind(on_press=self.go_to_application)
            self.main_layout.add_widget(apply_button)

    def go_to_application(self, instance):
        app_screen = self.manager.get_screen('club_apply')
        app_screen.club_data = self.club_data # 신청할 동아리 정보 전달
        self.go_to_screen('club_apply')

    def show_placeholder_popup(self, instance):
        Popup(title='알림', content=Label(text=f"'{instance.text}' 기능은 준비 중입니다.", font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


class ClubCreateScreen(Screen):
    """새로운 동아리를 개설하는 화면"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))
        
        # 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('club'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]동아리 개설[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
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
        create_button = get_styled_button("개설하기", [0.3, 0.7, 0.4, 1], [1, 1, 1, 1])
        create_button.bind(on_press=self.create_club)
        main_layout.add_widget(create_button)

        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def create_club(self, instance):
        name = self.club_name.text
        s_desc = self.short_desc.text
        l_desc = self.long_desc.text

        if not name or not s_desc or not l_desc:
            Popup(title='오류', content=Label(text='모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return

        new_club = {'name': name, 'short_desc': s_desc, 'long_desc': l_desc}
        
        # ClubScreen의 리스트에 새 동아리 추가
        club_screen = self.manager.get_screen('club')
        club_screen.all_clubs.append(new_club)
        
        # 필드 초기화
        self.club_name.text = ""
        self.short_desc.text = ""
        self.long_desc.text = ""

        self.go_to_screen('club')

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


class ClubApplicationScreen(Screen):
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
            self.user_name = get_rounded_textinput('이름')
            self.student_id = get_rounded_textinput('학번', input_type='number')
            self.intro = TextInput(hint_text='자기소개 및 지원 동기', font_name=FONT_NAME, size_hint_y=None, height=dp(150), padding=dp(15))

            self.main_layout.add_widget(self.user_name)
            self.main_layout.add_widget(self.student_id)
            self.main_layout.add_widget(self.intro)
            self.main_layout.add_widget(Label()) # Spacer

            # 신청하기 버튼
            apply_button = get_styled_button("신청하기", [0.2, 0.6, 1, 1], [1, 1, 1, 1])
            apply_button.bind(on_press=self.submit_application)
            self.main_layout.add_widget(apply_button)

    def submit_application(self, instance):
        if not self.user_name.text or not self.student_id.text or not self.intro.text:
            Popup(title='오류', content=Label(text='모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return
        
        # 신청 완료 팝업
        popup = Popup(title='신청 완료', content=Label(text='신청이 성공적으로 완료되었습니다.', font_name=FONT_NAME), size_hint=(0.8, 0.3))
        popup.bind(on_dismiss=lambda *args: self.go_to_screen('club'))
        popup.open()

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name

# --------------------------------------------------------
# 새 화면: 분실물 등록 페이지 (Add Item Screen)
# --------------------------------------------------------
class AddItemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(40)], spacing=dp(15))

        # 헤더
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))
        back_button = get_styled_button("←", [0.9, 0.9, 0.9, 1], [0, 0, 0, 1], font_size='24sp')
        back_button.height = dp(50)
        back_button.size_hint_x = None
        back_button.width = dp(60)
        back_button.bind(on_press=lambda *args: self.go_to_screen('lost_found'))
        header.add_widget(back_button)
        header.add_widget(Label(text="[b]분실물 등록[/b]", font_name=FONT_NAME, color=[0,0,0,1], markup=True, font_size='26sp'))
        main_layout.add_widget(header)

        # 입력 필드
        self.name_input = get_rounded_textinput('물건 이름 (예: 에어팟 프로)')
        self.loc_input = get_rounded_textinput('발견/분실 장소 (예: 중앙도서관 1층)')
        self.contact_input = get_rounded_textinput('연락처 (예: 010-1234-5678)')

        main_layout.add_widget(self.name_input)
        main_layout.add_widget(self.loc_input)
        main_layout.add_widget(self.contact_input)

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
        main_layout.add_widget(photo_layout)
        
        # 이미지 미리보기
        self.image_preview = Image(source=DEFAULT_IMAGE, size_hint_y=None, height=dp(150), fit_mode='contain')
        main_layout.add_widget(self.image_preview)

        main_layout.add_widget(Label()) # Spacer

        # 등록하기 버튼
        register_button = get_styled_button("등록하기", [1, 0.5, 0.3, 1], [1, 1, 1, 1])
        register_button.bind(on_press=self.register_item)
        main_layout.add_widget(register_button)

        self.add_widget(main_layout)

    def select_photo(self, instance):
        # 실제 앱에서는 plyer와 같은 라이브러리를 사용하여 파일 탐색기를 엽니다.
        # 여기서는 시뮬레이션을 위해 더미 경로와 이미지를 사용합니다.
        self.image_path = "dummy_selected_image.png" # 실제로는 선택된 파일 경로가 됩니다.
        self.photo_label.text = self.image_path
        self.image_preview.source = DEFAULT_IMAGE # 선택된 이미지 미리보기 (시뮬레이션)
        Popup(title='알림', content=Label(text='실제 앱에서는 파일 탐색기가 열립니다.\n(현재는 시뮬레이션)', font_name=FONT_NAME), size_hint=(0.8, 0.3)).open()

    def register_item(self, instance):
        name = self.name_input.text
        loc = self.loc_input.text
        contact = self.contact_input.text
        
        if not name or not loc or not contact:
            Popup(title='오류', content=Label(text='모든 항목을 입력해주세요.', font_name=FONT_NAME), size_hint=(0.7, 0.3)).open()
            return

        # 이미지 경로가 없으면 기본 이미지 사용
        image = self.image_path if self.image_path else ""

        new_item = {'name': name, 'loc': loc, 'contact': contact, 'image': image}

        # LostAndFoundScreen의 리스트에 새 아이템 추가
        lost_found_screen = self.manager.get_screen('lost_found')
        lost_found_screen.all_items.append(new_item)

        # 필드 초기화
        self.name_input.text = ""
        self.loc_input.text = ""
        self.contact_input.text = ""
        self.image_path = ""
        self.photo_label.text = "사진이 선택되지 않았습니다."
        self.image_preview.source = DEFAULT_IMAGE

        self.go_to_screen('lost_found')

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name

# --------------------------------------------------------
# 새 화면: 분실물 상세 정보 페이지 (Item Detail Screen)
# --------------------------------------------------------
class ItemDetailScreen(Screen):
    item_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
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
            self.main_layout.add_widget(Label(text=f"[b]장소:[/b] {self.item_data['loc']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True, size_hint_y=None, height=dp(40)))
            self.main_layout.add_widget(Label(text=f"[b]연락처:[/b] {self.item_data['contact']}", font_name=FONT_NAME, color=[0.3,0.3,0.3,1], markup=True, size_hint_y=None, height=dp(40)))
            
            self.main_layout.add_widget(Label()) # Spacer

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name

# --------------------------------------------------------
# 새 화면: 분실물 페이지 (Lost And Found Screen)
# --------------------------------------------------------
class LostAndFoundScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 분실물 데이터를 저장할 리스트 (image 키 추가)
        self.all_items = [
            {'name': '에어팟 프로', 'loc': '중앙도서관 1층', 'contact': '010-1234-5678', 'image': ''},
            {'name': '검은색 카드지갑', 'loc': '학생회관 앞 벤치', 'contact': '카카오톡 ID: findme', 'image': ''},
        ]

        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
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
        post_button.bind(on_press=lambda *args: self.go_to_screen('add_item')) # 팝업 대신 화면 전환
        header.add_widget(post_button) 
        
        main_layout.add_widget(header)
        
        # 분실물 목록을 표시할 스크롤 뷰
        scroll_view = ScrollView(size_hint=(1, 1))
        self.items_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
        self.items_grid.bind(minimum_height=self.items_grid.setter('height'))
        
        scroll_view.add_widget(self.items_grid)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)

        # 화면이 처음 보일 때 전체 목록을 표시
        self.bind(on_enter=self.refresh_list)

    def refresh_list(self, *args):
        self.update_item_list(self.all_items)
        
    def update_item_list(self, items):
        """ 주어진 분실물 목록으로 화면을 업데이트합니다. (이미지 포함) """
        self.items_grid.clear_widgets()
        if not items:
            no_items_label = Label(
                text="등록된 분실물이 없습니다.",
                font_name=FONT_NAME, 
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=dp(100)
            )
            self.items_grid.add_widget(no_items_label)
        else:
            for item_data in items:
                item = LostItemListItem(
                    orientation='horizontal', 
                    size_hint_y=None, 
                    height=dp(100),
                    spacing=dp(10),
                    padding=dp(5)
                )
                item.item_data = item_data
                item.bind(on_press=self.view_item_details)
                
                image = Image(
                    source=item_data.get('image') if item_data.get('image') else DEFAULT_IMAGE,
                    size_hint_x=None,
                    width=dp(90),
                    fit_mode='contain'
                )
                item.add_widget(image)

                text_layout = BoxLayout(
                    orientation='vertical', 
                    spacing=dp(5)
                )

                name_label = Label(
                    text=f"[b]물건:[/b] {item_data['name']}", font_name=FONT_NAME, color=[0, 0, 0, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(25)
                )
                loc_label = Label(
                    text=f"[b]장소:[/b] {item_data['loc']}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )
                contact_label = Label(
                    text=f"[b]연락처:[/b] {item_data['contact']}", font_name=FONT_NAME, color=[0.3, 0.3, 0.3, 1], markup=True,
                    halign='left', valign='middle', size_hint_y=None, height=dp(20)
                )

                for label in [name_label, loc_label, contact_label]:
                    label.bind(size=label.setter('text_size'))
                    text_layout.add_widget(label)

                item.add_widget(text_layout)
                self.items_grid.add_widget(item)
    
    def view_item_details(self, instance):
        """ 분실물 상세 정보 화면으로 이동 """
        detail_screen = self.manager.get_screen('item_detail')
        detail_screen.item_data = instance.item_data
        self.go_to_screen('item_detail')

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


# --------------------------------------------------------
# 새 화면: 시간표 페이지 (Timetable Screen)
# --------------------------------------------------------
class TimetableScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
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
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


# --------------------------------------------------------
# 새 화면: 회원가입 페이지 (2단계)
# --------------------------------------------------------
class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.current_step = 'step1'
        
        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
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
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

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

        # 입력 필드: 이메일, 닉네임, 비밀번호, 비밀번호 확인
        self.email_input = get_rounded_textinput('이메일 주소', input_type='mail') 
        self.nickname_input = get_rounded_textinput('닉네임')
        self.password_input = get_rounded_textinput('비밀번호 (최소 4자)', password=True)
        self.confirm_password_input = get_rounded_textinput('비밀번호 확인', password=True)
        
        self.step2_layout.add_widget(self.email_input)
        self.step2_layout.add_widget(self.nickname_input)
        self.step2_layout.add_widget(self.password_input)
        self.step2_layout.add_widget(self.confirm_password_input)
        
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
        self.nickname_input.text = ''
        self.password_input.text = ''
        self.confirm_password_input.text = ''
        
        self.current_step = 'step1' # 단계 초기화
        self.update_view() # 화면 초기화
        self.manager.current = 'login'


    def do_signup(self, instance):
        """최종 회원가입 버튼 클릭 시 실행되는 함수 (2단계 유효성 검사 포함)"""
        email = self.email_input.text
        nickname = self.nickname_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        
        # 2단계 유효성 검사
        if not email or not nickname or not password or not confirm_password:
            self.show_popup("오류", "모든 계정 정보를 채워주세요.")
        elif password != confirm_password:
            self.show_popup("오류", "비밀번호가 일치하지 않습니다.")
        elif len(password) < 4:
            self.show_popup("오류", "비밀번호는 최소 4자 이상이어야 합니다.")
        else:
            # 회원가입 성공 처리 (실제 DB 저장 로직은 생략)
            self.show_popup("성공", f"사용자 '{nickname}'님의 회원가입이 완료되었습니다!\n로그인 해주세요.", after_dismiss_callback=self.go_to_login)

    def show_popup(self, title, message, after_dismiss_callback=None):
        """결과 메시지를 팝업으로 표시하는 도우미 함수"""
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        popup_content = Label(text=message, font_size='18sp', font_name=FONT_NAME, color=[0, 0, 0, 1])
        content_layout.add_widget(popup_content)
        
        confirm_button = get_styled_button("확인", [0.2, 0.6, 1, 1], [1, 1, 1, 1], font_size='20sp')
        confirm_button.height = dp(50)

        popup = Popup(
            title=title, 
            title_font=FONT_NAME, 
            title_color=[0, 0, 0, 1],
            content=content_layout,
            size_hint=(0.8, 0.4), 
            auto_dismiss=False
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
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
        # 배경색을 흰색으로 설정
        with self.canvas.before:
            Color(1, 1, 1, 1) # R, G, B, A (흰색)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
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

        # 사용자 이름 입력 필드 (커스텀 스타일 적용)
        self.username_input = get_rounded_textinput('사용자 이름')
        main_layout.add_widget(self.username_input)

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

    def _update_rect(self, instance, value):
        """화면 크기가 변경될 때 배경 사각형 크기를 업데이트합니다."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def go_to_signup(self, instance):
        """회원가입 화면으로 전환합니다."""
        self.manager.current = 'signup'


    def show_popup(self, title, message, show_retry_button=False):
        """결과 메시지를 팝업으로 표시하는 도우미 함수"""
        
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
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
                auto_dismiss=False 
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
                auto_dismiss=True
            )

        popup.open()


    def do_login(self, instance):
        """로그인 버튼 클릭 시 실행되는 함수"""
        username = self.username_input.text
        password = self.password_input.text

        # 간단한 테스트 로직: admin/1234로 고정
        if username == "admin" and password == "1234":
            main_screen = self.manager.get_screen('main')
            main_screen.set_username(username)
            self.manager.current = 'main'
        else:
            title = "로그인 실패"
            message = "사용자 이름 또는 비밀번호를 다시 확인하세요."
            self.show_popup(title, message, show_retry_button=True)


class MyApp(App):
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
        
        sm.add_widget(LostAndFoundScreen(name='lost_found'))
        sm.add_widget(AddItemScreen(name='add_item'))
        sm.add_widget(ItemDetailScreen(name='item_detail'))
        sm.add_widget(TimetableScreen(name='timetable'))
        
        return sm 

if __name__ == '__main__':
    # 앱 실행
    MyApp().run()

