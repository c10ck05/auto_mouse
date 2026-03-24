import customtkinter as ctk
import pyautogui
from pynput import keyboard, mouse
import threading
import time
import random
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SlimGodClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Click Master Mini")
        self.geometry("360x520") 
        self.attributes('-topmost', True)
        
        self.running = False
        self.target_points = []
        self.target_image = None

        # --- 상단 상태 표시 ---
        self.status_label = ctk.CTkLabel(self, text="준비 완료", font=("Arial", 18, "bold"), text_color="#2ecc71")
        self.status_label.pack(pady=15)

        # --- 메인 탭 시스템 (설정 탭 추가) ---
        self.tabview = ctk.CTkTabview(self, width=320, height=250)
        self.tabview.pack(pady=5)
        self.tabview.add("📍 좌표")
        self.tabview.add("🖼️ 이미지")
        self.tabview.add("⚙️ 설정")
        self.tabview.add("📜 로그")

        # [탭 1] 좌표 설정
        self.pos_list = ctk.CTkTextbox(self.tabview.tab("📍 좌표"), width=300, height=100, font=("Arial", 11))
        self.pos_list.pack(pady=5)
        self.update_list()
        
        btn_f = ctk.CTkFrame(self.tabview.tab("📍 좌표"), fg_color="transparent")
        btn_f.pack(pady=5)
        ctk.CTkButton(btn_f, text="+ 추가", command=self.add_pos, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="초기화", fg_color="#c0392b", command=self.clear_pos, width=100).pack(side="left", padx=10)

        # [탭 2] 이미지 인식
        self.img_info = ctk.CTkLabel(self.tabview.tab("🖼️ 이미지"), text="이미지 미등록", text_color="gray")
        self.img_info.pack(pady=30)
        ctk.CTkButton(self.tabview.tab("🖼️ 이미지"), text="파일 불러오기", command=self.load_img).pack()

        # [탭 3] 설정 (짜잘한 것들 일로 모음!)
        tab_set = self.tabview.tab("⚙️ 설정")
        
        # 간격 설정
        set_f = ctk.CTkFrame(tab_set, fg_color="transparent")
        set_f.pack(pady=10)
        ctk.CTkLabel(set_f, text="클릭 간격(초):").pack(side="left", padx=5)
        self.int_entry = ctk.CTkEntry(set_f, width=60)
        self.int_entry.insert(0, "0.1")
        self.int_entry.pack(side="left", padx=5)

        # 안티밴 체크박스
        self.anti_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(tab_set, text="안티-밴 (랜덤 좌표/시간)", variable=self.anti_var).pack(pady=10)

        # 투명도 조절
        ctk.CTkLabel(tab_set, text="창 투명도", font=("Arial", 11)).pack(pady=(10, 0))
        self.t_slider = ctk.CTkSlider(tab_set, from_=0.3, to=1.0, height=15, command=lambda v: self.attributes('-alpha', v))
        self.t_slider.set(1.0)
        self.t_slider.pack(pady=5, padx=20)

        # [탭 4] 로그
        self.log_box = ctk.CTkTextbox(self.tabview.tab("📜 로그"), width=300, height=180, font=("Arial", 10))
        self.log_box.pack()

        # --- 하단 실행 버튼 ---
        self.start_btn = ctk.CTkButton(self, text="매크로 시작 (F9)", font=("Arial", 16, "bold"), 
                                      fg_color="#27ae60", hover_color="#2ecc71", height=50, command=self.start)
        self.start_btn.pack(pady=20, fill="x", padx=40)

        self.help_label = ctk.CTkLabel(self, text="※ 중지: ESC 키 또는 (0,0) 던지기", 
                                      font=("Arial", 10), text_color="gray")
        self.help_label.pack()

        # 전역 단축키 리스너
        keyboard.GlobalHotKeys({'<f9>': self.start}).start()
        keyboard.Listener(on_press=self.on_key).start()

    def write_log(self, m):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {m}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def add_pos(self):
        self.status_label.configure(text="클릭 대기 중...", text_color="orange")
        def on_c(x, y, b, p):
            if p:
                self.target_points.append((x, y))
                self.after(0, self.update_list)
                self.after(0, lambda: self.status_label.configure(text="좌표 추가 완료", text_color="#2ecc71"))
                return False
        mouse.Listener(on_click=on_c).start()

    def clear_pos(self):
        self.target_points = []
        self.update_list()
        self.write_log("모든 좌표 초기화.")

    def update_list(self):
        self.pos_list.configure(state="normal")
        self.pos_list.delete("0.0", "end")
        if not self.target_points: self.pos_list.insert("0.0", "비어있음 (현재 위치 사용)")
        else:
            for i, p in enumerate(self.target_points): self.pos_list.insert("end", f"{i+1}. {int(p[0])}, {int(p[1])}\n")
        self.pos_list.configure(state="disabled")

    def load_img(self):
        f = ctk.filedialog.askopenfilename()
        if f:
            self.target_image = f
            self.img_info.configure(text=f"등록: {os.path.basename(f)}", text_color="cyan")
            self.write_log(f"이미지 로드: {os.path.basename(f)}")

    def on_key(self, key):
        if key == keyboard.Key.esc: self.stop()

    def stop(self):
        if self.running:
            self.running = False
            self.status_label.configure(text="중단됨 (3초 뒤 초기화)", text_color="red")
            self.start_btn.configure(state="normal", text="매크로 다시 시작")
            self.write_log("매크로 중단.")
            
            def reset():
                time.sleep(3)
                if not self.running:
                    self.status_label.configure(text="준비 완료", text_color="#2ecc71")
            threading.Thread(target=reset, daemon=True).start()

    def start(self):
        if not self.running:
            self.running = True
            self.write_log("매크로 시작.")
            threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        try:
            for i in range(3, 0, -1):
                if not self.running: return
                self.status_label.configure(text=f"{i}초 후 시작...", text_color="orange")
                time.sleep(1)
            
            if not self.running: return
            self.status_label.configure(text="● 작동 중", text_color="#2ecc71")
            self.start_btn.configure(state="disabled")
            
            base = float(self.int_entry.get())
            mode = self.tabview.get()

            while self.running:
                mx, my = pyautogui.position()
                if mx < 5 and my < 5: 
                    self.after(0, self.stop)
                    break

                if mode == "📍 좌표":
                    pts = self.target_points if self.target_points else [pyautogui.position()]
                    for tx, ty in pts:
                        if not self.running: break
                        self.click(tx, ty)
                        self.s_sleep(base)
                elif mode == "🖼️ 이미지":
                    if self.target_image:
                        try:
                            l = pyautogui.locateOnScreen(self.target_image, confidence=0.8)
                            if l: 
                                c = pyautogui.center(l)
                                self.click(c.x, c.y)
                        except: pass
                    self.s_sleep(base)
        except Exception as e:
            self.write_log(f"Error: {e}")
            self.after(0, self.stop)

    def click(self, x, y):
        if self.anti_var.get():
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
        pyautogui.click(x, y)

    def s_sleep(self, b):
        if self.anti_var.get(): time.sleep(b + random.uniform(-b*0.1, b*0.1))
        else: time.sleep(b)

if __name__ == "__main__":
    app = SlimGodClicker()
    app.mainloop()