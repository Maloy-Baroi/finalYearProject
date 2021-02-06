from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import cv2
from django.urls import reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from App_main.models import PoliceProfile, Suspected, CriminalLocation, File, CustomUser
from App_main.forms import SignUpForm, PoliceProfileForm
import os


def justify_logger(login_id):
    print(login_id)
    print(CustomUser.objects.get(username=login_id).photo)
    cam = cv2.VideoCapture(0)
    s, img = cam.read()

    if s:
        face_1_img = face_recognition.load_image_file(CustomUser.objects.get(username=login_id).photo)
        # print(f"Media Image: {face_1_img}")
        face_1_face_encode = face_recognition.face_encodings(face_1_img)[0]

        small_frame = cv2.resize(img, (0, 0), fx=.25, fy=.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        print(face_encodings)
        try:
            check = face_recognition.compare_faces(face_1_face_encode, face_encodings)
        except Exception:
            check = [False]
        if check[0]:
            return True
        else:
            return False
        # top, right, bottom, left = (face_recognition.face_locations(img))[0]
        #
        # face_Image = img[top:bottom, left:right]
        # pil_image = Image.fromarray(face_Image)
        # pil_image.save('face.png')
    else:
        return False


def index(request):
    signup_form = SignUpForm()
    login_form = AuthenticationForm()
    if request.method == 'POST' and 'loginBTN' in request.POST:
        print("LOGIN")
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            real_user = justify_logger(str(username))
            if real_user:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse('App_main:home'))
            else:
                messages.error(request, "You are not the real user")
                return HttpResponseRedirect(reverse("App_main:login"))
    elif request.method == 'POST' and 'signupBTN' in request.POST:
        print("SIGNUP")
        signup_form = SignUpForm(request.POST, request.FILES)
        if signup_form.is_valid():
            signup_form.save()
            return HttpResponseRedirect(reverse('App_main:login'))

    diction = {'login_Form': login_form, 'signup_form': signup_form}
    return render(request, 'App_main/login.html', context=diction)


@login_required
def home(request):
    return render(request, "Home.html")


@login_required
def loggedout(request):
    logout(request)
    return HttpResponseRedirect(reverse('App_main:login'))


@login_required
def report_register(request):
    if request.method == 'POST':
        citizen = Suspected.objects.filter(national_id=request.POST["national_id"])
        if citizen.exists():
            messages.error(request, "Citizen with that National ID already exists")
            return redirect(report_register)
        else:
            myfile = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            person = Suspected.objects.create(
                name=request.POST["name"],
                national_id=request.POST["national_id"],
                address=request.POST["address"],
                picture=uploaded_file_url[1:],
                status="wanted"
            )
            person.save()
            messages.add_message(request, messages.INFO, "Citizen successfully added")
            return HttpResponseRedirect(reverse('App_main:register_report'))
    return render(request, 'App_main/report-register.html')


@login_required
def view_records(request):
    wanted = Suspected.objects.all()
    context = {
        "wanted": wanted
    }
    return render(request, 'App_main/view_suspected.html', context)


# Encode multiple images
def findEncodings(images):
    encodeList = []
    for img in images:
        print(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        print(encode)
        encodeList.append(encode)
    return encodeList


# End Encoding multiple images


@login_required
def detectWithWebcam(request):
    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    images = []
    encodings = []
    names = []
    files = []
    nationalIds = []

    if not Suspected.objects.all():
        return render(request, "App_main/view_suspected_info.html", context={'No_suspected': 'No suspected'})

    prsn = Suspected.objects.all()
    for crime in prsn:
        images.append(crime.name + '_image')
        encodings.append(crime.name + '_face_encoding')
        print(type(crime.picture))
        files.append(crime.picture[6:])
        names.append('Name: ' + crime.name + ', National ID: ' + crime.national_id + ', Address ' + crime.address)
        nationalIds.append(crime.national_id)

    filesFolder = []
    for i in files:
        filesFolder.append(cv2.imread(f"media/{i}"))

    encodingList = findEncodings(filesFolder)

    # Create arrays of known face encodings and their names
    known_face_encodings = encodingList
    known_face_names = names
    n_id = nationalIds

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face enqcodings in the frame of video
        face_location = face_recognition.face_locations(rgb_frame)
        face_encoding = face_recognition.face_encodings(rgb_frame, face_location)

        # Loop through each face in this frame of video
        for face_encode, face_loc in zip(face_encoding, face_location):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encode)

            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encode)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                ntnl_id = n_id[best_match_index]
                person = Suspected.objects.filter(national_id=ntnl_id)
                name = known_face_names[best_match_index] + ', Status: ' + person.get().status

                suspected = CriminalLocation.objects.create(
                    name=person.get().name,
                    national_id=person.get().national_id,
                    address=person.get().address,
                    picture=person.get().picture,
                    status='Wanted',
                    latitude='20202020',
                    longitude='040404040'
                )
                suspected.save()

                # print(f"{ntnl_id}: {name}")

        # Display the resulting image
        # cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('App_main:home')


@login_required
def police_profile(request):
    return render(request, "App_main/policeProfile.html")


@login_required
def edit_profile(request):
    # x = justify_logger(request.user.username)
    # print(x)
    # print(request.user.username)
    form = PoliceProfileForm()
    diction = {'form': form}
    if request.method == "POST":
        form = PoliceProfileForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return HttpResponseRedirect(reverse('App_main:login'))
    return render(request, "App_main/edit_police_profile.html", context=diction)


def view_suspected_info(request):
    suspected = CriminalLocation.objects.all()
    return render(request, "App_main/view_suspected_info.html", context={'suspected': suspected})
