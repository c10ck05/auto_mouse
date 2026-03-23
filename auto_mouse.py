import pyautogui
import customtkinter as ctk
from pynput import keyboard, mouse
import threading
import time

# 기본 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("God Mode v1.2")
        self.geometry("260x220")  # 더 작고 콤팩트하게 수정
        self.attributes("-topmost", True)  # 항상 위
        
        self.target_x = None
        self.target_y = None
        self.is_running = False

        # --- UI 레이아웃 ---
        self.label_status = ctk.CTkLabel(self, text="좌표를 설정해주세요", text_color="yellow")
        self.label_status.pack(pady=(15, 5))

        self.label_coord = ctk.CTkLabel(self, text="X: - , Y: -", font=("Arial", 12))
        self.label_coord.pack(pady=5)

        self.btn_action = ctk.CTkButton(self, text="좌표 설정 (F8)", command=self.start_pos_tracking)
        self.btn_action.pack(pady=10)

        # 긴급 정지 안내 (작은 글씨)
        self.label_help = ctk.CTkLabel(self, text="※ 중지: ESC 키 또는\n마우스를 화면 구석으로 던지세요!", 
                                       font=("Arial", 10), text_color="gray")
        self.label_help.pack(pady=5)

        # 단축키 리스너
        self.listener = keyboard.GlobalHotKeys({'<f8>': self.start_pos_tracking})
        self.listener.start()

    def update_status(self, msg, color="white"):
        self.label_status.configure(text=msg, text_color=color)

    # 1. 좌표 설정 모드
    def start_pos_tracking(self):
        if self.is_running: return
        self.update_status("클릭할 곳을 클릭하세요!", "orange")
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.target_x, self.target_y = x, y
            self.label_coord.configure(text=f"X: {int(x)}, Y: {int(y)}")
            self.update_status("설정 완료! (F9: 시작)", "green")
            
            # F9 시작 단축키 활성화
            try: self.start_listener.stop()
            except: pass
            self.start_listener = keyboard.GlobalHotKeys({'<f9>': self.start_clicking})
            self.start_listener.start()
            
            return False # 리스너 종료

    # 2. 매크로 시작
    def start_clicking(self):
        if not self.is_running:
            self.is_running = True
            self.update_status("매크로 가동 중...", "red")
            threading.Thread(target=self.run_macro, daemon=True).start()

    def run_macro(self):
        # ESC 감지 리스너
        stop_event = threading.Event()
        def on_press(key):
            if key == keyboard.Key.esc:
                stop_event.set()
                return False

        esc_listener = keyboard.Listener(on_press=on_press)
        esc_listener.start()

        try:
            while not stop_event.is_set():
                pyautogui.click(self.target_x, self.target_y)
                time.sleep(0.01) # 초고속 클릭
        except pyautogui.FailSafeException:
            pass # 구석으로 던졌을 때 예외 처리
        finally:
            self.is_running = False
            self.after(0, self.stop_ui_reset) # 메인 스레드에서 UI 업데이트

    # 3. 중단 후 3초 뒤 초기화 (피드백 반영)
    def stop_ui_reset(self):
        self.update_status("중단됨 (3초 뒤 초기화)", "orange")
        
        def reset():
            time.sleep(3)
            if not self.is_running: # 다시 시작 안 했을 경우만 초기화
                self.update_status("좌표를 설정해주세요", "yellow")
        
        threading.Thread(target=reset, daemon=True).start()

if __name__ == "__main__":
    app = AutoClicker()
    app.mainloop()