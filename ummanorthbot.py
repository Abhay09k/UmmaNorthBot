import logging
import os
import random
import base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, ChatMember
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
)

# --- CONFIGURATION AND STATE ---

# Set your BotFather token here or load it from environment variables
# 📢 UPDATED TOKEN: @ummanorthbot
# IMPORTANT: Replace the dummy token below with your actual token from BotFather!
BOT_TOKEN = "8295188229:AAFQFq6vhNZACsvchDYVE8kd3AwRYe7f1BI"

# ⚠️ IMPORTANT: Replace with your actual Telegram User ID for Owner Commands
OWNER_ID = 123456789  # Example ID

# Global State for tracking (data resets on bot restart)
chat_data = {
    'message_count': {},  # {user_id: count}
    'user_id_to_username': {},  # {user_id: @username_or_firstname}
    'username_to_id': {},  # {@username: user_id}
}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- CONTENT (EXPANDED TO 50+ ENTRIES) ---

# Roasts (50+ entries combined from Java and new)
ROASTS = [
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "You're proof evolution can go in reverse.",
    "You bring everyone so much joy… when you leave the group.",
    "You're the reason the gene pool needs a lifeguard.",
    "You have something on your chin... no, the third one down.",
    "You're not ugly… just allergic to good decisions.",
    "Even Google doesn't search as much as you search for her attention.",
    "Your typing speed is fast, but your thoughts are stuck in 2010.",
    "STOP SHOUTING. CAPS LOCK WON’T FIX YOUR INSECURITIES.",
    "You bring the whole group’s IQ down every time you type.",
    "You dropped your dignity again. Wanna pick it up?",
    "You talk like your brain is buffering on 2G.",
    "Reading your texts is like watching a snail do math.",
    "You're the reason people say ‘not everyone deserves Wi-Fi’.",
    "That motivation quote didn’t hit. Try silence.",
    "Your confidence is inspiring, for someone with zero logic.",
    "You treat her like a queen, but she treats your texts like spam.",
    "You're not in the friendzone. You're in the museum of ignored messages.",
    "GM? Bro, the sun isn’t even ready to deal with your energy.",
    "The louder you type, the emptier it sounds.",
    "Your replies are like a loading screen that never ends.",
    "Your gm/gn streak is more consistent than your career.",
    "Your life is like your phone storage — full of junk and regrets.",
    "Your brain uses dial-up.",
    "You are a monument to procrastination.",
    "I'm busy right now, can I ignore you some other time?",
    "You're so slow, the speed of light avoids you.",
    "Were you born on a highway? Because that's where most accidents happen.",
    "You're the human equivalent of a participation trophy.",
    "Is your brain made of sponges? Because it seems to soak up negativity.",
    "You must be the square root of 2, irrational.",
    "I've seen less awkward shadows.",
    "Your existence is proof that sometimes 'less is more' is ignored.",
    "You're the 'skip ad' button of life.",
    "Your best feature is that you're predictable.",
    "You have a face for radio, and a voice for silent movies.",
    "You look like the 'before' picture.",
    "If your brain was gasoline, you couldn't power a lawnmower.",
    "You're not stupid, you're just vertically challenged in the brain department.",
    "You're like a broken pencil. Pointless.",
    "You have the energy of a houseplant.",
    "Is your life a 'beta' test?",
    "You peak in the morning when you wake up.",
    "You should carry a plant with you to replace the oxygen you waste.",
    "You're the 'unsubscribed' email of this group.",
    "You’re about as useful as a screen door on a submarine.",
    "Tu mera future hai. Akela aur sad. (You are my future. Alone and sad.)",
    "Teri sippy nahi, puri zindagi noi rahegi. (Not just your crush, your whole life won't last.)",
    "Tera wifi signal bhi tere life choices se zyada stable hai. (Even your wifi is more stable than your life choices.)",
    "Tu toh woh dost hai jisko tag karne se 'reach' kam ho jati hai. (You are that friend whose tag decreases the reach.)"
]

# Auto-Roasts Map (GenZ/Hindi)
AUTO_ROAST_MAP = {
    "gm": "Gm? Bro even the sun regrets rising with you around.",
    "gn": "Gn. Hopefully your thoughts reboot overnight.",
    "bored": "You’re not bored, you’re just boring.",
    "wyd": "WYD? Hopefully getting therapy for that brain.",
    "miss me": "You? Missed? Even your shadow left voluntarily.",
    "single": "You’re not single by choice, you’re single by consequence.",
    "lol": "You typed ‘lol’ but haven’t laughed since 2017.",
    "same": "Same? You're not relatable, you're just basic.",
    "literally me": "Bro it's literally not you. It’s literally cringe.",
    "relatable": "Everything’s relatable when you have no personality.",
    "fr": "FR? Your whole life is NFR — Not Funny, Really.",
    "vibe": "Your vibe? More like 'vibe check failed'.",
    "sheesh": "Sheesh? You sound like a TikTok left in the microwave.",
    "on god": "On God? Bro, even God is typing 'seen'.",
    "no cap": "No cap? Start with no talk, please.",
    "bet": "Bet? Bet you won’t say something intelligent for once.",
    "mid": "Calling things mid won’t make you top tier.",
    "goat": "You’re not the GOAT. You’re just… the goat. Like the animal.",
    "future": "sippy noi rahegi teri bwahahahahaha",
    "yaar": "Yaar bolne se pehle soch, tu khud kiska 'dushman' hai. (Think before you say 'friend', you are your own 'enemy'.)"
}

# Jokes (Fun and lighthearted)
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Kya haal hai? Acha, tera 'haal' toh mujhe pehle se pata tha, 'bura' hi hoga. (What's up? I already knew your 'condition' would be 'bad'.)",
    "What do you call a fake noodle? An impasta.",
    "Why was the math book sad? Because it had too many problems.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why did the invisible man turn down the job? He couldn't see himself doing it.",
    "I'm reading a book on anti-gravity. It's impossible to put down!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Ek machhar ne doosre machhar se kya kaha? 'Chill kar, blood group apna hi hai.' (One mosquito said to the other? 'Chill, it's our blood group only.')",
    "What’s brown and sticky? A stick.",
    "I invented a new word: Plagiarism!"
]

# Quotes (Inspirational and fun)
QUOTES = [
    "Life is what happens when you're busy making other plans. - John Lennon",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Be yourself; everyone else is already taken. - Oscar Wilde",
    "If you want to live a happy life, tie it to a goal, not to people or things. - Albert Einstein",
    "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb",
    "Do what you can, with what you have, where you are. - Theodore Roosevelt",
    "Don't cry over spilt milk. Wipe up the milk and figure out why you were carrying milk in the first place.",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela"
]

# Possibility Responses
POSSIBILITY_RESPONSES = [
    "Absolutely, 100% possible. (Jhooth bol raha hu - I'm lying.)",
    "Mera dil nahi, tera luck bol raha hai: 'No chance'. (Not my heart, your luck says: 'No chance'.)",
    "Possibility? Utni hi jitni tere crush ka reply aane ki. (The same possibility as your crush replying.)",
    "Signs point to yes, but my gut says 'nah'.",
    "Don't count on it, bro. Better plan B.",
    "It is certain. (Jaise tera single rehna - Like you remaining single.)"
]

# Meow Attacks (10+ attacks)
MEOW_ATTACKS = [
    "Meow used Fury Swipes! Scratch, scratch, scratch! 🐾",
    "Meow used Pay Day! (Coins scattered, but none for you.) 💰",
    "Meow used Bite! Ouch! 😬",
    "Meow used Scratch! A minor inconvenience.",
    "Meow is just purring... The attack was too cute to resist.",
    "Meow used Catnip Bomb! You are now uncontrollably happy!",
    "Meow used Lick! It's... super sticky.",
    "Meow used Tail Whip! (Defense stat lowered.)",
    "Meow used Roar! (But it sounded like a small squeak.)",
    "Meow used Sucker Punch! (Hit hard when you weren't looking!)",
    "Meow used Feint Attack! (It was all a distraction.)",
    "Meow used Protect! (You can't hurt the fluffball.)"
]

# Pikachu Attacks (10+ attacks)
PIKACHU_ATTACKS = [
    "Pikachu used ThunderShock! Zzzzzap! ⚡️",
    "Pikachu used Quick Attack! Whoosh! 💨",
    "Pikachu used Volt Tackle! B O O M!",
    "Pikachu used Iron Tail! (Critical Hit!)",
    "Pikachu used Electro Ball! Target Locked! 🎯",
    "Pikachu used Wild Charge! (Self-damage also applied.)",
    "Pikachu used Thunderbolt! It's super effective!",
    "Pikachu used Slam! That's gotta hurt.",
    "Pikachu used Nuzzle! You've been paralyzed by cuteness.",
    "Pikachu used Discharge! (Hit everything nearby!)",
    "Pikachu used Focus Punch! (Missed due to your awkwardness.)",
    "Pikachu used Light Screen! (Protecting the innocent.)"
]


# --- UTILITY FUNCTIONS ---

def get_display_name(user):
    """Gets the best display name (@username or First Name) for a user."""
    if user.username:
        return f"@{user.username}"
    return user.first_name

async def reply_text(update: Update, text: str, quote: bool = True):
    """Helper function to send a reply."""
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_to_message_id=update.message.message_id if quote else None
    )

async def check_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if a user is the OWNER or an admin in a group chat."""
    if user_id == OWNER_ID:
        return True

    # Check if it's a private chat (not a group)
    if chat_id > 0:
        return False

    try:
        chat_member: ChatMember = await context.bot.get_chat_member(chat_id, user_id)
        if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
            return True
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False
    return False

# Function to get the target name for slap/punch/etc.
def get_target_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retrieves the target name from a reply or command argument."""
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        return get_display_name(target_user)
    elif context.args:
        # Check if the argument is a mention
        if context.args[0].startswith('@'):
            return context.args[0]
        # Otherwise, assume it's just a name
        return context.args[0]
    return None

# --- HANDLER FOR ALL MESSAGES (STATE MANAGEMENT & AUTO-ROAST) ---

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Updates state and checks for auto-roast keywords."""
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    user_id = user.id
    message_text = update.message.text

    # 1. Update State Management (Crucial for /whisper and /chattoppers)
    display_name = get_display_name(user)
    chat_data['user_id_to_username'][user_id] = display_name
    
    # Store username to ID mapping for easy lookup
    if user.username:
        chat_data['username_to_id'][user.username.lower()] = user_id

    # Update message count
    chat_data['message_count'][user_id] = chat_data['message_count'].get(user_id, 0) + 1

    # 2. Check for Auto-Roast
    lower_case_message = message_text.lower()
    for keyword, roast in AUTO_ROAST_MAP.items():
        if keyword in lower_case_message:
            await reply_text(update, f"🔥 {roast}")
            return # Only send one auto-roast per message


# --- COMMAND HANDLERS ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a message with all bot features."""
    help_text = (
        "✨ **@ummanorthbot Feature List!** ✨\n\n"
        "**👑 Admin/Mod Commands (Group Admins Only):**\n"
        "  `/ban` (Reply) - Ban a user.\n"
        "  `/mute` (Reply) - Mute a user for 1 hour.\n"
        "  `/pin` (Reply) - Pin a message.\n"
        "  `/delete` (Reply) - Delete a message.\n"
        "  `/make_admin` (Reply) - Promote a user to Admin (Bot must be group owner).\n"
        "  `/remove_admin` (Reply) - Demote an admin.\n"
        "  `/delete_all_msg` (Reply) - Delete ALL tracked messages from the replied user (In-Memory).\n\n"
        "**🤫 Whisper (Multi-Recipient Privacy):**\n"
        "  `/whisper @user1 @user2 <message>` - Sends a secret message ONLY visible to user1 AND user2 via a private pop-up alert. The command message is instantly deleted.\n\n"
        "**😂 Fun & Game Commands:**\n"
        "  `/lovecalc <Name1> <Name2>` - Calculates compatibility score.\n"
        "  `/slap` (Reply/Mention) - **Slap** another user in the chat.\n"
        "  `/punch` (Reply/Mention) - **Punch** another user in the chat.\n"
        "  `/dice` - Roll a 6-sided die.\n"
        "  `/roastme` - Get a random roast (50+ options).\n"
        "  `/joke` - Hear a random joke.\n"
        "  `/quotes` - Get a quote.\n"
        "  `/possibility` - Ask a yes/no question.\n"
        "  `/toss` - Flip a coin.\n"
        "  `/meow` - Meow's special attack! 🐾 (10+ attacks)\n"
        "  `/pikachu` - Pikachu's ThunderShock! ⚡️ (10+ attacks)\n\n"
        "**📈 Chat Analytics (In-Memory):**\n"
        "  `/chattoppers` - See the top 10 most active users.\n"
        "  `/chat_summary` - Get total messages and user count."
    )
    await reply_text(update, help_text)

# --- NEW GAME AND INTERACTION COMMANDS ---

async def love_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates a compatibility score between two names."""
    if len(context.args) < 2:
        await reply_text(update, "💔 Usage: `/lovecalc <Name1> <Name2>`")
        return

    # Use the first two arguments as names, handle multiple words for names
    # Note: If the user types /lovecalc John Doe Jane Smith, it will only use "John" and "Doe"
    name1 = context.args[0]
    name2 = context.args[1]

    # Simple deterministic calculation based on name letters
    combined = sorted((name1 + name2).lower().replace(" ", ""))
    love_score = 0
    for char in combined:
        if char.isalpha(): # Only count letters
            love_score += ord(char) 
    
    # Scale and normalize the score based on ASCII sum and a little randomness
    random.seed(love_score) # Seed randomness for determinism
    percentage = (love_score % 90) + random.randint(5, 15) # Ensure score is between 5 and 105 (max 100)
    percentage = min(percentage, 100) 

    if percentage >= 80:
        result_text = "✨ **Perfect Match!** A love written in the stars."
    elif percentage >= 60:
        result_text = "💖 **Strong Connection!** Things are looking very promising."
    elif percentage >= 40:
        result_text = "😊 **Friendly Vibes.** Some potential, but needs work."
    elif percentage >= 20:
        result_text = "😬 **Awkward Silence.** Maybe stick to being friends."
    else:
        result_text = "💥 **Run.** This is a disaster waiting to happen."
        
    response = (
        f"💞 **Love Calculator Result:** 💞\n"
        f"**{name1.title()}** and **{name2.title()}**\n"
        f"**Compatibility Score:** {percentage}%\n"
        f"{result_text}"
    )
    await reply_text(update, response)

async def slap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to slap each other."""
    target_name = get_target_name(update, context)
    sender_name = get_display_name(update.message.from_user)

    if not target_name:
        await reply_text(update, f"👋 Usage: `/slap <@username>` or reply to a message.")
        return
        
    if target_name.lower() == sender_name.lower():
        await reply_text(update, f"🤚 {sender_name} tried to slap themselves but missed badly.")
        return

    slap_actions = [
        f"gave {target_name} a soft, gentle slap with a large wet fish.",
        f"delivered a thunderous slap to {target_name} using a tortilla.",
        f"reached out and slapped {target_name} with the force of a thousand regrets.",
        f"politely asked {target_name} if they could slap them, and then did it with a glove."
    ]
    action = random.choice(slap_actions)
    await reply_text(update, f"🔥 **{sender_name}** {action}")

async def punch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to punch each other."""
    target_name = get_target_name(update, context)
    sender_name = get_display_name(update.message.from_user)

    if not target_name:
        await reply_text(update, f"👊 Usage: `/punch <@username>` or reply to a message.")
        return

    if target_name.lower() == sender_name.lower():
        await reply_text(update, f"🤕 {sender_name} accidentally punched themselves in the face. Ouch.")
        return

    punch_actions = [
        f"punched {target_name} right in the emotional instability.",
        f"winded up and delivered a critical hit punch to {target_name}.",
        f"gave {target_name} a 'friendly' jab in the shoulder.",
        f"delivered a high-speed punch, sending {target_name} into the next timezone."
    ]
    action = random.choice(punch_actions)
    await reply_text(update, f"💥 **{sender_name}** {action}")

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rolls a single 6-sided die."""
    roll = random.randint(1, 6)
    await reply_text(update, f"🎲 **Dice Roll:** The die lands on **{roll}**!")

# --- EXISTING FUN COMMANDS ---

async def roastme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a random roast."""
    username = update.message.from_user.first_name
    roast = random.choice(ROASTS)
    await reply_text(update, f"{username}, {roast}")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a random joke."""
    joke = random.choice(JOKES)
    await reply_text(update, f"🤣: {joke}")

async def quotes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a random quote."""
    quote = random.choice(QUOTES)
    await reply_text(update, f"📜: {quote}")

async def possibility_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Determines possibility."""
    response = random.choice(POSSIBILITY_RESPONSES)
    await reply_text(update, f"🔮 {response}")

async def toss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Flips a coin."""
    result = random.choice(["Heads (Chit) 🪙", "Tails (Pat) 👑"])
    await reply_text(update, f"Coin Toss: {result}. All your problems solved!")

async def meow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Meow's custom attacks (Easter Egg)."""
    attack = random.choice(MEOW_ATTACKS)
    await reply_text(update, f"😼 MeowBot attack initiated! {attack}")

async def pikachu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pikachu's custom attacks (Easter Egg)."""
    attack = random.choice(PIKACHU_ATTACKS)
    await reply_text(update, f"⚡️ Pikachu attack initiated! {attack}")


# --- ANALYTICS COMMANDS ---

async def chat_toppers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the top 10 most active users."""
    message_count = chat_data['message_count']
    if not message_count:
        await reply_text(update, "📈 No chat activity has been tracked yet. (Data resets on bot restart.)")
        return

    sorted_users = sorted(message_count.items(), key=lambda item: item[1], reverse=True)
    top_10 = sorted_users[:10]

    sb = ["🏆 **Top 10 Chat Toppers (Since last restart):** 🏆"]
    for rank, (user_id, count) in enumerate(top_10, 1):
        username = chat_data['user_id_to_username'].get(user_id, f"User ID: {user_id}")
        sb.append(f"{rank}. {username}: {count} messages")
        
    await reply_text(update, "\n".join(sb))

async def chat_summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gives a summary of chat activity."""
    total_messages = sum(chat_data['message_count'].values())
    total_users = len(chat_data['message_count'])
    
    avg_messages = total_messages / total_users if total_users > 0 else 0.0

    summary = (
        "📊 **Chat Activity Summary (In-Memory)** 📊\n"
        f"Total Messages Tracked: {total_messages}\n"
        f"Total Active Users: {total_users}\n"
        f"Average Messages per User: {avg_messages:.2f}\n"
        "(Note: This data resets when the bot restarts.)"
    )
    await reply_text(update, summary)


# --- WHISPER LOGIC (MULTI-RECIPIENT) ---

async def whisper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the multi-recipient private whisper feature."""
    message = update.message
    args = context.args

    # 1. Initial validation and argument parsing
    if len(args) < 3 or not args[0].startswith('@') or not args[1].startswith('@'):
        await reply_text(update, "🤫 Whisper format: `/whisper @user1 @user2 <message>` (You must tag two users and include a message).")
        # Delete the invalid command immediately
        await message.delete() 
        return

    recipient_usernames = [args[0][1:].lower(), args[1][1:].lower()]
    whisper_text = " ".join(args[2:])
    sender_display_name = get_display_name(message.from_user)

    # 2. Look up Recipient IDs
    recipient_ids = []
    for username in recipient_usernames:
        user_id = chat_data['username_to_id'].get(username)
        if user_id is None:
            await context.bot.send_message(
                chat_id=message.chat_id, 
                text=f"❌ Whisper failed. @{username} has not yet chatted with the bot. They must send a message to register their ID."
            )
            await message.delete()
            return
        recipient_ids.append(str(user_id))

    # 3. Securely encode the message
    try:
        encoded_message = base64.urlsafe_b64encode(whisper_text.encode('utf-8')).decode('ascii')
    except Exception as e:
        logger.error(f"Failed to encode whisper message: {e}")
        await reply_text(update, "⚠️ Whisper encoding failed. Try a simpler message.", quote=False)
        await message.delete()
        return

    # Data format: WHISPER_<Recipient1_ID>_<Recipient2_ID>_<Encoded_Message>
    callback_data = f"WHISPER_{recipient_ids[0]}_{recipient_ids[1]}_{encoded_message}"
    
    # 4. Delete the command message to hide the content
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete command message: {e}")

    # 5. Send the public button message
    button_text = f"🔓 Open Secret Message (Only for {args[0]} & {args[1]})"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, callback_data=callback_data)]])

    public_message_text = (
        "🤫 **New Private Message!**\n\n"
        f"_{sender_display_name}_ sent a secret to _{args[0]} and {args[1]}_.\n\n"
        "Click the button below to view it privately."
    )
    
    await context.bot.send_message(
        chat_id=message.chat_id,
        text=public_message_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_whisper_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the button click for the whisper."""
    query = update.callback_query
    data = query.data
    clicking_user_id = str(query.from_user.id)
    
    # Data format: WHISPER_<Recipient1_ID>_<Recipient2_ID>_<Encoded_Message>
    try:
        _, id1, id2, encoded_message = data.split('_', 3)
        recipient_ids = [id1, id2]

        if clicking_user_id in recipient_ids:
            # Authorized recipient - show the secret message in a large pop-up alert (modal)
            secret_message = base64.urlsafe_b64decode(encoded_message.encode('ascii')).decode('utf-8')
            
            await query.answer(
                text=f"🤫 Secret Whisper for you:\n\n{secret_message}", 
                show_alert=True
            )
        else:
            # Unauthorized user - show a small toast notification
            await query.answer(
                text="🚫 This whisper is not for you! It's private.", 
                show_alert=False
            )

    except Exception as e:
        logger.error(f"Error processing whisper callback: {e}")
        await query.answer(text="An error occurred while opening the whisper.", show_alert=False)


# --- ADMIN COMMANDS (Require Group Admin Status) ---

async def admin_required(update: Update, context: ContextTypes.DEFAULT_TYPE, func):
    """Decorator-like wrapper to check admin status before running a function."""
    if not update.message or not update.message.reply_to_message:
        await reply_text(update, "🚫 This command requires you to **reply** to a user's message.")
        return

    chat_id = update.message.chat_id
    sender_id = update.message.from_user.id

    if not await check_admin(chat_id, sender_id, context):
        await reply_text(update, "⚠️ Sorry, this command is only for group admins or the bot owner.")
        return

    # If admin check passes, execute the requested function
    await func(update, context)


async def ban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bans the replied-to user."""
    await admin_required(update, context, _ban_user)

async def _ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id
    try:
        await context.bot.ban_chat_member(chat_id, target_user.id)
        await reply_text(update, f"🔨 {get_display_name(target_user)} has been banned. Bye-bye!")
    except Exception as e:
        await reply_text(update, f"❌ Ban failed. The bot might lack 'Ban users' permissions. Error: {e}")

async def mute_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mutes the replied-to user for 1 hour (3600 seconds)."""
    await admin_required(update, context, _mute_user)

async def _mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id
    try:
        # Mute by setting permissions to none (can't send messages, media, etc.)
        await context.bot.restrict_chat_member(
            chat_id, 
            target_user.id, 
            permissions=ChatPermissions(can_send_messages=False), 
            until_date=int(update.message.date.timestamp()) + 3600 # 1 hour
        )
        await reply_text(update, f"🔇 {get_display_name(target_user)} has been muted for 1 hour. Time to 'chill'.")
    except Exception as e:
        await reply_text(update, f"❌ Mute failed. The bot might lack 'Restrict users' permissions. Error: {e}")

async def pin_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pins the replied-to message."""
    await admin_required(update, context, _pin_message)

async def _pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_to_pin_id = update.message.reply_to_message.message_id
    chat_id = update.message.chat_id
    try:
        await context.bot.pin_chat_message(chat_id, message_to_pin_id)
        await reply_text(update, "📌 Message pinned. Don't forget this important point!")
    except Exception as e:
        await reply_text(update, f"❌ Pin failed. The bot might lack 'Pin messages' permissions. Error: {e}")

async def delete_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes the replied-to message."""
    await admin_required(update, context, _delete_message)

async def _delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_to_delete_id = update.message.reply_to_message.message_id
    chat_id = update.message.chat_id
    
    # Also delete the command message itself
    command_message_id = update.message.message_id 

    try:
        await context.bot.delete_message(chat_id, message_to_delete_id)
        await context.bot.delete_message(chat_id, command_message_id)
    except Exception as e:
        await reply_text(update, f"❌ Delete failed. The bot might lack 'Delete messages' permissions. Error: {e}", quote=False)


async def make_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promotes the replied-to user to admin."""
    await admin_required(update, context, _make_admin)

async def _make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id
    try:
        # Promote with standard permissions (requires the bot itself to be an admin with permission to add new admins)
        await context.bot.promote_chat_member(
            chat_id, 
            target_user.id, 
            can_manage_chat=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_invite_users=True,
            can_change_info=False,  # Keep this false usually
            can_post_messages=False, # For channel posts
            can_edit_messages=False
        )
        await reply_text(update, f"👑 {get_display_name(target_user)} has been promoted to Admin! Welcome the new powerhouse!")
    except Exception as e:
        await reply_text(update, f"❌ Promotion failed. The bot must be an admin with 'Add new administrators' permission. Error: {e}")

async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demotes the replied-to user."""
    await admin_required(update, context, _remove_admin)

async def _remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id
    try:
        # Demote by setting all permissions to False
        await context.bot.promote_chat_member(
            chat_id, 
            target_user.id, 
            can_manage_chat=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_invite_users=False,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_promote_members=False
        )
        await reply_text(update, f"📉 {get_display_name(target_user)} has been demoted. Back to the peasants' chat!")
    except Exception as e:
        await reply_text(update, f"❌ Demotion failed. Error: {e}")
        
async def delete_all_msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes ALL tracked message counts for the replied-to user."""
    await admin_required(update, context, _delete_all_msg)

async def _delete_all_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user
    target_user_id = target_user.id
    
    if target_user_id in chat_data['message_count']:
        count = chat_data['message_count'].pop(target_user_id)
        await reply_text(update, f"🧹 Cleared {count} messages from the activity log for {get_display_name(target_user)}. Starting fresh!")
    else:
        await reply_text(update, f"🔍 No message history found for {get_display_name(target_user)} in memory.")

# --- MAIN SETUP FUNCTION ---

def main():
    """Starts the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Please set the BOT_TOKEN variable.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # General Message Handler (State and Auto-Roast)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    
    # Command Handlers
    application.add_handler(CommandHandler("help", help_command))

    # NEW GAME AND INTERACTION HANDLERS
    application.add_handler(CommandHandler("lovecalc", love_calculator))
    application.add_handler(CommandHandler("slap", slap_command))
    application.add_handler(CommandHandler("punch", punch_command))
    application.add_handler(CommandHandler("dice", dice_command))

    # EXISTING FUN HANDLERS
    application.add_handler(CommandHandler("roastme", roastme_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("quotes", quotes_command))
    application.add_handler(CommandHandler("possibility", possibility_command))
    application.add_handler(CommandHandler("toss", toss_command))
    application.add_handler(CommandHandler("meow", meow_command))
    application.add_handler(CommandHandler("pikachu", pikachu_command))

    # ANALYTICS HANDLERS
    application.add_handler(CommandHandler("chattoppers", chat_toppers_command))
    application.add_handler(CommandHandler("chat_summary", chat_summary_command))
    
    # WHISPER HANDLERS
    application.add_handler(CommandHandler("whisper", whisper_command))
    
    # Admin Command Handlers (using wrappers for admin check)
    application.add_handler(CommandHandler("ban", ban_user_command))
    application.add_handler(CommandHandler("mute", mute_user_command))
    application.add_handler(CommandHandler("pin", pin_message_command))
    application.add_handler(CommandHandler("delete", delete_message_command))
    application.add_handler(CommandHandler("make_admin", make_admin_command))
    application.add_handler(CommandHandler("remove_admin", remove_admin_command))
    application.add_handler(CommandHandler("delete_all_msg", delete_all_msg_command))


    # Callback Query Handler (Essential for the whisper button)
    # Filter only for whispers to avoid conflict with other buttons if any
    application.add_handler(CallbackQueryHandler(handle_whisper_callback, pattern='^WHISPER_'))

    # Start the Bot
    logger.info("Starting @ummanorthbot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
