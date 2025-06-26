# app/wrappers.py

from django.shortcuts import redirect
from typing import Any, Type, List, Dict, Optional, get_type_hints, Callable
from enum import Enum
from datetime import datetime
from django import forms
from django.utils.safestring import mark_safe

# app/forms.py
from django import forms
from django.utils.safestring import mark_safe

class MyForm(forms.Form):
    def as_p(self):
        html = super().as_p()
        html = html.replace('<p>', '<div class="form-group">')
        html = html.replace('</p>', '</div>')
        return mark_safe(html)

class ModelWrapper:
    def __init__(
        self,
        model_cls: Type,
        *,
        include_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
    ):
        self.model_cls = model_cls
        self.include_fields = set(include_fields) if include_fields else None
        self.exclude_fields = set(exclude_fields) if exclude_fields else None
        self.fields: List[Dict[str, Any]] = []
        self._inspect_fields()

    def _inspect_fields(self):
        hints = get_type_hints(self.model_cls)
        for name, typ in hints.items():
            if self.include_fields is not None and name not in self.include_fields:
                continue
            if self.exclude_fields is not None and name in self.exclude_fields:
                continue

            self.fields.append({
                'name': name,
                'label': name.replace('_', ' ').title(),
                'form_field': {
                    str: forms.CharField,
                    int: forms.IntegerField,
                    bool: forms.BooleanField,
                    datetime: forms.DateTimeField,
                }.get(typ, forms.CharField),
                'required': not hasattr(self.model_cls, name)
            })

    def get_table_columns(self) -> List[Dict[str, Any]]:
        return self.fields

    def serialize_instance(self, obj: Any) -> Dict[str, Any]:
        row: Dict[str, Any] = {}
        for f in self.fields:
            name = f['name']
            val = getattr(obj, name, None)

            if isinstance(val, datetime):
                formatted = val.strftime('%Y-%m-%d %H:%M')
            elif isinstance(val, bool):
                color = "green" if val else "red"
                formatted = mark_safe(
                    f'<div class="status-pill {color}" '
                    'data-title="Complete" data-toggle="tooltip" '
                    'data-original-title="" title=""></div>'
                )
            else:
                formatted = val

            row[name] = formatted
        return row

    def get_table_data(self, objects: List[Any]) -> List[List[Any]]:
        """
        Возвращает список списков (rows), готовых к выводу в шаблоне:
          [[val1, val2, ...], [...], ...]
        """
        cols = self.get_table_columns()
        rows: List[List[Any]] = []
        for obj in objects:
            serialized = self.serialize_instance(obj)
            row = [ serialized[col['name']] for col in cols ]
            rows.append(row)
        return rows


FIELD_WIDGET = {
    forms.CharField:     forms.TextInput,
    forms.IntegerField:  forms.NumberInput,
    forms.BooleanField:  forms.CheckboxInput,
    forms.DateTimeField: forms.DateTimeInput,
}

def build_form_class(
    wrapper: ModelWrapper,
    *,
    required_fields: Optional[List[str]] = None,
    optional_fields: Optional[List[str]] = None,
    readonly_fields: Optional[List[str]] = None
) -> Type[MyForm]:
    """
    Генерирует класс формы на основе метаданных из wrapper,
    автоматически превращая Enum-поля в ChoiceField.
    """
    readonly_fields = set(readonly_fields or [])
    attrs: Dict[str, forms.Field] = {}
    # Получаем аннотации, чтобы определить Enum-поля
    hints = get_type_hints(wrapper.model_cls)

    for f in wrapper.fields:
        name = f['name']
        field_type = hints.get(name)
        FieldCls = f['form_field']

        # 1) Обработка Enum-поля
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            # Список кортежей (value, label)
            choices = [(e.value, e.value) for e in field_type]
            field = forms.ChoiceField(
                label    = f.get('label', name.title()),
                choices  = choices,
                required = True if required_fields is None else (name in required_fields),
                widget   = forms.Select(
                              attrs={'class': 'form-control'}
                           )
            )
            # initial — если есть дефолт в модели (Enum instance), то его .value
            default = getattr(wrapper.model_cls, name, None)
            if isinstance(default, Enum):
                field.initial = default.value
            attrs[name] = field
            continue

        # 2) Обычные поля
        WidgetCls = FIELD_WIDGET.get(FieldCls, forms.TextInput)
        widget_attrs = {'class': 'form-control'}
        if name in (readonly_fields or []):
            widget_attrs['readonly'] = 'readonly'

        widget = WidgetCls(attrs=widget_attrs)

        # required
        if required_fields is not None:
            is_required = name in required_fields
        elif optional_fields is not None:
            is_required = name not in optional_fields
        else:
            is_required = f.get('required', True)

        params: Dict[str, Any] = {
            'label':    f.get('label', name.replace('_', ' ').title()),
            'required': is_required,
            'widget':   widget,
        }
        default = getattr(wrapper.model_cls, name, None)
        if default is not None:
            params['initial'] = default

        attrs[name] = FieldCls(**params)

    form_name = f"{wrapper.model_cls.__name__}Form"
    return type(form_name, (MyForm,), attrs)

def save_object_from_form(
    form: forms.Form,
    obj: Any,
    readonly_fields: List[str],
    save_fn: Callable[[Any], None],
    success_redirect_name: str
):
    """
    Если form.is_valid():
      - обновляет obj всеми полями из cleaned_data, кроме readonly_fields
      - вызывает save_fn(obj)
      - возвращает HttpResponseRedirect на success_redirect_name
    Иначе возвращает None.
    """
    if form.is_valid():
        for name, val in form.cleaned_data.items():
            if name in readonly_fields:
                continue
            setattr(obj, name, val)
        save_fn(obj)
        return redirect(success_redirect_name)
    return None