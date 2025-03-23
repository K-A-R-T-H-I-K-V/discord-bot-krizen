import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remindme(self, ctx, time: str, *, reminder: str):
        """Set a reminder. Example: !remindme 10m Take a break!"""
        time_multipliers = {"s": 1, "m": 60, "h": 3600}
        unit = time[-1]  # Last character (s, m, h)
        if unit not in time_multipliers or not time[:-1].isdigit():
            await ctx.send("⚠️ Invalid time format. Use `10m`, `2h`, etc.")
            return
        
        wait_time = int(time[:-1]) * time_multipliers[unit]
        await ctx.send(f"⏳ Reminder set: '{reminder}' in {time}.")
        await asyncio.sleep(wait_time)
        await ctx.send(f"🔔 {ctx.author.mention}, reminder: **{reminder}**")

    @commands.command()
    async def schedule(self, ctx, event: str, date: str, time: str):
        """Schedule an event. Example: !schedule Meeting 2025-01-01 15:00"""
        try:
            event_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            delay = (event_time - datetime.now()).total_seconds()
            if delay <= 0:
                await ctx.send("⚠️ The date/time must be in the future.")
                return

            await ctx.send(f"📅 Event '{event}' scheduled for {date} at {time}.")
            await asyncio.sleep(delay)
            await ctx.send(f"⏰ Reminder: **{event}** is happening now!")
        except ValueError:
            await ctx.send("⚠️ Invalid date/time format. Use `YYYY-MM-DD HH:MM`.")

async def setup(bot):
    await bot.add_cog(Events(bot))
