import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(r"C:\Users\sdemi\PycharmProjects\Barter")

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home.home.settings")

# Инициализируем Django
django.setup()

# Теперь можно импортировать Django-модули
from django.test import RequestFactory
from home.negocios.views import DocumentCreateView  # Убедись, что путь верный

factory = RequestFactory()
request = factory.get('/documents/create/')

view = DocumentCreateView()
view.request = request
view.object = None

context = view.get_context_data()
print(context.keys())  # Должно включать 'form' и 'formset'

formset = context['formset']
for form in formset:
    print(form.fields.keys())  # Должны быть 'file' и 'delete'
