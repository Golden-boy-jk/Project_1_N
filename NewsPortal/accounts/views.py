from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

def become_author(request):
    """Добавляет пользователя в группу 'authors'"""
    authors_group, _ = Group.objects.get_or_create(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        request.user.groups.add(authors_group)
    return redirect('profile')  # Перенаправление на профиль