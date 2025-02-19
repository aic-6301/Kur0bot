import asyncio
import os
import shutil
import traceback
from datetime import datetime
from json import load
from os import sep as ossep
from pathlib import Path

import discord
from discord.ext import commands
from discord.ext.tasks import loop
from dotenv import load_dotenv
from motor import motor_asyncio as motor
import urllib

# 環境変数(.env)をロード
load_dotenv()

token = os.environ['DISCORD_BOT_TOKEN']
bot = commands.Bot(
    command_prefix='k/',
    case_insensitive=True,
    activity=discord.Activity(
        name='くろでんのくろでんによるくろでんのためのぼっと', type=discord.ActivityType.playing),
    intents=discord.Intents.all(),
)

guild_id = 733707710784340100


@bot.event
async def on_ready():
    global osirase_ch, osirase_role
    bot.manageguild = bot.get_guild(981923517736046592)
    bot.guild = bot.get_guild(733707710784340100)
    bot.guild_id = 733707710784340100
    bot.owner = bot.get_user(699414261075804201)
    bot.unei_role = bot.guild.get_role(738956776258535575)
    bot.unei_members = bot.unei_role.members
    bot.unei_ch = bot.get_channel(738397603439444028)
    bot.everyone = bot.guild.get_role(733707710784340100)

    bot.stage = bot.get_channel(884734698759266324)
    osirase_ch = bot.get_channel(734605726491607091)
    osirase_role = bot.guild.get_role(738954587922235422)
    login_ch = bot.get_channel(888416525579612230)

    # UnbelievaBoatのAPI系のやつを定義
    UB_API_TOKEN = os.environ.get('UNB_TOKEN')
    bot.ub_url = 'https://unbelievaboat.com/api/v1/guilds/733707710784340100/users/'
    bot.ub_header = {'Authorization': UB_API_TOKEN, 'Accept': 'application/json'}

    # DataBase
    bot.dbclient = motor.AsyncIOMotorClient('mongodb://localhost:27017')
    bot.db = bot.dbclient["Kur0Bot"]
    bot.profiles_collection = bot.db.profiles
    bot.vc_info = bot.db.vc_info
    bot.ttsdb = bot.dbclient["TTSBot"]
    bot.ttsvc_info = bot.ttsdb.vc_info
    bot.ttsvc_lang = bot.ttsdb.vc_lang

    # しりとり機能のやつ定義
    bot.siritori_ch = bot.get_channel(982967189109878804)
    bot.siritori_list = []
    bot.siritori_idlist = {}
    async for msg in bot.siritori_ch.history(limit=None):
        if msg.author.bot or msg.content.startswith(bot.command_prefix) or msg.content in bot.siritori_list:
            continue
        bot.siritori_list.insert(0, msg.content)
        bot.siritori_idlist.update({msg.content:msg.id})


    bot.siritori = True

    # VC機能系定義
    bot.tts_file = '.tts_voice'
    try:
        shutil.rmtree(bot.tts_file)
    except:
        pass
    os.mkdir(bot.tts_file)

    bot.botrole = bot.guild.get_role(734059242977230969)


    # config.jsonをロード
    try:
        with open('config.json', 'r+', encoding='utf-8') as file:
            bot.config = load(file)
        print('Config loaded')
    except:
        traceback.print_exc()
        print('Config not loaded')
    # welcomeフォルダ内のcogをロード
    for file in os.listdir('./cog/welcome'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.welcome.{file[:-3]}')
                print(f'Loaded cog: welcome.{file[:-3]}')
            except:
                traceback.print_exc()
    # funフォルダ内のcogをロード
    for file in os.listdir('./cog/fun'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.fun.{file[:-3]}')
                print(f'Loaded cog: fun.{file[:-3]}')
            except:
                traceback.print_exc()
    # moneyフォルダ内のcogをロード
    for file in os.listdir('./cog/money'):
        if file.endswith('.py'):
            try:
                # 一時的にVC報酬を消し飛ばす
                if file == 'vcmoney.py':
                    continue

                await bot.load_extension(f'cog.money.{file[:-3]}')
                print(f'Loaded cog: money.{file[:-3]}')
            except:
                traceback.print_exc()
    # serverフォルダ内のcogをロード
    for file in os.listdir('./cog/server'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.server.{file[:-3]}')
                print(f'Loaded cog: server.{file[:-3]}')
            except:
                traceback.print_exc()
    # utilフォルダ内のcogをロード
    for file in os.listdir('./cog/util'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.util.{file[:-3]}')
                print(f'Loaded cog: util.{file[:-3]}')
            except:
                traceback.print_exc()
    # manageフォルダ内のcogをロード
    for file in os.listdir('./cog/manage'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.manage.{file[:-3]}')
                print(f'Loaded cog: manage.{file[:-3]}')
            except:
                traceback.print_exc()
    # vcフォルダ内のcogをロード
    for file in os.listdir('./cog/vc'):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'cog.vc.{file[:-3]}')
                print(f'Loaded cog: vc.{file[:-3]}')
            except:
                traceback.print_exc()
    try:
        await bot.load_extension('jishaku')
        print('Loaded cog: jishaku')
    except:
        traceback.print_exc()
    print('cog loaded')
    ttsinfo = await bot.vc_info.find_one({
        "tts": True
    }, {
        "_id": False  # 内部IDを取得しないように
    })
    radioinfo = await bot.vc_info.find_one({
        "tts": True
    }, {
        "_id": False  # 内部IDを取得しないように
    })
    if ttsinfo is not None:
        channel = bot.guild.get_channel(ttsinfo['channel_id'])
        await channel.connect()
        await channel.send('再接続しました')
    elif radioinfo is not None:
        channel = bot.guild.get_channel(ttsinfo['channel_id'])
        await channel.connect()
        bot.guild.voice_client.play(
            discord.FFmpegPCMAudio(radioinfo['radioURL']))
        await channel.send('再接続しました')
    print(f'ready: {bot.user} (ID: {bot.user.id})')
    await bot.owner.send(f'きどうしたよ！！！！！！！ほめて！！！！！！！！\n起動時刻: {datetime.now()}')


# エラー表示
@bot.event
async def on_command_error(ctx, error):
    error_ch = bot.get_channel(1002616704603525151)
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(
        traceback.TracebackException.from_exception(orig_error).format())
    embed = discord.Embed(title="<:guard_ng:748539994557120614> Error!", description='エラーが発生しました',
                          timestamp=ctx.message.created_at, color=discord.Colour.red())
    embed.add_field(
        name='メッセージID', value=f'お問い合わせの際にはこちらのidもお持ちください:\n`{ctx.message.id}`')
    embed.add_field(name='エラー内容', value=error, inline=False)
    embed.set_footer(text="お困りの場合はBot管理者までお問い合わせください")
    await ctx.send(embed=embed)
    embed2 = discord.Embed(title='エラー情報', description='',
                           timestamp=ctx.message.created_at, color=discord.Colour.red())
    embed2.add_field(name='サーバー', value=ctx.message.guild.name, inline=False)
    embed2.add_field(
        name='チャンネル', value=ctx.message.channel.name, inline=False)
    embed2.add_field(name='コマンド', value=ctx.message.content, inline=False)
    embed2.add_field(name='実行ユーザー名', value=ctx.author, inline=False)
    embed2.add_field(name='id', value=ctx.message.id, inline=False)
    embed2.add_field(name='内容', value=error, inline=False)
    await error_ch.send(embed=embed2)

bot.run(token)
