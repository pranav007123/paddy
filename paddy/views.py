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
            import re
            
            # Get form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            
            # Validate name (2-100 characters, letters and spaces only)
            if not name or len(name) < 2:
                messages.error(request, "Name must be at least 2 characters long")
                return redirect('/account')
            if len(name) > 100:
                messages.error(request, "Name must not exceed 100 characters")
                return redirect('/account')
            if not re.match(r'^[a-zA-Z\s]+$', name):
                messages.error(request, "Name can only contain letters and spaces")
                return redirect('/account')
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messages.error(request, "Please enter a valid email address")
                return redirect('/account')
            
            # Check email uniqueness (excluding current user)
            if user.objects.filter(email=email).exclude(id=userid).exists():
                messages.error(request, "This email is already registered to another account")
                return redirect('/account')
            
            # Validate phone number (exactly 10 digits)
            if not re.match(r'^\d{10}$', phone_number):
                messages.error(request, "Phone number must be exactly 10 digits")
                return redirect('/account')
            
            # Validate profile picture if uploaded
            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']
                
                # Check file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
                if profile_pic.content_type not in allowed_types:
                    messages.error(request, "Profile picture must be a JPG, JPEG, or PNG image")
                    return redirect('/account')
                
                # Check file size (max 5MB)
                if profile_pic.size > 5 * 1024 * 1024:
                    messages.error(request, "Profile picture must be less than 5MB")
                    return redirect('/account')
                
                user_obj.profile_pic = profile_pic
            
            # All validations passed, update user
            user_obj.name = name
            user_obj.email = email
            user_obj.phone_number = phone_number
            user_obj.save()
            request.session['uname'] = user_obj.name
            messages.success(request, "Profile details updated successfully")
            
        elif action == "change_password":
            import re
            
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate current password
            if user_obj.password != current_password:
                messages.error(request, "Incorrect current password")
                return redirect('/account')
            
            # Validate password match
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect('/account')
            
            # Validate password strength (min 8 chars, at least 1 uppercase, 1 lowercase, 1 number)
            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long")
                return redirect('/account')
            if not re.search(r'[A-Z]', new_password):
                messages.error(request, "Password must contain at least one uppercase letter")
                return redirect('/account')
            if not re.search(r'[a-z]', new_password):
                messages.error(request, "Password must contain at least one lowercase letter")
                return redirect('/account')
            if not re.search(r'\d', new_password):
                messages.error(request, "Password must contain at least one number")
                return redirect('/account')
            
            # All validations passed, update password
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
    

