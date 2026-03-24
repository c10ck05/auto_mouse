import customtkinter as ctk
import pyautogui
from pynput import keyboard, mouse
import threading
import time
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SlimGodClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Mouse")
        self.geometry("300x290") 
        self.attributes('-topmost', True)
        self.resizable(False, False)
        
        self.running = False
        self.target_points = []

        # 1. 상단 상태
        self.status_label = ctk.CTkLabel(self, text="준비 완료", font=("Arial", 16, "bold"), text_color="#2ecc71")
        self.status_label.pack(fill="x", pady=(10, 0))

        # 2. 탭 시스템
        self.tabview = ctk.CTkTabview(self, width=280, height=140)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        self.tabview.add("좌표 설정")
        self.tabview.add("세팅")
        self.tabview.add("로그")

        # [좌표 설정 탭]
        tp = self.tabview.tab("좌표 설정")
        tp.grid_columnconfigure(0, weight=1)
        self.pos_list = ctk.CTkTextbox(tp, height=50, font=("Arial", 12), border_width=1)
        self.pos_list.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(5, 5))
        ctk.CTkButton(tp, text="+ 추가", command=self.add_pos, width=100, height=28).grid(row=1, column=0, sticky="e", padx=5)
        ctk.CTkButton(tp, text="초기화", fg_color="#c0392b", command=self.clear_pos, width=100, height=28).grid(row=1, column=1, sticky="w", padx=5)
        self.update_list()

        # [세팅 탭] - 정렬 수정 핵심 구역
        ts = self.tabview.tab("세팅")
        ts.grid_columnconfigure(0, weight=1) # 왼쪽 공간 확보
        ts.grid_columnconfigure(1, weight=1) # 오른쪽 공간 확보

        # 라벨과 입력창을 같은 row에 두고 가운데 정렬
        ctk.CTkLabel(ts, text="클릭 간격(초):", font=("Arial", 12)).grid(row=0, column=0, padx=(20, 5), pady=8, sticky="e")
        self.int_entry = ctk.CTkEntry(ts, width=65, height=25)
        self.int_entry.insert(0, "0.1")
        self.int_entry.grid(row=0, column=1, padx=(5, 20), pady=8, sticky="w")
        
        self.anti_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(ts, text="안티-밴(차단 방지)", variable=self.anti_var, font=("Arial", 11)).grid(row=1, column=0, columnspan=2, pady=5)
        
        ctk.CTkLabel(ts, text="창 투명도:", font=("Arial", 10)).grid(row=2, column=0, columnspan=2, pady=(2, 0))
        self.t_slider = ctk.CTkSlider(ts, from_=0.3, to=1.0, height=12, command=lambda v: self.attributes('-alpha', v))
        self.t_slider.set(1.0)
        self.t_slider.grid(row=3, column=0, columnspan=2, sticky="ew", padx=25, pady=(0, 5))

        # [로그 탭]
        tl = self.tabview.tab("로그")
        tl.grid_columnconfigure(0, weight=1)
        self.log_box = ctk.CTkTextbox(tl, height=80, font=("Arial", 10))
        self.log_box.grid(row=0, column=0, sticky="nsew")

        # 3. 하단 실행 영역
        self.start_btn = ctk.CTkButton(self, text="매크로 시작 (F9)", font=("Arial", 14, "bold"), 
                                      fg_color="#27ae60", hover_color="#2ecc71", height=35, command=self.start)
        self.start_btn.pack(fill="x", padx=25, pady=(5, 0))

        self.help_label = ctk.CTkLabel(self, text="중지: ESC / 강제종료: 구석으로 던지기", font=("Arial", 9), text_color="gray")
        self.help_label.pack(fill="x", pady=(0, 5))

        keyboard.GlobalHotKeys({'<f9>': self.start}).start()
        keyboard.Listener(on_press=self.on_key).start()

    # --- 기능 함수 생략 (위와 동일) ---
    def update_list(self):
        self.pos_list.configure(state="normal")
        self.pos_list.delete("0.0", "end")
        if not self.target_points: self.pos_list.insert("0.0", "마우스 현재 위치 사용")
        else:
            for i, p in enumerate(self.target_points): self.pos_list.insert("end", f"{i+1}. {int(p[0])}, {int(p[1])}\n")
        self.pos_list.configure(state="disabled")

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
                self.after(0, lambda: self.status_label.configure(text="좌표 추가됨", text_color="#2ecc71"))
                return False
        mouse.Listener(on_click=on_c).start()

    def clear_pos(self):
        self.target_points = []
        self.update_list()
        self.write_log("초기화.")

    def on_key(self, key):
        if key == keyboard.Key.esc: self.stop()

    def stop(self):
        if self.running:
            self.running = False
            self.status_label.configure(text="중지됨", text_color="red")
            self.start_btn.configure(state="normal", text="시작 (F9)")
            def reset():
                time.sleep(2)
                if not self.running: self.status_label.configure(text="준비 완료", text_color="#2ecc71")
            threading.Thread(target=reset, daemon=True).start()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        try:
            for i in range(2, 0, -1):
                if not self.running: return
                self.status_label.configure(text=f"{i}초 후 시작...", text_color="orange")
                time.sleep(1)
            
            self.status_label.configure(text="● 작동 중", text_color="#2ecc71")
            self.start_btn.configure(state="disabled")
            base = float(self.int_entry.get())

            while self.running:
                mx, my = pyautogui.position()
                if mx < 5 and my < 5: self.after(0, self.stop); break
                
                pts = self.target_points if self.target_points else [pyautogui.position()]
                for tx, ty in pts:
                    if not self.running: break
                    target_x, target_y = tx, ty
                    if self.anti_var.get():
                        target_x += random.randint(-2, 2)
                        target_y += random.randint(-2, 2)
                    pyautogui.click(target_x, target_y)
                    if self.anti_var.get():
                        time.sleep(base + random.uniform(-base*0.1, base*0.1))
                    else:
                        time.sleep(base)
        except:
            self.after(0, self.stop)

if __name__ == "__main__":
    app = SlimGodClicker()
    app.mainloop()