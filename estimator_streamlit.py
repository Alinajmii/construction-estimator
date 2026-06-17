"""
Construction Quick Estimator - Streamlit Version
تخمین اولیه ساخت ساختمان با رابط کاربری وب
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

# ============================================================
# تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="Construction Quick Estimator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ضرایب مهندسی
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

ROOF_COEFFICIENTS = {
    "تیرچه بلوک": {"ضریب": 1.0, "توضیح": "رایج‌ترین سقف در ایران"},
    "وافل": {"ضریب": 1.15, "توضیح": "سقف سبک و یکپارچه - مناسب دهانه‌های بزرگ"},
    "دال بتنی": {"ضریب": 1.3, "توضیح": "سقف سنگین و مقاوم - مناسب مناطق زلزله‌خیز"},
    "کامپوزیت": {"ضریب": 1.05, "توضیح": "سقف با ورق فولادی - سرعت اجرای بالا"}
}

BUILDING_TYPES = {
    "مسکونی": {"ضریب": 1.0, "توضیح": "ساختمان مسکونی - مناسب برای آپارتمان‌ها"},
    "اداری": {"ضریب": 1.15, "توضیح": "ساختمان اداری - نیازمند تأسیسات بیشتر"},
    "تجاری": {"ضریب": 1.25, "توضیح": "ساختمان تجاری - مناسب برای فروشگاه‌ها"},
    "صنعتی": {"ضریب": 0.9, "توضیح": "ساختمان صنعتی - سازه سبک‌تر و کاربری خاص"}
}

CONSTRUCTION_PHASES = {
    "گودبرداری و خاکبرداری": {"min": 7, "max": 15},
    "فونداسیون و پی": {"min": 10, "max": 20},
    "اسکلت و ستون‌گذاری": {"min": 20, "max": 40},
    "سقف‌سازی": {"min": 15, "max": 30},
    "دیوارچینی و سفال": {"min": 20, "max": 35},
    "تأسیسات": {"min": 15, "max": 25},
    "نازک‌کاری و کف‌سازی": {"min": 20, "max": 35},
    "نما و دکوراسیون": {"min": 15, "max": 25}
}


# ============================================================
# توابع محاسباتی
# ============================================================

def clean_price(text):
    """پاکسازی قیمت از کاما و فاصله"""
    try:
        return float(text.replace(',', '').replace(' ', ''))
    except:
        return 0


def estimate_duration(area, floors, structure):
    """تخمین زمان اجرا"""
    base_days = 60 if area < 100 else 80 if area < 200 else 100 if area < 300 else 120
    floor_days = floors * 15
    structure_days = 0 if structure == "بتنی" else -10 if structure == "فولادی" else -5
    total = base_days + floor_days + structure_days
    phase_days = sum([v["max"] for v in CONSTRUCTION_PHASES.values()])
    return max(total, phase_days)


def calculate_estimate(area, floors, structure, roof_type, building_type, prices):
    """محاسبه اصلی"""
    total_area = area * floors
    
    coeff = COEFFICIENTS[structure]
    roof_coeff = ROOF_COEFFICIENTS[roof_type]["ضریب"]
    building_coeff = BUILDING_TYPES[building_type]["ضریب"]
    
    # مقادیر میانگین
    concrete_vol = total_area * coeff["بتن_میانگین"] * roof_coeff * building_coeff
    steel_kg = total_area * coeff["میلگرد_میانگین"] * roof_coeff * building_coeff
    formwork = total_area * coeff["قالب_بندی"] * roof_coeff * building_coeff
    
    # محدوده‌ها
    concrete_min = total_area * coeff["بتن_حداقل"] * roof_coeff * building_coeff
    concrete_max = total_area * coeff["بتن_حداکثر"] * roof_coeff * building_coeff
    steel_min = total_area * coeff["میلگرد_حداقل"] * roof_coeff * building_coeff
    steel_max = total_area * coeff["میلگرد_حداکثر"] * roof_coeff * building_coeff
    
    # هزینه‌ها
    concrete_cost = concrete_vol * prices["بتن"]
    steel_cost = steel_kg * prices["میلگرد"]
    formwork_cost = formwork * prices["قالب"]
    
    total_days = estimate_duration(area, floors, structure)
    labor_cost = total_days * prices["کارگر"]
    
    total_cost = concrete_cost + steel_cost + formwork_cost + labor_cost
    
    return {
        "total_area": total_area,
        "concrete_vol": concrete_vol,
        "concrete_min": concrete_min,
        "concrete_max": concrete_max,
        "steel_kg": steel_kg,
        "steel_min": steel_min,
        "steel_max": steel_max,
        "formwork": formwork,
        "concrete_cost": concrete_cost,
        "steel_cost": steel_cost,
        "formwork_cost": formwork_cost,
        "labor_cost": labor_cost,
        "total_cost": total_cost,
        "total_days": total_days,
        "structure_desc": coeff["توضیح"],
        "roof_desc": ROOF_COEFFICIENTS[roof_type]["توضیح"],
        "building_desc": BUILDING_TYPES[building_type]["توضیح"]
    }


# ============================================================
# رابط کاربری Streamlit
# ============================================================

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a5f 0%, #2E86AB 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
    <h1 style="color: white; text-align: center; margin: 0;">🏗️ Construction Quick Estimator</h1>
    <p style="color: #bdc3c7; text-align: center; margin: 5px 0 0 0;">تخمین سریع مصالح، هزینه و زمان ساخت ساختمان</p>
</div>
""", unsafe_allow_html=True)

# دو ستون اصلی
col1, col2 = st.columns([1, 1.5])

# ============================================================
# ستون چپ - ورودی‌ها
# ============================================================
with col1:
    st.markdown("### 📐 اطلاعات پروژه")
    
    # ورودی‌های اصلی
    area = st.number_input("سطح اشغال (متر مربع)", min_value=10, max_value=10000, value=180, step=10)
    floors = st.number_input("تعداد طبقات", min_value=1, max_value=50, value=5, step=1)
    
    structure = st.selectbox("نوع سازه", options=list(COEFFICIENTS.keys()))
    roof_type = st.selectbox("نوع سقف", options=list(ROOF_COEFFICIENTS.keys()))
    building_type = st.selectbox("نوع ساختمان", options=list(BUILDING_TYPES.keys()))
    
    st.markdown("---")
    st.markdown("### 💰 قیمت‌ها (تومان)")
    
    concrete_price = st.text_input("بتن (هر متر مکعب)", value="2,500,000")
    steel_price = st.text_input("میلگرد (هر کیلوگرم)", value="42,000")
    formwork_price = st.text_input("قالب‌بندی (هر متر مربع)", value="350,000")
    labor_price = st.text_input("دستمزد کارگر (روزانه)", value="1,500,000")
    
    # دکمه محاسبه
    if st.button("🧮 محاسبه کن", use_container_width=True, type="primary"):
        st.session_state['calculate'] = True
    
    if 'calculate' not in st.session_state:
        st.session_state['calculate'] = True

# ============================================================
# ستون راست - نتایج
# ============================================================
with col2:
    st.markdown("### 📊 نتایج تخمین")
    
    if st.session_state.get('calculate', True):
        try:
            # تبدیل قیمت‌ها
            prices = {
                "بتن": clean_price(concrete_price),
                "میلگرد": clean_price(steel_price),
                "قالب": clean_price(formwork_price),
                "کارگر": clean_price(labor_price)
            }
            
            # محاسبه
            result = calculate_estimate(area, floors, structure, roof_type, building_type, prices)
            
            # نمایش نتایج در کارت‌ها
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("زیربنای کل", f"{result['total_area']:,.0f} m²")
                st.metric("بتن", f"{result['concrete_vol']:,.2f} m³", 
                         delta=f"{result['concrete_min']:.1f} - {result['concrete_max']:.1f}")
            
            with col_b:
                st.metric("میلگرد", f"{result['steel_kg']:,.0f} kg", 
                         delta=f"{result['steel_min']:,.0f} - {result['steel_max']:,.0f}")
                st.metric("قالب‌بندی", f"{result['formwork']:,.0f} m²")
            
            with col_c:
                st.metric("زمان اجرا", f"{result['total_days']:,} روز", 
                         delta=f"~{result['total_days']/30:.1f} ماه")
                st.metric("هزینه کل", f"{result['total_cost']:,.0f} تومان")
            
            # گزارش کامل
            with st.expander("📋 گزارش کامل", expanded=True):
                st.markdown(f"""
                **📐 اطلاعات پروژه**
                - سطح اشغال: {area:,.0f} متر مربع
                - تعداد طبقات: {floors:,.0f}
                - زیربنای کل: {result['total_area']:,.0f} متر مربع
                - نوع سازه: {structure} ({result['structure_desc']})
                - نوع سقف: {roof_type} ({result['roof_desc']})
                - نوع ساختمان: {building_type} ({result['building_desc']})
                
                **🧱 مصالح مورد نیاز**
                - بتن: {result['concrete_vol']:,.2f} متر مکعب (محدوده: {result['concrete_min']:,.2f} - {result['concrete_max']:,.2f})
                - میلگرد: {result['steel_kg']:,.0f} کیلوگرم ({result['steel_kg']/1000:,.2f} تن) (محدوده: {result['steel_min']:,.0f} - {result['steel_max']:,.0f})
                - قالب‌بندی: {result['formwork']:,.0f} متر مربع
                
                **💰 برآورد هزینه**
                - بتن: {result['concrete_cost']:,.0f} تومان
                - میلگرد: {result['steel_cost']:,.0f} تومان
                - قالب‌بندی: {result['formwork_cost']:,.0f} تومان
                - دستمزد کارگر: {result['labor_cost']:,.0f} تومان
                - **جمع کل: {result['total_cost']:,.0f} تومان**
                
                **⏱️ زمان اجرا**
                - کل زمان: {result['total_days']:,} روز (~{result['total_days']/30:.1f} ماه)
                """)
                
                st.markdown("**📋 مراحل اجرا:**")
                for phase, days in CONSTRUCTION_PHASES.items():
                    st.write(f"• {phase}: {days['min']}-{days['max']} روز")
            
            # دکمه‌های خروجی
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                # خروجی Excel
                if st.button("📊 خروجی Excel", use_container_width=True):
                    data = {
                        "پارامتر": ["سطح اشغال", "طبقات", "زیربنا", "نوع سازه", "نوع سقف", "نوع ساختمان",
                                   "بتن", "میلگرد", "قالب‌بندی", "زمان اجرا", "هزینه کل"],
                        "مقدار": [area, floors, result['total_area'], structure, roof_type, building_type,
                                 round(result['concrete_vol'], 2), round(result['steel_kg'], 0), 
                                 round(result['formwork'], 0), result['total_days'], round(result['total_cost'], 0)]
                    }
                    df = pd.DataFrame(data)
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name="Estimation", index=False)
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 دانلود Excel",
                        data=output,
                        file_name=f"construction_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
            with col_dl2:
                # خروجی PDF (با استفاده از text)
                if st.button("📄 خروجی PDF", use_container_width=True):
                    report_text = f"""
Construction Quick Estimator - Report
==================================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PROJECT INFORMATION
--------------------------------------------------
Area: {area:,.0f} m²
Floors: {floors:,.0f}
Total Area: {result['total_area']:,.0f} m²
Structure: {structure}
Roof: {roof_type}
Building Type: {building_type}

MATERIALS
--------------------------------------------------
Concrete: {result['concrete_vol']:,.2f} m³ (Range: {result['concrete_min']:,.2f} - {result['concrete_max']:,.2f})
Steel: {result['steel_kg']:,.0f} kg ({result['steel_kg']/1000:,.2f} ton)
Formwork: {result['formwork']:,.0f} m²

COST ESTIMATION
--------------------------------------------------
Concrete: {result['concrete_cost']:,.0f} Toman
Steel: {result['steel_cost']:,.0f} Toman
Formwork: {result['formwork_cost']:,.0f} Toman
Labor: {result['labor_cost']:,.0f} Toman
--------------------------------------------------
TOTAL: {result['total_cost']:,.0f} Toman

DURATION
--------------------------------------------------
Total Days: {result['total_days']:,} days (~{result['total_days']/30:.1f} months)
"""
                    st.download_button(
                        label="📥 دانلود PDF",
                        data=report_text,
                        file_name=f"construction_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            st.info("💡 نکته: این تخمین اولیه بر اساس ضرایب متوسط است. برای برآورد دقیق‌تر نیاز به طراحی سازه و محاسبات دقیق است.")
            
        except Exception as e:
            st.error(f"❌ خطا در محاسبه: {str(e)}")

# ============================================================
# فوتر
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px;'>"
    "Construction Quick Estimator v2.0 | توسعه داده شده با Streamlit"
    "</div>",
    unsafe_allow_html=True
)