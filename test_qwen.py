# test_qwen.py - اختبار Qwen3.6-Plus
from router import SmartRouter
from dotenv import load_dotenv
load_dotenv()

router = SmartRouter()
test_msg = [{"role": "user", "content": "احسب: 15 × 27 + 42 ÷ 6 = ؟ (أظهر خطوات الحل)"}]

print("🧪 اختبار Qwen3.6-Plus...\n")
result = router.call_model("openrouter", test_msg)

if result["success"]:
    print(f"✅ الإجابة:\n{result['content']}")
    print(f"\n📊 استهلاك: {result.get('tokens', 0)} توكن")
else:
    print(f"❌ خطأ: {result['error']}")