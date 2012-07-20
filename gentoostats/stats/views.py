from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page, cache_control
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.db.models import Q, Min, Max, Count
from django.shortcuts import render, redirect, \
                             get_object_or_404, get_list_or_404

from .util import add_hyphens_to_uuid
from .forms import *
from .models import *

class ImprovedDetailView(DetailView):
    """
    A DetailView subclass that respects 'extra_context'.
    """

    extra_context = dict()
    def get_context_data(self, **kwargs):
        context = super(ImprovedDetailView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

class ImprovedListView(ListView):
    """
    A ListView subclass that respects 'extra_context'.
    """

    extra_context = dict()
    def get_context_data(self, **kwargs):
        context = super(ImprovedListView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

@cache_control(public=True)
@cache_page(1 * 60)
def index(request):
    """
    Index page of Gentoostats.
    """

    return render(request, 'stats/index.html')

@cache_control(public=True)
@cache_page(24 * 60 * 60)
def about(request):
    """
    Project about page.
    """

    return render(request, 'stats/about.html')

@cache_control(public=True)
@cache_page(1 * 60)
def overall_stats(request):
    """
    Show overall stats for the website.
    """

    latest_submission_q = Q(submissions__in=Submission.objects.latest_submission_ids)

    features = Feature.objects.filter(latest_submission_q).annotate(num_hosts_fast=Count('submissions')).order_by('name')
    langs    = Lang.objects.filter(latest_submission_q).annotate(num_hosts_fast=Count('submissions')).order_by('name')
    keywords = Keyword.objects.filter(latest_submission_q).annotate(num_hosts_fast=Count('submissions')).order_by('name')

    context = dict(
        hosts         = Host.objects.all(),
        submissions   = Submission.objects.select_related().order_by('-datetime'),
        country_stats = Submission.objects.latest_submissions.filter(country__isnull=False).values_list('country').annotate(num_hosts=Count('country')).order_by('country'),
        arch_stats    = Submission.objects.latest_submissions.values_list('arch').annotate(num_hosts=Count('arch')).order_by('arch'),
        profile_stats = Submission.objects.latest_submissions.values_list('profile').annotate(num_hosts=Count('profile')).order_by('profile'),

        features = features,
        langs    = langs,
        keywords = keywords,
    )

    return render(request, 'stats/overall_stats.html', context)

@cache_control(public=True)
@cache_page(24 * 60 * 60)
def host_search(request):
    """
    Search for a host by its full UUID.
    """

    if request.method == 'POST':
        form = HostSearchForm(request.POST)
        if form.is_valid():
            return redirect( 'stats:host_details_url'
                           , host_id   = form.cleaned_data['host_id']
                           , permanent = False
            )
    else:
        form = HostSearchForm(
            # initial = dict(host_id='Enter UUID'),
        )

    context = dict(
        form=form,
    )

    return render(request, 'stats/host_search.html', context)

@cache_control(private=True)
@cache_page(1 * 60)
def host_details(request, host_id):
    """
    Show statistics about a certain host.
    """

    # Accept UUIDs with no hyphens and/or with capital letters, but still
    # redirect the user to the 'proper' URL:
    host_id_new = add_hyphens_to_uuid(host_id)
    host_id_new = host_id_new.lower()

    if host_id != host_id_new:
        return redirect( 'stats:host_details_url'
                       , host_id   = host_id_new
                       , permanent = True
        )

    context = dict(
        host = get_object_or_404( Host.objects.select_related('submissions')
                                , id = host_id
        ),
    )

    return render(request, 'stats/host_details.html', context)

@cache_control(public=True)
@cache_page(1 * 60)
def arch_details(request, arch):
    """
    Show more detailed statistics about a specific arch.
    """

    context = dict(
        arch            = arch,
        num_submissions = Submission.objects.filter(arch=arch).count(),
        num_all_hosts   = Submission.objects.filter(arch=arch).order_by().aggregate(Count('host', distinct=True)).values()[0],
        num_hosts       = Submission.objects.latest_submissions.filter(arch=arch).count(),
    )

    return render(request, 'stats/arch_details.html', context)

@cache_control(public=True)
@cache_page(1 * 60)
def keyword_details(request, keyword):
    """
    Show statistics about a particular keyword (e.g. amd64).
    """

    context = dict(
        keyword = get_object_or_404(Keyword, name=keyword),
    )

    return render(request, 'stats/keyword_details.html', context)

@cache_control(public=True)
@cache_page(1 * 60)
def feature_details(request, feature):
    """
    Show statistics about a particular FEATURE.
    """

    context = dict(
        feature = get_object_or_404(Feature, name=feature),
    )

    return render(request, 'stats/feature_details.html', context)

@cache_control(public=True)
@cache_page(1 * 60)
def mirror_stats(request):
    """
    Show statistics about the known mirrors.
    """

    context = dict(
        mirrors = MirrorServer.objects.all()
    )

    return render(request, 'stats/mirror_stats.html', context)

@cache_control(public=True)
@cache_page(1 * 60)
def mirror_details(request, mirror):
    """
    Show more detailed statistics about a specific mirror.
    """

    context = dict(
        mirror = get_object_or_404(MirrorServer, url=mirror)
    )

    return render(request, 'stats/mirror_details.html', context)

@cache_control(public=True)
@cache_page(1 * 60)
def sync_stats(request):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def sync_details(request, sync):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def repository_stats(request):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def repository_details(request, repository):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def category_stats(request):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def category_details(request, category):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def lang_details(request, lang):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

# Submissions: #{{{
class SubmissionDetailView(ImprovedDetailView):
    context_object_name = 'submission'
    queryset = Submission.objects.select_related()
    pk_url_kwarg = 'id'

submission_details = \
    cache_control(private=True) (
        cache_page(1 * 60) (
            SubmissionDetailView.as_view()
        )
    )
#}}}

@cache_control(public=True)
@cache_page(1 * 60)
def useflag_stats(request):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def useflag_details(request, useflag):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')

@cache_control(public=True)
@cache_page(1 * 60)
def profile_details(request, profile):
    """
    TODO: add a description.
    """

    return render(request, 'stats/not_implemented.html')
