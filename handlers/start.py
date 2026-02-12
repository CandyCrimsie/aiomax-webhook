import aiomax

router = aiomax.Router()


@router.on_command("start")
async def start(message: aiomax.Message):
    await message.reply("Aiomax, add middleware, please!")