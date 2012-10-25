from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from chat.chatdemo import ChatSocketHandler
from league.models import League

# Create your views here.
@login_required
def league_chat(request, lid):
    try:
        league = League.objects.get(lid=lid)
    except ObjectDoesNotExist:
        raise Http404

    return render_to_response("league/league_chat.html",
                              {'messages':ChatSocketHandler.cache,
                               'league':league,},
                              context_instance=RequestContext(request))
