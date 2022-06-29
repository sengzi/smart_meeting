
def current_status(request):
    
    login = False

    if not request.session.has_key('status'):
        login = False
    elif request.session['status'] == "Login":
        login = True
    
    return {
        'login': login,
    }