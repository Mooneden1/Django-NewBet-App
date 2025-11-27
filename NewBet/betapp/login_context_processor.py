def login_cp(request):
    if request.user.is_authenticated:  # Remove the parentheses
        action = "/logout/"
        label = "Logout"
    else:
        action = "/login/"
        label = "Login"
    context = {
        "action": action,
        "label": label
    }
    return context
