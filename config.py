# config.py - إعدادات النماذج والمسارات (نسخة كاملة)

# قاموس النماذج: كل نموذج له إعداداته الخاصة
MODELS = {
    "groq": {
        "name": "💡 المبتكر (Groq)",
        "provider": "groq",
        "model_id": "llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
        "temperature": 0.7,
        "full_model_name": "groq/llama-3.3-70b-versatile"
    },
    "openrouter": {
        "name": "📊 المحلل (OpenRouter)",
        "provider": "openrouter",
        "model_id": "qwen/qwen-2.5-72b-instruct",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.7,
        "full_model_name": "openrouter/qwen/qwen-2.5-72b-instruct"
    },
    "mistral": {
        "name": "💻 المبرمج (Mistral)",
        "provider": "mistral",
        "model_id": "mistral-large-latest",
        "api_key_env": "MISTRAL_API_KEY",
        "temperature": 0.2,
        "full_model_name": "mistral/mistral-large-latest"
    },
    "cohere": {
        "name": "📚 الباحث (Cohere)",
        "provider": "cohere",
        "model_id": "command-r-08-2024",
        "api_key_env": "COHERE_API_KEY",
        "temperature": 0.3,
        "full_model_name": "cohere/command-r-08-2024"
    },
    "claude": {
        "name": "⚡ المنفذ (Claude Haiku)",
        "provider": "anthropic",
        "model_id": "claude-3-haiku-20240307",
        "api_key_env": "ANTHROPIC_API_KEY",
        "temperature": 0.5,
        "full_model_name": "anthropic/claude-3-haiku-20240307",
        "api_base": "https://api.anthropic.com/v1"
    },
    "qwen_plus": {
        "name": "🔷 الخبير المنطقي (Qwen 2.5 72B)",
        "provider": "openrouter",
        "model_id": "qwen/qwen-2.5-72b-instruct:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.3,
        "full_model_name": "openrouter/qwen/qwen-2.5-72b-instruct:free"
    },
    # 🔷 نموذج جوجل الجديد: Gemma 4 26B A4B IT (مجاني)
    "gemma": {
        "name": "🔷 Gemma 4 (Google - Free)",
        "provider": "openrouter",
        "model_id": "google/gemma-4-26b-a4b-it:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.5,
        "full_model_name": "openrouter/google/gemma-4-26b-a4b-it:free"
    },
        # ... (بعد قسم "gemma")
    
    # 📊 الوكيل الثامن: متخصص في الرسوم البيانية
    "chart_agent": {
        "name": "📊 خبير الرسوم",
        "provider": "openrouter",
        "model_id": "mistralai/mistral-7b-instruct:free",  # مجاني وجيد للكود
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.3,  # منخفض لدقة الكود
        "full_model_name": "openrouter/mistralai/mistral-7b-instruct:free"
    }
}

# خريطة توجيه المهام: أي نموذج نفضل لكل نوع مهمة
TASK_ROUTING = {
    "coding": ["mistral", "groq", "gemma", "claude"],
    "research": ["cohere", "openrouter", "groq"],
    "creative": ["groq", "openrouter", "claude", "gemma"],
    "reasoning": ["cohere", "mistral", "openrouter", "qwen_plus"],
    "general": ["gemma", "groq", "openrouter"],
    "quick": ["gemma"],  # مهام سريعة جداً
    "complex": ["qwen_plus", "mistral", "cohere", "claude"]  # مهام معقدة
}