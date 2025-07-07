# ─── Paths & I/O ───────────────────────────────────────────────────────────────
TMP_MP3_DIR              = "tmp_mp3"
OUTPUT_DIR               = r""
VOICEVOX_PATH            = r""
PROMPT_FILE              = "prompt.txt"
DEBUG_INPUT_FILE         = "debugging/input.txt"
DEBUG_RESPONSE_FILE      = "debugging/response.txt"
CSS_FILE                 = "anki_style.txt"
ICON_FILE                = "icons/icon.png"

# ─── VOICEVOX / TTS Settings ───────────────────────────────────────────────────
API_URL                   = "127.0.0.1"       
API_PORT                  = "50021"
AUDIO_QUERY_ENDPOINT      = "/audio_query"
AUDIO_SYNTHESIS_ENDPOINT  = "/synthesis"
VOICEVOX_SPEAKER          = 2

# ─── Application Window ────────────────────────────────────────────────────────
WINDOW_TITLE              = "Anki Deck Generator"
WINDOW_LENGTH             = 600
WINDOW_WIDTH              = 800
ICON_SIZE                 = 64
FONT_SIZE                 = 16
MARGINS                   = [20, 20, 20, 20]
SPACING                   = 16

# ─── Deck & Card Defaults ─────────────────────────────────────────────────────
DEFAULT_TITLE             = ""
SUBDECK_NAMES             = {"L": "lines", "W": "Words", "K": "Kanji"}
CARD_MODEL                = 1607392319
TRANSLATION_TYPE_KEYS     = ["L", "W", "K"]

# ─── AI/Translation Settings ──────────────────────────────────────────────────
AI_MODEL                  = "gpt-4o-mini"
# AI_MODEL                = "gpt-3.5-turbo"
MAX_TOKENS                = 1024
TEMPERATURE               = 0.2

# ─── Debug Flags & Terms ──────────────────────────────────────────────────────
DEBUG_INPUT               = False
DEBUG_API                 = False
TERMS_AGREEMENT_AGREED_TO = False
