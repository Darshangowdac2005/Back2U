# frontend/main.py

import sys
sys.path.insert(0, '..')

import flet as ft
from frontend.api_client import set_auth, TOKEN as API_TOKEN, USER_ROLE as API_USER_ROLE
from frontend.views.login_view import LoginView
from frontend.views.signup_view import SignupView
from frontend.views.home_view import HomeView
from frontend.views.report_item_view import ReportItemView
from frontend.views.admin_dashboard import AdminDashboard

# Global State
app_state = {"token": None, "role": None}

def main(page: ft.Page):
    page.title = "Back2U - Lost and Found Management System"
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 0
    page.spacing = 0
    # App-wide pubsub for simple cross-view notifications (e.g., refresh items)
    if not hasattr(page, "pubsub"):
        page.pubsub = ft.PubSub()
    
    # --- Theme Mode Toggle ---
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        # Update the icon in the navbar
        route_change(None)
        
    # --- Navbar ---
    def create_navbar():
        effective_token = app_state["token"] or API_TOKEN
        effective_role = (app_state["role"] or API_USER_ROLE or "").lower()
        is_logged_in = effective_token is not None
        is_admin = effective_role == "admin"
        
        def logout(e):
            app_state["token"] = None
            app_state["role"] = None
            set_auth(None, None)  # Clear API client token
            # Notify and force UI refresh
            page.snack_bar = ft.SnackBar(content=ft.Text("Logged out"))
            page.snack_bar.open = True
            page.go("/")
            # Ensure navbar & route content re-render immediately
            route_change(None)

        # Build actions list
        actions = [
            ft.TextButton(
                text="Home",
                on_click=lambda e: page.go("/"),
                style=ft.ButtonStyle(color=ft.colors.WHITE)
            ),
        ]

        if is_logged_in:
            actions.append(
                ft.TextButton(
                    text="Report Item",
                    on_click=lambda e: page.go("/report"),
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                )
            )

            if is_admin:
                actions.append(
                    ft.TextButton(
                        text="Admin Dashboard",
                        on_click=lambda e: page.go("/admin"),
                        style=ft.ButtonStyle(color=ft.colors.WHITE)
                    )
                )

            actions.append(
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    tooltip="Logout",
                    on_click=logout,
                    icon_color=ft.colors.WHITE
                )
            )
        else:
            actions.append(
                ft.TextButton(
                    text="Signup",
                    on_click=lambda e: page.go("/signup"),
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                )
            )
            actions.append(
                ft.TextButton(
                    text="Login",
                    on_click=lambda e: page.go("/login"),
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                )
            )

        # Theme toggle icon
        theme_icon = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE
        actions.append(
            ft.IconButton(
                icon=theme_icon,
                tooltip="Toggle Theme",
                on_click=toggle_theme,
                icon_color=ft.colors.WHITE
            )
        )

        return ft.AppBar(
            title=ft.Text("Back2U Portal", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.colors.BLUE_700,
            actions=actions,
            toolbar_height=60
        )

    # --- Routing Logic ---
    def route_change(route):
        page.controls.clear()

        # Add navbar
        page.controls.append(create_navbar())

        # Add content based on route
        if page.route == "/":
            page.controls.append(HomeView(page))
        elif page.route == "/login":
            page.controls.append(LoginView(page, app_state))
        elif page.route == "/signup":
            page.controls.append(SignupView(page))
        elif page.route == "/report":
            if app_state["token"]:
                page.controls.append(ReportItemView(page))
            else:
                # Redirect to login if not authenticated
                page.snack_bar = ft.SnackBar(content=ft.Text("Please login to report items"), bgcolor=ft.colors.RED_400)
                page.snack_bar.open = True
                page.go("/login")
                return  # Prevent further execution
        elif page.route == "/admin":
            effective_token = app_state["token"] or API_TOKEN
            effective_role = (app_state["role"] or API_USER_ROLE or "").lower()
            if effective_token and effective_role == "admin":
                page.controls.append(AdminDashboard(page))
            elif effective_token:
                # Logged in but not admin
                page.snack_bar = ft.SnackBar(content=ft.Text("Admin access required"), bgcolor=ft.colors.RED_400)
                page.snack_bar.open = True
                page.go("/")
                return
            else:
                # Not logged in
                page.snack_bar = ft.SnackBar(content=ft.Text("Please login as admin"), bgcolor=ft.colors.RED_400)
                page.snack_bar.open = True
                page.go("/login")
                return

        page.update()

    # Set up routing handlers
    page.on_route_change = route_change
    
    # Navigate to initial route
    page.go(page.route)

if __name__ == "__main__":
    print("Starting Flet app on http://localhost:8550")
    ft.app(target=main, view=ft.WEB_BROWSER, port=8550)