import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import pyautogui
import pygetwindow as gw
import keyboard
from deep_translator import GoogleTranslator
import json
import os
from pynput.keyboard import Key, Controller as KeyboardController
import random
from PIL import Image, ImageTk
import base64
from io import BytesIO

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FloatingTranslator(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("⚡ Quick Translate")
        self.geometry("360x230")
        self.resizable(False, False)
        self.attributes('-alpha', 0.88)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = screen_w - 380
        y = screen_h - 310
        self.geometry(f"360x230+{x}+{y}")
        
        self.colors = {
            'bg': '#0D1117', 'card': '#161B22', 'border': '#30363D',
            'accent': '#58A6FF', 'accent_hover': '#79B8FF', 'text': '#F0F6FC',
            'text_secondary': '#8B949E', 'success': '#3FB950', 'danger': '#F85149',
            'warning': '#D29922', 'input_bg': '#0D1117'
        }
        
        self.configure(fg_color=self.colors['bg'])
        
        self.personas = {
            "👤 Normal": {"icon": "👤", "name": "Normal", "color": "#58A6FF"},
            "😎 Gamer": {"icon": "😎", "name": "Gamer", "color": "#9B59B6"},
            "😈 Toxic": {"icon": "😈", "name": "Toxic", "color": "#FF4444"},
            "🗿 Sigma": {"icon": "🗿", "name": "Sigma", "color": "#4A6741"},
            "🥶 Chill": {"icon": "🥶", "name": "Chill", "color": "#88AACC"},
        }
        
        self.languages = {
            "🇬🇧 EN": "en", "🇸🇦 AR": "ar", "🇯🇵 JP": "ja",
            "🇰🇷 KR": "ko", "🇨🇳 CN": "zh-CN", "🇪🇸 ES": "es",
            "🇫🇷 FR": "fr", "🇩🇪 DE": "de", "🇷🇺 RU": "ru",
            "🇹🇷 TR": "tr", "🇧🇷 PT": "pt", "🇮🇹 IT": "it"
        }
        
        self.config_file = "settings.json"
        self.load_config()
        self.keyboard_controller = KeyboardController()
        
        self.create_widgets()
        
        self.persona_var = ctk.StringVar(value=self.config.get("persona", "👤 Normal"))
        self.select_persona(self.persona_var.get())
        
        keyboard.add_hotkey("ctrl+/", self.toggle_visibility)
        keyboard.add_hotkey("ctrl+1", self.translate_and_send)
        
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, lambda: self.persian_text.focus_set())
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                raise FileNotFoundError
        except:
            self.config = {
                "typing_delay": 0.03, "window_title": "",
                "auto_enter": True, "target_lang": "en",
                "persona": "👤 Normal"
            }
    
    def save_config(self):
        try:
            self.config["typing_delay"] = float(self.delay_var.get())
            self.config["window_title"] = self.window_var.get()
            self.config["auto_enter"] = self.auto_enter_var.get()
            self.config["target_lang"] = self.lang_codes[self.lang_var.get()]
            self.config["persona"] = self.persona_var.get()
        except:
            pass
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def do_move(self, event):
        if hasattr(self, 'x') and self.x is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")
    
    def toggle_visibility(self):
        try:
            if self.winfo_viewable():
                self.withdraw()
            else:
                self.deiconify()
                self.lift()
                self.attributes('-topmost', True)
                self.after(50, lambda: self.persian_text.focus_set())
        except:
            pass
    
    def create_widgets(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Header
        header = ctk.CTkFrame(main, fg_color="transparent", height=28)
        header.pack(fill="x", pady=(0, 4))
        header.pack_propagate(False)
        
        self.persona_icon_label = ctk.CTkLabel(header, text="👤", font=ctk.CTkFont(size=16))
        self.persona_icon_label.pack(side="left")
        
        self.persona_name_label = ctk.CTkLabel(header, text="Normal", font=ctk.CTkFont(size=11, weight="bold"), text_color="#58A6FF")
        self.persona_name_label.pack(side="left", padx=(4, 0))
        
        persona_frame = ctk.CTkFrame(header, fg_color="transparent")
        persona_frame.pack(side="right")
        
        for icon in ["👤", "😎", "😈", "🗿", "🥶"]:
            full_key = [k for k in self.personas.keys() if k.startswith(icon)][0]
            data = self.personas[full_key]
            btn = ctk.CTkButton(
                persona_frame, text=icon,
                width=26, height=24, corner_radius=5,
                fg_color="transparent",
                hover_color=data['color'],
                font=ctk.CTkFont(size=11),
                command=lambda k=full_key: self.select_persona(k)
            )
            btn.pack(side="left", padx=1)
        
        # Text box
        text_frame = ctk.CTkFrame(main, fg_color=self.colors['card'], corner_radius=10, border_width=1, border_color=self.colors['border'])
        text_frame.pack(fill="x", pady=(0, 5))
        
        self.persian_text = ctk.CTkTextbox(
            text_frame, height=65,
            font=ctk.CTkFont(size=13),
            corner_radius=0, border_width=0,
            fg_color="transparent",
            text_color=self.colors['text']
        )
        self.persian_text.pack(fill="x", padx=4, pady=4)
        
        self.persian_text.insert("1.0", "متن فارسی رو اینجا بنویس...")
        self.persian_text.configure(text_color=self.colors['text_secondary'])
        self.persian_text.bind("<FocusIn>", self.clear_placeholder)
        self.persian_text.bind("<FocusOut>", self.add_placeholder)
        
        # Bottom row
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.pack(fill="x")
        
        current_lang_code = self.config.get("target_lang", "en")
        current_lang_name = "🇬🇧 EN"
        for name, code in self.languages.items():
            if code == current_lang_code:
                current_lang_name = name
                break
        
        self.lang_var = ctk.StringVar(value=current_lang_name)
        self.lang_codes = self.languages
        
        lang_combo = ctk.CTkComboBox(
            bottom, variable=self.lang_var,
            values=list(self.languages.keys()),
            width=72, height=30,
            font=ctk.CTkFont(size=10),
            fg_color=self.colors['card'],
            border_color=self.colors['border'],
            button_color=self.colors['border'],
            dropdown_font=ctk.CTkFont(size=10)
        )
        lang_combo.pack(side="left", padx=(0, 4))
        
        self.send_btn = ctk.CTkButton(
            bottom, text="🚀 Send (Ctrl+1)",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            text_color="#000000",
            command=self.translate_and_send
        )
        self.send_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkButton(
            bottom, text="⚙️",
            width=32, height=32,
            corner_radius=8,
            fg_color=self.colors['card'],
            hover_color=self.colors['border'],
            text_color=self.colors['text'],
            command=self.open_settings
        ).pack(side="left", padx=(0, 4))
        
        ctk.CTkButton(
            bottom, text="✕",
            width=32, height=32,
            corner_radius=8,
            fg_color=self.colors['card'],
            hover_color=self.colors['danger'],
            text_color=self.colors['text'],
            command=self.withdraw
        ).pack(side="left")
        
        # ===== FOOTER =====
        footer = ctk.CTkFrame(main, fg_color="#1a1a1a", height=36)
        footer.pack(fill="x", pady=(5, 0))
        footer.pack_propagate(False)
        
        footer_inner = ctk.CTkFrame(footer, fg_color="transparent")
        footer_inner.pack(expand=True)
        
        # عکس
        try:
           
            image_base64 = "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"
            
            
            img_data = base64.b64decode(image_base64)
            img = Image.open(BytesIO(img_data))
            img = img.resize((50, 50), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            avatar_label = ctk.CTkLabel(footer_inner, text="")
            avatar_label.configure(image=photo)
            avatar_label.image = photo
            avatar_label.pack(side="left", padx=(0, 6))
        except:
            pass
        
        ctk.CTkLabel(
            footer_inner,
            text="Made by [SHADOW.KAGERIO]",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#CCCCCC"
        ).pack(side="left")
        
        ctk.CTkLabel(footer_inner, text="  •  ", font=ctk.CTkFont(size=10), text_color="#555555").pack(side="left")
        
        ctk.CTkLabel(
            footer_inner,
            text="v6.0",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(side="left")
    
    def clear_placeholder(self, event=None):
        if self.persian_text.get("1.0", "end-1c").strip() == "متن فارسی رو اینجا بنویس...":
            self.persian_text.delete("1.0", "end")
            self.persian_text.configure(text_color=self.colors['text'])
    
    def add_placeholder(self, event=None):
        if not self.persian_text.get("1.0", "end-1c").strip():
            self.persian_text.insert("1.0", "متن فارسی رو اینجا بنویس...")
            self.persian_text.configure(text_color=self.colors['text_secondary'])
    
    def open_settings(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("450x420")
        settings_win.resizable(False, False)
        settings_win.attributes('-topmost', True)
        settings_win.configure(fg_color=self.colors['bg'])
        
        content = ctk.CTkFrame(settings_win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="⚙️ Settings", font=ctk.CTkFont(size=18, weight="bold"), text_color=self.colors['text']).pack(anchor="w", pady=(0, 18))
        
        s1 = ctk.CTkFrame(content, fg_color=self.colors['card'], corner_radius=10, border_width=1, border_color=self.colors['border'])
        s1.pack(fill="x", pady=(0, 10))
        s1i = ctk.CTkFrame(s1, fg_color="transparent")
        s1i.pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(s1i, text="⌨️ Typing Speed (seconds)", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors['text']).pack(anchor="w", pady=(0, 6))
        
        df = ctk.CTkFrame(s1i, fg_color="transparent")
        df.pack(fill="x")
        self.delay_var = ctk.StringVar(value=str(self.config["typing_delay"]))
        ctk.CTkButton(df, text="−", width=28, height=28, corner_radius=6, fg_color=self.colors['border'], text_color=self.colors['text'], command=lambda: self.adjust_delay(-0.01)).pack(side="left", padx=(0, 6))
        ctk.CTkEntry(df, textvariable=self.delay_var, width=70, height=28, justify="center", font=ctk.CTkFont(size=12), fg_color=self.colors['input_bg'], border_color=self.colors['border']).pack(side="left", padx=(0, 6))
        ctk.CTkButton(df, text="+", width=28, height=28, corner_radius=6, fg_color=self.colors['border'], text_color=self.colors['text'], command=lambda: self.adjust_delay(0.01)).pack(side="left")
        
        s2 = ctk.CTkFrame(content, fg_color=self.colors['card'], corner_radius=10, border_width=1, border_color=self.colors['border'])
        s2.pack(fill="x", pady=(0, 10))
        s2i = ctk.CTkFrame(s2, fg_color="transparent")
        s2i.pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(s2i, text="🎯 Game Window", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors['text']).pack(anchor="w", pady=(0, 6))
        
        wf = ctk.CTkFrame(s2i, fg_color="transparent")
        wf.pack(fill="x")
        self.window_var = ctk.StringVar(value=self.config["window_title"])
        self.window_combo = ctk.CTkComboBox(wf, variable=self.window_var, values=self.get_all_windows(), width=260, height=28, font=ctk.CTkFont(size=11), fg_color=self.colors['input_bg'], border_color=self.colors['border'], button_color=self.colors['border'])
        self.window_combo.pack(side="left", padx=(0, 6))
        ctk.CTkButton(wf, text="↻", width=28, height=28, corner_radius=6, fg_color=self.colors['border'], text_color=self.colors['text'], command=self.refresh_windows).pack(side="left")
        
        s3 = ctk.CTkFrame(content, fg_color=self.colors['card'], corner_radius=10, border_width=1, border_color=self.colors['border'])
        s3.pack(fill="x")
        s3i = ctk.CTkFrame(s3, fg_color="transparent")
        s3i.pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(s3i, text="🔧 Options", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors['text']).pack(anchor="w", pady=(0, 6))
        
        self.auto_enter_var = ctk.BooleanVar(value=self.config["auto_enter"])
        ctk.CTkCheckBox(s3i, text="Auto-send with Enter", variable=self.auto_enter_var, font=ctk.CTkFont(size=11), text_color=self.colors['text'], fg_color=self.colors['accent'], border_color=self.colors['border'], checkmark_color="#000000").pack(anchor="w")
        
        ctk.CTkButton(
            content, text="💾 Save Settings", height=38,
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=10,
            fg_color=self.colors['accent'], hover_color=self.colors['accent_hover'],
            text_color="#000000", command=self.save_settings
        ).pack(fill="x", pady=(12, 0))
    
    def adjust_delay(self, amount):
        try:
            current = float(self.delay_var.get())
            new = max(0.01, min(0.5, current + amount))
            self.delay_var.set(f"{new:.2f}")
        except:
            self.delay_var.set("0.03")
    
    def get_all_windows(self):
        windows = []
        for w in gw.getAllWindows():
            if w.title and w.title.strip() and len(w.title) < 80:
                windows.append(w.title)
        return windows if windows else ["No windows found"]
    
    def refresh_windows(self):
        self.window_combo.configure(values=self.get_all_windows())
    
    def select_persona(self, persona_key):
        if persona_key not in self.personas:
            persona_key = "👤 Normal"
        self.persona_var.set(persona_key)
        persona = self.personas[persona_key]
        self.persona_icon_label.configure(text=persona['icon'])
        self.persona_name_label.configure(text=persona['name'], text_color=persona['color'])
    
    def translate_text(self, text, target_lang="en"):
        try:
            translator = GoogleTranslator(source='fa', target=target_lang)
            base = translator.translate(text)
        except:
            try:
                translator = GoogleTranslator(source='auto', target=target_lang)
                base = translator.translate(text)
            except:
                return None
        
        persona_key = self.persona_var.get()
        
        if persona_key == "👤 Normal":
            return base
        elif persona_key == "😎 Gamer":
            return self._gamer(base)
        elif persona_key == "😈 Toxic":
            return self._toxic(base)
        elif persona_key == "🗿 Sigma":
            return self._sigma(base)
        elif persona_key == "🥶 Chill":
            return self._chill(base)
        return base
    
    def _gamer(self, t):
        m = {"hello":"yo","hi":"wassup","good":"pog","nice":"sheesh","well":"wp","sorry":"my bad","go":"GOOO","yes":"bet","no":"nah","thanks":"thx","friend":"homie","bro":"bruh","bye":"peace","really":"fr","crazy":"goated","best":"GOAT","you":"u","bad":"cringe","easy":"ez"}
        w = t.lower().split()
        r = " ".join([m.get(x.strip(",.!?"), x) for x in w])
        return r.upper() if any(k in r.lower() for k in ['pog','ez','goat','sheesh','gooo']) else r
    
    def _toxic(self, t):
        a = random.choice([" sit down lol"," ez"," L + ratio"," skill issue"," cope"," lil bro"," 💀"])
        m = {"hello":"yo","hi":"sup","good":"mid","nice":"lucky","sorry":"cry","thanks":"whatever","bad":"garbage","easy":"free","well":"whatever","best":"worst","game":"match","friend":"random"}
        w = t.lower().split()
        return " ".join([m.get(x.strip(",.!?"), x) for x in w]) + a
    
    def _sigma(self, t):
        a = random.choice([" . . ."," *sigh*"," whatever"," keep grinding"," stay focused","",""])
        m = {"hello":"hm","hi":"hey","good":"solid","nice":"decent","well":"fine","sorry":"my fault","thanks":"appreciate it","friend":"associate","bad":"suboptimal","easy":"light work","yes":"indeed","no":"negative","go":"proceed","win":"expected","game":"session"}
        w = t.lower().split()
        return " ".join([m.get(x.strip(",.!?"), x) for x in w]) + a
    
    def _chill(self, t):
        a = random.choice([" lol"," fr"," man"," you know","",""])
        m = {"hello":"yo","hi":"heyyy","good":"cool","nice":"chill","well":"all good","sorry":"no worries","thanks":"thx man","friend":"bro","bad":"eh","easy":"breeze","yes":"sure thing","no":"nahh","go":"let's goo","win":"gg","game":"game","really":"for real","crazy":"wild","best":"goated"}
        w = t.lower().split()
        return " ".join([m.get(x.strip(",.!?"), x) for x in w]) + a
    
    def focus_game(self):
        window_title = self.window_var.get()
        if not window_title or window_title == "No windows found":
            return False
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                win = windows[0]
                if win.isMinimized: win.restore()
                win.activate()
                time.sleep(0.3)
                return True
            for w in gw.getAllWindows():
                if w.title and window_title.lower() in w.title.lower():
                    if w.isMinimized: w.restore()
                    w.activate()
                    time.sleep(0.3)
                    return True
            return False
        except:
            return False
    
    def type_text(self, text):
        try: delay = float(self.delay_var.get())
        except: delay = 0.03
        try:
            for char in text:
                self.keyboard_controller.type(char)
                time.sleep(delay)
            return True
        except:
            try:
                pyautogui.write(text, interval=delay)
                return True
            except:
                return False
    
    def translate_and_send(self, event=None):
        text = self.persian_text.get("1.0", "end-1c").strip()
        if not text or text == "متن فارسی رو اینجا بنویس...":
            return
        
        target_lang = self.lang_codes.get(self.lang_var.get(), "en")
        persona = self.personas.get(self.persona_var.get(), self.personas["👤 Normal"])
        
        self.send_btn.configure(state="disabled", text="⏳...", fg_color=persona['color'])
        
        def worker():
            translated = self.translate_text(text, target_lang)
            if translated:
                if self.focus_game():
                    time.sleep(0.2)
                    if self.type_text(translated):
                        if self.auto_enter_var.get():
                            time.sleep(0.15)
                            self.keyboard_controller.press(Key.enter)
                            self.keyboard_controller.release(Key.enter)
                        # فقط متن پاک بشه، پنجره بمونه
                        self.after(0, lambda: self.persian_text.delete("1.0", "end"))
                        self.after(0, lambda: self.add_placeholder())
            self.after(0, lambda: self.send_btn.configure(state="normal", text="🚀 Send (Ctrl+1)", fg_color=self.colors['accent']))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def save_settings(self):
        try:
            self.save_config()
            messagebox.showinfo("✅", "Settings saved!")
        except:
            messagebox.showerror("❌", "Error!")
    
    def on_closing(self):
        try:
            self.save_config()
            keyboard.unhook_all()
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = FloatingTranslator()
    app.mainloop()