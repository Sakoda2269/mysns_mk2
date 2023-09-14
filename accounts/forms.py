from typing import Any
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
import random, string

def randomname(n) -> str:
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)

class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "usertag", "password1", "password2",]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usertag'].widget.attrs['value'] = randomname(16)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class UserChangeForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'usertag',
        ]
    
    def __init__(self, username=None, email=None, usertag=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        if username:
            self.fields['username'].widget.attrs['value'] = username
        if email:
            self.fields['email'].widget.attrs['value'] = email
        if usertag:
            self.fields['usertag'].widget.attrs['value'] = usertag
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class SetPassword(SetPasswordForm):
    def __init__(self, user: AbstractBaseUser | None, *args: Any, **kwargs: Any) -> None:
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
