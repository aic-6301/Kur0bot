from discord.ext import commands
from discord import app_commands
import discord
import subprocess


class name(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.p = None

    group = app_commands.Group(name="testbot", description="TestBot", guild_ids=[733707710784340100], guild_only=True)

    @group.command()
    async def start(self, interaction: discord.Interaction):
        await interaction.response.send_message('実行しました')
        self.p = subprocess.Popen(f'py 0den.py', cwd=r'C:/Users/Kur0den/Desktop/Kur0BotTest/', shell=True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        try:
            for line in iter(self.p.stdout.readline,b''):
                if line.rstrip().decode("utf8") != '':
                    await self.bot.owner.send(line.rstrip().decode("utf8"))
        except:
            return


    @group.command()
    async def kill(self, interaction: discord.Interaction):
        self.p.kill()
        await interaction.responce.send_message('実行しました')



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(name(bot))