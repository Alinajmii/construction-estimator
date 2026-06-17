"""
Construction Quick Estimator - نسخه کامل با اسکرول و ضرایب اصلاح‌شده
تخمین اولیه ساخت ساختمان با امکان تغییر نوع سازه و سقف
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
from datetime import datetime
import json
import os

# ============================================================
# ضرایب مهندسی (بر اساس آیین‌نامه و تجربه)
# ============================================================

COEFFICIENTS = {
    "بتنی": {
        "بتن_میانگین": 0.42,
        "بتن_حداقل": 0.35,
        "بتن_حداکثر": 0.50,
        "میلگرد_میانگین": 45,
        "میلگرد_حداقل": 38,
        "میلگرد_حداکثر": 55,
        "قالب_بندی": 1.2,
        "زمان_اسکلت": 75,
        "ضریب_هزینه": 1.0,
        "توضیح": "سازه بتنی - مناسب برای ساختمان‌های متوسط و بلند"
    },
    "فولادی": {
        "بتن_میانگین": 0.25,
        "بتن_حداقل": 0.20,
        "بتن_حداکثر": 0.32,
        "میلگرد_میانگین": 38,
        "میلگرد_حداقل": 30,
        "میلگرد_حداکثر": 48,
        "قالب_بندی": 0.6,
        "زمان_اسکلت": 50,
        "ضریب_هزینه": 1.15,
        "توضیح": "سازه فولادی - مناسب برای سوله‌ها و ساختمان‌های بلندمرتبه"
    },
    "ترکیبی": {
        "بتن_میانگین": 0.35,
        "بتن_حداقل": 0.28,
        "بتن_حداکثر": 0.42,
        "میلگرد_میانگین": 42,
        "میلگرد_حداقل": 35,
        "میلگرد_حداکثر": 50,
        "قالب_بندی": 0.9,
        "زمان_اسکلت": 65,
        "ضریب_هزینه": 1.08,
        "توضیح": "سازه ترکیبی - بهینه برای ساختمان‌های با دهانه‌های بلند"
    }
}

# ضرایب سقف‌ها
ROOF_COEFFICIENTS = {
    "تیرچه بلوک": {"ضریب": 1.0, "توضیح": "رایج‌ترین سقف در ایران"},
    "وافل": {"ضریب": 1.15, "توضیح": "سقف سبک و یکپارچه - مناسب دهانه‌های بزرگ"},
    "دال بتنی": {"ضریب": 1.3, "توضیح": "سقف سنگین و مقاوم - مناسب مناطق زلزله‌خیز"},
    "کامپوزیت": {"ضریب": 1.05, "توضیح": "سقف با ورق فولادی - سرعت اجرای بالا"}
}

# ضرایب نوع ساختمان
BUILDING_TYPES = {
    "مسکونی": {"ضریب": 1.0, "توضیح": "ساختمان مسکونی - مناسب برای آپارتمان‌ها"},
    "اداری": {"ضریب": 1.15, "توضیح": "ساختمان اداری - نیازمند تأسیسات بیشتر"},
    "تجاری": {"ضریب": 1.25, "توضیح": "ساختمان تجاری - مناسب برای فروشگاه‌ها و مراکز خرید"},
    "صنعتی": {"ضریب": 0.9, "توضیح": "ساختمان صنعتی - سازه سبک‌تر و کاربری خاص"}
}

# زمان‌بندی مراحل اجرا
CONSTRUCTION_PHASES = {
    "گودبرداری و خاکبرداری": {"min": 7, "max": 15},
    "فونداسیون و پی": {"min": 10, "max": 20},
    "اسکلت و ستون‌گذاری": {"min": 20, "max": 40},
    "سقف‌سازی": {"min": 15, "max": 30},
    "دیوارچینی و سفال": {"min": 20, "max": 35},
    "تأسیسات (برق، آب، گاز)": {"min": 15, "max": 25},
    "نازک‌کاری و کف‌سازی": {"min": 20, "max": 35},
    "نما و دکوراسیون": {"min": 15, "max": 25}
}

# ============================================================
# کلاس اصلی برنامه
# ============================================================

class ConstructionEstimator:
    def __init__(self, root):
        self.root = root
        self.root.title("🏗️ Construction Quick Estimator")
        self.root.geometry("950x800")
        self.root.configure(bg='#f0f2f5')
        
        # مقداردهی اولیه
        self.coefficients = COEFFICIENTS
        self.roof_coeffs = ROOF_COEFFICIENTS
        self.building_types = BUILDING_TYPES
        
        # قیمت‌های پیش‌فرض
        self.prices = {
            "بتن": 2500000,
            "میلگرد": 42000,
            "قالب": 350000,
            "کارگر": 1500000
        }
        
        # ایجاد رابط کاربری
        self.setup_ui()
        
        # محاسبه اولیه
        self.calculate()
    
    def setup_ui(self):
        # ==================== هدر ====================
        header = tk.Frame(self.root, bg='#1e3a5f', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🏗️ Construction Quick Estimator",
            font=('Segoe UI', 20, 'bold'),
            bg='#1e3a5f',
            fg='white'
        ).pack(expand=True)
        
        tk.Label(
            header,
            text="تخمین سریع مصالح، هزینه و زمان ساخت ساختمان",
            font=('Segoe UI', 10),
            bg='#1e3a5f',
            fg='#bdc3c7'
        ).pack()
        
        # ==================== کانتینر اصلی با اسکرول ====================
        canvas = tk.Canvas(self.root, bg='#f0f2f5', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f2f5')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # اسکرول با ماوس
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # ==================== فریم ورودی‌ها ====================
        input_frame = tk.LabelFrame(
            scrollable_frame,
            text="📐 اطلاعات پروژه",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#1e3a5f',
            padx=15,
            pady=15
        )
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # ردیف 1: سطح اشغال و تعداد طبقات
        row1 = tk.Frame(input_frame, bg='white')
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="سطح اشغال (متر مربع):", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.area_entry = tk.Entry(row1, font=('Segoe UI', 10), width=15)
        self.area_entry.pack(side=tk.LEFT, padx=(0, 30))
        self.area_entry.insert(0, "180")
        self.area_entry.bind('<KeyRelease>', lambda e: self.calculate())
        
        tk.Label(row1, text="تعداد طبقات:", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.floors_entry = tk.Entry(row1, font=('Segoe UI', 10), width=15)
        self.floors_entry.pack(side=tk.LEFT)
        self.floors_entry.insert(0, "5")
        self.floors_entry.bind('<KeyRelease>', lambda e: self.calculate())
        
        # ردیف 2: نوع سازه و نوع سقف
        row2 = tk.Frame(input_frame, bg='white')
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(row2, text="نوع سازه:", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.structure_var = tk.StringVar(value="بتنی")
        structure_menu = ttk.Combobox(row2, textvariable=self.structure_var, values=list(self.coefficients.keys()), width=15)
        structure_menu.pack(side=tk.LEFT, padx=(0, 30))
        structure_menu.bind('<<ComboboxSelected>>', lambda e: self.calculate())
        
        tk.Label(row2, text="نوع سقف:", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.roof_var = tk.StringVar(value="تیرچه بلوک")
        roof_menu = ttk.Combobox(row2, textvariable=self.roof_var, values=list(self.roof_coeffs.keys()), width=15)
        roof_menu.pack(side=tk.LEFT)
        roof_menu.bind('<<ComboboxSelected>>', lambda e: self.calculate())
        
        # ردیف 3: نوع ساختمان
        row3 = tk.Frame(input_frame, bg='white')
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(row3, text="نوع ساختمان:", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.building_var = tk.StringVar(value="مسکونی")
        building_menu = ttk.Combobox(row3, textvariable=self.building_var, values=list(self.building_types.keys()), width=15)
        building_menu.pack(side=tk.LEFT)
        building_menu.bind('<<ComboboxSelected>>', lambda e: self.calculate())
        
        # ==================== فریم قیمت‌ها ====================
        price_frame = tk.LabelFrame(
            scrollable_frame,
            text="💰 قیمت‌ها (تومان)",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#1e3a5f',
            padx=15,
            pady=15
        )
        price_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # ردیف قیمت‌ها
        price_row1 = tk.Frame(price_frame, bg='white')
        price_row1.pack(fill=tk.X, pady=3)
        
        tk.Label(price_row1, text="بتن (هر متر مکعب):", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.concrete_price = tk.Entry(price_row1, font=('Segoe UI', 10), width=18)
        self.concrete_price.pack(side=tk.LEFT, padx=(0, 30))
        self.concrete_price.insert(0, "2,500,000")
        self.concrete_price.bind('<KeyRelease>', lambda e: self.calculate())
        
        tk.Label(price_row1, text="میلگرد (هر کیلوگرم):", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.steel_price = tk.Entry(price_row1, font=('Segoe UI', 10), width=18)
        self.steel_price.pack(side=tk.LEFT)
        self.steel_price.insert(0, "42,000")
        self.steel_price.bind('<KeyRelease>', lambda e: self.calculate())
        
        price_row2 = tk.Frame(price_frame, bg='white')
        price_row2.pack(fill=tk.X, pady=3)
        
        tk.Label(price_row2, text="قالب‌بندی (هر متر مربع):", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.formwork_price = tk.Entry(price_row2, font=('Segoe UI', 10), width=18)
        self.formwork_price.pack(side=tk.LEFT, padx=(0, 30))
        self.formwork_price.insert(0, "350,000")
        self.formwork_price.bind('<KeyRelease>', lambda e: self.calculate())
        
        tk.Label(price_row2, text="دستمزد کارگر (روزانه):", font=('Segoe UI', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.labor_price = tk.Entry(price_row2, font=('Segoe UI', 10), width=18)
        self.labor_price.pack(side=tk.LEFT)
        self.labor_price.insert(0, "1,500,000")
        self.labor_price.bind('<KeyRelease>', lambda e: self.calculate())
        
        # ==================== دکمه‌ها ====================
        btn_frame = tk.Frame(scrollable_frame, bg='#f0f2f5')
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="🧮 محاسبه مجدد",
            command=self.calculate,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=30,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="📊 خروجی اکسل",
            command=self.export_excel,
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="📄 خروجی PDF",
            command=self.export_pdf,
            bg='#e67e22',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=8
        ).pack(side=tk.LEFT)
        
        # ==================== فریم نتایج ====================
        result_frame = tk.LabelFrame(
            scrollable_frame,
            text="📊 نتایج تخمین",
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#1e3a5f',
            padx=15,
            pady=10
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=('Tahoma', 10),
            bg='#f8f9fa',
            fg='#2c3e50',
            height=18,
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def clean_price(self, text):
        """پاکسازی قیمت از کاما و فاصله"""
        try:
            return float(text.replace(',', '').replace(' ', ''))
        except:
            return 0
    
    def calculate(self, event=None):
        """محاسبه اصلی با ضرایب به‌روز"""
        try:
            # دریافت ورودی‌ها
            area = float(self.area_entry.get())
            floors = float(self.floors_entry.get())
            structure = self.structure_var.get()
            roof_type = self.roof_var.get()
            building_type = self.building_var.get()
            
            # قیمت‌ها
            concrete_price = self.clean_price(self.concrete_price.get())
            steel_price = self.clean_price(self.steel_price.get())
            formwork_price = self.clean_price(self.formwork_price.get())
            labor_price = self.clean_price(self.labor_price.get())
            
            # محاسبه زیربنا
            total_area = area * floors
            
            # ضرایب
            coeff = self.coefficients[structure]
            roof_coeff = self.roof_coeffs[roof_type]["ضریب"]
            building_coeff = self.building_types[building_type]["ضریب"]
            
            # محاسبات با میانگین ضرایب
            concrete_volume = total_area * coeff["بتن_میانگین"] * roof_coeff * building_coeff
            steel_kg = total_area * coeff["میلگرد_میانگین"] * roof_coeff * building_coeff
            formwork_area = total_area * coeff["قالب_بندی"] * roof_coeff * building_coeff
            
            # محدوده‌ها
            concrete_min = total_area * coeff["بتن_حداقل"] * roof_coeff * building_coeff
            concrete_max = total_area * coeff["بتن_حداکثر"] * roof_coeff * building_coeff
            steel_min = total_area * coeff["میلگرد_حداقل"] * roof_coeff * building_coeff
            steel_max = total_area * coeff["میلگرد_حداکثر"] * roof_coeff * building_coeff
            
            # هزینه‌ها
            concrete_cost = concrete_volume * concrete_price
            steel_cost = steel_kg * steel_price
            formwork_cost = formwork_area * formwork_price
            
            # زمان اجرا
            total_days = self.estimate_duration(area, floors, structure)
            labor_cost = total_days * labor_price
            
            # جمع کل
            total_cost = concrete_cost + steel_cost + formwork_cost + labor_cost
            
            # نمایش نتایج
            self.display_results(
                total_area=total_area,
                concrete_volume=concrete_volume,
                concrete_min=concrete_min,
                concrete_max=concrete_max,
                steel_kg=steel_kg,
                steel_min=steel_min,
                steel_max=steel_max,
                formwork_area=formwork_area,
                concrete_cost=concrete_cost,
                steel_cost=steel_cost,
                formwork_cost=formwork_cost,
                labor_cost=labor_cost,
                total_cost=total_cost,
                total_days=total_days,
                structure=structure,
                roof_type=roof_type,
                building_type=building_type,
                roof_desc=self.roof_coeffs[roof_type]["توضیح"],
                building_desc=self.building_types[building_type]["توضیح"],
                structure_desc=coeff["توضیح"]
            )
            
        except ValueError as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"❌ خطا: لطفاً اعداد معتبر وارد کنید.\n{str(e)}")
    
    def estimate_duration(self, area, floors, structure):
        """تخمین زمان اجرا"""
        base_days = 0
        
        if area < 100:
            base_days = 60
        elif area < 200:
            base_days = 80
        elif area < 300:
            base_days = 100
        else:
            base_days = 120
        
        floor_days = floors * 15
        
        if structure == "بتنی":
            structure_days = 0
        elif structure == "فولادی":
            structure_days = -10
        else:
            structure_days = -5
        
        total = base_days + floor_days + structure_days
        phase_days = sum([v["max"] for v in CONSTRUCTION_PHASES.values()])
        total = max(total, phase_days)
        
        return total
    
    def display_results(self, **kwargs):
        """نمایش نتایج"""
        self.result_text.delete(1.0, tk.END)
        
        result = f"""
{'='*65}
🏗️ گزارش تخمین اولیه ساخت ساختمان
{'='*65}

📐 اطلاعات پروژه
{'-'*50}
سطح اشغال:        {float(self.area_entry.get()):,.0f} متر مربع
تعداد طبقات:      {float(self.floors_entry.get()):,.0f}
زیربنای کل:       {kwargs['total_area']:,.0f} متر مربع
نوع سازه:         {kwargs['structure']}
نوع سقف:          {kwargs['roof_type']} ({kwargs['roof_desc']})
نوع ساختمان:      {kwargs['building_type']} ({kwargs['building_desc']})

🧱 مصالح مورد نیاز
{'-'*50}
بتن:              {kwargs['concrete_volume']:,.2f} متر مکعب
                  (محدوده: {kwargs['concrete_min']:,.2f} - {kwargs['concrete_max']:,.2f})

میلگرد:           {kwargs['steel_kg']:,.0f} کیلوگرم ({kwargs['steel_kg']/1000:,.2f} تن)
                  (محدوده: {kwargs['steel_min']:,.0f} - {kwargs['steel_max']:,.0f} کیلوگرم)

قالب‌بندی:        {kwargs['formwork_area']:,.0f} متر مربع

💰 برآورد هزینه (تومان)
{'-'*50}
بتن:              {kwargs['concrete_cost']:,.0f}
میلگرد:           {kwargs['steel_cost']:,.0f}
قالب‌بندی:        {kwargs['formwork_cost']:,.0f}
دستمزد کارگر:     {kwargs['labor_cost']:,.0f}
{'-'*50}
جمع کل:           {kwargs['total_cost']:,.0f}
{'='*65}

⏱️ زمان اجرا (تخمینی)
{'-'*50}
کل زمان:          {kwargs['total_days']:,} روز (~{kwargs['total_days']/30:.1f} ماه)

📋 مراحل اجرا:
"""
        for phase, days in CONSTRUCTION_PHASES.items():
            result += f"   • {phase}: {days['min']}-{days['max']} روز\n"
        
        result += f"""
{'='*65}
📌 نکات مهم:
• این تخمین اولیه بر اساس ضرایب متوسط است.
• برای برآورد دقیق‌تر نیاز به طراحی سازه و محاسبات دقیق است.
• هزینه‌ها به قیمت‌های وارد شده وابسته است.
• محدوده‌های ارائه شده بر اساس ضرایب حداقل و حداکثر محاسبه شده‌اند.
{'='*65}
"""
        
        self.result_text.insert(1.0, result)
    
    def export_excel(self):
        """خروجی اکسل"""
        try:
            area = float(self.area_entry.get())
            floors = float(self.floors_entry.get())
            total_area = area * floors
            
            structure = self.structure_var.get()
            roof_type = self.roof_var.get()
            building_type = self.building_var.get()
            
            coeff = self.coefficients[structure]
            roof_coeff = self.roof_coeffs[roof_type]["ضریب"]
            building_coeff = self.building_types[building_type]["ضریب"]
            
            concrete_vol = total_area * coeff["بتن_میانگین"] * roof_coeff * building_coeff
            steel_kg = total_area * coeff["میلگرد_میانگین"] * roof_coeff * building_coeff
            formwork = total_area * coeff["قالب_بندی"] * roof_coeff * building_coeff
            
            data = {
                "پارامتر": [
                    "سطح اشغال", "تعداد طبقات", "زیربنای کل", "نوع سازه", "نوع سقف", "نوع ساختمان",
                    "بتن (میانگین)", "بتن (حداقل)", "بتن (حداکثر)",
                    "میلگرد (میانگین)", "میلگرد (حداقل)", "میلگرد (حداکثر)",
                    "قالب‌بندی", "هزینه بتن", "هزینه میلگرد", "هزینه قالب", "هزینه کارگر", "جمع کل", "زمان اجرا"
                ],
                "مقدار": [
                    area, floors, total_area, structure, roof_type, building_type,
                    round(concrete_vol, 2),
                    round(total_area * coeff["بتن_حداقل"] * roof_coeff * building_coeff, 2),
                    round(total_area * coeff["بتن_حداکثر"] * roof_coeff * building_coeff, 2),
                    round(steel_kg, 0),
                    round(total_area * coeff["میلگرد_حداقل"] * roof_coeff * building_coeff, 0),
                    round(total_area * coeff["میلگرد_حداکثر"] * roof_coeff * building_coeff, 0),
                    round(formwork, 0),
                    round(concrete_vol * self.clean_price(self.concrete_price.get()), 0),
                    round(steel_kg * self.clean_price(self.steel_price.get()), 0),
                    round(formwork * self.clean_price(self.formwork_price.get()), 0),
                    round(self.estimate_duration(area, floors, structure) * self.clean_price(self.labor_price.get()), 0),
                    round(concrete_vol * self.clean_price(self.concrete_price.get()) + 
                          steel_kg * self.clean_price(self.steel_price.get()) + 
                          formwork * self.clean_price(self.formwork_price.get()) + 
                          self.estimate_duration(area, floors, structure) * self.clean_price(self.labor_price.get()), 0),
                    self.estimate_duration(area, floors, structure)
                ]
            }
            
            df = pd.DataFrame(data)
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"construction_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("موفق", f"فایل با موفقیت ذخیره شد.")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل:\n{str(e)}")
    
    def export_pdf(self):
        """خروجی PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"construction_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if not filename:
                return
            
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            # عنوان
            c.setFont("Helvetica-Bold", 16)
            c.drawString(20, height - 30, "Construction Quick Estimator - Report")
            
            # تاریخ
            c.setFont("Helvetica", 10)
            c.drawString(20, height - 50, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # اطلاعات پروژه
            y = height - 80
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20, y, "Project Information:")
            
            y -= 20
            c.setFont("Helvetica", 10)
            c.drawString(20, y, f"Area: {float(self.area_entry.get()):,.0f} m²")
            y -= 15
            c.drawString(20, y, f"Floors: {float(self.floors_entry.get()):,.0f}")
            y -= 15
            c.drawString(20, y, f"Structure: {self.structure_var.get()}")
            y -= 15
            c.drawString(20, y, f"Roof: {self.roof_var.get()}")
            y -= 15
            c.drawString(20, y, f"Building Type: {self.building_var.get()}")
            
            # نتایج
            y -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20, y, "Estimation Results:")
            
            # دریافت متن نتیجه
            result_text = self.result_text.get(1.0, tk.END).split('\n')
            
            y -= 20
            c.setFont("Helvetica", 9)
            for line in result_text[:30]:
                if y < 50:
                    c.showPage()
                    y = height - 30
                    c.setFont("Helvetica", 9)
                c.drawString(20, y, line[:100])
                y -= 12
            
            c.save()
            messagebox.showinfo("موفق", f"فایل PDF با موفقیت ذخیره شد.")
            
        except ImportError:
            messagebox.showerror("خطا", "برای خروجی PDF نیاز به نصب کتابخانه reportlab است.\nنصب: pip install reportlab")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره PDF:\n{str(e)}")


# ============================================================
# اجرا
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ConstructionEstimator(root)
    root.mainloop()