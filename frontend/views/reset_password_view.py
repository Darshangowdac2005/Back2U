# frontend/views/reset_password_view.py

import threading
import flet as ft
from frontend.api_client import reset_password_api


class ResetPasswordView(ft.Container):
    def __init__(self, page: ft.Page, email: str = ""):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page

        self.email_field = ft.TextField(
            label="Email Address",
            value=email,
            width=320,
            read_only=bool(email),
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        self.otp_field = ft.TextField(
            label="OTP Code (6 digits)",
            width=320,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=6,
        )
        self.new_password_field = ft.TextField(
            label="New Password",
            password=True,
            can_reveal_password=True,
            width=320,
        )
        self.confirm_password_field = ft.TextField(
            label="Confirm New Password",
            password=True,
            can_reveal_password=True,
            width=320,
        )
        self.message_text = ft.Text("", color=ft.colors.RED_400)
        self.reset_button = ft.ElevatedButton(
            text="Reset Password",
            on_click=self._handle_reset,
            width=320,
        )

        self.content = self._build_ui()

    def _handle_reset(self, e):
        email = (self.email_field.value or "").strip()
        otp = (self.otp_field.value or "").strip()
        new_password = self.new_password_field.value or ""
        confirm_password = self.confirm_password_field.value or ""

        # Client-side validation
        if not all([email, otp, new_password, confirm_password]):
            self.message_text.color = ft.colors.RED_400
            self.message_text.value = "All fields are required."
            self.page.update()
            return

        if new_password != confirm_password:
            self.message_text.color = ft.colors.RED_400
            self.message_text.value = "Passwords do not match."
            self.page.update()
            return

        if len(new_password) < 6:
            self.message_text.color = ft.colors.RED_400
            self.message_text.value = "Password must be at least 6 characters."
            self.page.update()
            return

        self.reset_button.disabled = True
        self.message_text.color = ft.colors.BLUE_300
        self.message_text.value = "Verifying OTP..."
        self.page.update()

        result = reset_password_api(email, otp, new_password)

        self.reset_button.disabled = False
        if result and "message" in result:
            self.message_text.color = ft.colors.GREEN_400
            self.message_text.value = result["message"]
            self.page.update()
            # Navigate to login after a brief delay (non-blocking)
            threading.Timer(1.5, lambda: self.page.go("/login")).start()
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
                                ft.Icon(ft.icons.LOCK_OPEN, size=48, color=ft.colors.GREEN_400),
                                ft.Text(
                                    "Reset Your Password",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Enter the OTP sent to your email, then set a new password.",
                                    size=13,
                                    color=ft.colors.GREY_400,
                                    text_align=ft.TextAlign.CENTER,
                                    width=280,
                                ),
                                self.email_field,
                                self.otp_field,
                                self.new_password_field,
                                self.confirm_password_field,
                                self.reset_button,
                                self.message_text,
                                ft.Row(
                                    [
                                        ft.TextButton(
                                            text="Back to Login",
                                            on_click=lambda e: self.page.go("/login"),
                                        ),
                                        ft.TextButton(
                                            text="Resend OTP",
                                            on_click=lambda e: self.page.go("/forgot-password"),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    width=320,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
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
