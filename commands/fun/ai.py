from __future__ import annotations

import os
import discord
import asyncio
import config
import re
from collections import defaultdict

from discord.ext import commands
from asgiref.sync import sync_to_async
from typing import TYPE_CHECKING
from utils.logging import log, Ansi
from datetime import datetime

import g4f.debug
from g4f.client import Client
from g4f.stubs import ChatCompletion
from g4f.Provider import Blackbox

from utils.aiprompts import get_prompts

g4f.debug.logging = config.DEBUG

if TYPE_CHECKING:
    from main import Bot

class AiChat(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.chatBot = Client(provider=Blackbox)
        self.chatModel = config.MODEL
        self.conversation_history = defaultdict(list)
        self.message_queue = asyncio.Queue()
        self.bot.loop.create_task(self.process_messages())

        config_dir = os.path.abspath(f"{__file__}/../../../")
        prompt_path = os.path.join(config_dir, "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.starting_prompt = f.read()

    async def process_messages(self):
        while True:
            while not self.message_queue.empty():
                ctx, user_message, attachment_content = await self.message_queue.get()
                async with ctx.channel.typing():
                    try:
                        await self.send_message(ctx, user_message, attachment_content)
                    except Exception as e:
                        log(f"Error while processing message: {e}", Ansi.RED)
                    finally:
                        self.message_queue.task_done()

            await asyncio.sleep(1)

    @commands.command(name="chat", description="chat with kselon!")
    async def chat(self, ctx: commands.Context, *, user_message: str) -> None:
        """chat with kselon! usage: `!chat hello kselon`"""
        await ctx.defer()
        user_id = str(ctx.author.id)
        if not self.conversation_history[user_id]:
            await self.initialize_conversation(user_id)
            
        attachment_content = await self._get_attachment_content(ctx.message.attachments[0] if ctx.message.attachments else None)
        await self.message_queue.put((ctx, user_message, attachment_content))

    @discord.app_commands.command(name="chat", description="chat with kselon!")
    async def chat_slash(self, interaction: discord.Interaction, message: str, attachment: discord.Attachment = None, ephemeral: bool = False) -> None:
        """chat with kselon! Usage: `/chat hello kselon`"""
        await interaction.response.defer(ephemeral=ephemeral)

        user_id = str(interaction.user.id)
        if not self.conversation_history[user_id]:
            await self.initialize_conversation(user_id)
            
        attachment_content = await self._get_attachment_content(attachment)
        await self.message_queue.put((interaction, message, attachment_content))

    @commands.command(name="resetai", aliases=['rst', 'reset'], description="Resets the AI's brain")
    async def reset_chat(self, ctx: commands.Context) -> None:
        """resets the ai's brain"""
        await ctx.defer()
        user_id = str(ctx.author.id)
        self.conversation_history[user_id] = []
        await self.initialize_conversation(user_id)
        await ctx.send("DONE :rofl: :rofl: :rofl: :rofl:")

    async def _get_attachment_content(self, attachment):
        if attachment and attachment.filename.endswith(".txt"):
            content = await attachment.read()
            return attachment.filename, content
        return None

    async def initialize_conversation(self, user_id: str) -> None:
        if not config.use_start_prompt:
            log('use start prompt is false, skipping start prompt.', Ansi.YELLOW)
            return

        try:
            if self.starting_prompt:
                log(f"initializing conversation for user {user_id} with system prompt", Ansi.CYAN)

                self.conversation_history[user_id].append({
                    'role': 'system',
                    'content': self.starting_prompt
                })
                
                response = await self.handle_response(user_id, "Hello")
                
                if config.DEBUG:
                    log(f"response for user {user_id}: {response}", Ansi.GREEN)
            else:
                log("no starting prompt, skipping initialization.", Ansi.YELLOW)
        except Exception as e:
            log(f"error while initializing conversation: {e}", Ansi.RED)

    async def send_message(self, ctx: commands.Context | discord.Interaction, user_message: str, attachment_content: tuple | None):
        user = ctx.author if isinstance(ctx, commands.Context) else ctx.user
        user_id = str(user.id)
        
        try:
            display_message, user_message_for_ai = self._prepare_message(user_message, attachment_content)
            response = await self.handle_response(user_id, f'{user.name}: {user_message_for_ai}')
            response_content = f'> {user.name}: {display_message} \n{response}'
            await self.send_split_message(response_content, ctx)
        
        except Exception as e:
            log(f"error while sending: {e}", Ansi.YELLOW)

    def _prepare_message(self, user_message: str, attachment_content: tuple | None):
        if attachment_content:
            filename, content = attachment_content
            display_message = f"{user_message} (file attached: {filename})"
            user_message_for_ai = f"[{datetime.now().strftime('%d|%A|%B|%Y')}] {user_message}\n{content.decode('utf-8')}"
        else:
            display_message = user_message
            user_message_for_ai = f"[{datetime.now().strftime('%d|%A|%B|%Y')}] " + user_message

        return display_message, user_message_for_ai

    async def handle_response(self, user_id: str, user_message: str) -> str:
        self.conversation_history[user_id].append({'role': 'user', 'content': user_message})
        if len(self.conversation_history[user_id]) > 26:
            system_prompt = next((msg for msg in self.conversation_history[user_id] if msg['role'] == 'system'), None)
            del self.conversation_history[user_id][4:6]
            if system_prompt and system_prompt not in self.conversation_history[user_id]:
                self.conversation_history[user_id].insert(0, system_prompt)

        async_create = sync_to_async(self.chatBot.chat.completions.create, thread_sensitive=True)
        response: ChatCompletion = await async_create(model=self.chatModel, messages=self.conversation_history[user_id])

        bot_response = response.choices[0].message.content
        bot_response = re.sub(r"(?i)generated by blackbox\.ai,? try unlimited chat https://www\.blackbox\.ai/?", "", bot_response).strip()

        self.conversation_history[user_id].append({'role': 'assistant', 'content': bot_response})
        return bot_response

    @discord.app_commands.command(name="switchprompt", description="switches how kselon talks")
    @discord.app_commands.choices(prompt=[
        discord.app_commands.Choice(name="Beatrice", value="beako"), # i suppose
        discord.app_commands.Choice(name="Kselon", value="ksl"), # femboy
        discord.app_commands.Choice(name="Ano", value="ano"), # Me
        discord.app_commands.Choice(name="Echidna", value="ech"), # ...
    ])
    async def prompts(self, interaction: discord.Interaction, prompt: discord.app_commands.Choice[str]):
        await interaction.response.defer(thinking=True)
        user_id = str(interaction.user.id)
        p = prompt.value
        self.conversation_history[user_id] = []

        prompt_content = get_prompts(p)
        self.conversation_history[user_id].append({
            'role': 'system',
            'content': prompt_content
        })
        
        response = await self.handle_response(user_id, "Hello")
        await interaction.followup.send(f"switched to {p}!")
        
        if config.DEBUG:
            log(f"initial response: {response}")

    async def send_split_message(self, response: str, ctx: commands.Context | discord.Interaction, has_followed_up=False):
        char_limit = 1900
        send_method = self._get_send_method(ctx)
        
        if len(response) > char_limit:
            is_code_block = False
            parts = response.split("```")
            for part in parts:
                chunks = [part[i:i + char_limit] for i in range(0, len(part), char_limit)]
                for chunk in chunks:
                    content = f"```{chunk}```" if is_code_block else chunk
                    await self._send_chunk(ctx, send_method, content, has_followed_up)
                    has_followed_up = True
                is_code_block = not is_code_block
        else:
            await self._send_chunk(ctx, send_method, response, has_followed_up)
        
        return has_followed_up

    def _get_send_method(self, ctx):
        if isinstance(ctx, discord.Interaction):
            return ctx.response.send_message if not ctx.response.is_done() else ctx.followup.send
        return ctx.send

    async def _send_chunk(self, ctx, send_method, content, has_followed_up):
        if has_followed_up:
            await ctx.channel.send(content)
        else:
            await send_method(content)

async def setup(bot: Bot):
    await bot.add_cog(AiChat(bot))