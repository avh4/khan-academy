
def is_honeypot_empty(request):
    return not request.get("honey_input") and not request.get("honey_textarea")
