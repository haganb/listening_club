import telegram
import random, os
import pprint
import spotipy
from json import load, loads, dumps, dump
from datetime import date
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from spotipy.oauth2 import SpotifyClientCredentials


# Global vars and api stuff
os.environ["SPOTIPY_CLIENT_ID"] = "afff1a5a8adb417399ac98335bd48f65"
os.environ["SPOTIPY_CLIENT_SECRET"] = "5a0f85558e764ace91f127603fa4d438"
os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Not in repo for obvious reasons, replace with your own API tokens/secrets to test
vars_path = "vars.json"
with open(vars_path) as f:
    INFO = load(f)

def get_album(album):
    #
    search = spotify.search(album)
    try:
        first_res = search["tracks"]["items"][0]["album"]
    except KeyError:
        return {}
    except IndexError:
        return {}
    return {
        "name": first_res["name"],
        "link" : first_res["external_urls"]["spotify"],
        "artist" : first_res["artists"][0]["name"]
    }

def refresh_info(INFO):
    #Helper function to re-write config json
    with open(vars_path, "w") as f:
        dump(INFO, f, indent=2) 

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Parse if user wants to add themselves or another
    user_name = update.message.text.split("/add")[1].strip()
    if user_name == '':
        member = update.message.from_user
        user_name = f"{member.first_name} {member.last_name}"

    # Add user if applicable
    print(f"Adding {user_name}")
    if user_name not in INFO["USERS"]:
        INFO["USERS"].append(user_name)
        refresh_info(INFO)
        response = f"Adding user {user_name} to Listening Club..."
    else:
        response = f"User {user_name} is already a member!"
    await update.message.reply_text(response, parse_mode=telegram.constants.ParseMode.HTML)

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Parse if user is requesting self removal or removal of another member
    selected_member = update.message.text.split("/remove")[1].strip()
    if selected_member == '':
        member = update.message.from_user
        selected_member = f"{member.first_name} {member.last_name}"

    # Remove from user list if necessary
    print(f"Adding {selected_member}")
    if selected_member in INFO["USERS"]:
        INFO["USERS"].remove(selected_member)
        # Handle removing them from HOSTS list
        if selected_member in INFO["HOSTS"]:
            INFO["HOSTS"].remove(selected_member)
        refresh_info(INFO)
        response = f"Removed member {selected_member} from Listening Club..."
    else:
        response = f"Member {selected_member} not found!"
    await update.message.reply_text(response, parse_mode=telegram.constants.ParseMode.HTML)

async def clear_hosts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Reset host list
    print("Resetting host list...")
    INFO["HOSTS"] = []
    with open(vars_path, "w") as f:
        dump(INFO, f)
    await update.message.reply_text(f"Host list reset!", parse_mode=telegram.constants.ParseMode.HTML)

async def view_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #View formatted list of members
    formatted_members = "".join([user + "\n" for user in INFO["USERS"]])
    await update.message.reply_text(f"Current members:\n{formatted_members}", parse_mode=telegram.constants.ParseMode.HTML)

async def select_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Pick a host from user list
    # Handle case where slate should be wiped clean
    if len(INFO["HOSTS"]) == len(INFO["USERS"]):
        print("Resetting host list...")
        INFO["HOSTS"] = []
        refresh_info(INFO)

    # Find someone that hasn't yet hosted
    while True:
        selected_host = INFO["USERS"][random.randrange(0, len(INFO["USERS"]))]
        if selected_host not in INFO["HOSTS"]:
            INFO["CURRENT_HOST"] = selected_host
            INFO["HOSTS"].append(selected_host)
            break 

    refresh_info(INFO)
    print(f"New selected host = {selected_host}\nHost list: {INFO['HOSTS']}")
    await update.message.reply_text(text=f"Listening club host is <b>{selected_host}</b>, please use the /pick_album command to make your selection", parse_mode=telegram.constants.ParseMode.HTML)

async def host(update: Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    # Echo the currently selected host
    await update.message.reply_text(f"Current host is <b>{INFO['CURRENT_HOST']}</b>", parse_mode=telegram.constants.ParseMode.HTML)

async def pick_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Make album selection
    album = update.message.text.split("/pick_album")[1].lstrip()
    user_info =update.message.from_user
    username = f"{user_info.first_name} {user_info.last_name}"
    print(f"Picking album from host {username}, selection {album}")
    # Check if user is current host 
    if INFO["CURRENT_HOST"] == username:
        spotify_data = get_album(album)
        if spotify_data == {}:
            update_msg = f"Query failed for input {album}, please try formatting it in the fashion of [Album] by [Artist]"
        else:
            album_data = {
                "NAME" : spotify_data["name"],
                "ARTIST" : spotify_data["artist"] ,
                "USER" : username,
                "DATE_SELECTED": str(date.today()),
                "SPOTIFY_LINK" : spotify_data["link"]
            }
            INFO["ALBUM"] = album_data
            INFO["HISTORY"].append(album_data)
            refresh_info(INFO)
            print(f"New album = {album_data}")
            update_msg = f"You have selected {album} for this weeks Listening Club!\nListen here: {spotify_data['link']}"
    else:
        update_msg = f"You aren't the host, bozo."
    await update.message.reply_text(update_msg)

async def album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Display which album is currently selected
    await update.message.reply_text(f"This weeks Listening Club album is <b>{INFO['ALBUM']['NAME']}</b> by <b>{INFO['ALBUM']['ARTIST']}</b>, selected by {INFO['ALBUM']['USER']} on {INFO['ALBUM']['DATE_SELECTED']}.\n<i><b>Please listen by Sunday!</b></i>\n{INFO['ALBUM']['SPOTIFY_LINK']}", 
                                    parse_mode=telegram.constants.ParseMode.HTML
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Helper to explain how all commands work
    HELP = """
        Listening Club bot commands are as follows:\n
        <i>/add</i>: Adds a user to the listening club membership list. Leave just command if you want to register yourself, otherwise type in the users first name and last name.\n
        <i>/members</i>: Display all users registered in the listening club\n
        <i>/remove</i>: Removes a user to the listening club membership list. Leave just command if you want to remove yourself, otherwise type in the users first name and last name.\n
        <i>/select_host</i>: Choose a host for this weeks Listening Club. You cannot be a host again until everyone has gotten a chance.\n
        <i>/clear_hosts</i>: Resets the internal host list, only used for maintenance.\n
        <i>/host</i>: Return who the current host of the Listening Club is.\n
        <i>/pick_album</i>: Once you are selected as host, use this command to set the album of the week. Simply type in the name in [Name] by [Artist] format.\n
        <i>/album</i>: Return the current album selected for listening.
    """
    await update.message.reply_text(HELP, parse_mode=telegram.constants.ParseMode.HTML)
# Main
if __name__ == "__main__":
    # Setup and object instantiation
    application = telegram.ext.Application.builder().token(INFO["TOKEN"]).build()
    print("Running application with config...")
    # pprint.pprint(INFO)
    # for key, value in INFO.items():
    #     print(key, value)
    
 
    # Member commands
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("members", view_members))
    application.add_handler(CommandHandler("remove", remove))

    # Hosting commands
    application.add_handler(CommandHandler("select_host", select_host))
    application.add_handler(CommandHandler("clear_hosts", clear_hosts))
    application.add_handler(CommandHandler("host", host))

    # Album commands
    application.add_handler(CommandHandler("pick_album", pick_album))
    application.add_handler(CommandHandler("album", album))

    # Reminder commands, etc
    application.add_handler(CommandHandler("help", help))

    # Bot starter
    print("Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
