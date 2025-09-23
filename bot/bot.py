from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from huggingface_hub import InferenceClient
import aiofiles
import json
import os
import logging
from datetime import datetime

class Bot:
    config = None
    client = InferenceClient()
    logger = None
    @staticmethod
    def setup_logger():
        log_dir = Bot.config['logs']
        os.makedirs(log_dir, exist_ok=True)
        logger = logging.getLogger('telegram_bot')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s | %(user_id)s | %(username)s | %(action)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    @staticmethod
    def get_user_info(update: Update) -> dict:
        """Получение информации о пользователе"""
        user = update.message.from_user if update.message else update.callback_query.from_user
        return {
            'user_id': str(user.id),
            'username': user.username or 'no_username',
            'first_name': user.first_name or '',
            'last_name': user.last_name or ''
        }
    
    @staticmethod
    def log_user_action(update: Update, action: str, message: str = ""):
        """Удобный метод для логирования действий пользователя"""
        user_info = Bot.get_user_info(update)
        Bot.logger.info(
            message, 
            extra={
                'user_id': user_info['user_id'],
                'username': user_info['username'],
                'action': action
            }
        )
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_info = Bot.get_user_info(update)
        welcome_message = f"Приветствую вас, {user_info['first_name'] or 'товарищ'}!\n" + Bot.config["info"]
        
        Bot.log_user_action(update, "COMMAND_START", "User started bot")
        await update.message.reply_text(welcome_message)
        
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        Bot.log_user_action(update, "COMMAND_HELP", "User requested help")
        await update.message.reply_text(Bot.config["info"])
    
    @staticmethod
    async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        user_file_path = f"{Bot.config['user_dir']}/{user_id}.json"
        
        if os.path.exists(user_file_path):
            os.remove(user_file_path)
            Bot.log_user_action(update, "COMMAND_NEW_CHAT", "User cleared chat history")
        else:
            Bot.log_user_action(update, "COMMAND_NEW_CHAT", "User requested new chat (no history found)")
            
        await update.message.reply_text("Новый диалог создан!")

    @staticmethod
    async def generate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        user_message = update.message.text
        user_id = user.id
        Bot.log_user_action(
            update, 
            "MESSAGE_RECEIVED", 
            f"Text: {user_message[:100]}{'...' if len(user_message) > 100 else ''}"
        )
        
        wait_message = await update.message.reply_text("⏳ Пожалуйста, подождите...")

        try:
            result = await Bot.generate_llm_text(user_id, user_message)
            await wait_message.delete()
            
            # Логируем успешный ответ
            Bot.log_user_action(
                update, 
                "MESSAGE_SENT", 
                f"Response length: {len(result)} chars, Text: {result[:100]}{'...' if len(result) > 100 else ''}"
            )
            
            await update.message.reply_text(result)

        except Exception as e:
            error_msg = f"❌ Произошла ошибка: {str(e)}"
            Bot.log_user_action(update, "ERROR", f"Error: {str(e)}")
            await wait_message.edit_text(error_msg)
            
    @staticmethod
    async def generate_llm_text(user_id: int, text: str) -> str:
        user_file_path = f"{Bot.config['user_dir']}/{user_id}.json"
        Bot.logger.info(
            f"Starting LLM processing, text length: {len(text)}",
            extra={
                'user_id': str(user_id),
                'username': 'system',
                'action': 'LLM_PROCESSING_START'
            }
        )
        
        if os.path.exists(user_file_path):
            async with aiofiles.open(user_file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                context_messages = json.loads(content)
        else:
            context_messages = []

        context_messages.append({"role": "user", "content": text})

        if len(context_messages) > 10: # to avoid overfilling the memory
            context_messages = context_messages[-10:]

        loop = asyncio.get_event_loop()
        completion = await loop.run_in_executor(None, lambda: Bot.client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=context_messages,
        ))

        assistant_response = completion.choices[0].message.content
        context_messages.append({"role": "assistant", "content": assistant_response})

        async with aiofiles.open(user_file_path, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(context_messages, ensure_ascii=False, indent=2))
        Bot.logger.info(
            f"LLM processing completed, response length: {len(assistant_response)}",
            extra={
                'user_id': str(user_id),
                'username': 'system',
                'action': 'LLM_PROCESSING_END'
            }
        )

        return assistant_response

def main() -> None:
    with open("config.json") as file:
        Bot.config = json.load(file)
    Bot.logger = Bot.setup_logger()
    Bot.logger.info(
        "Bot started",
        extra={
            'user_id': 'SYSTEM',
            'username': 'system',
            'action': 'BOT_START'
        }
    )
    token = Bot.config['token']
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", Bot.start))
    app.add_handler(CommandHandler("help", Bot.help_command))
    app.add_handler(CommandHandler("new_chat", Bot.new_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.generate_text))
    
    Bot.logger.info(
        "Bot handlers registered, starting polling",
        extra={
            'user_id': 'SYSTEM',
            'username': 'system',
            'action': 'BOT_READY'
        }
    )
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()