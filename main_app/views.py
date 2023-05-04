from django.shortcuts import render, redirect

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
# Create your views here.
from django.http import HttpResponse

import uuid # this helps generate random numbers for naming our files on aws, they all have to be unique names, so we can prepend random numbers to the filename
import boto3 # the aws sdk that allows us to talk to aws s3
from .models import Cat, Toy, Photo
from botocore.exceptions import ClientError

from django.contrib.auth import login # login function accepts a user to log them in
from django.contrib.auth.forms import UserCreationForm

from .forms import FeedingForm

### Authorization tools!
# for a view functions
from django.contrib.auth.decorators import login_required
# for our Class Based Views
from django.contrib.auth.mixins import LoginRequiredMixin




def signup(request):
	# handle the get request, which should return the form
	# handle the POST request, which take the contents of the form, create the user, 
	# and log them in
	error_message = ''
	if request.method == 'POST':
		# create the user object from our form
		# request.POST is like req.body
		form = UserCreationForm(request.POST)
		if form.is_valid():
			# add the user to the database
			user = form.save()
			# login the user
			login(request, user)# this adds the user's id to your session cookie, and 
			# make request.user availiable in all of your view functions
			return redirect('index')
		else: 
			error_message = 'Invalid sign up - try again'
	
	# Here is handling the GET request
	form = UserCreationForm()
	return render(request, 'registration/signup.html', {'error_message': error_message, 'form': form})






###==================================================
### ALERT ==================================================
# write your bucket name!
### IF YOU FETCH UPDATE THIS TO YOUR BUCKET NAME and UPDATE YOUR S3_BASE_URL to yours
BUCKET = 'emilymerrow'
S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com/'
###==================================================
###==================================================

@login_required
def add_photo(request, cat_id):
	# photo-file will be the "name" attribute on the <input name='photo-file' type='file'>
	photo_file = request.FILES.get('photo-file', None)
	if photo_file:
		# setup the aws client 
		s3 = boto3.client('s3')
		# Make a unique name to store the photo			# franklin.png
														# photo_file.name.rfind('.'): this gets us the file exstension .png
			 # store the file in a catcollector folder/randomnumber + the file name with the extension
		key = 'catcollector/' + uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
		try:
			s3.upload_fileobj(photo_file, BUCKET, key)
			# build the url string of where it is hosted to store db
			url = f"{S3_BASE_URL}{BUCKET}/{key}"
			# add it to the db
			Photo.objects.create(url=url, cat_id=cat_id)
		except ClientError as e:
			print(e, " error from aws!")
		
	return redirect('detail', cat_id=cat_id)





# the arguments come from the params in the urls.py
# 'cats/<int:cat_id>/assoc_toy/<int:toy_id>/'
@login_required
def assoc_toy(request, cat_id, toy_id):
	# associating a cat with a toy
	Cat.objects.get(id=cat_id).toys.add(toy_id)

	# One line version of below ^
	# cat = Cat.object.get(id=cat_id)
	# cat.toys.add(toy_id)

	return redirect('detail', cat_id=cat_id)



# cat_id matches the url
# path('cats/<int:cat_id>/add_feeding/'
def add_feeding(request, cat_id):
    # create a modelForm instance using the information from the post request
    # request.POST is like req.body
    form = FeedingForm(request.POST)
    # validate the form
    if form.is_valid():
        # don't want to save it until we add the cat_id to the feeding
        new_feeding = form.save(commit=False)
        # tying the cat to the feeding
        # defining the FK
        new_feeding.cat_id = cat_id
        new_feeding.save()
        # import redirect on the top line from django.shortcuts
    return redirect('detail', cat_id=cat_id)

# Handles GET AND POST of the form
# The form expectations is templates/<name_of_app>/<model_form.html
# templates/main_app/cat_form.html
# CBV class based view


class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    # fields says what fields on our model should be included in the form
    fields = ['name', 'breed', 'description', 'age']  # all the fields
    # fields = ['breed', 'description', 'age'] # you can choose the fields
    # from your model if you don't want to include every field
    # success_url = '/cats/' # redirect to the list page
    #inherited method from CreateView
    def form_valid(self, form):
        # assing the logged in user (self.request.user)
        # to the the form instance that is being submitted when we 
        # send a post request ot the server
        form.instance.user = self.request.user
        # Let the createview do the rest of its job
        return super().form_valid(form)


# The form expectations is templates/<name_of_app>/<model_form.html
# templates/main_app/cat_form.html
# Same form as the create!
class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    # disallow the name as input on the form, so no one can update the name
    fields = ['breed', 'description', 'age']

# templates/<name_of_app>/<model>_confirm_delete.html
# templates/main_app/cat_confirm_delete.html


class CatDelete(DeleteView):
    model = Cat
    # since we can't redirect to a detail page of a cat we deleted
    success_url = '/cats/'

@login_required
def cats_index(request):

    # key 'cats' will be the variable name in the cats/index.html
    # cats will be the array that we are storing in the 'cats' variable
    cats = Cat.objects.filter(user=request.user)  # finding all the cats from the database!
    return render(request, 'cats/index.html', {'cats': cats})

# path('cats/<int:cat_id>/', views.cats_detail, name='detail'), <- urls.py
# <int: cat_id> that must be the argument to your detail function
# cat_id is the param


def cats_detail(request, cat_id):
    # find the cat with the id that was in the params in the db
    cat = Cat.objects.get(id=cat_id)
    # Find all the toys not in the cat.toys.all() array

    # cat.toys.all().values_list('id') <- this finds all the cats toys and returns a list
    # of just their id's
    #  Find all toys that are not in the cat.toys id list
	# id__in <- Field Look up, theser for complicated queries 
    toys_cat_doesnt_have = Toy.objects.exclude(
        id__in=cat.toys.all().values_list('id'))

    # creating a form (instance) from our FeedingForm class!
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {
		'cat': cat, 
		'feeding_form': feeding_form, 
		'toys': toys_cat_doesnt_have
	})


def home(request):
    return render(request, 'home.html')


def about(request):
    # django is configured to know automatically
    # to look inside of a templates folder for the html files
    return render(request, 'about.html')


class ToyList(ListView):
    model = Toy


class ToyDetail(DetailView):
    model = Toy


class ToyCreate(CreateView):
    model = Toy
    fields = '__all__'


class ToyUpdate(UpdateView):
    model = Toy
    fields = ['name', 'color']


class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys/'
