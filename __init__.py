import os, logging, datetime

from google.appengine.ext import db
from google.appengine.ext import deferred

from tipfy.handler import RequestHandler
from tipfy.app import Request,Response,RequestContext,redirect
from tipfy.routing import import_string

from tipfyext.wtforms import Form, fields, validators
from tipfyext.jinja2 import Jinja2Mixin

from wtforms.ext.appengine.db import ModelConverter, model_form


class HandlerHolder(object):
    def __init__(self,*args,**kwargs):
        pass
    



class BaseHandler(RequestHandler,Jinja2Mixin):
  def render_to_response(self, template_name, template_vals=None, theme=None):
    template = os.path.join("admin", template_name)
    context = {
    'config': self.app.config
    }
    if template_vals:
      context.update(template_vals)

    return self.render_response(template, **context)
    
    
def getModels(app_name,model_list):
    app_models = None
    try:
        try:
            app_models = import_string('%s.models' % app_name)
        except (ImportError,AttributeError), e:
            app_models = import_string('%s.model' % app_name)
        model_names = dir(app_models)
        for name in model_names:
            try:
                if issubclass(getattr(app_models,name),db.Model):
                    model_list.append(name)
            except TypeError, e:
                pass
    
    except (ImportError,AttributeError), e:
        logging.info("import error from both")
        
    return app_models
    
class EntityDeleteHandler(BaseHandler):
    def post(self, **kwargs):
        allapps = []
        apps_installed = self.app.config['tipfy']['apps_installed']
        allapps.extend(apps_installed)
        allapps.extend(self.app.config['tipfy']['sys_apps'])
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        entity_key_str = kwargs.get('entity_key')
        logging.info("\nput called\n")
        if not app_name in allapps:
            self.abort(404)
            
        model_list = []
        app_models = getModels(app_name,model_list)
        
        
        
        if not model_name in model_list or not app_models:
            self.abort(404)
            
        try:
            entity_key = db.Key(entity_key_str)
        except db.BadKeyError, e:
            self.abort(404)
        
        
        theModel = getattr(app_models,model_name)
        
        db.delete(entity_key)
            
        location = self.url_for('tipadmin/app/model/list', \
            appname=app_name,modelname=model_name)
        
        return redirect(location)
            




    
class EntityReadUpdateHandler(BaseHandler):
    def render_form(self,model,entity=None):
        if hasattr(self,'form') and self.form:
            pass
        else:
            self.form = self.get_form(model,entity)
            
        fields = self.form._fields
        
        rendered_form = "".join(["%s:<br>%s<br>"%(value.label,value()) \
        for label,value in fields.iteritems()])
        
        rendered_form = "<form action='' method='post'>%s \
        <input type='submit' name='submit'></form>%s"%(rendered_form,self.form.errors)
        
        return rendered_form
    
    def get_form(self,model,entity=None):
        FormClass = model_form(model)
        form = FormClass(self.request.values,obj=entity)
        return form
    
    def get(self, **kwargs):
        """ edit entity """
        allapps = []
        apps_installed = self.app.config['tipfy']['apps_installed']
        allapps.extend(apps_installed)
        allapps.extend(self.app.config['tipfy']['sys_apps'])
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        entity_key_str = kwargs.get('entity_key')
        
        if not app_name in allapps:
            self.abort(404)
            
        model_list = []
        app_models = getModels(app_name,model_list)
        
        if not model_name in model_list or not app_models:
            self.abort(404)
            
            
        theModel = getattr(app_models,model_name)
            
        entity = None
        if entity_key_str:
            try:
                entity_key = db.Key(entity_key_str)
            except db.BadKeyError, e:
                self.abort(404)
            entity = db.get(entity_key)
        
        #import gaepdb;gaepdb.set_trace()
        
        parent_url = "<a href=\""+self.url_for('tipadmin/app/model/list', \
        appname=app_name,modelname=model_name)+"\">"+model_name+"</a>"
        
        rendered_form = self.render_form(theModel,entity)
        delete_form = None

        if entity:
            delete_form = "<form action='delete' method='post'> \
            <input type='submit' name='submit' value='Delete'></form>"
        
        return Response("admin app %s, model %s<br><hr>%s<hr><br>\n%s\n<br>%s"%(parent_url, \
            model_name,entity, rendered_form,delete_form))
        
    def post(self, **kwargs):
        allapps = []
        apps_installed = self.app.config['tipfy']['apps_installed']
        allapps.extend(apps_installed)
        allapps.extend(self.app.config['tipfy']['sys_apps'])
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        entity_key_str = kwargs.get('entity_key')
        logging.info("\nput called\n")
        if not app_name in allapps:
            self.abort(404)
            
        model_list = []
        app_models = getModels(app_name,model_list)
        
        if not model_name in model_list or not app_models:
            self.abort(404)
            
        theModel = getattr(app_models,model_name)
        entity = None
        if entity_key_str:
            try:
                entity_key = db.Key(entity_key_str)
            except db.BadKeyError, e:
                self.abort(404)
            entity = db.get(entity_key)
        
        #raise ValueError("blah")
        if not entity:
            entity = theModel()
        
        
        self.form = self.get_form(theModel)
        
        if self.form.validate():
            self.form.populate_obj(entity)
            entity.put()
            
            location = self.url_for('tipadmin/app/model/list', \
                appname=app_name,modelname=model_name)
            
            return redirect(location)
            
        return self.get(**kwargs)
        
        
        
        
    
    
class ModelListHandler(BaseHandler):
    """ list of models of an app"""
    def __init__(self,*args, **kwargs):
        return super(ModelListHandler, self).__init__(*args, **kwargs)
        
    #@admin_required
    def get(self, **kwargs):
        app_name = kwargs.get('appname')
        allapps = []
        apps_installed = self.app.config['tipfy']['apps_installed']
        allapps.extend(apps_installed)
        allapps.extend(self.app.config['tipfy']['sys_apps'])
        
        if not app_name in allapps:
            self.abort(404)
        #    
        model_list = []
        app_models = getModels(app_name,model_list)
        
        urls = ["<a href=\""+self.url_for('tipadmin/app/model/list', \
        appname=app_name,modelname=model_name)+"\">"+model_name+"</a>" for model_name in model_list]
        #raise ValueError("blah")
        parent_url = "<a href=\""+self.url_for('tipadmin')+"\">admin</a>"
        
        return Response("%s app %s, models: %s"%(parent_url,app_name,urls))
        
        
class EntityListHandler(BaseHandler):
    """ list of entities of a model of an app"""
    def __init__(self,*args, **kwargs):
        return super(EntityListHandler, self).__init__(*args, **kwargs)
        
    #@admin_required
    def get(self, **kwargs):
        allapps = []
        apps_installed = self.app.config['tipfy']['apps_installed']
        allapps.extend(apps_installed)
        allapps.extend(self.app.config['tipfy']['sys_apps'])
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        
        if not app_name in allapps:
            self.abort(404)
            
        model_list = []
        app_models = getModels(app_name,model_list)
        
        if not model_name in model_list or not app_models:
            self.abort(404)
        
        parent_url = "<a href=\""+self.url_for('tipadmin/app/list', \
        appname=app_name)+"\">"+app_name+"</a>"
        
        #paged list of entities
        theModel = getattr(app_models,model_name)
        
        #testEntity = theModel(path="/applications/fun/");
        #testEntity.put()
        start_cursor = self.request.args.get('sc')
        orderby = self.request.args.get('ob')
        
        query = theModel.all()
        if orderby:
            query.order(orderby)
            
            
        if not start_cursor:
            entities = query.fetch(20)
        else:
            try:
                query.with_cursor(start_cursor)
                entities = query.fetch(20)
            except datastore_errors.BadRequestError, e:
                entities = query.fetch(20)
        
        if len(entities) == 20:
            more_available = 1
        else:
            more_available = 0
            
        next_start_cursor = query.cursor()
        
        fetch_more_url = "<a href=\"%s?sc=%s&ob=%s\">Fetch More</a>"%( \
            self.url_for('tipadmin/app/model/list', \
        appname=app_name,modelname=model_name),next_start_cursor,orderby)
        
        
        create_new_url = "<a href=\"%s\">New %s</a>"%( \
            self.url_for('tipadmin/app/model/create', \
                appname=app_name,modelname=model_name),model_name)
        
        thelist = "<ul>\n"
        for entity in entities:
            entity_url = "<a href=\"%s\">%s</a>"%(self.url_for('tipadmin/app/model/readupdate', \
                appname=app_name,modelname=model_name,entity_key=entity.key()),entity)
            thelist += "<li>%s</li>\n"%(entity_url)
            
        thelist += "</ul>\n"
        
        if more_available:
            thelist += "<br>"+fetch_more_url
        
        
        
        return Response("admin app %s, model %s<br>%s<br>\n%s"%(parent_url, \
            model_name, create_new_url,thelist))

        
class AdminHandler(BaseHandler):
    """ list of apps"""
    def __init__(self,*args, **kwargs):
        return super(AdminHandler, self).__init__(*args, **kwargs)
        
    def get(self, **kwargs):
        allapps = []
        apps_installed = self.app.config['tipfy']['apps_installed']
        allapps.extend(apps_installed)
        allapps.extend(self.app.config['tipfy']['sys_apps'])
        
        urls = ["<a href=\""+self.url_for('tipadmin/app/list', \
        appname=app_name)+"\">"+app_name+"</a>" for app_name in allapps]
        
        
        return Response("apps: %s, urls: :%s"%(allapps,urls))
        
        