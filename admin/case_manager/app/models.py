# app/wrappers.py

from typing import Any, Type, List, Dict, Optional, get_type_hints
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
