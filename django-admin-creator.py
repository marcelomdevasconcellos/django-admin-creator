import sys, getopt, os


def save_file(filename, content):
    file = open(filename, "w")
    file.write(content)
    file.close()


def read_file(filename):
    import codecs
    file = codecs.open(filename, "r", "utf-8")
    content = file.read()
    file.close()
    return content


ADMIN_BASE = """from django.contrib import admin
from django.db import models
from django_currentuser.middleware import get_current_user
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from django.forms import Select, Textarea

from django_currentuser.middleware import get_current_user

from .models import *
from .forms import *"""


ADMIN = """


@admin.register(%(model_name)s)
class %(model_name)sAdmin(%(admin_class)s):

    form = %(model_name)sForm
    search_fields = (
        %(search_fields)s
    )
    list_filter = (
        %(list_filter)s
    )
    list_display = (
        %(list_display)s
    )
    inlines = []"""


ADMIN_INLINE = """


class %(model_name)sInline(%(admin_inline_class)s):

    model = %(model_name)s
    form = %(model_name)sForm
    extra = 3
    readonly_fields = ()
    fields = (
        %(all_fields)s
    )"""


FORM_BASE = """from datetime import datetime

from django import forms
from django.db.models import Q

from django_currentuser.middleware import get_current_user

from .models import *"""


FORM = """


class %(model_name)sForm(forms.ModelForm):

    class Meta:
        model = %(model_name)s
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(%(model_name)sForm, self).__init__(*args, **kwargs)"""


def clear_content(content):

    content = content.replace('=', ' = ')
    content = content.replace(':', '')
    content = content.replace('%(class)s', '%|class|s')
    for n in range(10):
        content = content.replace('\n', '')
        content = content.replace('  ', ' ')
        content = content.replace(" '", "'")
        content = content.replace("' ", "'")
    
    return content

def get_fieldname(text):
    t1 = text.split(' = models.')
    return t1[0].replace(' ', '')


def get_fieldtype(text):
    t1 = text.split(' = models.')
    t2 = t1[1].split('(')
    return t2[0].replace(' ', '')


def create_admin(file, admin_class, admin_inline_class):

    content_model = read_file(file)
    content_model = clear_content(content_model)
    models = content_model.split('class ')
    del models[0]
    content_admin = ADMIN_BASE
    content_forms = FORM_BASE

    for m in models:
    
        t1 = m.split('(')

        if 'Meta' not in t1[0]:
        
            data_dict = {}
            data_dict['model_name'] = t1[0]
            data_dict['admin_class'] = admin_class
            data_dict['admin_inline_class'] = admin_inline_class
            t1 = m.split(')')
            del t1[len(t1)-1]

            search_fields = []
            all_fields = []
            list_filter = []
            list_display = []


            for t2 in t1:
                
                if 'models.' in t2:
            
                    fieldname = get_fieldname(t2)
                    fieldtype = get_fieldtype(t2)
                    all_fields.append("'%s'," % fieldname)
                    
                    if fieldtype in ('CharField', 
                                     'TextField'):
                        search_fields.append("'%s'," % fieldname)
                    
                    if fieldtype in ('ForeignKey', 
                                     'DateTimeField', 
                                     'DateField', 
                                     'BooleanField'):
                        list_filter.append("'%s'," % fieldname)
                    
                    if 'choices' in t2:
                        list_filter.append("'%s'," % fieldname)
                    
                    if fieldtype in ('CharField', 
                                     'ForeignKey', 
                                     'DateTimeField', 
                                     'DateField', 
                                     'BooleanField'):
                        list_display.append("'%s'," % fieldname)

            
            data_dict['search_fields'] = '\n        '.join(search_fields)
            data_dict['list_filter'] = '\n        '.join(list_filter)
            data_dict['list_display'] = '\n        '.join(list_display)
            data_dict['all_fields'] = '\n        '.join(all_fields)

            txt = "ForeignKey('%(model_name)s'" % data_dict

            inline_question = input('Include inline admin on %(model_name)s ? (Y/N) ' % data_dict)
            if inline_question == 'Y':
                content_admin += ADMIN_INLINE % data_dict

            content_admin += ADMIN % data_dict
            content_forms += FORM % data_dict

    admin_file = file.replace('models.py', 'admin.py')
    forms_file = file.replace('models.py', 'forms.py')

    if not os.path.isfile(admin_file):
        save_file(admin_file, content_admin)
        print('%s successfully saved!' % admin_file)

    else:
        replace_file = input('%s already exists ! Do you want replace it ? (Y/N) ' % admin_file)
        if replace_file == 'Y':
            save_file(admin_file, content_admin)
            print('%s successfully saved!' % admin_file)

    if not os.path.isfile(forms_file):
        save_file(forms_file, content_forms)
        print('%s successfully saved!' % forms_file)
    
    else:
        replace_file = input('%s already exists ! Do you want replace it ? (Y/N) ' % forms_file)
        if replace_file == 'Y':
            save_file(forms_file, content_forms)
            print('%s successfully saved!' % forms_file)


def main(argv):

    file = None
    admin_class = 'admin.ModelAdmin'
    admin_inline_class = 'admin.TabularInline'

    try:
        opts, args = getopt.getopt(argv, "f:", ["file=", ])

    except getopt.GetoptError:
        print('python django-admin-creator.py -f <file>')
        sys.exit(2)

    for opt, arg in opts:

        if opt in ("-h", "--help", '-?'):
            print('python django-admin-creator.py -f <file>')
            sys.exit()

        elif opt in ("-f", "--file"):
            file = arg

    if file:
        create_admin(file, admin_class, admin_inline_class)
        print()
    else:
        print('Example:')
        print('python django-admin-creator.py -f <file>')


if __name__ == "__main__":
    main(sys.argv[1:])
