import pyautogui
import customtkinter as ctk
from pynput import keyboard, mouse
import threading
import time

# 맥북 보안 설정을 위한 안전장치
pyautogui.FAILSAFE = True 

class AutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- UI 설정 (더 작고 슬림하게) ---
        self.title("God Mode")
        self.geometry("260x240") 
        self.attributes("-topmost", True)
        
        self.target_x = None
        self.target_y = None
        self.is_running = False

        # --- UI 요소 ---
        self.label_status = ctk.CTkLabel(self, text="좌표를 설정해주세요", text_color="yellow", font=("Arial", 14, "bold"))
        self.label_status.pack(pady=(15, 5))

        self.label_coord = ctk.CTkLabel(self, text="X: - , Y: -", font=("Arial", 12))
        self.label_coord.pack(pady=5)

        self.btn_action = ctk.CTkButton(self, text="좌표 설정 (F8)", command=self.start_pos_tracking, fg_color="#2c3e50")
        self.btn_action.pack(pady=10)

        # 현재님이 요청하신 안내 문구
        self.label_help = ctk.CTkLabel(self, text="💡 중지하려면 ESC를 누르거나\n마우스를 화면 구석으로 던지세요!", 
                                       font=("Arial", 10), text_color="gray")
        self.label_help.pack(pady=5)

        # F8 단축키 리스너 (언제든 좌표 재설정 가능)
        self.listener = keyboard.GlobalHotKeys({'<f8>': self.start_pos_tracking})
        self.listener.start()

    def update_status(self, msg, color="white"):
        self.label_status.configure(text=msg, text_color=color)

    # 1. 좌표 설정 (현재님 기존 로직 유지)
    def start_pos_tracking(self):
        if self.is_running: return
        self.update_status("클릭할 곳을 선택하세요", "orange")
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.target_x, self.target_y = x, y
            self.label_coord.configure(text=f"X: {int(x)}, Y: {int(y)}")
            self.update_status("설정 완료! (F9: 시작)", "green")
            
            # F9 시작 단축키 연결
            try: self.start_listener.stop()
            except: pass
            self.start_listener = keyboard.GlobalHotKeys({'<f9>': self.start_clicking})
            self.start_listener.start()
            return False 

    # 2. 매크로 실행 (현재님의 광클 기능)
    def start_clicking(self):
        if not self.is_running:
            self.is_running = True
            self.update_status("매크로 가동 중!!", "red")
            threading.Thread(target=self.run_macro, daemon=True).start()

    def run_macro(self):
        # ESC 감지를 위한 별도 리스너
        stop_event = threading.Event()
        def on_press(key):
            if key == keyboard.Key.esc:
                stop_event.set()
                return False
        
        esc_listener = keyboard.Listener(on_press=on_press)
        esc_listener.start()

        try:
            while not stop_event.is_set():
                # 현재님의 핵심 기능: 지정된 좌표 광클
                pyautogui.click(self.target_x, self.target_y)
                time.sleep(0.001) # 딜레이 최소화 (현재님 스타일)
        except pyautogui.FailSafeException:
            print("Fail-safe triggered!") 
        finally:
            self.is_running = False
            self.after(0, self.stop_ui_reset)

    # 3. 피드백 반영: 3초 뒤 초기화 기능
    def stop_ui_reset(self):
        self.update_status("중단됨 (3초 뒤 초기화)", "orange")
        
        def reset_thread():
            time.sleep(3)
            # 3초 뒤에 다시 시작 상태가 아닐 때만 문구 변경
            if not self.is_running:
                self.update_status("좌표를 설정해주세요", "yellow")
        
        threading.Thread(target=reset_thread, daemon=True).start()

if __name__ == "__main__":
    app = AutoClicker()
    app.mainloop()