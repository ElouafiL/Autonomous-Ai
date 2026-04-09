# check_memory.py - عرض ما تعلمه نظامك
from memory import DynamicMemory

memory = DynamicMemory()
lessons = memory.data.get("long_term", [])

print("\n🧠 ما تعلمه نظامك حتى الآن:")
print("=" * 50)
for i, lesson in enumerate(lessons, 1):
    print(f"{i}. 📝 {lesson['task'][:60]}...")
    print(f"   ✅ الجودة: {lesson['quality']}/10 | الوسوم: {lesson['tags']}")
    print(f"   🕒 الوقت: {lesson['time'][:19]}")
    print()
print(f"📊 إجمالي الدروس: {len(lessons)}")