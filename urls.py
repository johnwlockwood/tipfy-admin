from werkzeug.routing import Map,Submount, RuleTemplate,EndpointPrefix
from tipfy import Rule as TipRule, import_string
from google.appengine.ext import db


def get_rules(app):
    """Returns a list of URL rules for the application. The list can be
    defined entirely here or in separate ``urls.py`` files.

    :param app:
        The WSGI application instance.
    :return:
        A list of class:`tipfy.Rule` instances.
    """
    #  Here we show an example of joining all rules from the
    # ``apps_installed`` definition set in config.py.
    
    
    rules =[
        TipRule('/tipadmin/<appname>/<modelname>/<entity_key>/delete', \
            endpoint='tipadmin/app/model/entity/delete', \
        handler='apps.admin.EntityDeleteHandler'),
            
        TipRule('/tipadmin/<appname>/<modelname>/<entity_key>/', 
            endpoint='tipadmin/app/model/readupdate', \
        handler='apps.admin.EntityReadUpdateHandler'),
        
        TipRule('/tipadmin/<appname>/<modelname>/create', \
            endpoint='tipadmin/app/model/create', \
        handler='apps.admin.EntityReadUpdateHandler'),
        
        TipRule('/tipadmin/<appname>/<modelname>/', \
            endpoint='tipadmin/app/model/list', \
        handler='apps.admin.EntityListHandler'),
        
        TipRule('/tipadmin/<appname>/', endpoint='tipadmin/app/list', \
        handler='apps.admin.ModelListHandler'),
        
        TipRule('/tipadmin/', endpoint='tipadmin', \
        handler='apps.admin.AdminHandler')]

    return rules
