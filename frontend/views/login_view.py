# frontend/views/login_view.py

import flet as ft
from frontend.api_client import login_user

class LoginView(ft.Container):
    def __init__(self, page: ft.Page, app_state):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.app_state = app_state
        
        self.email_field = ft.TextField(label="Email", width=300)
        self.password_field = ft.TextField(label="Password", password=True, width=300)
        self.message_text = ft.Text("")

        self.content = self._build_ui()

    def _handle_login(self, e):
        email = self.email_field.value
        password = self.password_field.value
        
        self.message_text.value = "Logging in..."
        self.page.update()
        
        result = login_user(email, password)
        
        if result and 'token' in result:
            self.app_state["token"] = result['token']
            self.app_state["role"] = (result.get('role') or "").strip().lower()
            self.message_text.value = f"Success! Role: {result['role']}"
            
            # Navigate home and force a view refresh to update the navbar
            self.page.go("/") 
        else:
            self.message_text.value = result.get('error', 'Unknown login error.')
            self.page.update()

    def _build_ui(self):
        return ft.Column(
            [
                ft.Card(
                    content=ft.Container(
                        ft.Column(
                            [
                                ft.Text("Back2u Login", size=24, weight=ft.FontWeight.BOLD),
                                self.email_field,
                                self.password_field,
                                ft.Row(
                                    [
                                        ft.ElevatedButton(text="Login", on_click=self._handle_login),
                                        ft.TextButton(text="Sign Up Here", on_click=lambda e: self.page.go("/signup"))
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.TextButton(
                                    text="Forgot Password?",
                                    on_click=lambda e: self.page.go("/forgot-password"),
                                    style=ft.ButtonStyle(color=ft.colors.BLUE_300),
                                ),
                                self.message_text
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        ),
                        padding=30
                    ),
                    elevation=10,
                    width=400
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )