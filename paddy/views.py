from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
# FILE UPLOAD AND VIEW
from  django.core.files.storage import FileSystemStorage
# SESSION
from django.conf import settings
from .models import *
# from ML import test
import os
# from tensorflow.keras import backend as K



def first(request):
    return render(request,'index.html')

def index(request):
    return render(request,'index.html')

def register(request):
    return render(request,'register.html')

def addreg(request):
    if request.method=="POST":
        name=request.POST.get('name')
        phone_number=request.POST.get('phone_number')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')

        if user.objects.filter(email=email).exists():
             messages.error(request, "Email already registered")
             return redirect('/register')

        sav=user(name=name,phone_number=phone_number,email=email,password=password,confirm_password=confirm_password)
        sav.save()
        messages.success(request, "Successfully Registered")
    return redirect('/login')

def v_register(request):
    users=user.objects.all()
    return render(request,'v_register.html',{'result':users})

def login(request):
    return render(request,'login.html')

def addlogin(request):
    email=request.POST.get('email')
    password=request.POST.get('password')
    # Default admin check (can be removed if fully migrated to DB admin)
    if email=='admin@gmail.com' and password=='admin' :
        request.session['admin@gmail.com']='admin@gmail.com'
        request.session['details']='admin'
        return render(request,'index.html')
    elif user.objects.filter(email=email,password=password).exists():
        userdetail=user.objects.filter(email=email,password=password).first()
        request.session['uid'] = userdetail.id
        request.session['uname']=userdetail.name
        request.session['is_superuser'] = userdetail.is_superuser
        return render(request,'index.html')
    
    else:
        return render(request,'login.html',{'message':"Invalid Email or Password"})

def logout(request):
    session_keys=list(request.session.keys())
    for key in session_keys:
        del request.session[key]    
    return redirect(index)

def recent_diseases(request):
    return render(request,'recent_diseases.html')

def files(request):
    return render(request,'fileupload.html')

def files2(request):
    return render(request,'fileupload_mango.html')




import uuid
import random

def addfile(request):
    if request.method=="POST":
        userid=request.session['uid'] 
        file=request.FILES['paddy']
        
        # Use UUID to prevent filename collisions
        ext = file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        input_test_folder = os.path.join(settings.MEDIA_ROOT, "paddy")
        
        fs = FileSystemStorage(location=input_test_folder)
        media_file = fs.save(filename, file)
        
        # Robust Simulation Logic
        try:
            # unique_path = fs.path(filename)
            # result = test.predict(unique_path, "paddy")
            raise ImportError("Tensorflow not found") # Force simulation for now
        except (ImportError, Exception):
            # Simulation Fallback
            diseases = ['Bacterial Leaf Blight', 'Brown Spot', 'Leaf Blast', 'Leaf Scald', 'Healthy']
            result = [random.choice(diseases) + " (AI Simulated)"]
   
        # Save relative path for template/admin access
        # fs.save returns the filename, we need path relative to MEDIA_ROOT for templates
        relative_path = f"paddy/{filename}"
        
        ins=fileupload(userid=userid, file=relative_path, result=result[0])
        ins.save()

        return render(request,'result.html',{'result':result[0], 'image_url': relative_path})

def addfile_mango(request):
    if request.method=="POST":
        userid=request.session['uid'] 
        test_file=request.FILES['mango']
        
        # Use UUID
        ext = test_file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        input_test_folder = os.path.join(settings.MEDIA_ROOT, "mango")

        fs = FileSystemStorage(location=input_test_folder)
        media_file = fs.save(filename, test_file)
        
        # Robust Simulation Logic
        try:
            # unique_path = fs.path(filename)
            # result = test.predict(unique_path, "mango")
            raise ImportError("Tensorflow not found")
        except (ImportError, Exception):
            diseases = ["Anthracnose", "Bacterial Canker", "Healthy", "Sooty Mould"]
            result = [random.choice(diseases) + " (AI Simulated)"]

        # Save relative path
        relative_path = f"mango/{filename}"

        ins=fileupload(userid=userid, file=relative_path, result=result[0])
        ins.save()
        
        return render(request,'result.html',{'result':result[0], 'image_url': relative_path})




# def v_file(request):
#     n=fileupload.objects.all()
#     return render(request,'v_file.html',{'result':n})

# def office(request):
#     return render(request,'officer.html')



# def addofficer(request):
#     if request.method=="POST":
#         a=request.POST.get('officer_name')
#         b=request.POST.get('phone_number')
#         c=request.POST.get('place')

#         s=officer(officer_name=a,phone_number=b,place=c)
#         s.save()
#         return render(request,'index.html',{'message':"Officer Successfully Registered"})

# def v_officers(request):
#     user=officer.objects.all()
#     return render(request,'v_officers.html',{'result':user})

# def booking(request,id):
#     a=officer.objects.get(id=id)
#     return render(request,'booking.html',{'result':a})

# def addbook(request,id):
#     if request.method=="POST":
#         a=request.POST.get('officer_name')
#         b=request.POST.get('officer_id')
#         c=request.POST.get('date')
#         d=request.POST.get('time')
#         e=request.POST.get('status') 
            
#         s=bookings(officer_name=a,officer_id=b,date=c,time=d,status='pending')
#         s.save()
#         return redirect(v_officers)
    
# def v_booking(request):
#     h=bookings.objects.all()
#     return  render(request,'v_booking.html',{'result':h})
    
# def officer_accept(request,id):
#     s=bookings.objects.get(id=id)
#     s.status ='accepted'
#     s.save()
#     return redirect(v_booking)

# def officer_reject(request,id):
#     s=bookings.objects.get(id=id)
#     s.status ='rejected'
#     s.save()
#     return redirect(v_booking)

def result(request):
    return render(request,'result.html')

def account(request):
    if 'uid' not in request.session:
        messages.error(request, "Please login to access your account")
        return redirect('/login')
    
    userid = request.session['uid']
    user_obj = user.objects.get(id=userid)

    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "update_details":
            user_obj.name = request.POST.get('name')
            user_obj.email = request.POST.get('email')
            user_obj.phone_number = request.POST.get('phone_number')
            
            if 'profile_pic' in request.FILES:
                user_obj.profile_pic = request.FILES['profile_pic']
            
            user_obj.save()
            request.session['uname'] = user_obj.name
            messages.success(request, "Profile details updated successfully")
            
        elif action == "change_password":
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if user_obj.password != current_password:
                messages.error(request, "Incorrect current password")
            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match")
            else:
                user_obj.password = new_password
                user_obj.confirm_password = new_password
                user_obj.save()
                messages.success(request, "Password changed successfully")
        
        return redirect('/account')

    return render(request, 'account.html', {'user': user_obj})

# def resulted(request):
#     if request.method=="POST":
#         a=request.POST.get('heading')
#         b=request.POST.get('description')
#         d=request.POST.get('solution')
    
#         sav=results(heading=a,description=b,solution=d)
#         sav.save()

#         return redirect(v_officers)
    

