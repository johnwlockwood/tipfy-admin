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
        handler='tipadmin.EntityDeleteHandler'),
            
        TipRule('/tipadmin/<appname>/<modelname>/<entity_key>/', 
            endpoint='tipadmin/app/model/readupdate', \
        handler='tipadmin.EntityReadUpdateHandler'),
        
        TipRule('/tipadmin/<appname>/<modelname>/create', \
            endpoint='tipadmin/app/model/create', \
        handler='tipadmin.EntityReadUpdateHandler'),
        
        TipRule('/tipadmin/<appname>/<modelname>/', \
            endpoint='tipadmin/app/model/list', \
        handler='tipadmin.EntityListHandler'),
        
        TipRule('/tipadmin/<appname>/', endpoint='tipadmin/app/list', \
        handler='tipadmin.ModelListHandler'),
        
        TipRule('/tipadmin/', endpoint='tipadmin', \
        handler='tipadmin.AdminHandler')]

    return rules
