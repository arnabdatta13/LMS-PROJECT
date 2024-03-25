from django.shortcuts import render,redirect,HttpResponse
from app.EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import CustomUser
from app.models import Teacher,Add_Notice

def HOME(request):
    return render(request,'home.html')

def CONTRACT(request):
    return render(request,'contract.html')


def ABOUT(request):
    teacher= Teacher.objects.all()

    context={
        'teacher':teacher,
    }
    return render(request,'about.html',context)



def clear_notifications(request):
   
    notifications = Add_Notice.objects.all()
    notifications.delete()  
    
    return redirect('login')


def BASE(request):
    return render(request,'base.html')
def LOGIN(request):
    return render(request,'login.html')

def JOIN_NOW(request):
    return render(request,'join_now.html')

def dologin(request):
    user_type = None
    if request.method == "POST":
        user  = EmailBackEnd().authenticate(request,
                                          username=request.POST.get('username'),
                                          password=request.POST.get('password'))
        if user != None:
            login(request,user)
            user_type= user.user_type
        if user_type == 1:
           return redirect('admin_home')
            
        elif user_type == 2:
            return redirect('teacher-home')
        elif user_type == 3:
            return redirect('student-home')
            
        else:
            messages.error(request,'Username and Password Are Invalid')
            return redirect('login')
    else:
        messages.error(request,'Username and Password Are Invalid')
        return redirect('login')
    
def dologout(request):
    logout(request)
    return redirect('login')



@login_required(login_url='login')
def PROFILE(request):
    user= CustomUser.objects.get(id=request.user.id)
    context ={
        'user':user,
    }
    return render(request,'profile.html',context)

@login_required(login_url='login')
def PROFILE_UPDATE(request):
    if request.method == 'POST':
        first_name =request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        username =request.POST.get('username')
        password =request.POST.get('password')
        
        
      
        profile_pic = request.FILES.get('profile_pic')
        print(profile_pic)
        
        #upolad this data django database
        try:
            customuser = CustomUser.objects.get(id= request.user.id)
            
            if first_name != None and first_name != "":
                customuser.first_name=first_name
            
            if last_name != None and last_name != "":
                customuser.last_name=last_name

            

            
            if profile_pic != None and profile_pic != "":
                customuser.profile_pic=profile_pic

            #customuser.username= username
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request,'Your Profile Updated Successfully')
            return redirect('profile')
            
      
        except:
            messages.error(request,'Failed To Update Your Profile')

    return render(request,'profile.html')


