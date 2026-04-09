# router.py - نظام توجيه الطلبات للنماذج (نسخة هادئة + مستقرة)
# تم إخفاء رسائل التصحيح المزعجة من litellm

import os
import time
import logging

# ========================================
# 🔇 إخفاء رسائل litellm المزعجة (مهم!)
# ========================================
# استيراد litellm أولاً
import litellm

# إخفاء جميع رسائل التصحيح والمعلومات من litellm
litellm.set_verbose = False
litellm.suppress_debug_info = True
litellm.suppress_debug_messages = True

# تكوين نظام التسجيل (logging) لفلترة رسائل litellm
logging.getLogger("litellm").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# الآن نستورد دالة completion بعد التهيئة
from litellm import completion
from config import MODELS, TASK_ROUTING


class SmartRouter:
    """
    كلاس يدير اختيار النموذج وإرسال الطلبات مع:
    - مقاومة للأعطال (Retry Logic)
    - سلسلة بدائل تلقائية (Fallback Chain)
    - مراقبة استهلاك التوكنز
    - تتبع آخر مكالمة
    - واجهة هادئة (بدون رسائل مزعجة)
    """
    
    # 🔗 خريطة البدائل التلقائية
    FALLBACK_CHAIN = {
        "qwen_plus": ["openrouter", "gemma", "groq"],
        "claude": ["openrouter", "gemma", "groq"],
        "cohere": ["openrouter", "gemma", "groq"],
        "mistral": ["groq", "openrouter", "gemma"],
        "groq": ["openrouter", "gemma"],
        "openrouter": ["groq", "gemma"],
        "gemma": ["openrouter", "groq"],
        "chart_agent": ["openrouter", "gemma", "groq"]  # ✅ بدائل لوكيل الرسوم
    }
    
    def __init__(self):
        self.call_count = 0
        self.total_tokens = 0
        self.fallback_count = 0
        self.last_call_info = {}
    
    def get_model_config(self, model_key):
        return MODELS.get(model_key)
    
    def _apply_fallback_config(self, config, fallback_key):
        """تعديل إعدادات النموذج لاستخدام نموذج بديل"""
        fallback_config = MODELS.get(fallback_key)
        if not fallback_config:
            return None
        
        return {
            "name": f"{fallback_config['name']} (Fallback)",
            "provider": fallback_config["provider"],
            "model_id": fallback_config["model_id"],
            "api_key_env": fallback_config["api_key_env"],
            "temperature": config.get("temperature", 0.7),
            "full_model_name": fallback_config.get("full_model_name"),
            "base_url": fallback_config.get("base_url")
        }
    
    def call_model(self, model_key, messages, max_retries=2, use_fallback=True):
        """
        إرسال رسالة لنموذج مع تتبع واضح للبدائل
        
        Returns:
            dict: {success, content, error, model, tokens, fallback_used, ...}
        """
        config = self.get_model_config(model_key)
        if not config:
            self.last_call_info = {"success": False, "error": f"Model {model_key} not found"}
            return {"success": False, "error": f"Model {model_key} not found in config"}
        
        api_key = os.getenv(config["api_key_env"])
        if not api_key:
            self.last_call_info = {"success": False, "error": f"Missing API key"}
            return {"success": False, "error": f"Missing API key for {model_key}"}
        
        # قائمة النماذج للتجربة
        models_to_try = [(model_key, config, "primary")]
        
        if use_fallback and model_key in self.FALLBACK_CHAIN:
            for fallback_key in self.FALLBACK_CHAIN[model_key]:
                fallback_config = self._apply_fallback_config(config, fallback_key)
                if fallback_config:
                    models_to_try.append((fallback_key, fallback_config, "fallback"))
        
        last_error = None
        
        for current_key, current_config, model_type in models_to_try:
            
            if model_type == "fallback":
                print(f"   🔄 ⚠️  نموذج '{model_key}' غير متاح، استخدام بديل: {current_config['name']}")
                self.fallback_count += 1
            
            for attempt in range(max_retries + 1):
                try:
                    model_name = current_config.get("full_model_name")
                    if not model_name:
                        model_name = f"{current_config['provider']}/{current_config['model_id']}"
                    
                    print(f"   📤 Sending request to: {current_config['name']}...")
                    
                    completion_kwargs = {
                        "model": model_name,
                        "messages": messages,
                        "api_key": os.getenv(current_config["api_key_env"]),
                        "temperature": current_config["temperature"]
                    }
                    
                    if current_config.get("base_url"):
                        completion_kwargs["api_base"] = current_config["base_url"]
                    
                    # ✅ إرسال الطلب مع كتم رسائل التصحيح
                    response = completion(**completion_kwargs)
                    content = response["choices"][0]["message"]["content"]
                    
                    # مراقبة الاستهلاك
                    usage = response.get("usage", {})
                    tokens = usage.get("total_tokens", 0)
                    self.total_tokens += tokens
                    print(f"   📊 استهلاك: {tokens} توكن | الإجمالي: {self.total_tokens}")
                    
                    self.call_count += 1
                    
                    # حفظ معلومات المكالمة الأخيرة
                    self.last_call_info = {
                        "success": True,
                        "model_used": current_key,
                        "model_name": current_config["name"],
                        "model_type": model_type,
                        "tokens": tokens,
                        "fallback_used": (model_type == "fallback")
                    }
                    
                    return {
                        "success": True,
                        "content": content,
                        "model": current_key,
                        "model_type": model_type,
                        "call_number": self.call_count,
                        "tokens": tokens,
                        "fallback_used": (model_type == "fallback")
                    }
                    
                except Exception as e:
                    error_msg = str(e)
                    last_error = error_msg
                    
                    # إعادة المحاولة عند Rate Limit
                    if "rate limit" in error_msg.lower() and attempt < max_retries:
                        wait_time = 10 * (attempt + 1)
                        print(f"   ⏳ Rate limit، إعادة المحاولة خلال {wait_time}ث...")
                        time.sleep(wait_time)
                        continue
                    
                    # الانتقال للنموذج التالي عند أخطاء معينة
                    should_try_next = any(kw in error_msg.lower() for kw in 
                        ["not found", "404", "authentication", "invalid api", 
                         "insufficient balance", "quota", "provider not provided"])
                    
                    if should_try_next:
                        break
                    
                    if attempt == max_retries:
                        print(f"   ❌ فشل {current_key} بعد {max_retries+1} محاولات")
                        break
        
        # فشل جميع النماذج
        self.last_call_info = {
            "success": False,
            "error": last_error[:200] if last_error else "خطأ غير معروف",
            "fallbacks_tried": len(models_to_try) - 1
        }
        
        return {
            "success": False,
            "error": f"فشل جميع النماذج: {last_error[:200] if last_error else 'خطأ غير معروف'}",
            "model": model_key,
            "fallbacks_tried": len(models_to_try) - 1
        }
    
    def select_best_model(self, task_type="general"):
        candidates = TASK_ROUTING.get(task_type, TASK_ROUTING["general"])
        return candidates[0] if candidates else "groq"
    
    def get_usage_report(self):
        estimated_cost = self.total_tokens * 0.000001
        total_attempts = self.call_count + self.fallback_count
        
        return {
            "total_calls": self.call_count,
            "total_tokens": self.total_tokens,
            "fallback_count": self.fallback_count,
            "fallback_rate": f"{(self.fallback_count / max(1, total_attempts)) * 100:.1f}%",
            "estimated_cost_usd": round(estimated_cost, 4),
            "avg_tokens_per_call": round(self.total_tokens / max(1, self.call_count), 1)
        }
    
    def reset_usage(self):
        self.call_count = 0
        self.total_tokens = 0
        self.fallback_count = 0
        self.last_call_info = {}
    
    def get_last_call_summary(self):
        info = self.last_call_info
        if not info:
            return "لا توجد معلومات"
        
        if info.get("success"):
            status = "✅ ناجح"
            model_info = f"{info.get('model_name')} ({info.get('model_type')})"
            if info.get("fallback_used"):
                status += " ⚠️ (بديل)"
            return f"{status} | النموذج: {model_info} | التوكنز: {info.get('tokens', 0)}"
        else:
            return f"❌ فشل: {info.get('error', 'خطأ غير معروف')}"