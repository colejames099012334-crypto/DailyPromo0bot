import os
import logging
import tempfile
import sys
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language options
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Mandarin)',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

# User preferences
user_preferences = {}

def get_token():
    """Get token from environment variables"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token != "YOUR_BOT_TOKEN_HERE" and token != "your_bot_token_here":
        return token
    
    token = os.getenv('BOT_TOKEN')
    if token and token != "YOUR_BOT_TOKEN_HERE":
        return token
    
    token = os.getenv('TELEGRAM_TOKEN')
    if token and token != "YOUR_BOT_TOKEN_HERE":
        return token
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"🎙️ Welcome to DailyPromo0bot, {user.first_name}! 👋\n\n"
        "I'm your Text-to-Speech assistant. Send me any text and I'll convert it to speech!\n\n"
        "📝 Commands:\n"
        "/start - Show this message\n"
        "/lang - Change language\n"
        "/help - Get help\n"
        "/about - About this bot\n\n"
        "🌍 Just send me any text and I'll reply with an audio file!"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about information."""
    await update.message.reply_text(
        "🤖 About DailyPromo0bot\n\n"
        "🎯 Purpose: Convert text to speech in multiple languages\n"
        "🌐 Languages: 12+ languages supported\n"
        "⚡ Features: Fast, accurate, and free\n"
        "🔧 Technology: Python + Google TTS\n"
        "📅 Created: 2026\n\n"
        "💡 Perfect for:\n"
        "• Learning pronunciation\n"
        "• Creating voice notes\n"
        "• Accessibility\n"
        "• Language practice"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    await update.message.reply_text(
        "🎙️ DailyPromo0bot Help\n\n"
        "📖 How to use:\n"
        "1. Send me any text message\n"
        "2. I'll convert it to speech\n"
        "3. You'll receive an audio file\n\n"
        "🌐 Commands:\n"
        "/start - Welcome message\n"
        "/help - This help menu\n"
        "/lang - Change language\n"
        "/about - About this bot\n\n"
        "🗣️ Supported languages:\n"
        "English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi\n\n"
        "💡 Tip: Use /lang to change your preferred language!"
    )

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu."""
    keyboard = []
    row = []
    for i, (code, name) in enumerate(LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Select your preferred language:",
        reply_markup=reply_markup
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    user_preferences[user_id] = {'lang': lang_code}
    
    await query.edit_message_text(
        f"✅ Language set to: {LANGUAGES[lang_code]}\n\n"
        f"🎤 Now send me any text to convert to speech!"
    )

async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert text to speech and send audio."""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if text is too long
    if len(text) > 5000:
        await update.message.reply_text(
            "⚠️ Text is too long! Please send text under 5000 characters."
        )
        return
    
    # Get user's language preference
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    
    # Send typing action
    await update.message.chat.send_action(action="record_voice")
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        # Convert text to speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_path)
        
        # Send audio file
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🔊 Text-to-Speech (Language: {LANGUAGES[lang]})\n"
                       f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}",
                title="TTS Audio",
                performer="DailyPromo0bot"
            )
        
        # Clean up temp file
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        await update.message.reply_text(
            "❌ Sorry, an error occurred while converting text to speech. Please try again."
        )

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await update.message.reply_text(
        "🎤 I can only convert text messages to speech.\n"
        "Please send me a text message instead!"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

def main() -> None:
    """Start the bot."""
    logger.info("🎙️ DailyPromo0bot Starting...")
    logger.info("🔍 Looking for bot token...")
    
    # Get token
    token = get_token()
    
    if not token:
        logger.error("❌ No valid token found!")
        logger.info("Please set TELEGRAM_BOT_TOKEN in Railway environment variables")
        logger.info("Go to: Railway Dashboard -> Your Project -> Variables -> Add Variable")
        sys.exit(1)
    
    logger.info(f"✅ Token found! Token starts with: {token[:10]}...")
    logger.info("🚀 Starting DailyPromo0bot...")
    
    try:
        # Create application
        application = Application.builder().token(token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("lang", language_menu))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
        
        # Add message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ DailyPromo0bot is running and ready!")
        logger.info("🎯 Bot Username: @DailyPromo0bot")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
