# src/main.py
import flet as ft
import requests
import uuid
import time
from config import ENDPOINT, DATABASE_ID, COLLECTION_ID, HEADERS

# --- BACKEND LOGIC (Our Trusted Appwrite Engine) ---
def send_to_appwrite(sender_name, message_text):
    url = f"{ENDPOINT}/databases/{DATABASE_ID}/collections/{COLLECTION_ID}/documents"
    document_id = str(uuid.uuid4())[:20].replace('-', '')
    now_int = int(time.time() * 1000)
    
    payload = {
        "documentId": document_id,
        "data": {
            "senderName": sender_name,
            "content": message_text,
            "isDeleted": False,
            "timestamp": now_int
        }
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return response.status_code == 201

def fetch_from_appwrite(god_mode=False):
    url = f"{ENDPOINT}/databases/{DATABASE_ID}/collections/{COLLECTION_ID}/documents"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        all_docs = response.json().get("documents", [])
        all_docs.sort(key=lambda x: x.get("data", {}).get("timestamp", 0))
        
        messages = []
        for doc in all_docs:
            data = doc.get("data", doc)
            sender = data.get("senderName", "Unknown")
            text = data.get("content", "")
            is_deleted = data.get("isDeleted", False)
            
            if god_mode or not is_deleted:
                messages.append({"sender": sender, "text": text, "is_deleted": is_deleted})
        return messages
    return []

# --- FRONTEND UI LOGIC (Flet Visual Interface) ---
def main(page: ft.Page):
    page.title = "SquadTalk"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    
    # State tracking variables
    user_name = ft.Ref[ft.TextField]()
    god_mode = [False] # Wrapped in list to modify inside inner functions

    # UI Elements: Chat Window & Input Field
    chat_history = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    message_input = ft.TextField(hint_text="Type a message...", expand=True, autofocus=True)

    def load_chat_ui():
        """Refreshes the visual chat timeline with live database packets."""
        chat_history.controls.clear()
        live_messages = fetch_from_appwrite(god_mode=god_mode[0])
        
        for msg in live_messages:
            is_me = msg["sender"] == user_name.current.value
            bg_color = ft.colors.BLUE_700 if is_me else ft.colors.SURFACE_VARIANT
            align = ft.CrossAxisAlignment.END if is_me else ft.CrossAxisAlignment.START
            
            # Special indicator for deleted logs in admin mode
            display_text = f"{msg['text']} 🛑 [DELETED]" if msg["is_deleted"] else msg["text"]

            chat_history.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(msg["sender"], size=11, color=ft.colors.TEXT, weight=ft.FontWeight.BOLD),
                        ft.Text(display_text, size=15, color=ft.colors.WHITE),
                    ]),
                    margin=5,
                    padding=10,
                    border_radius=10,
                    bgcolor=bg_color,
                    alignment=ft.alignment.center_right if is_me else ft.alignment.center_left
                )
            )
        page.update()

    def send_click(e):
        if not message_input.value.strip():
            return
        # Ship to cloud
        success = send_to_appwrite(user_name.current.value, message_input.value)
        if success:
            message_input.value = ""
            load_chat_ui()

    def toggle_god_mode(e):
        god_mode[0] = not god_mode[0]
        e.control.selected = god_mode[0]
        e.control.icon_color = ft.colors.RED_ACCENT if god_mode[0] else ft.colors.WHITE
        load_chat_ui()

    # --- SCREEN 1: Enter Username Setup ---
    def start_chat(e):
        if not user_name.current.value.strip():
            user_name.current.error_text = "Name cannot be empty!"
            page.update()
            return
        
        # Build the complete primary dashboard view layout
        page.controls.clear()
        page.add(
            ft.AppBar(
                title=ft.Text("💥 SquadTalk Cloud Chat"),
                center_title=True,
                bgcolor=ft.colors.SURFACE,
                actions=[
                    ft.IconButton(ft.icons.SECURITY, on_click=toggle_god_mode, tooltip="Toggle God Mode"),
                    ft.IconButton(ft.icons.REFRESH, on_click=lambda _: load_chat_ui())
                ]
            ),
            chat_history,
            ft.Row([message_input, ft.IconButton(ft.icons.SEND, on_click=send_click, icon_color=ft.colors.BLUE_ACCENT)]),
        )
        load_chat_ui()

    # Initial Welcome Layout view container
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("🔥 SquadTalk Setup 🔥", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("Enter your display name to enter the graphic app matrix", size=14),
                ft.TextField(ref=user_name, label="Your Screen Name", on_submit=start_chat),
                ft.ElevatedButton("Enter Chat Room 🚀", on_click=start_chat, width=200)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
    )

if __name__ == "__main__":
    # Runs the application engine over local network preview settings
    ft.app(target=main, port=8550) 

