import customtkinter as ctk
import pyautogui
from pynput import keyboard, mouse
import threading
import time
import random
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green") # 조금 더 세련된 초록색

class SlimGodClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Click Master Mini")
        self.geometry("360x520") # 한 손에 들어오는 사이즈
        self.attributes('-topmost', True)
        
        self.running = False
        self.target_points = []
        self.target_image = None

        # --- 메인 라벨 ---
        self.status_label = ctk.CTkLabel(self, text="준비 완료", font=("Arial", 16, "bold"), text_color="#2ecc71")
        self.status_label.pack(pady=10)

        # --- 탭 구성 (작게) ---
        self.tabview = ctk.CTkTabview(self, width=320, height=220)
        self.tabview.pack(pady=5)
        self.tabview.add("📍 좌표")
        self.tabview.add("🖼️ 이미지")
        self.tabview.add("📜 로그")

        # [탭 1] 다중 좌표
        self.pos_list = ctk.CTkTextbox(self.tabview.tab("📍 좌표"), width=300, height=80, font=("Arial", 11))
        self.pos_list.pack(pady=5)
        self.update_list()
        
        btn_f = ctk.CTkFrame(self.tabview.tab("📍 좌표"), fg_color="transparent")
        btn_f.pack()
        ctk.CTkButton(btn_f, text="+ 추가", command=self.add_pos, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="초기화", fg_color="#c0392b", command=self.clear_pos, width=80).pack(side="left", padx=5)

        # [탭 2] 이미지 인식
        self.img_info = ctk.CTkLabel(self.tabview.tab("🖼️ 이미지"), text="이미지 미등록", text_color="gray")
        self.img_info.pack(pady=20)
        ctk.CTkButton(self.tabview.tab("🖼️ 이미지"), text="파일 불러오기", command=self.load_img).pack()

        # [탭 3] 로그
        self.log_box = ctk.CTkTextbox(self.tabview.tab("📜 로그"), width=300, height=140, font=("Arial", 10))
        self.log_box.pack()

        # --- 설정 섹션 ---
        set_f = ctk.CTkFrame(self, fg_color="transparent")
        set_f.pack(pady=10)
        
        ctk.CTkLabel(set_f, text="간격(초):").pack(side="left", padx=5)
        self.int_entry = ctk.CTkEntry(set_f, width=50)
        self.int_entry.insert(0, "0.1")
        self.int_entry.pack(side="left", padx=5)

        self.anti_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="안티-밴(랜덤 모드) 활성화", variable=self.anti_var, font=("Arial", 11)).pack()

        # 투명도 (슬림하게)
        self.t_slider = ctk.CTkSlider(self, from_=0.3, to=1.0, height=15, command=lambda v: self.attributes('-alpha', v))
        self.t_slider.set(1.0)
        self.t_slider.pack(pady=(15,0), padx=50)

        # 시작 버튼 (강조)
        self.start_btn = ctk.CTkButton(self, text="매크로 시작 (ESC 종료)", font=("Arial", 15, "bold"), 
                                      fg_color="#27ae60", hover_color="#2ecc71", height=45, command=self.start)
        self.start_btn.pack(pady=20, fill="x", padx=30)

        keyboard.Listener(on_press=self.on_key).start()

    def write_log(self, m):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {m}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def add_pos(self):
        self.status_label.configure(text="화면 클릭 대기 중...", text_color="orange")
        def on_c(x, y, b, p):
            if p:
                self.target_points.append((x, y))
                self.update_list()
                self.status_label.configure(text="좌표 추가 완료", text_color="#2ecc71")
                return False
        mouse.Listener(on_click=on_c).start()

    def clear_pos(self):
        self.target_points = []
        self.update_list()
        self.write_log("좌표 초기화.")

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

    def on_key(self, key):
        if key == keyboard.Key.esc: self.stop()

    def stop(self):
        if self.running:
            self.running = False
            self.status_label.configure(text="중단됨 (ESC)", text_color="red")
            self.start_btn.configure(state="normal", text="매크로 다시 시작")

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        try:
            for i in range(3, 0, -1):
                self.status_label.configure(text=f"{i}초 후 시작...")
                time.sleep(1)
            
            if not self.running: return
            self.status_label.configure(text="● 작동 중", text_color="#2ecc71")
            self.start_btn.configure(state="disabled")
            
            base = float(self.int_entry.get())
            mode = self.tabview.get()

            while self.running:
                # 세이프존 (0,0)
                mx, my = pyautogui.position()
                if mx < 5 and my < 5: self.stop(); break

                if mode == "📍 좌표":
                    pts = self.target_points if self.target_points else [pyautogui.position()]
                    for tx, ty in pts:
                        if not self.running: break
                        self.click(tx, ty)
                        self.s_sleep(base)
                elif mode == "🖼️ 이미지":
                    try:
                        l = pyautogui.locateOnScreen(self.target_image, confidence=0.8)
                        if l: 
                            c = pyautogui.center(l)
                            self.click(c.x, c.y)
                    except: pass
                    self.s_sleep(base)
        except: self.stop()

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