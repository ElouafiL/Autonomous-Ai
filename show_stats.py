# show_stats.py - عرض إحصائيات النظام
from memory import AgentMemory
import json

memory = AgentMemory()
stats = memory.get_stats()

print("\n🧠 إحصائيات الذاكرة:")
print(f"   • إجمالي الدروس: {stats['total_lessons']}")
print(f"   • متوسط الجودة: {stats['avg_quality']:.1f}/10")
print(f"   • دروس عالية الجودة: {stats['high_quality_lessons']}")
print(f"   • تقييمات المستخدمين: {stats['user_feedback_count']}")

# عرض آخر 3 دروس عالية الجودة
high_quality = [l for l in memory.memories["lessons"] if l["quality_score"] >= 8][-3:]
if high_quality:
    print(f"\n🏆 آخر الدروس الممتازة:")
    for i, lesson in enumerate(reversed(high_quality), 1):
        print(f"   {i}. {lesson['task'][:80]}... (جودة: {lesson['quality_score']}/10)")