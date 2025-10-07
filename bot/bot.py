from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from huggingface_hub import InferenceClient
import aiofiles
import json
import os
import asyncpg

class Bot:
    config = None
    client = InferenceClient()
    db_pool = None
    
    @staticmethod
    def get_user_info(update: Update) -> dict:
        user = update.message.from_user if update.message else update.callback_query.from_user
        return {
            'user_id': str(user.id),
            'username': user.username or 'unknown',
            'first_name': user.first_name or ''
            }
    
    @staticmethod
    async def log_user_action(update: Update, action: str, message: str = ""):
        """Удобный метод для логирования действий пользователя"""
        try:
            user_info = Bot.get_user_info(update)
            user_id = user_info['user_id']
            username = user_info['username']
            
            log_data = {
                'user_id': user_id,
                'username': username,
                'action': action,
                'message': message,
            }
            
            async with Bot.db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO tgdb_log (user_id, username, action, message)
                    VALUES ($1, $2, $3, $4)
                    """,
                    log_data['user_id'],
                    log_data['username'],
                    log_data['action'],
                    log_data['message'],
                )
        except Exception as e:
            print(f"Ошибка при логировании: {e}")
            
    @staticmethod
    async def init_db():
        db_config = Bot.config['db']
        Bot.db_pool = await asyncpg.create_pool(
            database=db_config['name'],
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['pass'],
            min_size=1,
            max_size=10
        )
        print("Подключение прошло успешно")
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_info = Bot.get_user_info(update)
        welcome_message = f"Приветствую вас, {user_info['first_name'] or 'товарищ'}!\n" + Bot.config["info"]
        
        await Bot.log_user_action(update, "COMMAND_START", "User started bot")
        await update.message.reply_text(welcome_message)
        
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await Bot.log_user_action(update, "COMMAND_HELP", "User requested help")
        await update.message.reply_text(Bot.config["info"])
    
    @staticmethod
    async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        user_file_path = f"{Bot.config['user_dir']}/{user_id}.json"
        
        if os.path.exists(user_file_path):
            os.remove(user_file_path)
            await Bot.log_user_action(update, "COMMAND_NEW_CHAT", "User cleared chat history")
        else:
            await Bot.log_user_action(update, "COMMAND_NEW_CHAT", "User requested new chat (no history found)")
            
        await update.message.reply_text("Новый диалог создан!")

    @staticmethod
    async def generate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        user_message = update.message.text
        user_id = user.id
        await Bot.log_user_action(
            update, 
            "MESSAGE_RECEIVED", 
            f"Text: {user_message[:100]}{'...' if len(user_message) > 100 else ''}"
        )
        
        wait_message = await update.message.reply_text("⏳ Пожалуйста, подождите...")

        try:
            result = await Bot.generate_llm_text(user_id, user_message)
            await wait_message.delete()
            
            await Bot.log_user_action(
                update, 
                "MESSAGE_SENT", 
                f"Response length: {len(result)} chars, Text: {result[:100]}{'...' if len(result) > 100 else ''}"
            )
            
            await update.message.reply_text(result)

        except Exception as e:
            error_msg = f"❌ Произошла ошибка: {str(e)}"
            await Bot.log_user_action(update, "ERROR", f"Error: {str(e)}")
            await wait_message.edit_text(error_msg)
            
    @staticmethod
    async def generate_llm_text(user_id: int, text: str) -> str:
        user_file_path = f"{Bot.config['user_dir']}/{user_id}.json"
        
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

        return assistant_response

def main() -> None:
    with open("config.json") as file:
        Bot.config = json.load(file)
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Bot.init_db())
    
    token = Bot.config['token']
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", Bot.start))
    app.add_handler(CommandHandler("help", Bot.help_command))
    app.add_handler(CommandHandler("new_chat", Bot.new_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.generate_text))
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()