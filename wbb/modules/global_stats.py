"""
MIT License

Copyright (c) 2021 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from wbb import app, SUDOERS, BOT_ID, BOT_NAME
from wbb.core.decorators.errors import capture_err
from wbb.utils.fetch import fetch
from wbb.modules import ALL_MODULES
from wbb.utils.dbfunctions import (
    get_served_chats,
    remove_served_chat,
    get_notes_count,
    get_filters_count,
    get_warns_count,
    get_karmas_count,
    get_gbans_count
)
from pyrogram import filters
import asyncio

""" CHAT WATCHER IS IN filters.py"""


@app.on_message(
    filters.command("gstats") & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def global_stats(_, message):
    m = await app.send_message(
        message.chat.id,
        text="__**Analysing Stats**__",
        disable_web_page_preview=True
    )

    # For bot served chat and users count
    served_chats = []
    total_users = 0
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    await m.edit(
        f"__**Generating Statistics Report, Should Take {len(served_chats)*6}+ Seconds.**__",
        disable_web_page_preview=True
    )
    for served_chat in served_chats:
        try:
            await app.get_chat_members(served_chat, BOT_ID)
            await asyncio.sleep(2)
        except Exception:
            await remove_served_chat(served_chat)
            served_chats.remove(served_chat)
            pass
    for i in served_chats:
        try:
            mc = (await app.get_chat(i)).members_count
            total_users += int(mc)
        except Exception:
            await remove_served_chat(served_chat)
            pass
        await asyncio.sleep(2)

    # Gbans count
    gbans = await get_gbans_count()
    _notes = await get_notes_count()
    notes_count = _notes["notes_count"]
    notes_chats_count = _notes["chats_count"]

    # Filters count across chats
    _filters = await get_filters_count()
    filters_count = _filters["filters_count"]
    filters_chats_count = _filters["chats_count"]

    # Warns count across chats
    _warns = await get_warns_count()
    warns_count = _warns["warns_count"]
    warns_chats_count = _warns["chats_count"]

    # Karmas count across chats
    _karmas = await get_karmas_count()
    karmas_count = _karmas["karmas_count"]
    karmas_chats_count = _karmas["chats_count"]

    # Contributors/Developers count and commits on github
    url = "https://api.github.com/repos/thehamkercat/williambutcherbot/contributors"
    rurl = "https://github.com/thehamkercat/williambutcherbot"
    developers = await fetch(url)
    commits = 0
    for developer in developers:
        commits += developer['contributions']
    developers = len(developers)

    # Modules info
    modules_count = len(ALL_MODULES)

    msg = f"""
**Global Stats of {BOT_NAME}**:
**{modules_count}** Modules Loaded
**{gbans}** Globally banned users.
**{filters_count}** Filters, Across **{filters_chats_count}** chats.
**{notes_count}** Notes, Across **{notes_chats_count}** chats.
**{warns_count}** Warns, Across **{warns_chats_count}** chats.
**{karmas_count}** Karma, Across **{karmas_chats_count}** chats.
**{total_users}** Users, Across **{len(served_chats)}** chats.
**{developers}** Developers And **{commits}** Commits On **[Github]({rurl})**."""

    await m.edit(msg, disable_web_page_preview=True)
