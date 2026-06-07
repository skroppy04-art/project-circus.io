import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from mcrcon import MCRcon
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def init_db():
    async with aiosqlite.connect("applications.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS applications(
            message_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            minecraft_nick TEXT NOT NULL,
            age TEXT NOT NULL,
            source TEXT NOT NULL,
            goal TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
        """)
        await db.commit()


class RejectReasonModal(discord.ui.Modal, title="Причина отказа"):

    reason = discord.ui.TextInput(
        label="Укажите причину отказа",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    def __init__(self, applicant_id: int):
        super().__init__()
        self.applicant_id = applicant_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user = await bot.fetch_user(self.applicant_id)

            embed = discord.Embed(
                title="❌ Заявка отклонена",
                description=f"Причина:\n{self.reason.value}",
                color=discord.Color.red()
            )

            await user.send(embed=embed)

        except Exception:
            pass

        await interaction.response.send_message(
            "Заявка отклонена.",
            ephemeral=True
        )


class AdminView(discord.ui.View):

    def __init__(self, applicant_id: int, minecraft_nick: str):
        super().__init__(timeout=None)

        self.applicant_id = applicant_id
        self.minecraft_nick = minecraft_nick

    @discord.ui.button(
    label="Одобрить",
    emoji="✅",
    style=discord.ButtonStyle.success,
    custom_id="approve_application"
    )   
    async def approve(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)
        member = interaction.guild.get_member(
            self.applicant_id
        )

        if member:
            role = interaction.guild.get_role(
                APPROVED_ROLE_ID
            )

            if role:
                await member.add_roles(role)

        try:
            user = await bot.fetch_user(
                self.applicant_id
            )

            embed = discord.Embed(
                title="✅ Заявка одобрена",
                description=(
                    "Поздравляем! "
                    "Ваша заявка была одобрена."
                ),
                color=discord.Color.green()
            )

            await user.send(embed=embed)

        except Exception:
            pass

        try:
            with MCRcon(
                RCON_HOST,
                RCON_PASSWORD,
                port=RCON_PORT
            ) as mcr:

                mcr.command(
                    f"swl add {self.minecraft_nick}"
                )

        except Exception as e:
            print("RCON error:", e)

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Одобренная заявка"

        await interaction.message.edit(
            embed=embed,
            view=None
        )

        async with aiosqlite.connect(
            "applications.db"
        ) as db:

            await db.execute(
                """
                UPDATE applications
                SET status='approved'
                WHERE message_id=?
                """,
                (interaction.message.id,)
            )

            await db.commit()

        await interaction.followup.send(
    "Заявка одобрена.",
    ephemeral=True
)

    @discord.ui.button(
    label="Отклонить",
    emoji="❌",
    style=discord.ButtonStyle.danger,
    custom_id="reject_application"
)
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            RejectReasonModal(
                self.applicant_id
            )
        )


class ApplicationModal(
    discord.ui.Modal,
    title="Заявка на сервер"
):

    minecraft_nick = discord.ui.TextInput(
        label="Ник Minecraft",
        max_length=16
    )

    age = discord.ui.TextInput(
        label="Возраст",
        max_length=3
    )

    source = discord.ui.TextInput(
        label="Откуда узнали о сервере"
    )

    goal = discord.ui.TextInput(
        label="Цель игры",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        channel = await bot.fetch_channel(
    APPLICATION_CHANNEL_ID
)

        embed = discord.Embed(
            title="📋 Новая заявка",
            color=discord.Color.orange()
        )

        embed.set_author(
            name=str(interaction.user),
            icon_url=interaction.user.display_avatar.url
        )

        embed.add_field(
            name="🎮 Ник",
            value=self.minecraft_nick.value,
            inline=False
        )

        embed.add_field(
            name="🎂 Возраст",
            value=self.age.value,
            inline=False
        )

        embed.add_field(
            name="📢 Откуда узнал",
            value=self.source.value,
            inline=False
        )

        embed.add_field(
            name="🎯 Цель",
            value=self.goal.value,
            inline=False
        )

        embed.set_footer(
            text=f"ID пользователя: {interaction.user.id}"
        )

        msg = await channel.send(
            embed=embed,
            view=AdminView(
                interaction.user.id,
                self.minecraft_nick.value
            )
        )

        async with aiosqlite.connect(
            "applications.db"
        ) as db:

            await db.execute(
                """
                INSERT INTO applications(
                    message_id,
                    user_id,
                    minecraft_nick,
                    age,
                    source,
                    goal
                )
                VALUES(?,?,?,?,?,?)
                """,
                (
                    msg.id,
                    interaction.user.id,
                    self.minecraft_nick.value,
                    self.age.value,
                    self.source.value,
                    self.goal.value
                )
            )

            await db.commit()

        await interaction.response.send_message(
            "✅ Ваша заявка успешно отправлена.",
            ephemeral=True
        )


class ApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Подать заявку",
        emoji="📨",
        style=discord.ButtonStyle.primary,
        custom_id="apply_button"
    )
    async def apply(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            ApplicationModal()
        )


@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):

    embed = discord.Embed(
        title="Набор на сервер",
        description="Нажмите кнопку ниже для подачи заявки.",
        color=discord.Color.blurple()
    )

    await ctx.send(
        embed=embed,
        view=ApplyView()
    )

@bot.event
async def on_ready():
    await init_db()

    bot.add_view(ApplyView())

    print(f"Вошёл как {bot.user}")


bot.run(TOKEN)
