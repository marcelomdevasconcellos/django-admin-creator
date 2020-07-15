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

from models import *
from forms import *"""


ADMIN = """


@admin.register(%(model_name)s)
class %(model_name)sAdmin(%(admin_class)s):

    form = %(model_name)sForm
    search_fields = ()
    list_filter = ()
    list_display = (
        %(fields)s
    )
    inlines = []"""


ADMIN_INLINE = """


class %(model_name)sInline(%(admin_inline_class)s):

    model = %(model_name)s
    form = %(model_name)sForm
    extra = 3
    readonly_fields = ()
    fields = (
        %(fields)s
    )"""


FORM_BASE = """from datetime import datetime

from django import forms
from django.db.models import Q

from django_currentuser.middleware import get_current_user

from models import *"""


FORM = """


class %(model_name)sForm(forms.ModelForm):

    class Meta:
        model = %(model_name)s
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(%(model_name)sForm, self).__init__(*args, **kwargs)"""


def clear_content(content):

    for n in range(10):
        content = content.replace('\n', '')
        content = content.replace('  ', ' ')
        content = content.replace(" '", "'")
        content = content.replace("' ", "'")
    
    return content


def create_admin(file):

    content_model = read_file(file)
    models = content_model.split('\nclass ')
    del models[0]
    content_admin = ADMIN_BASE
    content_forms = FORM_BASE

    for m in models:
        
        t1 = m.split('(')
        data_dict = {}
        data_dict['model_name'] = t1[0]
        data_dict['admin_class'] = admin_class
        data_dict['admin_inline_class'] = admin_inline_class
        t1 = m.split(' = models.')
        del t1[len(t1)-1]
        fields = []

        for t2 in t1:
            t3 = t2.split(' ')
            field_name = t3[len(t3)-1]
            fields.append("'%s'," % field_name)
        
        data_dict['fields'] = '\n        '.join(fields)

        txt = "ForeignKey('%(model_name)s'" % data_dict

        if txt in clear_content(content_model):
            content_admin += ADMIN_INLINE % data_dict

        content_admin += ADMIN % data_dict
        content_forms += FORM % data_dict

    admin_file = file.replace('models.py', 'admin.py')
    forms_file = file.replace('models.py', 'forms.py')

    if not os.path.isfile(admin_file):
        save_file(admin_file, content_admin)
        print('%s successfully saved!' % admin_file)

    if not os.path.isfile(forms_file):
        save_file(forms_file, content_forms)
        print('%s successfully saved!' % forms_file)


def main(argv):

    file = None
    admin_class = 'admin.ModelAdmin'
    admin_inline_class = 'admin.TabularInline'

    try:
        opts, args = getopt.getopt(argv, "hfai:", ["file=", ])

    except getopt.GetoptError:
        print('python django-admin-creator.py -f <file> -a <admin_class> -i <admin_inline_class>')
        sys.exit(2)

    for opt, arg in opts:

        if opt in ("-h", "--help", '-?'):
            print('python django-admin-creator.py -f <file> -a <admin_class> -i <admin_inline_class>')
            sys.exit()

        elif opt in ("-f", "--file"):
            file = arg

        elif opt in ("-a", "--admin"):
            admin_class = arg

        elif opt in ("-i", "--admininline"):
            admin_inline_class = arg

    if file:
        create_admin(file)


if __name__ == "__main__":
    main(sys.argv[1:])
