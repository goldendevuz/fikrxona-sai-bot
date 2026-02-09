# Announcements configuration
#
# Format:
#   # Define reusable messages (can be referenced multiple times)
#   msg-name =
#       Message text here
#       Can be multiline
#
#   # Announcements - either inline or with @message reference
#   announcement-N =
#       @message: msg-name     (reference a message defined above)
#       @every: seconds        (interval between sends, can be defined as range ex. 1000-2000)
#       @groups: id1, id2      (optional: specific groups, omit for all)
#
#   # Or with inline message text
#   announcement-N =
#       Inline message text
#       @every: 3600


# =============================
# MESSAGE TEMPLATES (reusable)
# =============================

msg-report-reminder =
    ❕ Не забывайте про команду <b>!report</b> благодаря которой Вы можете обратить внимание администрации на <u>нарушителя в чате</u>.
    
    <tg-spoiler><i>Спам данной командой карается вечным баном.</i></tg-spoiler>

msg-chat-rules =
    <b>📁 Это чат канала @howdyho_official</b>
    Общайтесь вежливо и не нарушайте правила!
    
    📈 В чате действует <u>система репутации</u>
    ⛔️ Новичкам запрещено отправлять медиа
    🤬 Мат <u>удаляется автоматически</u>
    👹 Оффтоп/спам наказывается 🍌 бананами
    
    <b>Всем мира 🤞</b>

msg-donate =
    <b>🫰 Донат автору канала:</b>
    
    <i>Мой Boosty:</i> https://boosty.to/howdyho
    <i>Мой Patreon:</i> <a href='https://www.patreon.com/user?u=22843414'>https://www.patreon.com/howdyho</a>
    <i>Наш Discord:</i> <a href='https://discord.gg/6khaudi-kho-1123002520072097953'>https://discord.gg/howdyho</a>

msg-website =
    <b>😈 У нас есть сайт, ты знал?</b>
    
    Вот он - https://howdyho.net
    Мы там постим топовый софт, обои, игры, и кучу всего для ПК!
    
    <i>Заходи, тебе там всегда рады!</i>

msg-share-bot =
    <b>🫰 Хочешь чтобы твой мем/пост закинули в канал?</b>
    Тыкай сюда - @hhsharebot


# ================================
# ANNOUNCEMENTS (scheduled sends)
# ================================

announcement-1 =
    @message: msg-report-reminder
    @every: 10000-20000

announcement-2 =
    @message: msg-chat-rules
    @every: 9600-12000
    @groups: -1003002995352

announcement-3 =
    @message: msg-donate
    @every: 19800-23400
    @groups: -1003002995352

announcement-4 =
    @message: msg-website
    @every: 16200-19800
    @groups: -1003002995352

announcement-5 =
    @message: msg-share-bot
    @every: 12600-16200
    @groups: -1003002995352
