
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from .models import UserProfile, Link, Vote
from .forms import UserProfileForm, LinkForm, VoteForm
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.shortcuts import redirect, get_object_or_404
import json
from django.http import HttpResponse

class LinkListView(ListView):
	model = Link
	queryset = Link.with_votes.all()
	paginate_by = 5

	def get_context_data(self, **kwargs):
		context = super(LinkListView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			voted = Vote.objects.filter(voter=self.request.user)
			links_in_page = [link.id for link in context["object_list"]]
			voted = voted.filter(link_id__in=links_in_page)
			voted = voted.values_list('link_id', flat=True)
			context["voted"] = voted
		return context

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


class JSONFormMixin(object):
	def create_response(self, vdict=dict(), valid_form=True):
		response = HttpResponse(json.dumps(vdict), content_type='application/json')
		response.status=200 if valid_form else 500
		return response

class VoteFormBaseView(FormView):
	form_class = VoteForm

	def create_response(self, vdict=dict(), valid_form=True):
		response = HttpResponse(json.dumps(vdict))
		response.status=200 if valid_form else 500
		return response


	def form_valid(self, form):
		print("form_valid")
		link = get_object_or_404(Link, pk=form.data["link"])
		user = self.request.user
		prev_votes = Vote.objects.filter(voter=user, link=link)
		has_voted = (prev_votes).count() > 0

		ret = {"success":1}

		if not has_voted:
			#add vote
			v = Vote.objects.create(voter=user, link=link)
			ret["voteobj"] = v.id
			print("voted !")
		else:
			#delete vote
			prev_votes[0].delete()
			ret["unvoted"] = 1
			print("unvoted !")

		return self.create_response(ret, True)

	def form_invalid(self, form):
		ret = {"success":0, "form_errors":form.errors}
		return self.create_response(ret, False)

class VoteFormView(JSONFormMixin, VoteFormBaseView):
	pass		
		