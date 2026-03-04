from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from . import forms
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse

class Register(View):
    def get(self, request):
        form = forms.RegisterForm()

        return render(request, 'register.html', {'form': form})
    
    def post(self, request):
        form = forms.RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.email = form.cleaned_data["email"]
            
            # 1. Lưu user vào DB trước để tạo ID
            user.save() 

            # 2. Bây giờ mới lấy Group và add vào user đã có ID
            try:
                customer_group = Group.objects.get(name="Customer")
                user.groups.add(customer_group)
            except Group.DoesNotExist:
                # Xử lý nếu lỡ trong DB chưa tạo group "Customer"
                pass

            # 3. Xử lý avatar (vì avatar thường là file, nên cập nhật sau cũng được)
            avatar = form.cleaned_data.get("avatar")
            if avatar:
                user.avatar = avatar
                user.save() # Lưu lại lần nữa để cập nhật avatar

            return redirect('login')
        return render(request, 'register.html', {'form': form}) 

class Login(LoginView):
    template_name= 'login.html'

    def get_success_url(self) -> str:
        return reverse_lazy('home')

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))