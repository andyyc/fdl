from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from league.models import GeneralManager


@login_required
def gm_home(request):
    gm = GeneralManager.objects.get(user=request.user)
    leagues = gm.league_set.all()
    return render_to_response("gm/gm_home.html", 
                              {'gm':gm,
                               'leagues':leagues},
                              context_instance=RequestContext(request))

