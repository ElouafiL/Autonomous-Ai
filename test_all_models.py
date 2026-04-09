# test_all_models.py - اختبار جميع النماذج الخمسة
from router import SmartRouter
from dotenv import load_dotenv

# تحميل المفاتيح من ملف .env
load_dotenv()

def test_all_models():
    """اختبار بسيط لكل نموذج بكلمة واحدة"""
    
    router = SmartRouter()
    # سؤال بسيط جداً للاختبار السريع
    test_msg = [{"role": "user", "content": "أجب بكلمة واحدة فقط: ما لون السماء؟"}]
    
    print("🧪 اختبار جميع النماذج...\n")
    print("-" * 40)
    
    # قائمة النماذج للاختبار
    models = ["groq", "openrouter", "mistral", "cohere", "claude"]
    
    success_count = 0
    
    for key in models:
        print(f"\n🔵 جاري اختبار {key}...")
        
        result = router.call_model(key, test_msg)
        
        if result["success"]:
            # عرض أول 50 حرف من الرد
            preview = result["content"].strip()[:50]
            print(f"   ✅ {key}: {preview}...")
            success_count += 1
        else:
            print(f"   ❌ {key}: {result['error'][:60]}...")
    
    print("\n" + "-" * 40)
    print(f"✨ النتيجة: {success_count}/{len(models)} نماذج تعمل!")
    
    if success_count == len(models):
        print("🎉 ممتاز! كل النماذج جاهزة!")
    elif success_count >= 3:
        print("✅ جيد! يمكنك تشغيل النظام الرئيسي.")
    else:
        print("⚠️ تحقق من مفاتيح .env للنماذج التي فشلت.")

if __name__ == "__main__":
    test_all_models()