# tools.py - أدوات الوكلاء الذكية (مع رسم بياني احترافي)
# يدعم: حساب، بحث ويب، وقت، حفظ ملاحظات، ورسم بياني

import re
import math
import json
import os
from datetime import datetime

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # وضع غير تفاعلي للسيرفرات
    import matplotlib.pyplot as plt
    import pandas as pd
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False

# تعريف الأدوات المتاحة
TOOLS_REGISTRY = {
    "calculator": {
        "name": "calculator",
        "description": "تحسب المعادلات الرياضية بدقة. الاستخدام: [TOOL:calculator|2+2*3]",
        "handler": "execute_math"
    },
    "search": {
        "name": "search", 
        "description": "يبحث في الإنترنت عن معلومات حديثة. الاستخدام: [TOOL:search|عاصمة اليابان]",
        "handler": "web_search"
    },
    "time": {
        "name": "time",
        "description": "يُرجع التاريخ والوقت الحالي. الاستخدام: [TOOL:time]",
        "handler": "get_time"
    },
    "save_note": {
        "name": "save_note",
        "description": "يحفظ ملاحظة أو فكرة في الذاكرة. الاستخدام: [TOOL:save_note|فكرة المشروع]",
        "handler": "save_note"
    },
    "chart": {
        "name": "chart",
        "description": "يرسم مخططاً بيانياً من بيانات. الاستخدام: [TOOL:chart|نوع:bar|عناوين:يناير,فبراير,مارس|قيم:10,20,15|عنوان:المبيعات]",
        "handler": "generate_chart"
    }
}

def execute_math(expression: str) -> str:
    """حساب آمن للمعادلات الرياضية"""
    try:
        safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        if not safe_expr.strip():
            return "❌ تعبير رياضي فارغ"
        result = eval(safe_expr)
        return f"✅ النتيجة: {result}"
    except ZeroDivisionError:
        return "❌ خطأ: قسمة على صفر"
    except SyntaxError:
        return "❌ خطأ: تعبير رياضي غير صحيح"
    except Exception as e:
        return f"❌ خطأ رياضي: {str(e)}"

def web_search(query: str, max_results: int = 3) -> str:
    """بحث حقيقي في الإنترنت باستخدام DuckDuckGo"""
    if not DDGS_AVAILABLE:
        return "⚠️ مكتبة duckduckgo-search غير مثبتة."
    
    if not query or len(query.strip()) < 2:
        return "❌ يرجى إدخال كلمة بحث صحيحة"
    
    try:
        results = []
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                title = result.get("title", "بدون عنوان")
                href = result.get("href", "")
                body = result.get("body", "")[:200]
                results.append(f"• {title}\n  🔗 {href}\n  📄 {body}...")
        
        if not results:
            return f"🔍 لم أجد نتائج لـ '{query}'."
        
        formatted = f"🔍 نتائج البحث عن '{query}':\n\n" + "\n\n".join(results)
        formatted += f"\n\n💡 ملاحظة: النتائج من DuckDuckGo"
        return formatted
        
    except Exception as e:
        return f"⚠️ خطأ في البحث: {str(e)[:150]}"

def get_time() -> str:
    """إرجاع الوقت والتاريخ الحالي"""
    now = datetime.now()
    return f"🕒 التاريخ والوقت الحالي: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def save_note(note: str) -> str:
    """حفظ ملاحظة في ملف خارجي"""
    if not note or len(note.strip()) < 1:
        return "❌ الملاحظة فارغة"
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("agent_notes.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {note}\n")
        preview = note[:50] + "..." if len(note) > 50 else note
        return f"💾 تم حفظ الملاحظة: '{preview}'"
    except Exception as e:
        return f"❌ خطأ في الحفظ: {str(e)}"

def generate_chart(chart_config: str) -> str:
    """
    رسم مخطط بياني احترافي من بيانات نصية
    التنسيق: نوع:bar|عناوين:أ,ب,ج|قيم:10,20,15|عنوان:المبيعات|ألوان:blue
    """
    if not CHART_AVAILABLE:
        return "⚠️ مكتبات الرسم غير مثبتة. شغّل: pip install matplotlib pandas"
    
    try:
        # تحليل الإعدادات
        params = {}
        for part in chart_config.split('|'):
            if ':' in part:
                key, value = part.split(':', 1)
                params[key.strip()] = value.strip()
        
        chart_type = params.get('نوع', params.get('type', 'bar')).lower()
        labels_str = params.get('عناوين', params.get('labels', ''))
        values_str = params.get('قيم', params.get('values', ''))
        title = params.get('عنوان', params.get('title', 'مخطط بياني'))
        color = params.get('ألوان', params.get('color', '#3498db'))
        
        # تحويل البيانات
        labels = [l.strip() for l in labels_str.split(',') if l.strip()]
        values = [float(v.strip()) for v in values_str.split(',') if v.strip()]
        
        if not labels or not values or len(labels) != len(values):
            return "❌ تأكد من أن عدد العناوين يطابق عدد القيم. مثال: [TOOL:chart|نوع:bar|عناوين:أ,ب,ج|قيم:10,20,15|عنوان:اختبار]"
        
        # إنشاء المجلد إذا لم يوجد
        os.makedirs("charts", exist_ok=True)
        
        # اسم الملف الفريد
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"charts/chart_{timestamp}.png"
        
        # رسم المخطط
        plt.figure(figsize=(10, 6), dpi=100)
        
        if chart_type in ['bar', 'bar_chart', 'عمودي']:
            plt.bar(labels, values, color=color, edgecolor='black')
        elif chart_type in ['line', 'line_chart', 'خطي']:
            plt.plot(labels, values, color=color, marker='o', linewidth=2)
            plt.fill_between(range(len(values)), values, alpha=0.3, color=color)
        elif chart_type in ['pie', 'pie_chart', 'دائري']:
            plt.pie(values, labels=labels, autopct='%1.1f%%', colors=[color]*len(values), startangle=90)
        else:
            # افتراضي: شريطي
            plt.bar(labels, values, color=color, edgecolor='black')
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('الفئات' if chart_type != 'pie' else '')
        plt.ylabel('القيم' if chart_type != 'pie' else '')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        # حفظ الصورة
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        
        return f"📊 تم إنشاء المخطط: `{filename}`\n📁 النوع: {chart_type} | العناوين: {len(labels)} | العنوان: {title}"
        
    except Exception as e:
        return f"❌ خطأ في الرسم: {str(e)[:150]}...\n💡 تأكد من التنسيق: [TOOL:chart|نوع:bar|عناوين:أ,ب|قيم:10,20|عنوان:اختبار]"

def parse_and_execute_tool(text: str) -> tuple[str, str]:
    """تحليل واستدعاء الأدوات"""
    pattern = r'\[TOOL:(\w+)\|?(.*?)\]'
    match = re.search(pattern, text)
    
    if not match:
        return text, ""
    
    tool_name = match.group(1)
    args = match.group(2).strip()
    
    if tool_name not in TOOLS_REGISTRY:
        return text.replace(match.group(0), f"⚠️ أداة '{tool_name}' غير معروفة"), ""
    
    handler_name = TOOLS_REGISTRY[tool_name]["handler"]
    handler = globals()[handler_name]
    
    result = handler(args) if args else handler()
    cleaned_text = text.replace(match.group(0), f"[{result}]")
    return cleaned_text, result

def get_tools_prompt() -> str:
    """تعليمات استخدام الأدوات"""
    tools_desc = "\n".join([f"- {t['description']}" for t in TOOLS_REGISTRY.values()])
    return f"""
 **🔧 الأدوات المتاحة:**
{tools_desc}

**قواعد الاستخدام:**
1. استخدم التنسيق: [TOOL:اسم_الأداة|المدخلات]
2. لا تخمن النتائج، استخدم الأداة عند الشك.
3. بعد تنفيذ الأداة، أكمل إجابتك بناءً على النتيجة.

**مثال للرسم البياني:**
[TOOL:chart|نوع:bar|عناوين:يناير,فبراير,مارس|قيم:100,150,200|عنوان:المبيعات الربع الأول|ألوان:#2ecc71]
→ سيقوم برسم مخطط شريطي وحفظه في charts/chart_*.png
"""