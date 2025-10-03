import kivy
# Kivy 기본 위젯 및 레이아웃 모듈 임포트
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
# --------------------------------------------------------
# 1. Kivy 코어 텍스트 모듈 임포트 및 ScreenManager, FloatLayout 추가
from kivy.core.text import LabelBase # 폰트 등록을 위해 필요
from kivy.uix.screenmanager import ScreenManager, Screen # 화면 관리를 위해 필요
from kivy.uix.floatlayout import FloatLayout # 우측 상단 버튼 배치를 위해 필요
# --------------------------------------------------------

# Kivy 버전 명시
kivy.require('1.11.1')

# --------------------------------------------------------
# 2. 폰트 설정 및 등록
FONT_NAME = 'NanumFont' # Kivy 내부에서 사용할 폰트 이름
FONT_PATH = 'NanumGothic.ttf' # 폰트 파일 경로

# Kivy에 사용할 폰트 등록
try:
    LabelBase.register(name=FONT_NAME, fn_regular=FONT_PATH) 
except Exception as e:
    # 폰트 파일을 찾지 못하면 오류 메시지를 콘솔에 출력
    print(f"폰트 등록 오류: {e}. 'NanumGothic.ttf' 파일이 현재 폴더에 있는지 확인하세요.")
# --------------------------------------------------------


# --------------------------------------------------------
# 새 화면: 메인 화면 (로그인 성공 후 진입)
# --------------------------------------------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.current_user = "guest" # 현재 로그인 사용자 ID를 저장할 변수 (초기값: guest)
        
        # FloatLayout을 사용하여 설정 버튼을 우측 상단에 배치
        root_float = FloatLayout() 
        
        # 메인 컨텐츠 레이아웃 (환영 메시지와 네비게이션 버튼을 수직으로 담음)
        # padding: [좌, 상, 우, 하], spacing: 위젯 간 간격
        main_content = BoxLayout(orientation='vertical', padding=[50, 100, 50, 80], spacing=30)
        
        # 1. 메인 타이틀
        main_content.add_widget(Label(
            text="[b]메인 화면[/b]",
            font_size='36sp',
            color=[0.2, 0.6, 1, 1], # 파란색 계열
            font_name=FONT_NAME,
            markup=True, # 마크업(볼드 등) 사용 가능 설정
            size_hint_y=None, height=70,
            halign='center', valign='middle'
        ))
        
        # 2. 환영 메시지
        welcome_label = Label(
            text="환영합니다! 앱의 주요 기능들을 사용해 보세요.",
            font_size='18sp',
            font_name=FONT_NAME,
            size_hint_y=None, height=50
        )
        main_content.add_widget(welcome_label)
        
        #  텍스트와 버튼 사이에 명시적인 큰 공간 추가
        main_content.add_widget(Label(size_hint_y=None, height=40)) 
        
        # 3. 네비게이션 버튼 레이아웃
        nav_layout = BoxLayout(orientation='vertical', spacing=15) 
        
        # 네비게이션 버튼 생성 및 바인딩 헬퍼 함수
        def create_nav_button(text, screen_name):
            btn = Button(
                text=text,
                font_size='24sp',
                font_name=FONT_NAME,
                background_color=[0.1, 0.3, 0.5, 1], # 어두운 파란색
                color=[1, 1, 1, 1],
                size_hint_y=None,
                height=70
            )
            # 버튼 클릭 시 go_to_screen 메서드를 호출하여 화면 전환
            btn.bind(on_press=lambda *args: self.go_to_screen(screen_name))
            return btn

        # 각 기능별 버튼 추가
        nav_layout.add_widget(create_nav_button("동아리", 'club'))
        nav_layout.add_widget(create_nav_button("분실물", 'lost_found'))
        nav_layout.add_widget(create_nav_button("시간표", 'timetable'))
        
        main_content.add_widget(nav_layout)
        # 스페이서: 남은 공간을 차지하여 위젯을 상단으로 밀어 올림
        main_content.add_widget(Label()) 
        
        root_float.add_widget(main_content)
        
        # 4. 설정 버튼 (FloatLayout을 이용한 우측 상단 배치)
        settings_button = Button(
            text="설정", 
            font_size='18sp',
            font_name=FONT_NAME, 
            background_color=[0.4, 0.4, 0.4, 0], # 배경 투명
            color=[0.2, 0.6, 1, 1], # 텍스트 색상
            size_hint=(None, None), # 크기 직접 지정
            size=(90, 50), 
            pos_hint={'right': 1, 'top': 1}, # 우측 상단에 위치
            border=[0, 0, 0, 0] # 버튼 테두리 제거
        )
        settings_button.bind(on_press=self.show_settings_popup) 
        root_float.add_widget(settings_button)
        
        self.add_widget(root_float)
    
    def go_to_screen(self, screen_name):
        """지정된 화면으로 전환합니다."""
        self.manager.current = screen_name

    def set_username(self, username):
        """로그인 화면에서 사용자 ID를 전달받아 저장합니다."""
        self.current_user = username
        
    def show_settings_popup(self, instance):
        """설정 팝업 (사이드 패널 형태)을 표시하고 로그인 정보 및 로그아웃 버튼을 포함합니다."""
        
        # 팝업 내부 레이아웃
        content_layout = BoxLayout(orientation='vertical', spacing=20, padding=15)
        
        # 1. 로그인 정보 표시 (저장된 ID 사용)
        info_label = Label(
            text=f"[b]로그인 정보[/b]\n\n현재 사용자: {self.current_user}\n\n앱 설정 관리",
            font_size='18sp',
            font_name=FONT_NAME,
            markup=True,
            size_hint_y=None,
            height=150,
            halign='center', 
            valign='top'
        )
        content_layout.add_widget(info_label)
        
        # 2. 로그아웃 버튼
        logout_button = Button(
            text="로그아웃",
            font_size='22sp',
            font_name=FONT_NAME,
            background_color=[0.8, 0.4, 0.2, 1], # 주황색 계열
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=55
        )

        # 팝업 설정: 오른쪽에서 슬라이드되는 사이드 패널 형태
        popup = Popup(
            title="앱 설정",
            title_font=FONT_NAME,
            content=content_layout,
            size_hint=(0.6, 1.0), # 너비 60%, 높이 100%
            pos_hint={'x': 0.4, 'y': 0}, # X축 40% 위치에서 시작 (화면의 오른쪽 60% 차지)
            auto_dismiss=True
        )
        
        # 로그아웃 버튼 바인딩 함수 정의
        def perform_logout(btn_instance):
            self.manager.current = 'login' # 로그인 화면으로 전환
            
            # 로그인 화면의 입력 필드를 초기화
            login_screen = self.manager.get_screen('login')
            if login_screen:
                login_screen.username_input.text = ''
                login_screen.password_input.text = ''
                
            popup.dismiss() # 팝업 닫기

        logout_button.bind(on_press=perform_logout)
        
        content_layout.add_widget(logout_button)
        
        popup.open()


# --------------------------------------------------------
#  새 화면: 동아리 페이지 
# --------------------------------------------------------
class ClubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 페이지 제목
        layout.add_widget(Label(
            text="[b]동아리 페이지[/b]\n\n동아리 관련 내용을 여기에 추가하세요.", 
            font_name=FONT_NAME, 
            markup=True,
            font_size='26sp'
        ))
        
        # 뒤로가기 버튼
        back_button = Button(
            text="메인 화면으로",
            font_name=FONT_NAME,
            size_hint_y=None,
            height=50,
            background_color=[0.5, 0.5, 0.5, 1]
        )
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        
        layout.add_widget(Label()) # 스페이서
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


# --------------------------------------------------------
# 새 화면: 분실물 페이지
# --------------------------------------------------------
class LostAndFoundScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 페이지 제목
        layout.add_widget(Label(
            text="[b]분실물 페이지[/b]\n\n분실물 신고/조회 기능을 여기에 추가합니다.", 
            font_name=FONT_NAME, 
            markup=True,
            font_size='26sp'
        ))
        
        # 뒤로가기 버튼
        back_button = Button(
            text="메인 화면으로",
            font_name=FONT_NAME,
            size_hint_y=None,
            height=50,
            background_color=[0.5, 0.5, 0.5, 1]
        )
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        
        layout.add_widget(Label()) # 스페이서
        layout.add_widget(back_button)
        self.add_widget(layout)
        
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


# --------------------------------------------------------
# 새 화면: 시간표 페이지
# --------------------------------------------------------
class TimetableScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # 페이지 제목
        layout.add_widget(Label(
            text="[b]시간표 페이지[/b]\n\n개인 시간표를 확인하는 기능을 여기에 추가합니다.", 
            font_name=FONT_NAME, 
            markup=True,
            font_size='26sp'
        ))
        
        # 뒤로가기 버튼
        back_button = Button(
            text="메인 화면으로",
            font_name=FONT_NAME,
            size_hint_y=None,
            height=50,
            background_color=[0.5, 0.5, 0.5, 1]
        )
        back_button.bind(on_press=lambda *args: self.go_to_screen('main'))
        
        layout.add_widget(Label()) # 스페이서
        layout.add_widget(back_button)
        self.add_widget(layout)
        
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


# --------------------------------------------------------
# 기존 로그인 화면 (ScreenManager를 위해 Screen을 상속받음)
# --------------------------------------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
        # 모든 위젯을 담을 메인 레이아웃 (수직 배치)
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[50, 40, 50, 40],
            spacing=15
        )
        
        # 1. 앱 이름 표시 (Label)
        app_name_label = Label(
            text="[b]CAMPUS LINK[/b]",
            font_size='36sp',
            color=[0.2, 0.6, 1, 1],
            font_name=FONT_NAME, 
            markup=True,
            size_hint_y=None,
            height=70
        )
        main_layout.add_widget(app_name_label)

        # 빈 공간 추가 (스페이서)
        main_layout.add_widget(Label(size_hint_y=None, height=10))

        # 사용자 이름 입력 필드
        self.username_input = TextInput(
            hint_text='사용자 이름',
            multiline=False,
            font_size='18sp',
            font_name=FONT_NAME,
            padding=[10, 10, 10, 10],
            size_hint_y=None,
            height=48
        )
        main_layout.add_widget(self.username_input)

        # 비밀번호 입력 필드
        self.password_input = TextInput(
            hint_text='비밀번호',
            multiline=False,
            password=True, # 비밀번호 숨김 처리
            font_size='18sp',
            font_name=FONT_NAME,
            padding=[10, 10, 10, 10],
            size_hint_y=None,
            height=48
        )
        main_layout.add_widget(self.password_input)

        # 로그인 버튼
        login_button = Button(
            text="로그인",
            font_size='22sp',
            font_name=FONT_NAME,
            background_color=[0.2, 0.6, 1, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=55
        )
        # 버튼 클릭 시 do_login 메서드 실행
        login_button.bind(on_press=self.do_login)
        main_layout.add_widget(login_button)

        # 하단에 빈 공간 추가 (남은 공간을 차지하여 위젯을 중앙에 가깝게 배치)
        main_layout.add_widget(Label())
        
        # Screen에 메인 레이아웃 추가
        self.add_widget(main_layout)

    def show_popup(self, title, message, show_retry_button=False):
        """결과 메시지를 팝업으로 표시하는 도우미 함수"""
        
        # 팝업 내용과 버튼을 담을 레이아웃
        content_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        popup_content = Label(
            text=message, 
            font_size='18sp',
            font_name=FONT_NAME 
        )
        content_layout.add_widget(popup_content)

        # ----------------------------------------------------
        #  실패 시 '다시 시도' 버튼 추가 로직
        # ----------------------------------------------------
        if show_retry_button:
            retry_button = Button(
                text="다시 시도",
                font_size='20sp',
                font_name=FONT_NAME,
                size_hint_y=None,
                height=50,
                background_color=[0.9, 0.2, 0.2, 1] # 빨간색 계열
            )
            # 팝업 설정: 버튼이 필요하므로 auto_dismiss를 False로 설정
            popup = Popup(
                title=title, 
                title_font=FONT_NAME, 
                content=content_layout,
                size_hint=(0.8, 0.4), 
                auto_dismiss=False 
            )
            # 버튼 클릭 시 팝업 닫기
            retry_button.bind(on_press=lambda x: popup.dismiss())
            content_layout.add_widget(retry_button)
        else:
            # 성공 또는 일반 메시지 팝업 (자동 닫힘)
            popup = Popup(
                title=title, 
                title_font=FONT_NAME, 
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
            # 로그인 성공: 'main' 화면으로 전환
            main_screen = self.manager.get_screen('main')
            # 메인 화면으로 사용자 이름 전달 및 저장
            main_screen.set_username(username)
            self.manager.current = 'main'
        else:
            # 로그인 실패: 팝업 메시지 표시
            title = "로그인 실패"
            message = "사용자 이름 또는 비밀번호를 다시 확인하세요."
            self.show_popup(title, message, show_retry_button=True)


class MyApp(App):
    def build(self):
        self.title = "Kivy 한글 앱"
        
        # ----------------------------------------------------
        #  ScreenManager 설정: 화면들을 관리하고 전환하는 역할
        sm = ScreenManager()
        
        # 로그인 화면 추가 (최초 진입 화면)
        login_screen = LoginScreen(name='login')
        sm.add_widget(login_screen)
        
        #  메인 화면 및 네비게이션 화면 추가
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ClubScreen(name='club'))
        sm.add_widget(LostAndFoundScreen(name='lost_found'))
        sm.add_widget(TimetableScreen(name='timetable'))
        
        return sm # ScreenManager를 루트 위젯으로 반환
        # ----------------------------------------------------

if __name__ == '__main__':
    # 앱 실행
    MyApp().run()
    