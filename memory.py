# memory.py - نظام الذاكرة الديناميكية (قصيرة + طويلة + أدوات)
# ✅ تم تصحيح مفتاح 'quality_score' وإضافة حماية .get() لتجنب الأخطاء

import json
import os
from datetime import datetime
from typing import List, Dict

class DynamicMemory:
    def __init__(self, short_term_limit: int = 12, file_path: str = "memory.json"):
        self.file_path = file_path
        self.short_term_limit = short_term_limit
        self.data = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "long_term": [], 
            "short_term": [], 
            "tools_used": [], 
            "failed_patterns": [], 
            "metadata": {}
        }
    
    def add_short_term(self, role: str, content: str):
        """إضافة للذاكرة القصيرة (سياق المحادثة)"""
        if "short_term" not in self.data:
            self.data["short_term"] = []
        self.data["short_term"].append({
            "role": role, 
            "content": content, 
            "time": datetime.now().isoformat()
        })
        # الحفاظ على الحد الأقصى
        if len(self.data["short_term"]) > self.short_term_limit:
            self.data["short_term"] = self.data["short_term"][-self.short_term_limit:]
    
    def add_long_term(self, task: str, outcome: str, quality: int, tags: List[str] = None):
        """إضافة درس للذاكرة الطويلة"""
        self.data["long_term"].append({
            "task": task, 
            "outcome": outcome[:500], 
            "quality_score": quality,  # ✅ تم التصحيح: مطابقة الاسم مع main.py
            "tags": tags or [], 
            "time": datetime.now().isoformat()
        })
        self._save()
    
    def log_tool_usage(self, tool_name: str, success: bool):
        """تسجيل استخدام الأدوات للتعلم"""
        self.data["tools_used"].append({
            "tool": tool_name, 
            "success": success, 
            "time": datetime.now().isoformat()
        })
        self._save()
    
    def get_context(self) -> str:
        """تجميع السياق للوكلاء (قصيرة + ملخص طويلة)"""
        short_items = self.data.get("short_term", [])
        short = "\n".join([f"{m.get('role', '?')}: {m.get('content', '')[:150]}" for m in short_items])
        
        long_items = self.data.get("long_term", [])
        high_quality = [l for l in long_items if l.get("quality_score", 0) >= 8]
        long_summary = "\n".join([f"• {l.get('task', '')[:60]}... (حل ناجح)" for l in high_quality[-3:]])
        
        return f"📜 الذاكرة القصيرة:\n{short}\n\n📚 دروس سابقة ناجحة:\n{long_summary}"
    
    def get_similar_tasks(self, query: str, limit: int = 2) -> List[Dict]:
        """بحث بسيط في الذاكرة الطويلة"""
        query_words = set(query.lower().split())
        similar = []
        
        for lesson in self.data.get("long_term", []):
            # ✅ حماية ضد الأخطاء: استخدام .get() وقيم افتراضية
            q_score = lesson.get("quality_score", 5)
            if q_score < 6:
                continue  # تجاهل الدروس منخفضة الجودة
            
            lesson_words = set(lesson.get("task", "").lower().split())
            overlap = len(query_words & lesson_words)
            if overlap >= 1:
                similar.append({**lesson, "similarity_score": overlap})
        
        # ترتيب حسب التشابه والجودة
        similar.sort(key=lambda x: (x["similarity_score"], x.get("quality_score", 0)), reverse=True)
        return similar[:limit]
    
    def _save(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ خطأ في حفظ الذاكرة: {e}")
    
    def clear(self):
        """مسح الذاكرة (للاختبار)"""
        self.data = {
            "long_term": [], 
            "short_term": [], 
            "tools_used": [], 
            "failed_patterns": [], 
            "metadata": {}
        }
        self._save()
        print("🗑️ تم مسح الذاكرة")
    
    def get_stats(self) -> Dict:
        """إحصائيات الذاكرة"""
        lessons = self.data.get("long_term", [])
        if not lessons:
            return {"total_lessons": 0, "avg_quality": 0.0, "high_quality_lessons": 0, "user_feedback_count": 0}
        
        qualities = [l.get("quality_score", 0) for l in lessons]
        return {
            "total_lessons": len(lessons),
            "avg_quality": sum(qualities) / len(qualities),
            "high_quality_lessons": len([q for q in qualities if q >= 8]),
            "user_feedback_count": len([l for l in lessons if "user_feedback" in l.get("tags", [])])
        }