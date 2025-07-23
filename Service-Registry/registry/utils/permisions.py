from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin


User = get_user_model()

class Student(LoginRequiredMixin):
    ...

class Instructor(LoginRequiredMixin):
    ...
    
class Admin(LoginRequiredMixin):
    ...
    
