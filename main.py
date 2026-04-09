# main.py - نظام الوكلاء الذكي v6.1 (8 وكلاء + أدوات + ذاكرة + ذكاء كامل)
# ✅ جاهز للمبتدئين: انسخ الكل، الصقه في main.py، احفظ، وشغّل!

import os
import json
import datetime
import re
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
from typing import List, Dict
from agent import SmartAgent
from memory import DynamicMemory
from dotenv import load_dotenv

# تحميل المفاتيح من ملف .env
load_dotenv()

# التأكد من وجود مجلدات النظام
os.makedirs("logs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

# ========================================
# 🧠 دوال الإدراك فوق المعرفي (مراقبة ذكية)
# ========================================
def meta_cognition_monitor(responses: List[str], turn: int) -> dict:
    """
    مراقب الأداء: يوقف الجدال العقيم، ويقيّم الكفاءة
    ✅ يتحقق من وجود ردَّين على الأقل قبل المقارنة
    """
    # لا نراقب قبل الجولة الثانية
    if turn < 2 or len(responses) < 2:
        return {"action": "continue"}
    
    # أخذ آخر ردَّين للمقارنة
    last_two = [r[:200] for r in responses[-2:]]
    
    # التأكد من أن لدينا ردَّين للمقارنة
    if len(last_two) < 2:
        return {"action": "continue"}
    
    # حساب نسبة التشابه البسيطة
    words1 = last_two[0].split()
    words2 = last_two[1].split()
    
    if not words1 or not words2:
        return {"action": "continue"}
    
    similarity = sum(1 for a, b in zip(words1, words2) if a == b) / max(len(words1), 1)
    
    # إذا التشابه عالي جداً، نوقف النقاش لتوفير الوقت
    if similarity > 0.7:
        return {"action": "stop_debate", "reason": "🛑 تكرار عالي، إنهاء النقاش."}
    
    return {"action": "continue"}


def dynamic_agent_routing(complexity: str, history_length: int, task: str = "") -> List[str]:
    """
    توزيع ديناميكي للوكلاء حسب الصعوبة ونوع المهمة
    ✅ يضيف خبير الرسوم تلقائياً إذا كانت المهمة تحتوي على كلمات رسم
    """
    # كلمات تدل على حاجة لرسم بياني
    chart_keywords = ["رسم", "مخطط", "بياني", "chart", "graph", "plot", "visualize"]
    needs_chart = any(kw in task.lower() for kw in chart_keywords)
    
    if complexity == "simple":
        agents = ["gemma", "groq"]
    elif complexity == "medium":
        agents = ["groq", "openrouter", "gemma"]
    else:  # complex
        agents = ["groq", "openrouter", "mistral", "claude"]
        if history_length > 3:
            agents.append("qwen_plus")
    
    # ✅ إضافة خبير الرسوم إذا كانت المهمة تحتاج ذلك
    if needs_chart and "chart_agent" not in agents:
        agents.append("chart_agent")
    
    return agents


# ========================================
# 🎯 الدالة الرئيسية
# ========================================
def main():
    print("\n🤖 AI Negotiation System v6.1 (8 Agents + Tools + Memory + Meta-Cognition)")
    print("=" * 70)
    
    # تهيئة الذاكرة الديناميكية
    memory = DynamicMemory(short_term_limit=12)
    
    # ========================================
    # تعريف الوكلاء الثمانية (يشاركون نفس الذاكرة)
    # ========================================
    agents_map = {
        # 1️⃣ المبتكر: أفكار إبداعية سريعة
        "groq": SmartAgent(
            name="💡 المبتكر", 
            role="يولد أفكاراً إبداعية وجريئة. ركّز على الابتكار والبساطة.", 
            model_key="groq", 
            memory=memory
        ),
        
        # 2️⃣ المحلل: نقد وتحسين عملي
        "openrouter": SmartAgent(
            name="📊 المحلل", 
            role="ينقد الأفكار بموضوعية ويقدم نسخة عملية محسنة. استخدم المنطق والواقعية.", 
            model_key="openrouter", 
            memory=memory
        ),
        
        # 3️⃣ المبرمج: حلول تقنية وأكواد
        "mistral": SmartAgent(
            name="💻 المبرمج", 
            role="يكتب أكواداً نظيفة، يشرح الخوارزميات، ويقدم حلولاً برمجية عملية.", 
            model_key="mistral", 
            memory=memory
        ),
        
        # 4️⃣ الباحث: معلومات موثقة وبيانات
        "cohere": SmartAgent(
            name="📚 الباحث", 
            role="يقدم معلومات دقيقة، يستشهد بمصادر موثوقة، ويلخص البيانات المعقدة.", 
            model_key="cohere", 
            memory=memory
        ),
        
        # 5️⃣ المنفذ: خطوات تنفيذية فورية
        "claude": SmartAgent(
            name="⚡ المنفذ", 
            role="يحول الأفكار إلى خطوات تنفيذية واضحة وقابلة للتطبيق فوراً.", 
            model_key="claude", 
            memory=memory
        ),
        
        # 6️⃣ الخبير المنطقي: تفكير عميق وتحليل معقد
        "qwen_plus": SmartAgent(
            name="🔷 الخبير المنطقي", 
            role="متخصص في حل المسائل المعقدة، التحليل الرياضي، والبرمجة المتقدمة. فكّر خطوة بخطوة.", 
            model_key="qwen_plus", 
            memory=memory
        ),
        
        # 7️⃣ Gemma 4: سريع ودقيق للمهام العامة
        "gemma": SmartAgent(
            name="🔷 Gemma 4", 
            role="نموذج جوجل السريع. دقيق في النصوص، سريع في الرد، وممتاز في المهام العامة.", 
            model_key="gemma", 
            memory=memory
        ),
        
        # 8️⃣ 📊 خبير الرسوم: متخصص في الرسوم البيانية (جديد!)
        "chart_agent": SmartAgent(
            name="📊 خبير الرسوم", 
            role="متخصص في تحويل البيانات إلى رسوم بيانية احترافية. استخدم [TOOL:chart|...] للرسم. اشرح نوع المخطط الأنسب.", 
            model_key="chart_agent", 
            memory=memory
        ),
    }
    
    # قائمة الوكلاء للعرض
    print("✅ الوكلاء جاهزون للنقاش:")
    agent_list = [
        ("1", "💡 المبتكر", "أفكار إبداعية"),
        ("2", "📊 المحلل", "نقد وتحسين"),
        ("3", "💻 المبرمج", "أكواد وحلول"),
        ("4", "📚 الباحث", "معلومات موثقة"),
        ("5", "⚡ المنفذ", "خطوات تنفيذية"),
        ("6", "🔷 الخبير المنطقي", "تحليل معقد"),
        ("7", "🔷 Gemma 4", "سريع ودقيق"),
        ("8", "📊 خبير الرسوم", "رسوم بيانية"),
    ]
    for num, name, role in agent_list:
        print(f"   {num}. {name} ← {role}")
    
    print("\n💡 اكتب مهمتك (أو 'exit' للخروج):")
    print("💡 استخدم '!' للمهام السريعة | 'tools' لقائمة الأدوات | 'stats' للإحصائيات")
    print("-" * 70)
    
    # ========================================
    # حلقة النقاش الرئيسية
    # ========================================
    while True:
        try:
            task = input("\n👤 أنت: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 وداعاً! تم حفظ جميع الجلسات في مجلد logs/")
            break
            
        # أوامر الخروج
        if task.lower() in ['exit', 'quit', 'خروج', 'ق']:
            print("\n👋 وداعاً! شكراً لاستخدامك النظام.")
            break
        
        # تجاهل المدخلات الفارغة
        if not task:
            continue
        
        # عرض قائمة الأدوات
        if task == "tools":
            print("\n🔧 الأدوات المتاحة:")
            print("  • [TOOL:calculator|2+2*3]     ← حساب رياضي دقيق")
            print("  • [TOOL:search|عاصمة فرنسا]   ← بحث في الإنترنت (حقيقي)")
            print("  • [TOOL:time]                 ← الوقت والتاريخ الحالي")
            print("  • [TOOL:save_note|فكرة]       ← حفظ ملاحظة في الذاكرة")
            print("  • [TOOL:chart|نوع:bar|عناوين:أ,ب|قيم:10,20|عنوان:اختبار] ← رسم مخطط")
            print("\n💡 مثال مركب:")
            print("   احسب 15% من 300 ثم ابحث عن استخدامات هذه النسبة")
            print("   [TOOL:calculator|300*0.15] [TOOL:search|15 percent applications]")
            print()
            continue
        
        # عرض إحصائيات النظام
        if task == "stats":
            stats = memory.get_stats()
            print(f"\n📊 إحصائيات النظام:")
            print(f"   • إجمالي الدروس في الذاكرة: {stats['total_lessons']}")
            print(f"   • متوسط جودة الإجابات: {stats['avg_quality']:.1f}/10")
            print(f"   • الدروس عالية الجودة (8+/10): {stats['high_quality_lessons']}")
            print(f"   • تقييمات المستخدمين: {stats['user_feedback_count']}")
            print()
            continue
        
        # ========================================
        # معالجة المهمة
        # ========================================
        
        # الوضع السريع: وكيل واحد فقط
        is_quick = task.startswith("!")
        task_clean = task[1:].strip() if is_quick else task
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # تقييم تعقيد المهمة
        complexity = assess_task_complexity(task_clean)
        complexity_emoji = "🔴 معقد" if complexity == "complex" else "🟡 متوسط" if complexity == "medium" else "🟢 بسيط"
        
        print(f"\n📌 {task_clean} | 🧠 التعقيد: {complexity_emoji}")
        
        # البحث في الذاكرة عن مهام مشابهة
        similar = memory.get_similar_tasks(task_clean, limit=2)
        memory_context = ""
        if similar:
            memory_context = "\n\n📚 مهام سابقة مشابهة:\n" + "\n".join(
                [f"• {s['task'][:80]}... (جودة: {s['quality_score']}/10)" for s in similar]
            )
            print(f"📚 وجدت {len(similar)} مهمة مشابهة في الذاكرة")
        
        # تحليل المدير للمهام المتوسطة والمعقدة
        manager_plan = ""
        if complexity in ["medium", "complex"] and not is_quick:
            manager = agents_map.get("gemma")  # نستخدم Gemma كمدير سريع
            if manager:
                manager_prompt = f"""المهمة: {task_clean}
التعقيد: {complexity}
{memory_context if memory_context else ''}

حدّد باختصار:
1. نوع المهمة؟ (برمجة/تحليل/إبداع/بحث/عام)
2. كم وكيل نحتاج؟ (2-4 للمتوسطة، 5-8 للمعقدة)
3. من هم الوكلاء الأنسب؟
4. ما هي الأولويات في الإجابة؟

قدّم الخطة في 3-4 نقاط مختصرة."""
                
                try:
                    manager_plan = manager.think(manager_prompt, "", use_tools=False)
                    if manager_plan and len(manager_plan.strip()) > 20:
                        print(f"\n🎯 خطة المدير:\n{manager_plan}\n")
                except:
                    pass  # نتجاهل إذا فشل المدير
        
        # اختيار الوكلاء ديناميكياً
        selected_keys = dynamic_agent_routing(complexity, len(memory.data.get("short_term", [])), task_clean)
        selected_agents = [agents_map[k] for k in selected_keys if k in agents_map]
        
        if not selected_agents:
            print("⚠️ لا يوجد وكلاء متاحين، جرب مرة أخرى.")
            continue
        
        # تهيئة متغيرات الجلسة
        full_history = f"المستخدم يطلب: {task_clean}{memory_context}\n"
        session_log = []
        responses = []
        fallback_summary = []
        
        # ========================================
        # حلقة الوكلاء المختارين
        # ========================================
        for i, agent in enumerate(selected_agents, 1):
            # وصف دور الوكيل في الجولة الحالية
            role_actions = {
                1: "يقترح الفكرة الأولية...",
                2: "ينقد ويحسن الاقتراح...",
                3: "يضيف الجانب التقني والبرمجي...",
                4: "يدعم بالمعلومات والبيانات الموثقة...",
                5: "يحول الأفكار لخطوات تنفيذية...",
                6: "يناقش بعمق ويخرج بخلاصة منطقية...",
                7: "يقدم ملخصاً سريعاً ودقيقاً...",
                8: "يرسم مخططاً بيانياً أو يحلل بيانات..."
            }
            action = role_actions.get(i, "يناقش...")
            
            print(f"\n{i}️⃣ {agent.name} {action}")
            
            # استخدام التفكير مع النقد الذاتي للمهام المعقدة
            use_reflection = (complexity == "complex" and agent.model_key in ["mistral", "openrouter", "qwen_plus"])
            use_tools = (complexity != "simple")  # تفعيل الأدوات للمهام غير البسيطة
            
            try:
                if use_reflection:
                    result = agent.think_with_reflection(task_clean, full_history, use_tools=use_tools)
                    response = result["final"]
                    print(f"   🔄 تم استخدام النقد الذاتي ({result['iterations']} جولات)")
                else:
                    response = agent.think(task_clean, full_history, use_tools=use_tools)
            except Exception as e:
                print(f"   ❌ خطأ في {agent.name}: {str(e)[:100]}")
                continue
            
            # عرض إشعار إذا تم استخدام بديل
            if agent.last_response_info.get("fallback_used"):
                model_used = agent.last_response_info.get("model_used", "غير معروف")
                print(f"\n   🔄 ⚠️  تم استخدام نموذج بديل: {model_used}")
                fallback_summary.append(f"{agent.name} → {model_used}")
            
            # عرض رد الوكيل
            print(f"\n💬 {agent.name}:\n{response}")
            
            # تحديث السياق والردود
            full_history += f"\n[رد {agent.name}]: {response[:300]}...\n"
            session_log.append(f"[{agent.name}]\n{response}")
            session_log.append("-" * 60)
            responses.append(response)
        
        # ========================================
        # التصويت (للمهام المعقدة فقط)
        # ========================================
        best_response = responses[-1] if responses else ""
        if complexity == "complex" and len(responses) >= 3:
            voting_result = run_voting(selected_agents, task_clean, responses)
            best_response = voting_result["winner_response"]
            print(f"\n🏆 الإجابة المختارة بالتصويت من {voting_result['winner_agent']}")
        
        # ========================================
        # تقرير الجلسة المجمع
        # ========================================
        total_tokens = sum(a.last_info.get("tokens", 0) for a in selected_agents)
        total_calls = sum(1 for a in selected_agents if a.last_info.get("success"))
        total_fallbacks = sum(1 for a in selected_agents if a.last_response_info.get("fallback_used"))
        
        print(f"\n📈 تقرير الجلسة المجمع:")
        print(f"   • الوكلاء المشاركين: {len(selected_agents)}/8")
        print(f"   • المكالمات الناجحة: {total_calls}/{len(selected_agents)}")
        print(f"   • إجمالي التوكنز: {total_tokens:,}")
        print(f"   • البدائل المستخدمة: {total_fallbacks}/{len(selected_agents)}")
        
        if fallback_summary:
            print(f"\n   🔄 ملخص البدائل:")
            for item in fallback_summary:
                print(f"      • {item}")
        
        # عرض إحصائيات الذاكرة
        mem_stats = memory.get_stats()
        if mem_stats["total_lessons"] > 0:
            print(f"\n   🧠 الذاكرة: {mem_stats['total_lessons']} درس | متوسط الجودة: {mem_stats['avg_quality']:.1f}/10")
        
        estimated_cost = total_tokens * 0.000001
        print(f"   • التكلفة التقديرية: ${estimated_cost:.4f}")
        print(f"   • ملاحظة: النماذج المجانية قد لا تحسب التكلفة بدقة")
        
        # ========================================
        # جمع التغذية الراجعة (اختياري)
        # ========================================
        # يمكن تفعيله بإزالة التعليق عن الأسطر التالية:
        # rating = get_feedback_from_user(task_clean, best_response, memory)
        
        # ========================================
        # حفظ الجلسة في ملف
        # ========================================
        filename = f"logs/debate_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Task: {task_clean}\nTimestamp: {timestamp}\nComplexity: {complexity}\n")
                f.write(f"Total Tokens: {total_tokens}\nFallbacks: {total_fallbacks}\n")
                f.write("=" * 70 + "\n\n")
                if manager_plan:
                    f.write(f"[Manager Plan]\n{manager_plan}\n\n")
                f.write("\n\n".join(session_log))
                if best_response and best_response != responses[-1]:
                    f.write(f"\n\n[Best Response by Voting]\n{best_response}")
            print(f"\n💾 تم حفظ الجلسة في: {filename}")
        except Exception as e:
            print(f"\n⚠️ تحذير: فشل حفظ الملف: {e}")
        
        # ========================================
        # نهاية الجلسة
        # ========================================
        # تصفير عدادات الوكلاء للجلسة التالية (اختياري)
        # for agent in selected_agents:
        #     agent.router.reset_usage()
        
        print("\n" + "=" * 70)
        print("✅ انتهى النقاش! اكتب مهمة جديدة أو 'exit' للإنهاء.")
        print("-" * 70)


# ========================================
# 🧠 دوال مساعدة إضافية
# ========================================

def assess_task_complexity(task: str) -> str:
    """تقييم تعقيد المهمة لاختيار استراتيجية المعالجة"""
    
    complex_keywords = [
        "صمّم", "ابنِ", "حلّل", "قارن", "فسّر", "اشرح بالتفصيل",
        "خوارزمية", "نظام", "معمارية", "استراتيجية", "متعدد",
        "كامل", "شامل", "احترافي", "إنتاجي", "رسم", "مخطط"
    ]
    
    simple_keywords = [
        "ما هي", "من هو", "أين", "متى", "كم", "عرّف", "اذكر",
        "بسيط", "سريع", "مختصر", "!"
    ]
    
    task_lower = task.lower()
    complex_score = sum(1 for kw in complex_keywords if kw in task_lower)
    simple_score = sum(1 for kw in simple_keywords if kw in task_lower)
    
    if complex_score >= 2:
        return "complex"
    elif simple_score >= 2 or len(task.split()) < 8:
        return "simple"
    else:
        return "medium"


def run_voting(agents: List[SmartAgent], task: str, responses: List[str]) -> Dict:
    """نظام تصويت الوكلاء لاختيار أفضل إجابة"""
    
    print("\n🗳️ بدء التصويت على أفضل إجابة...")
    
    votes = {}
    vote_details = []
    
    for voter in agents:
        voting_prompt = f"""المهمة: {task}

الإجابات المتاحة للتصويت:
{chr(10).join([f"{i+1}. {agents[i].name}: {resp[:250]}{'...' if len(resp) > 250 else ''}" 
               for i, resp in enumerate(responses)])}

صوّت للإجابة الأفضل بناءً على:
- الدقة والاكتمال
- الوضوح والتنظيم  
- الفائدة العملية

اكتب رقم الإجابة الأفضل فقط (1، 2، 3، إلخ)."""
        
        try:
            vote = voter.think(voting_prompt, "", use_tools=False, use_cot=False)
            
            # استخراج الرقم من التصويت
            import re
            numbers = re.findall(r'\d+', vote)
            if numbers:
                vote_num = int(numbers[0]) - 1
                if 0 <= vote_num < len(responses):
                    votes[vote_num] = votes.get(vote_num, 0) + 1
                    vote_details.append(f"{voter.name} → #{vote_num + 1}")
        except:
            continue  # نتجاهل إذا فشل التصويت
    
    # العثور على الفائز
    if votes:
        winner_idx = max(votes, key=votes.get)
        winner_votes = votes[winner_idx]
        print(f"🏆 الفائز: {agents[winner_idx].name} (الإجابة #{winner_idx + 1}) بـ {winner_votes} صوت")
        print(f"📊 تفاصيل التصويت: {' | '.join(vote_details)}")
        return {
            "winner_index": winner_idx,
            "winner_response": responses[winner_idx],
            "winner_agent": agents[winner_idx].name,
            "votes": votes,
            "details": vote_details
        }
    else:
        print("⚠️ لم يتم الحصول على أصوات، استخدام الإجابة الأخيرة")
        return {
            "winner_index": len(responses) - 1,
            "winner_response": responses[-1] if responses else "",
            "winner_agent": agents[-1].name if agents else "غير معروف",
            "votes": {},
            "details": []
        }


def get_feedback_from_user(task: str, response: str, memory: DynamicMemory) -> int:
    """جمع وتقييم التغذية الراجعة من المستخدم"""
    
    print("\n📊 كيف تقيّم هذه الإجابة؟")
    print("   1-3: ضعيفة | 4-6: مقبولة | 7-8: جيدة | 9-10: ممتازة")
    print("   (اكتب الرقم أو اضغط Enter للتخطي): ", end="")
    
    try:
        rating_input = input().strip()
        if rating_input and rating_input.isdigit():
            rating = int(rating_input)
            if 1 <= rating <= 10:
                # حفظ التقييم في الذاكرة
                memory.add_lesson(
                    task=task,
                    response=response,
                    quality_score=rating,
                    tags=["user_feedback"]
                )
                
                if rating >= 8:
                    print("✅ شكراً! سأستخدم هذا النمط أكثر في المستقبل.")
                elif rating <= 4:
                    print("🔧 سأحسّن إجاباتي بناءً على ملاحظاتك.")
                return rating
    except:
        pass
    return 0


# ========================================
# نقطة الدخول للبرنامج
# ========================================
if __name__ == "__main__":
    main()