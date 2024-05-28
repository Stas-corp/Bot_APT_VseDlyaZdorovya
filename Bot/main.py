import asyncio

import __bot_init__ as b_init
import async_bot 

bot = b_init.bot
dp = b_init.dp

if __name__ == '__main__':
    asyncio.run(async_bot.main())