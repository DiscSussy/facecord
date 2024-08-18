import discord, pytz, datetime, io, random, webserver
from discord.ext import commands
from discord import Embed
from PIL import Image, ImageEnhance, ImageFilter

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
tz = pytz.timezone("Asia/Ho_Chi_Minh")
colors = [0xff8fe7, 0xab8fff, 0x8ff0ff, 0x93ff8f, 0xd0ff8f, 0xfff88f, 0xffbc8f]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


class Buttons(discord.ui.View):
    def __init__(self, userid):
        super().__init__(timeout=None)
        self.userid = userid

    @discord.ui.button(label="Comment", style=discord.ButtonStyle.primary)
    async def button1(self, interaction: discord.Interaction, button: discord.Button):
        msg = interaction.message
        if msg.thread is None:
            thread = await msg.create_thread(name="Comment")
            await thread.add_user(interaction.user)
            await interaction.response.send_message("Added to comment thread", ephemeral=True, delete_after=3)
        else:
            members = await msg.thread.fetch_members()
            if any(member.id == interaction.user.id for member in members):
                await interaction.response.send_message("You are already in the comment thread", ephemeral=True, delete_after=3)
            else:
                await msg.thread.add_user(interaction.user)
                await interaction.response.send_message("Added to comment thread", ephemeral=True, delete_after=3)

    @discord.ui.button(label="Close Thread", style=discord.ButtonStyle.gray)
    async def button2(self, interaction: discord.Interaction, button: discord.Button):
        msg = interaction.message
        if msg.thread is None:
            await interaction.response.send_message("There's no comment thread", ephemeral=True, delete_after=3)
        else:
            members = await msg.thread.fetch_members()
            if any(member.id == interaction.user.id for member in members):
                await msg.thread.remove_user(interaction.user)
                await interaction.response.send_message("Removed from comment thread", ephemeral=True, delete_after=3)
            else:
                await interaction.response.send_message("You are not in comment thread", ephemeral=True, delete_after=3)

    @discord.ui.button(label="Delete Post", style=discord.ButtonStyle.red)
    async def button3(self, interaction: discord.Interaction, button: discord.Button):
        msg = interaction.message
        if interaction.user.id == self.userid:
            await interaction.response.send_message("Deleted Post", ephemeral=True, delete_after=4)
            await msg.delete()
        else:
            await interaction.response.send_message("Bro ur not the author", ephemeral=True, delete_after=4)

@bot.event
async def on_message(msg: discord.Message):
    if msg.channel.id != 1271384507076968529: return

    images = [att.url for att in msg.attachments if att.content_type.startswith('image/')][:3]
    embeds = [Embed(url='https://lostluma.dev').set_image(url=img) for img in images[:4]]
    
    facecord = bot.get_channel(1271384190046179339)
    now = datetime.datetime.now(tz)

    if len(images) == 1:
        image_bytes = await msg.attachments[0].read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        aspect_ratio = image.width / image.height
        target_ratio = 1.7

        if aspect_ratio < target_ratio:
            new_width = int(image.height * target_ratio)
            crop_height = int(image.width / target_ratio)
            top = (image.height - crop_height) // 2
            bottom = top + crop_height
            cropped_image = image.crop((0, top, image.width, bottom))
            blurred_image = cropped_image.resize((new_width, image.height), Image.LANCZOS).filter(ImageFilter.GaussianBlur(15))

            if blurred_image.mode != 'RGBA':
                blurred_image = blurred_image.convert('RGBA')

            # Make the blurred image slightly transparent
            alpha = blurred_image.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(.5)
            blurred_image.putalpha(alpha)

            blurred_image.paste(image, ((new_width - image.width) // 2, 0), image)
            image = blurred_image

        with io.BytesIO() as image_binary:
            image.save(image_binary, format='PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='processed_image.png')

            embed = discord.Embed()
            embed.set_image(url="attachment://processed_image.png")

            embed.set_author(
                name = f"{msg.author.name}\n{now.strftime('%d/%m/%Y')}",
                icon_url = msg.author.avatar.url
            )
            embed.timestamp = now
            embed.description = msg.content
            embed.color = random.choice(colors)

            post = await facecord.send(embed=embed, file=file, view=Buttons(msg.author.id))
    
    elif len(images) > 1:
        embeds = [Embed(url='https://lostluma.dev').set_image(url=img) for img in images[:4]]

        embeds[0].set_author(
            name = f"{msg.author.name}\n{now.strftime('%d/%m/%Y')}",
            icon_url = msg.author.avatar.url
        )
        embeds[0].timestamp = now
        embeds[0].description = msg.content
        embeds[0].color = random.choice(colors)

        post = await facecord.send(embeds=embeds, view=Buttons(msg.author.id))
    
    else:
        embed = Embed()
        embed.set_author(
            name = f"{msg.author.name}\n{now.strftime('%d/%m/%Y')}",
            icon_url = msg.author.avatar.url
        )
        embed.timestamp = now
        embed.description = msg.content
        embed.color = random.choice(colors)

        post = await facecord.send(embed=embed, view=Buttons(msg.author.id))



    emojis = [discord.utils.get(msg.guild.emojis, name=name) for name in['like', 'love', 'care', 'haha', 'wow', 'sad', 'angry']]
    for emoji in emojis:
        await post.add_reaction(emoji)
        

webserver.keep_alive()
bot.run("ODcxMDQxODk3MDQzNDYwMTM2.Gv2hkB.5w6c3koC90XVYIiFOoREhtecnbGTpTpeOQj-8E")
