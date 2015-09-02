def principal_callback(userid, request):
	if userid == request.matchdict.get('user_id', ''):
		return ['principal:permitted']
	else:
		return []