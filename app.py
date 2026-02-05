import streamlit as st

st.set_page_config(page_title="Pediatric Obesity Dosing", layout="centered")

st.title("🩺 تطبيق حساب جرعات الأدوية للأطفال البدينين")
st.write("بناءً على بروتوكولات وحدة العناية المشددة")

# --- 1. مدخلات المريض ---
with st.sidebar:
    st.header("بيانات الطفل")
    tbw = st.number_input("الوزن الحالي (Total Body Weight) بالكغ", min_value=1.0, value=70.0)
    height_cm = st.number_input("الطول بالسم", min_value=30.0, value=150.0)
    height_m = height_cm / 100
    
    bmi_actual = tbw / (height_m ** 2)
    st.info(f"BMI الحالي: {bmi_actual:.2f}")

    # مدخلات المخططات (Centiles)
    st.subheader("قيم المخططات (من CDC/WHO)")
    bmi_50 = st.number_input("قيمة BMI على خط 50 centile", value=17.3) # مثال لسن 12 سنة
    bmi_98 = st.number_input("قيمة BMI على خط 98 centile", value=24.0)

# --- 2. تصنيف الحالة ---
is_obese = bmi_actual >= bmi_98
status = "بدين (Obese)" if is_obese else "غير بدين"

st.subheader(f"الحالة: {status}")

# حساب الوزن المثالي IBW والوزن الخالي من الدهون LBW
ibw = bmi_50 * (height_m ** 2)
lbw = ibw + 0.29 * (tbw - ibw)

# --- 3. قاعدة بيانات الأدوية المستخرجة من الصور ---
# الصيغة: 'اسم الدواء': ['النوع', 'عامل التصحيح F إن وجد', 'ملاحظات']
drugs_db = {
    # Antimicrobials
    "Aciclovir": ["IBW", None, "استخدام الوزن المثالي"],
    "Amikacin": ["ABW", 0.4, "عامل التصحيح 0.4"],
    "Amphotericin B": ["TBW", None, "الوزن الكلي"],
    "Ciprofloxacin": ["ABW", 0.45, "عامل التصحيح 0.45"],
    "Gentamicin": ["ABW", 0.4, "عامل التصحيح 0.4"],
    "Tobramycin": ["ABW", 0.4, "عامل التصحيح 0.4"],
    "Vancomycin": ["TBW", None, "مراقبة المستويات، لا تتجاوز الجرعة القصوى للبالغين"],
    "Voriconazole": ["IBW", None, "خطر السمية إذا استخدم TBW"],
    "Rifampicin": ["IBW", None, "استخدام TBW قد يؤدي لسمية"],
    "Macrolides": ["IBW", None, ""],
    
    # Anticonvulsants
    "Benzodiazepines": ["IBW", None, "قد تحتاج جرعة تحميل بناءً على TBW"],
    "Levetiracetam": ["ABW", 0.25, "عامل التصحيح 0.25"],
    "Phenytoin (Loading)": ["ABW", 0.3, "جرعة التحميل تعتمد على ABW (F=0.3)"],
    "Phenytoin (Maint.)": ["IBW", None, "جرعة الصيانة على IBW"],
    
    # Sedation & Analgesics
    "Dexmedetomidine": ["ABW", 0.4, "عامل التصحيح 0.4"],
    "Ibuprofen": ["ABW", 0.4, "عامل التصحيح 0.4"],
    "Ketamine": ["IBW", None, ""],
    "Midazolam (Infusion)": ["IBW", None, "للتسريب المستمر"],
    "Opioids": ["IBW", None, "يفضل إعطاء بولصات متقطعة ومراقبة سريرية"],
    "Paracetamol": ["TBW", None, "بحد أقصى 15mg/kg/dose (max 1g)"],
    "Rocuronium": ["ABW", 0.25, "عامل التصحيح 0.25"],
    
    # Miscellaneous
    "Enoxaparin": ["TBW", None, "تحتاج مراقبة مستويات، دراسة اقترحت ABW F=0.4"],
    "Heparin": ["ABW", 0.4, "لا تتجاوز جرعة تحميل 5000 وحدة"],
    "Furosemide": ["IBW", None, "خطر سمية أذنية"],
    "Theophylline (Loading)": ["TBW", None, "جرعة التحميل"],
    "Theophylline (Maint.)": ["IBW", None, "جرعة الصيانة"]
}

# --- 4. اختيار الدواء وحساب الجرعة ---
selected_drug = st.selectbox("اختر الدواء المطلوبه جرعته:", list(drugs_db.keys()))

drug_info = drugs_db[selected_drug]
dosing_type = drug_info[0]
f_factor = drug_info[1]
comments = drug_info[2]

st.divider()

if not is_obese:
    final_weight = tbw
    st.success(f"الطفل غير بدين: يتم استخدام الوزن الحقيقي **({final_weight:.2f} كغ)**")
else:
    if dosing_type == "TBW":
        final_weight = tbw
    elif dosing_type == "IBW":
        final_weight = ibw
    elif dosing_type == "LBW":
        final_weight = lbw
    elif dosing_type == "ABW":
        final_weight = ibw + f_factor * (tbw - ibw)
    
    st.warning(f"الطفل بدين: يجب استخدام **{dosing_type}**")
    st.write(f"الوزن الذي يجب حساب الجرعة عليه: **{final_weight:.2f} كغ**")

if comments:
    st.info(f"ملاحظات إضافية: {comments}")

# عرض القيم المحسوبة للتأكد
with st.expander("تفاصيل الحسابات الرياضية"):
    st.write(f"الوزن المثالي (IBW): {ibw:.2f} كغ")
    st.write(f"الوزن الخالي من الدهون (LBW): {lbw:.2f} كغ")
    if is_obese and dosing_type == "ABW":
        st.write(f"معادلة ABW المستخدمة: {ibw:.2f} + {f_factor}({tbw} - {ibw:.2f})")
