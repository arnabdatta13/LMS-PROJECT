from django.shortcuts import render,redirect,HttpResponse
from app.EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import CustomUser
from app.models import Teacher,Add_Notification,Message,Notice,ImageGallery
from django.http import JsonResponse
import face_recognition as fr
import base64
import numpy as np
import io
import cv2
import face_recognition



def HOME(request):
    notice = Notice.objects.all()
    context = {
        "notice":notice
    }
    return render(request,'home.html',context)


def CONTRACT(request):
    if request.method == "POST":
        name= request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(name)
        print(phone)
        print(email)
        print(message)
        save_massage = Message.objects.create(
            name = name,
            phone=phone,
            email=email,
            message=message
        )
        messages.success(request,'Massage Sent Successfully')
        return redirect('contract')
    
    return render(request,'contract.html')


def ABOUT(request):
    teacher= Teacher.objects.all()

    context={
        'teacher':teacher,
    }
    return render(request,'about.html',context)


def GALLERY(request):
    images = ImageGallery.objects.all()  # Retrieve all image entries from the database

    context = {
        "images":images,
    }
    return render(request,"gallery.html",context)

def clear_notifications(request):
   
    notifications = Add_Notification.objects.all()
    notifications.delete()  
    
    user_type= request.user.user_type
    if user_type == 1:
        return redirect('admin_home')
        
    elif user_type == 2:
        return redirect('teacher-home')
    elif user_type == 3:
        return redirect('student-home')
        


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




def  FACE_ID_LOGIN(request):
    return render(request,"face_id_login.html")



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




def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def get_encoded_faces():
    users = CustomUser.objects.all()
    encoded = {}

    for user in users:
        if user.profile_pic:
            try:
                # Load the user's profile picture and encode the face
                img = face_recognition.load_image_file(user.profile_pic.path)
                encoding = face_recognition.face_encodings(img)
                if encoding:  # Make sure at least one face encoding is found
                    encoded[user.username] = encoding[0]
            except Exception as e:
                print(f"Error encoding face for user {user.username}: {e}")
        else:
            print(f"No profile picture found for user: {user.username}")

    return encoded

def classify_face(img_file):
    """
    This function takes an image file-like object as input and returns the name of the face it contains.
    """
    try:
        # Convert the file-like object to a numpy array
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Convert image to RGB (face_recognition expects RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Load all the known faces and their encodings
        faces = get_encoded_faces()
        known_face_names = list(faces.keys())
        known_face_encodings = list(faces.values())

        # Get face encodings for the uploaded image
        face_encodings = face_recognition.face_encodings(rgb_img)

        for face_encoding in face_encodings:
            # Compare the uploaded face with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            # Find the best match
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return known_face_names[best_match_index]

        return "Unknown"
    except Exception as e:
        print(f"Error in face classification: {e}")
        return False

def FACE_ID_DOLOGIN(request):
    if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        decoded_file = base64.b64decode(str_img)

        # Convert the decoded image data to a file-like object
        img_file = io.BytesIO(decoded_file)

        # Pass the file-like object to the classify_face function
        res = classify_face(img_file)

        if res:  # Check if face classification was successful
            user_exists = CustomUser.objects.filter(username=res).exists()
            if user_exists:
                user = CustomUser.objects.get(username=res)
                login(request, user)
                user_type = user.user_type

                if user_type == 1:
                    redirect_url = 'admin-home'
                elif user_type == 2:
                    redirect_url = 'teacher-home'
                elif user_type == 3:
                    redirect_url = 'student-home'
                else:
                    redirect_url = None

                if redirect_url:
                    return JsonResponse({'redirect_url': redirect_url})

    error_msg = "Face Not Found. Please Take The Photo Again."
    return JsonResponse({'error': error_msg}, status=400)