import os
import sys
from typing import Any

import discord
from ezjsonpy import get_config_value
from loguru import logger
from discord.ext.commands.bot import Bot

from ..constants import PathConstants


class DiscordBot(Bot):
    def __init__(self, command_prefix: str, *, intents: discord.Intents, **options: Any):
        super().__init__(command_prefix, intents=intents, **options)
        self.guild_id: int = get_config_value('guildId')
        self.loaded_cogs: list[str] = []

    @logger.catch
    async def setup_hook(self) -> None:
        """Hook to be called after the bot has been initialized."""
        await self._load_extensions()
        await self.tree.sync()

    @logger.catch
    async def _load_extensions(self) -> None:
        """Load the initial extensions."""
        cogs_folders: list[str] = [folder for folder in os.listdir(PathConstants.COGS_PATH) if folder != "__pycache__"]

        for folder in cogs_folders:
            files: list[str] = os.listdir(f"{PathConstants.COGS_PATH}/{folder}")

            for file in files:
                if not file.endswith('.py') or file == '__pycache__.py':
                    continue

                cog: str = f'{PathConstants.COG_PATH}.{folder}.{file[:-3]}'
                self.loaded_cogs.append(cog)

        for cog in self.loaded_cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded extension {cog}")

            except Exception as e:
                logger.critical(f"Failed to load extension {cog}: {e}")
                sys.exit(1)

    async def on_ready(self):
        """The on_ready function for the bot."""
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    @staticmethod
    def create_bot(command_prefix: str, *, intents: discord.Intents, **options: Any) -> Bot:
        """
        Create a new bot instance.

        :param command_prefix: The command prefix for the bot.
        :param intents: The intents for the bot.
        :param options: Additional options for the bot.
        :return: A new bot instance.
        """
        return DiscordBot(command_prefix, intents=intents, **options)
