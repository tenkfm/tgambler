from django.shortcuts import render, redirect
from .models import ModelWrapper
from .container import container
from enum import Enum
from common.models.domain.user import UserInfo
from common.models.domain.wallet import Wallet
from .models import build_form_class, save_object_from_form

def home(request):
    return render(request, "app/home.html")

#
# Users
#
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
    UserForm = build_form_class(
        uw,
        required_fields=['username', 'first_name'],
        readonly_fields=['tg_id', 'id', 'username']
        )
    user = container.firebase_service.fetch_by_id(UserInfo, id)

    if request.method == 'POST':
        form = UserForm(request.POST)
        response = save_object_from_form(
            form=form,
            obj=user,
            readonly_fields=['tg_id', 'id', 'username'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='users'
        )
        if response:
            return response
        return render(request, "app/user.html", {'form': form})
    else:
        # заполняем начальные значения из obj
        init = {
            field['name']: getattr(user, field['name']) for field in uw.fields
        }
        form = UserForm(initial=init)

    return render(request, "app/user.html", {'form': form})


#
# Wallets
#
def wallets(request):
    objs = container.firebase_service.fetch_all(Wallet)
    wrapper = ModelWrapper(
        Wallet
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(objs)
    return render(request, 'app/wallets.html', {
        'columns': cols,
        'rows': rows,
    })

def wallet(request, id):
    uw = ModelWrapper(Wallet)
    WalletForm = build_form_class(
        uw,
        readonly_fields=['id']
    )
    obj = container.firebase_service.fetch_by_id(Wallet, id)

    if request.method == 'POST':
        form = WalletForm(request.POST)
        response = save_object_from_form(
            form=form,
            obj=obj,
            readonly_fields=['id'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='wallets'
        )
        if response:
            return response
        return render(request, "app/wallet.html", {'form': form})
    else:
        init = {}
        for f in uw.fields:
            name = f['name']
            val = getattr(obj, name)
            # если это Enum, используем его .value, иначе сам val
            if isinstance(val, Enum):
                init[name] = val.value
            else:
                init[name] = val
        form = WalletForm(initial=init)
    return render(request, "app/wallet.html", {'form': form})



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
