from pyramid.view import view_config


#TODO: Delete this later and replace it with our frontend
@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'chestify'}