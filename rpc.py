import pypresence
import time
client_id = "1093969187375947776"
RPC = pypresence.Presence(client_id)
RPC.connect()


RPC.update(
    state="Checking",
    details="PeerBrain",
    large_image="https://cdn.discordapp.com/app-icons/1093969187375947776/a618709b63c4936ebc8f02acaa57e9f4.png",
    small_image="your_small_image_key_here",
    start=int(time.time()),
    buttons=[
        {"label": "Visit PeerBrain", "url": "https://peerbrain.net"}
    ]
)