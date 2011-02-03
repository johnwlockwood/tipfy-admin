import os, logging, datetime

from google.appengine.ext import db
from google.appengine.ext import deferred

from tipfy import (RequestHandler, RequestRedirect, Response, abort,
    cached_property, redirect, url_for, render_json_response,import_string)
from tipfy.ext.auth import AppEngineAuthMixin, login_required, user_required, admin_required

from tipfy.ext.jinja2 import Jinja2Mixin, render_response, render_template
from tipfy.ext.session import AllSessionMixins, SessionMiddleware
from tipfy.ext.wtforms import Form, fields, validators
import config 

from wtforms.ext.appengine.db import ModelConverter, model_form


class HandlerHolder(object):
    def __init__(self,*args,**kwargs):
        pass
    



class BaseHandler(RequestHandler, AppEngineAuthMixin, Jinja2Mixin):
  def render_to_response(self, template_name, template_vals=None, theme=None):
    template = os.path.join("admin", template_name)
    context = {
    'config': config
    }
    if template_vals:
      context.update(template_vals)

    return self.render_response(template, **context)    
    
    
class EntityDeleteHandler(BaseHandler):
    def post(self, **kwargs):
        apps_installed = self.get_config('tipfy', 'apps_installed')
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        entity_key_str = kwargs.get('entity_key')
        logging.info("\nput called\n")
        if not app_name in apps_installed:
            self.abort(404)
            
        model_list = []
        try:
            app_models = import_string('%s.models' % app_name)
            model_names = dir(app_models)
            for name in model_names:
                try:
                    if issubclass(getattr(app_models,name),db.Model):
                        model_list.append(name)
                except TypeError, e:
                    pass
            
        except ImportError, e:
            pass
        
        except AttributeError, e:
            pass
        
        if not model_name in model_list:
            self.abort(404)
            
        try:
            entity_key = db.Key(entity_key_str)
        except db.BadKeyError, e:
            self.abort(404)
        
        
        theModel = getattr(app_models,model_name)
        
        db.delete(entity_key)
            
        location = url_for('tipadmin/app/model/list', \
            appname=app_name,modelname=model_name)
        
        return RequestRedirect(location)
            




    
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
        apps_installed = self.get_config('tipfy', 'apps_installed')
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        entity_key_str = kwargs.get('entity_key')
        
        if not app_name in apps_installed:
            self.abort(404)
            
        model_list = []
        try:
            app_models = import_string('%s.models' % app_name)
            model_names = dir(app_models)
            for name in model_names:
                try:
                    if issubclass(getattr(app_models,name),db.Model):
                        model_list.append(name)
                except TypeError, e:
                    pass
            
        except ImportError, e:
            pass
        
        except AttributeError, e:
            pass
        
        if not model_name in model_list:
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
        
        parent_url = "<a href=\""+url_for('tipadmin/app/model/list', \
        appname=app_name,modelname=model_name)+"\">"+model_name+"</a>"
        
        rendered_form = self.render_form(theModel,entity)
        delete_form = None

        if entity:
            delete_form = "<form action='delete' method='post'> \
            <input type='submit' name='submit' value='Delete'></form>"
        
        return Response("admin app %s, model %s<br>\n%s\n<br>%s"%(parent_url, \
            model_name, rendered_form,delete_form))
        
    def post(self, **kwargs):
        apps_installed = self.get_config('tipfy', 'apps_installed')
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        entity_key_str = kwargs.get('entity_key')
        logging.info("\nput called\n")
        if not app_name in apps_installed:
            self.abort(404)
            
        model_list = []
        try:
            app_models = import_string('%s.models' % app_name)
            model_names = dir(app_models)
            for name in model_names:
                try:
                    if issubclass(getattr(app_models,name),db.Model):
                        model_list.append(name)
                except TypeError, e:
                    pass
            
        except ImportError, e:
            pass
        
        except AttributeError, e:
            pass
        
        if not model_name in model_list:
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
            
            location = url_for('tipadmin/app/model/list', \
                appname=app_name,modelname=model_name)
            
            return RequestRedirect(location)
            
        return self.get(**kwargs)
        
        
        
        
    
    
class ModelListHandler(BaseHandler):
    """ list of models of an app"""
    def __init__(self,*args, **kwargs):
        return super(ModelListHandler, self).__init__(*args, **kwargs)
        
    #@admin_required
    def get(self, **kwargs):
        app_name = kwargs.get('appname')
        apps_installed = self.get_config('tipfy', 'apps_installed')
        
        if not app_name in apps_installed:
            self.abort(404)
        #    
        model_list = []
        try:
            app_models = import_string('%s.models' % app_name)
            model_names = dir(app_models)
            for name in model_names:
                try:
                    if issubclass(getattr(app_models,name),db.Model):
                        model_list.append(name)
                except TypeError, e:
                    pass
            
        except ImportError, e:
            pass
        
        except AttributeError, e:
            pass
        
        urls = ["<a href=\""+url_for('tipadmin/app/model/list', \
        appname=app_name,modelname=model_name)+"\">"+model_name+"</a>" for model_name in model_list]
        #raise ValueError("blah")
        parent_url = "<a href=\""+url_for('tipadmin')+"\">admin</a>"
        
        return Response("%s app %s, models: %s"%(parent_url,app_name,urls))
        
        
class EntityListHandler(BaseHandler):
    """ list of entities of a model of an app"""
    def __init__(self,*args, **kwargs):
        return super(EntityListHandler, self).__init__(*args, **kwargs)
        
    #@admin_required
    def get(self, **kwargs):
        apps_installed = self.get_config('tipfy', 'apps_installed')
        app_name = kwargs.get('appname')
        model_name = kwargs.get('modelname')
        
        if not app_name in apps_installed:
            self.abort(404)
            
        model_list = []
        try:
            app_models = import_string('%s.models' % app_name)
            model_names = dir(app_models)
            for name in model_names:
                try:
                    if issubclass(getattr(app_models,name),db.Model):
                        model_list.append(name)
                except TypeError, e:
                    pass
            
        except ImportError, e:
            pass
        
        except AttributeError, e:
            pass
        
        if not model_name in model_list:
            self.abort(404)
        
        parent_url = "<a href=\""+url_for('tipadmin/app/list', \
        appname=app_name)+"\">"+app_name+"</a>"
        
        #paged list of entities
        theModel = getattr(app_models,model_name)
        
        #testEntity = theModel(path="/applications/fun/");
        #testEntity.put()
        
        
        query = theModel.all()
        
        create_new_url = "<a href=\"%s\">New %s</a>"%( \
            url_for('tipadmin/app/model/create', \
                appname=app_name,modelname=model_name),model_name)
        
        thelist = "<ul>\n"
        for entity in query:
            entity_url = "<a href=\"%s\">%s</a>"%(url_for('tipadmin/app/model/readupdate', \
                appname=app_name,modelname=model_name,entity_key=entity.key()),entity)
            thelist += "<li>%s</li>\n"%(entity_url)
            
        thelist += "</ul>\n"
        
        
        
        return Response("admin app %s, model %s<br>%s<br>\n%s"%(parent_url, \
            model_name, create_new_url,thelist))

        
class AdminHandler(BaseHandler):
    """ list of apps"""
    def __init__(self,*args, **kwargs):
        return super(AdminHandler, self).__init__(*args, **kwargs)
        
    def get(self, **kwargs):
        apps_installed = self.get_config('tipfy', 'apps_installed')
        
        urls = ["<a href=\""+url_for('tipadmin/app/list', \
        appname=app_name)+"\">"+app_name+"</a>" for app_name in apps_installed]
        #raise ValueError("blah")
        
        
        return Response("apps: %s, urls: :%s"%(apps_installed,urls))
        
        