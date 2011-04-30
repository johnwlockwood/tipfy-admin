from tipfy.routing import Rule as TipRule


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

