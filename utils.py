import logging
from config import OLLAMA_MODEL, OLLAMA_URL

# Re-export from services
from services.ai_service import (
    clean_json_output,
    analyze_image,
    repair_lazy_json,
    fix_truncated_json,
    remove_json_comments,
    clean_and_parse_json,
    query_ollama,
    CHAT_ENDPOINT,
    base_url
)
from services.rag_service import (
    get_embedding,
    cosine_similarity,
    retrieve_relevant_context,
    EMBED_ENDPOINT,
    embedding_cache
)
from services.session_service import get_session, sessions
from services.tools import (
    calculate_bmi,
    estimate_daily_calories,
    AVAILABLE_TOOLS,
    execute_tool_call
)

logger = logging.getLogger(__name__)
