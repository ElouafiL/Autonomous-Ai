# agent.py - وكيل ذكي يدعم الأدوات، الذاكرة الديناميكية، والتفكير مع النقد الذاتي
# ✅ جاهز للمبتدئين: انسخ الكل، الصقه في agent.py، احفظ، وشغّل!

from router import SmartRouter
from tools import parse_and_execute_tool, get_tools_prompt
from memory import DynamicMemory
from typing import Dict, Any, Union, List, Optional


class SmartAgent:
    """
    وكيل ذكي متكامل مع:
    - دعم الأدوات الخارجية (حاسبة، بحث، وقت، ملاحظات، رسوم)
    - ذاكرة ديناميكية قصيرة/طويلة
    - تفكير متسلسل (Chain-of-Thought)
    - نقد ذاتي وتحسين تلقائي (Reflection)
    - تتبع حالة المكالمات والبدائل
    """
    
    def __init__(self, name: str, role: str, model_key: str, memory: DynamicMemory):
        self.name = name
        self.role = role
        self.model_key = model_key
        self.router = SmartRouter()
        self.memory = memory
        self.last_info = {}  # معلومات آخر مكالمة تقنية
        self.last_response_info = {}  # معلومات الرد للعرض في main.py
    
    def think(self, task: str, history: str = "", 
              use_tools: bool = True, 
              use_cot: bool = True,
              max_tool_calls: int = 2) -> str:
        """
        الوكيل يفكر في المهمة ويعطي إجابة
        
        Args:
            task: المهمة المطلوبة
            history: سياق المحادثة السابق
            use_tools: هل نستخدم الأدوات الخارجية؟
            use_cot: هل نستخدم التفكير المتسلسل؟
            max_tool_calls: أقصى عدد لاستدعاءات الأدوات
        
        Returns:
            str: الإجابة النهائية
        """
        
        # تعليمات التفكير المتسلسل (Chain-of-Thought)
        cot_instruction = """
فكّر خطوة بخطوة قبل الإجابة:
1. افهم المهمة جيداً
2. حدّد النقاط الرئيسية
3. فكّر في الحلول الممكنة
4. اختر الحل الأمثل
5. قدّم الإجابة بشكل منظم
""" if use_cot else ""
        
        # بناء رسالة النظام
        system_msg = f"""أنت {self.name}.
دورك: {self.role}

{cot_instruction}
{get_tools_prompt() if use_tools else ''}

قدّم إجابة واضحة ومنظمة. استخدم نقاط مرقمة إذا كان مناسباً.
كن مختصراً لكن شامل. استخدم اللغة العربية الفصحى الواضحة.
إذا كانت نتائج البحث أو الأدوات طويلة، لخّص أهم 3 نقاط فقط."""

        # دمج الذاكرة والسياق
        context = self.memory.get_context()
        user_msg = f"المهمة: {task}\n\n📜 سياق النظام:\n{context}\n\n💬 النقاش السابق:\n{history}"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

        result = self.router.call_model(self.model_key, messages)
        
        # حفظ معلومات المكالمة
        self.last_info = {
            "success": result.get("success", False),
            "tokens": result.get("tokens", 0),
            "model": result.get("model", self.model_key),
            "error": result.get("error") if not result.get("success") else None
        }
        
        # ✅ تحديث last_response_info للعرض في main.py
        self.last_response_info = {
            "success": result.get("success", False),
            "model_used": self.router.last_call_info.get("model_used"),
            "fallback_used": self.router.last_call_info.get("fallback_used", False),
            "tokens": result.get("tokens", 0),
            "content": result.get("content", "") if result.get("success") else ""
        }
        
        if not result.get("success"):
            return f"⚠️ خطأ في الاتصال: {result.get('error', 'خطأ غير معروف')}"

        response = result["content"]
        
        # 🔍 معالجة الأدوات تلقائياً (مع دعم البحث والرسوم)
        if use_tools:
            for _ in range(max_tool_calls):
                cleaned, tool_result = parse_and_execute_tool(response)
                if not tool_result:
                    break  # لا توجد أدوات في هذا الرد
                
                # تسجيل استخدام الأداة في الذاكرة
                tool_name = "unknown"
                if "|" in cleaned:
                    try:
                        tool_name = cleaned.split(":")[1].split("|")[0]
                    except:
                        pass
                self.memory.log_tool_usage(tool_name, True)
                
                # إذا كانت نتيجة البحث طويلة، نلخّص
                if "نتائج البحث" in tool_result and len(tool_result) > 500:
                    tool_result = tool_result[:500] + "\n...(نتائج إضافية متوفرة)"
                
                # إعادة الإرسال مع نتيجة الأداة
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"🔧 نتيجة الأداة: {tool_result}\nأكمل الإجابة بناءً على هذه النتيجة."})
                
                result = self.router.call_model(self.model_key, messages)
                if result.get("success"):
                    response = result["content"]
                    # تحديث last_response_info مع نتيجة الأداة
                    self.last_response_info["content"] = response
                else:
                    break

        # حفظ في الذاكرة القصيرة
        self.memory.add_short_term("assistant", response[:300])
        return response
    
    def think_with_reflection(self, task: str, history: str = "", 
                             use_tools: bool = True,
                             max_iterations: int = 2,
                             **kwargs) -> Dict[str, Any]:
        """
        الوكيل يفكر، يراجع نفسه، ثم يحسّن الإجابة تلقائياً
        
        Args:
            task: المهمة المطلوبة
            history: سياق المحادثة السابق
            use_tools: هل نستخدم الأدوات؟
            max_iterations: أقصى عدد لجولات التحسين
        
        Returns:
            Dict: {initial, critique, final, iterations}
        """
        iterations = []
        
        # 🔹 الجولة 1: الإجابة الأولية
        initial = self.think(task, history, use_tools=use_tools, use_cot=True, **kwargs)
        iterations.append({"step": "initial", "content": initial})
        
        for i in range(max_iterations):
            # 🔹 الجولة 2: النقد الذاتي
            critique_prompt = f"""
راجع الإجابة التالية بدقة ونقدية للمهمة: "{task}"

الإجابة الحالية:
"{initial if i == 0 else iterations[-1]['content']}"

اسأل نفسك:
1. هل الإجابة كاملة وتغطي جميع جوانب المهمة؟
2. هل هناك أخطاء منطقية أو معلومات غير دقيقة؟
3. هل يمكن تبسيط الشرح أو جعله أكثر وضوحاً؟
4. هل فاتني أي نقطة مهمة؟
5. هل يمكن إضافة مثال عملي أو كود إذا كان مناسباً؟

قدّم نقدك البناء في 3-5 نقاط مختصرة ومحددة.
"""
            critique = self.think(critique_prompt, "", use_tools=False, use_cot=False, **kwargs)
            iterations.append({"step": f"critique_{i+1}", "content": critique})
            
            # 🔹 الجولة 3: التحسين النهائي
            improve_prompt = f"""
بناءً على النقد البناء التالي:
"{critique}"

حسّن الإجابة الأصلية لجعلها:
- أكثر دقة وشمولية
- أسهل في الفهم والتنظيم
- أكثر عملية مع أمثلة إذا كان مناسباً
- خالية من الأخطاء أو التكرار

الإجابة الأصلية:
"{initial if i == 0 else iterations[-2]['content']}"

قدّم النسخة النهائية المحسّنة فقط (بدون شرح التحسينات أو ذكر النقد).
"""
            improved = self.think(improve_prompt, "", use_tools=False, use_cot=False, **kwargs)
            iterations.append({"step": f"improved_{i+1}", "content": improved})
            
            # ✅ إذا كانت الإجابة جيدة، نتوقف مبكراً
            if any(kw in critique.lower() for kw in ["ممتاز", "جيد جداً", "لا يحتاج تحسين", "perfect", "excellent"]):
                break
        
        # تحديث last_response_info مع النتيجة النهائية
        self.last_response_info = {
            "success": True,
            "model_used": self.last_info.get("model"),
            "fallback_used": self.router.last_call_info.get("fallback_used", False),
            "tokens": self.last_info.get("tokens", 0),
            "content": iterations[-1]["content"]
        }
        
        return {
            "initial": initial,
            "critique": iterations[-2]["content"] if len(iterations) >= 2 else "",
            "final": iterations[-1]["content"],
            "iterations": len(iterations),
            "all_steps": iterations
        }
    
    def critique(self, content: str, task: str) -> str:
        """نقد ذاتي سريع لرد معين"""
        prompt = f"""راجع هذا الرد للمهمة: '{task}'

الرد للمراجعة:
"{content[:500]}{'...' if len(content) > 500 else ''}"

اذكر 3 نقاط تحسين دقيقة فقط (لا تعدل الرد، فقط اقترح تحسينات)."""
        return self.think(prompt, "", use_tools=False, use_cot=False)
    
    def get_call_summary(self) -> str:
        """عرض ملخص آخر مكالمة"""
        info = self.last_response_info
        if not info:
            return "لا توجد معلومات"
        
        if info.get("success"):
            status = "✅ ناجح"
            model_info = f"{info.get('model_used', self.model_key)}"
            if info.get("fallback_used"):
                status += " ⚠️ (بديل)"
            return f"{status} | النموذج: {model_info} | التوكنز: {info.get('tokens', 0)}"
        else:
            return f"❌ فشل: {info.get('error', 'خطأ غير معروف')}"
    
    def clear_memory(self):
        """مسح ذاكرة الوكيل للجلسة الجديدة"""
        self.router.reset_usage()
        self.last_info = {}
        self.last_response_info = {}
    
    def get_thought_stats(self) -> Dict:
        """إحصائيات تاريخ التفكير للوكيل"""
        # يمكن توسيع هذا لاحقاً لتخزين تاريخ كامل
        return {
            "agent_name": self.name,
            "model_key": self.model_key,
            "last_call_success": self.last_info.get("success", False),
            "last_tokens": self.last_info.get("tokens", 0)
        }