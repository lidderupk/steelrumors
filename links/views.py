
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from .models import UserProfile, Link
from .forms import UserProfileForm, LinkForm
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, DeleteView

class LinkListView(ListView):
	model = Link
	queryset = Link.with_votes.all()
	paginate_by = 5

class UserProfileDetailView(DetailView):
	model = get_user_model()
	#key that is used to look up the model
	slug_field = "username"	
	template_name = "user_detail.html"

	def get_object(self, queryset=None):
		user = super(UserProfileDetailView, self).get_object(queryset)
		UserProfile.objects.get_or_create(user=user)
		return user

class UserProfileEditView(UpdateView):
	model = UserProfile
	template_name = "edit_profile.html"
	form_class = UserProfileForm

	def get_object(self, queryset=None):
		return UserProfile.objects.get_or_create(user = self.request.user)[0]

	def get_success_url(self):
		return reverse("profile", kwargs={"slug":self.request.user})

class LinkCreateView(CreateView):
	model = Link
	form_class = LinkForm

	def form_valid(self, form):
		f = form.save(commit=False)
		f.rank_score = 0.0
		f.submitter = self.request.user
		f.save()
		return super(LinkCreateView, self).form_valid(form)

class LinkDetailView(DetailView):
	model = Link

class LinkUpdateView(UpdateView):
	model = Link
	form_class = LinkForm

class LinkDeleteView(DeleteView):
	model = Link
	success_url = reverse_lazy("home")
