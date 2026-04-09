# list_qwen_models.py - لعرض أسماء نماذج Qwen الصحيحة من OpenRouter API
import requests

def list_qwen_models():
    """جلب وعرض جميع نماذج Qwen المتاحة على OpenRouter"""
    
    print("🔍 جاري الاتصال بـ OpenRouter...\n")
    
    try:
        # جلب قائمة جميع النماذج من الـ API
        response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        response.raise_for_status()
        
        models = response.json().get("data", [])
        
        # تصفية نماذج Qwen فقط
        qwen_models = [m for m in models if "qwen" in m["id"].lower()]
        
        if qwen_models:
            print(f"✅ وجدت {len(qwen_models)} نموذجاً من عائلة Qwen:\n")
            print("=" * 70)
            
            for i, m in enumerate(qwen_models, 1):
                model_id = m["id"]
                is_free = "🆓 مجاني" if ":free" in model_id else "💰 مدفوع"
                context = m.get("context_length", "غير محدد")
                pricing = m.get("pricing", {})
                
                print(f"\n{i}. {model_id}")
                print(f"   • الحالة: {is_free}")
                print(f"   • السياق: {context:,} توكن")
                
                # عرض السعر إذا كان مدفوعاً
                if pricing and "prompt" in pricing:
                    prompt_price = pricing["prompt"]
                    completion_price = pricing.get("completion", prompt_price)
                    print(f"   • السعر: ${prompt_price}/1K توكن (مدخل) | ${completion_price}/1K (مخرج)")
                
                # عرض اسم النسخة للنسخ
                print(f"   • للنسخ: `{model_id}`")
            
            print("\n" + "=" * 70)
            print("💡 انسخ الاسم من خانة 'للنسخ' واستخدمه في config.py")
            print("💡 الصيغة في config.py: 'openrouter/' + الاسم")
            
        else:
            print("❌ لم أجد أي نموذج باسم Qwen في القائمة")
            print("💡 جرّب البحث عن: 'qwen', 'Qwen', 'qwq'")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الاتصال: {e}")
        print("💡 تأكد من اتصالك بالإنترنت وحاول مرة أخرى")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

if __name__ == "__main__":
    list_qwen_models()