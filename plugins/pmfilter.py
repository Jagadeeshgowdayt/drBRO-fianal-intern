import asyncio
import re
import math
import random
import pytz
from datetime import datetime, timedelta
lock = asyncio.Lock()
from database.users_chats_db import db
from database.refer import referdb
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, WebAppInfo
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, ChatAdminRequired
from utils import get_size, is_subscribed,is_req_subscribed, group_setting_buttons, get_poster, temp, get_settings, save_group_settings, get_cap, imdb, is_check_admin, extract_request_content, log_error, clean_filename, generate_season_variations
from database.users_chats_db import db
from database.config_db import mdb
from database.ia_filterdb import Media, Media2, get_file_details, get_search_results, get_bad_files
import logging
from urllib.parse import quote_plus
from dreamxbotz.util.file_properties import get_name, get_hash
from database.config_db import mdb
from fuzzywuzzy import process

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import tracemalloc
tracemalloc.start()


TIMEZONE = "Asia/Kolkata"
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if EMOJI_MODE:
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception:
            await message.react(emoji="⚡️", big=True)
    await mdb.update_top_messages(message.from_user.id, message.text)
    if message.chat.id != SUPPORT_CHAT_ID:
        settings = await get_settings(message.chat.id)
        try:
            if settings['auto_ffilter']:
                if re.search(r'https?://\S+|www\.\S+|t\.me/\S+', message.text):
                    if await is_check_admin(client, message.chat.id, message.from_user.id):
                        return
                    return await message.delete()  
                await auto_filter(client, message)
        except KeyError:
            pass
    else:
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results( chat_id=message.chat.id, query=search.lower(), offset=0, filter=True )
        if total_results == 0:
            return
        await message.reply_text(
            f"<b>Hᴇʏ {message.from_user.mention},\n\n"
            f"ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ✅\n\n"
            f"📂 ꜰɪʟᴇꜱ ꜰᴏᴜɴᴅ : {str(total_results)}\n"
            f"🔍 ꜱᴇᴀʀᴄʜ :</b> <code>{search}</code>\n\n"
            f"<b>‼️ ᴛʜɪs ɪs ᴀ <u>sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ</u> sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\n"
            f"📝 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ : 👇</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 ᴊᴏɪɴ ᴀɴᴅ ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url=GRP_LNK)]])
        )

@Client.on_message(filters.private & filters.text & filters.incoming & ~filters.regex(r"^/"))
async def pm_text(bot, message):
    bot_id = bot.me.id
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if EMOJI_MODE:
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception:
            await message.react(emoji="⚡️", big=True)
    if content.startswith(("#")):
        return
    try:
        await mdb.update_top_messages(user_id, content)
        pm_search = await db.pm_search_status(bot_id)
        if pm_search:
            await auto_filter(bot, message)
        else:
            await message.reply_text(
                text=(
                    f"<b>🙋 ʜᴇʏ {user} 😍 ,\n\n"
                    "𝒀𝒐𝒖 𝒄𝒂𝒏 𝒔𝒆𝒂𝒓𝒄𝒉 𝒇𝒐𝒓 𝒎𝒐𝒗𝒊𝒆𝒔 𝒐𝒏𝒍𝒚 𝒐𝒏 𝒐𝒖𝒓 𝑴𝒐𝒗𝒊𝒆 𝑮𝒓𝒐𝒖𝒑. 𝒀𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒕 𝒂𝒍𝒍𝒐𝒘𝒆𝒅 𝒕𝒐 𝒔𝒆𝒂𝒓𝒄𝒉 𝒇𝒐𝒓 𝒎𝒐𝒗𝒊𝒆𝒔 𝒐𝒏 𝑫𝒊𝒓𝒆𝒄𝒕 𝑩𝒐𝒕. 𝑷𝒍𝒆𝒂𝒔𝒆 𝒋𝒐𝒊𝒏 𝒐𝒖𝒓 𝒎𝒐𝒗𝒊𝒆 𝒈𝒓𝒐𝒖𝒑 𝒃𝒚 𝒄𝒍𝒊𝒄𝒌𝒊𝒏𝒈 𝒐𝒏 𝒕𝒉𝒆  𝑹𝑬𝑼𝑬𝑺𝑻 𝑯𝑬𝑹𝑬 𝒃𝒖𝒕𝒕𝒐𝒏 𝒈𝒊𝒗𝒆𝒏 𝒃𝒆𝒍𝒐𝒘 𝒂𝒏𝒅 𝒔𝒆𝒂𝒓𝒄𝒉 𝒚𝒐𝒖𝒓 𝒇𝒂𝒗𝒐𝒓𝒊𝒕𝒆 𝒎𝒐𝒗𝒊𝒆 𝒕𝒉𝒆𝒓𝒆 👇\n\n"
                    "<blockquote>"
                    "आप केवल हमारे 𝑴𝒐𝒗𝒊𝒆 𝑮𝒓𝒐𝒖𝒑 पर ही 𝑴𝒐𝒗𝒊𝒆 𝑺𝒆𝒂𝒓𝒄𝒉 कर सकते हो । "
                    "आपको 𝑫𝒊𝒓𝒆𝒄𝒕 𝑩𝒐𝒕 पर 𝑴𝒐𝒗𝒊𝒆 𝑺𝒆𝒂𝒓𝒄𝒉 करने की 𝑷𝒆𝒓𝒎𝒊𝒔𝒔𝒊𝒐𝒏 नहीं है कृपया नीचे दिए गए 𝑹𝑬𝑼𝑬𝑺𝑻 𝑯𝑬𝑹𝑬 वाले 𝑩𝒖𝒕𝒕𝒐𝒏 पर क्लिक करके हमारे 𝑴𝒐𝒗𝒊𝒆 𝑮𝒓ᴏ𝒖𝒑 को 𝑱𝒐𝒊𝒏 करें और वहां पर अपनी मनपसंद 𝑴𝒐𝒗𝒊𝒆 𝑺𝒆𝒂𝒓𝒄𝒉 करें ।"
                    "</blockquote></b>"
                ),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ", url=GRP_LNK)]]))
            await bot.send_message( chat_id=LOG_CHANNEL,
                text=(
                    f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\n"
                    f"👤 Nᴀᴍᴇ : {user}\n"
                    f"🆔 ID : {user_id}\n"
                    f"💬 Mᴇssᴀɢᴇ : {content}</b>"
                )
            )
    except Exception:
        pass

@Client.on_callback_query(filters.regex(r"^reffff"))
async def refercall(bot, query):
    btn = [[
        InlineKeyboardButton('invite link', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{query.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {referdb.get_refer_points(query.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('Back', callback_data='premium_info')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
        )
    await query.message.edit_text(
        text=f'Hay Your refer link:\n\nhttps://t.me/{bot.me.username}?start=reff_{query.from_user.id}\n\nShare this link with your friends, Each time they join,  you will get 10 refferal points and after 100 points you will get 1 month premium subscription.',
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
        )
    await query.answer()

@Client.on_callback_query(filters.regex(r"^generate_stream_link"))
async def generate_stream_link_handler(bot, query):
    """Handle the Download Now button click and generate streaming links"""
    try:
        # Extract file_id from callback data
        _, file_id = query.data.split(":", 1)
        
        # Get the file details from database
        files = await get_file_details(file_id)
        if not files:
            return await query.answer("⚠️ File not found!", show_alert=True)
        
        # Get the first file
        file = files[0]
        
        # Get the message that was sent with the file
        # The callback query message is the message with the file
        file_msg = query.message
        
        # Generate streaming URLs
        file_name = get_name(file_msg)
        file_hash = get_hash(file_msg)
        
        # Generate download and stream links
        dreamx_stream = f"{URL}watch/{file_hash}{file_msg.id}"
        dreamx_download = f"{URL}{file_msg.id}/{quote_plus(file_name)}?hash={file_hash}"
        
        # Send the links to user
        btn = [
            [InlineKeyboardButton("🚀 Fast Download 🚀", url=dreamx_download)],
            [InlineKeyboardButton('🖥️ Watch Online 🖥️', url=dreamx_stream)]
        ]
        
        await query.message.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ☠︎⚔\n\n📁 ꜰɪʟᴇ ɴᴀᴍᴇ: {file_name}\n\n⚡ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴏʀ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ",
            reply_markup=InlineKeyboardMarkup(btn),
            quote=True
        )
        await query.answer("✅ Links generated successfully!")
        
    except Exception as e:
        logger.error(f"Error in generate_stream_link_handler: {e}")
        await query.answer("⚠️ Error generating links. Please try again.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    if BUTTONS.get(key)!=None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0, 
            [ 
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, 
            [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Sᴇɴᴅ Aʟʟ", callback_data=f"sendfiles#{key}")
           
            ]
        )

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Sᴇɴᴅ Aʟʟ", callback_data=f"sendfiles#{key}") 
        ])
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movies = await get_poster(id, id=True)
    movie = movies.get('title')
    movie = re.sub(r"[:-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        reqstr1 = query.from_user.id if query.from_user else 0
        reqstr = await bot.get_users(reqstr1)
        if NO_RESULTS_MSG:
            try:
                await bot.send_message(chat_id=BIN_CHANNEL,text=script.NORSLTS.format(reqstr.id, reqstr.mention, movie))
            except Exception as e:
                print(f"Error In Spol - {e}   Make Sure Bot Admin BIN CHANNEL")
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔰Cʟɪᴄᴋ ʜᴇʀᴇ & ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴀᴅᴍɪɴ🔰", url=OWNER_LNK)]])
        k = await query.message.edit(script.MVE_NT_FND,reply_markup=btn)
        await asyncio.sleep(10)
        await k.delete()
                
#Qualities 
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏɴᴇʏ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",show_alert=True,)
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([InlineKeyboardButton(text=QUALITIES[i].title(),callback_data=f"fq#{QUALITIES[i].lower()}#{key}"),
                    InlineKeyboardButton(text=QUALITIES[i+1].title(),callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}"),])
    btn.insert(0, 
               [InlineKeyboardButton(text="⇊ ꜱᴇʟᴇᴄᴛ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident")],)
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇस ↭", callback_data=f"fq#homepage#{key}")])
    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
 

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏɴᴇʏ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...", show_alert=True)
    except:
        pass
    if qual != "homepage":
        search = f"{search} {qual}" 
    BUTTONS[key] = search
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0, 
            [ 
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, 
            [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Sᴇɴᴅ Aʟʟ", callback_data=f"sendfiles#{key}")
           
            ]
        )

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Sᴇɴᴅ Aʟʟ", callback_data=f"sendfiles#{key}") 
        ])
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movies = await get_poster(id, id=True)
    movie = movies.get('title')
    movie = re.sub(r"[:-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        reqstr1 = query.from_user.id if query.from_user else 0
        reqstr = await bot.get_users(reqstr1)
        if NO_RESULTS_MSG:
            try:
                await bot.send_message(chat_id=BIN_CHANNEL,text=script.NORSLTS.format(reqstr.id, reqstr.mention, movie))
            except Exception as e:
                print(f"Error In Spol - {e}   Make Sure Bot Admin BIN CHANNEL")
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔰Cʟɪᴄᴋ ʜᴇʀᴇ & ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴀᴅᴍɪɴ🔰", url=OWNER_LNK)]])
        k = await query.message.edit(script.MVE_NT_FND,reply_markup=btn)
        await asyncio.sleep(10)
        await k.delete()
                
#Qualities 
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏɴᴇʏ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",show_alert=True,)
    except:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key)
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([InlineKeyboardButton(text=QUALITIES[i].title(),callback_data=f"fq#{QUALITIES[i].lower()}#{key}"),
                    InlineKeyboardButton(text=QUALITIES[i+1].title(),callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}"),])
    btn.insert(0, 
               [InlineKeyboardButton(text="⇊ ꜱᴇʟᴇᴄᴛ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident")],)
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇस ↭", callback_data=f"fq#homepage#{key}")])
    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
 

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏɴᴇʏ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...", show_alert=True)
    except:
        pass
    if qual != "homepage":
        search = f"{search} {qual}" 
    BUTTONS[key] = search
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0, 
            [ 
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, 
            [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Sᴇɴᴅ Aʟʟ", callback_data=f"sendfiles#{key}")
           
            ]
        )

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Sᴇɴᴅ Aʟʟ", callback_data=f"sendfiles#{key}") 
        ])
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()

async def auto_filter(client, message, k=None):
    """
    Auto filter function to search and display movie results
    """
    if k:
        # Called from callback query with pre-fetched results
        search, files, offset, total_results = k
        req = message.from_user.id
        chat_id = message.message.chat.id
        message_id = message.message.id
        query = message
    else:
        # Called from regular message
        search = message.text
        chat_id = message.chat.id
        message_id = message.id
        req = message.from_user.id
        
        # Get search results
        files, offset, total_results = await get_search_results(
            chat_id=chat_id,
            query=search.lower(),
            offset=0,
            filter=True
        )
    
    if not files:
        # No results found - try spell check
        if k:
            await query.answer("No files found!")
            return
        
        try:
            # Try to find similar matches
            all_files = await Media.find().to_list(length=None)
            file_names = [f.file_name for f in all_files if f.file_name]
            
            if file_names:
                matches = process.extract(search, file_names, limit=10)
                suggestions = [match[0] for match in matches if match[1] > 60]
                
                if suggestions:
                    btn = []
                    for suggestion in suggestions[:10]:
                        try:
                            poster_data = await get_poster(suggestion, bulk=True)
                            poster_id = poster_data or 'nop'
                        except:
                            poster_id = 'nop'
                        
                        btn.append([
                            InlineKeyboardButton(
                                text=clean_filename(suggestion),
                                callback_data=f"spol#{poster_id}#{req}"
                            )
                        ])
                    
                    await message.reply_text(
                        script.SPELLING_ERROR_TXT,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
        except Exception as e:
            print(f"Error in spell check: {e}")
        
        # No suggestions found
        await message.reply_text(script.I_CUDNT.format(search))
        return
    
    # Files found - prepare response
    key = f"{chat_id}_{message_id}_{req}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[req] = chat_id
    
    settings = await get_settings(chat_id)
    
    # Group similar files
    grouped_files = group_similar_files(files)
    
    # Create the text-based format with grouped results
    caption = f"<b>📂 Found {total_results} results for: {search}</b>\n\n"
    
    displayed_count = 0
    for base_name, file_group in list(grouped_files.items())[:10]:  # Limit to 10 groups
        # Use the cleanest name from the group for display
        display_names = [clean_filename(f.file_name) for f in file_group]
        best_name = min(display_names, key=len) if display_names else base_name.title()
        
        # Create a unique key for this group
        group_key = f"{key}_{hash(base_name)}"
        temp.GETALL[group_key] = file_group
        
        # Create hyperlink that will send all files in this group
        file_count = len(file_group)
        size_info = f"({file_count} files)" if file_count > 1 else f"({get_size(file_group[0].file_size)})"
        
        # Create link to send all files in this group
        group_link = f"https://telegram.me/{temp.U_NAME}?start=allfiles_{chat_id}_{group_key}"
        
        caption += f"<b>🎬 {best_name}</b> {size_info}\n"
        caption += f"👉👉 <a href='{group_link}'>Download All Files</a> 👈👈\n\n"
        displayed_count += file_count
    
    if total_results > displayed_count:
        remaining = total_results - displayed_count
        caption += f"<i>...and {remaining} more files available</i>\n\n"
    
    # Add filter buttons
    btn = [
        [
            InlineKeyboardButton('Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
            InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
            InlineKeyboardButton("Sᴇᴀsᴏɴ", callback_data=f"seasons#{key}")
        ],
        [
            InlineKeyboardButton("⚜️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚𝐝𝐬 ⚜️", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ Fɪʟᴇs", callback_data=f"sendfiles#{key}")
        ]
    ]
    
    # Add pagination if needed
    if offset:
        try:
            if settings.get('max_btn', True):
                btn.append([
                    InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"),
                    InlineKeyboardButton(text=f"1/{math.ceil(total_results/10)}", callback_data="pages"),
                    InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")
                ])
            else:
                btn.append([
                    InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"),
                    InlineKeyboardButton(text=f"1/{math.ceil(total_results/int(MAX_B_TN))}", callback_data="pages"),
                    InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")
                ])
        except:
            btn.append([
                InlineKeyboardButton("ᴘᴀɡᴇ", callback_data="pages"),
                InlineKeyboardButton(text=f"1/{math.ceil(total_results/10)}", callback_data="pages"),
                InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")
            ])
    else:
        btn.append([InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɡᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭", callback_data="pages")])
    
    # Send or edit message
    if k:
        # Edit existing message
        try:
            await query.message.edit_text(
                text=caption,
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True
            )
        except MessageNotModified:
            pass
    else:
        # Send new message
        try:
            await message.reply_text(
                text=caption,
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"Error sending auto_filter message: {e}")
            # Fallback simple message
            await message.reply_text(f"Found {total_results} results for '{search}' but couldn't display them properly.")

def group_similar_files(files):
    """Group files by similar movie names"""
    grouped = {}
    
    for file in files:
        # Clean and normalize file name for grouping
        clean_name = clean_filename(file.file_name)
        # Remove year, quality, and other extras to get base movie name
        base_name = re.sub(r'\b(19|20)\d{2}\b', '', clean_name)  # Remove years
        base_name = re.sub(r'\b(480p|720p|1080p|2160p|4k|hd|hdr|bluray|webrip|hdts|cam|dvdrip)\b', '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'\b(hindi|english|tamil|telugu|malayalam|dubbed)\b', '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'[^\w\s]', ' ', base_name)  # Remove special chars
        base_name = ' '.join(base_name.split()[:3])  # Take first 3 words
        base_name = base_name.strip().lower()
        
        if len(base_name) < 3:  # Skip very short names
            base_name = clean_name.lower()
            
        if base_name not in grouped:
            grouped[base_name] = []
        grouped[base_name].append(file)
    
    return grouped