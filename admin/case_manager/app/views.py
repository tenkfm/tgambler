from django.shortcuts import render
from django import forms
from .models import ModelWrapper
from typing import Type, List, Dict, Any
from .container import container
from common.models.domain.user import UserInfo
from .models import MyForm

FIELD_WIDGET = {
    forms.CharField:        forms.TextInput,
    forms.IntegerField:     forms.NumberInput,
    forms.BooleanField:     forms.CheckboxInput,
    forms.DateTimeField:    forms.DateTimeInput,
}

def build_form_class(wrapper: ModelWrapper) -> Type[MyForm]:
    attrs: Dict[str, forms.Field] = {}
    for f in wrapper.fields:
        FieldCls = f['form_field']
        # выбираем свой виджет (или TextInput по умолчанию)
        WidgetCls = FIELD_WIDGET.get(FieldCls, forms.TextInput)
        widget = WidgetCls(attrs={'class': 'form-control'})

        params: Dict[str, Any] = {
            'label':    f.get('label', f['name'].replace('_', ' ').title()),
            'required': f['required'],
            'widget':   widget,
        }
        default = getattr(wrapper.model_cls, f['name'], None)
        if default is not None:
            params['initial'] = default

        attrs[f['name']] = FieldCls(**params)

    form_name = wrapper.model_cls.__name__ + 'Form'
    return type(form_name, (MyForm,), attrs)


def home(request):
    return render(request, "app/home.html")

def users(request):
    users = container.firebase_service.fetch_all(UserInfo)
    wrapper = ModelWrapper(
        UserInfo,
        include_fields=['id', 'tg_id', 'username', 'first_name', 'auth_date', 'is_premium']
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(users)
    return render(request, 'app/users.html', {
        'columns': cols,
        'rows': rows,
    })

def user(request, id):
    uw = ModelWrapper(UserInfo)
    userInfoForm = build_form_class(uw)
    user = container.firebase_service.fetch_by_id(UserInfo, id)

    if request.method == 'POST':
        # form = userInfoForm(request.POST)
        # if form.is_valid():
        #     data = form.cleaned_data
        #     # применяем данные обратно в obj и сохраняем
        #     for k, v in data.items():
        #         setattr(user, k, v)
        #     user.save()
        #     return redirect('case_list')
        print("POST request received")
    else:
        # заполняем начальные значения из obj
        init = {
            field['name']: getattr(user, field['name']) for field in uw.fields
        }
        form = userInfoForm(initial=init)

    return render(request, "app/user.html", {'form': form})


def cases(request):
    uw = ModelWrapper(UserInfo)
    userInfoForm = build_form_class(uw)

    users = container.firebase_service.fetch_all(UserInfo)
    user = users[0]

    if request.method == 'POST':
        # form = userInfoForm(request.POST)
        # if form.is_valid():
        #     data = form.cleaned_data
        #     # применяем данные обратно в obj и сохраняем
        #     for k, v in data.items():
        #         setattr(user, k, v)
        #     user.save()
        #     return redirect('case_list')
        print("POST request received")
    else:
        # заполняем начальные значения из obj
        init = {
            field['name']: getattr(user, field['name']) for field in uw.fields
        }
        form = userInfoForm(initial=init)

    return render(request, "app/cases.html", {'form': form})
