# test_gemma4.py - اختبار نموذج Gemma 4
from router import SmartRouter
from dotenv import load_dotenv
load_dotenv()

router = SmartRouter()
test_msg = [{"role": "user", "content": "اشرح باختصار: ما هو الـ API؟"}]

print("🧪 اختبار Gemma 4 26B A4B IT (مجاني)...\n")
result = router.call_model("gemma", test_msg)

if result["success"]:
    print(f"✅ الإجابة:\n{result['content']}")
    print(f"\n📊 استهلاك: {result.get('tokens', 0)} توكن")
    if result.get("fallback_used"):
        print(f"⚠️ تم استخدام بديل: {result.get('model')}")
else:
    print(f"❌ خطأ: {result['error']}")