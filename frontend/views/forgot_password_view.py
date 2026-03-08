# frontend/views/forgot_password_view.py

import flet as ft
from frontend.api_client import forgot_password_api


class ForgotPasswordView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page

        self.email_field = ft.TextField(
            label="Registered Email Address",
            width=320,
            keyboard_type=ft.KeyboardType.EMAIL,
            autofocus=True,
        )
        self.message_text = ft.Text("", color=ft.colors.GREEN_400)
        self.send_button = ft.ElevatedButton(
            text="Send OTP",
            on_click=self._handle_send_otp,
            width=320,
        )

        self.content = self._build_ui()

    def _handle_send_otp(self, e):
        email = (self.email_field.value or "").strip()
        if not email:
            self.message_text.color = ft.colors.RED_400
            self.message_text.value = "Please enter your email address."
            self.page.update()
            return

        self.send_button.disabled = True
        self.message_text.color = ft.colors.BLUE_300
        self.message_text.value = "Sending OTP..."
        self.page.update()

        result = forgot_password_api(email)

        self.send_button.disabled = False
        if result and "message" in result:
            self.message_text.color = ft.colors.GREEN_400
            self.message_text.value = result["message"]
            self.page.update()
            # Navigate to reset page, passing email via query param
            self.page.go(f"/reset-password?email={email}")
        else:
            self.message_text.color = ft.colors.RED_400
            self.message_text.value = result.get("error", "Something went wrong. Please try again.")
            self.page.update()

    def _build_ui(self):
        return ft.Column(
            [
                ft.Card(
                    content=ft.Container(
                        ft.Column(
                            [
                                ft.Icon(ft.icons.LOCK_RESET, size=48, color=ft.colors.BLUE_400),
                                ft.Text(
                                    "Forgot Password",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Enter your registered email and we'll send you a one-time password (OTP).",
                                    size=13,
                                    color=ft.colors.GREY_400,
                                    text_align=ft.TextAlign.CENTER,
                                    width=280,
                                ),
                                self.email_field,
                                self.send_button,
                                self.message_text,
                                ft.TextButton(
                                    text="Back to Login",
                                    on_click=lambda e: self.page.go("/login"),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=18,
                        ),
                        padding=ft.padding.symmetric(horizontal=32, vertical=28),
                    ),
                    elevation=10,
                    width=420,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
