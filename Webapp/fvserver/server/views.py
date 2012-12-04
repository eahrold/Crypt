from models import *
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext, Template, Context
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse, Http404
from django.contrib.auth.models import Permission, User
from django.conf import settings
from django.shortcuts import render_to_response
# Create your views here.

##index view
@login_required 
def index(request):
    #show table with all the keys
    computers = Computer.objects.all()
    c = {'user': request.user, 'computers':computers, }
    return render_to_response('server/index.html', c, context_instance=RequestContext(request)) 

##checkin view
@csrf_exempt
def checkin(request):
    try:
        serial_num = request.POST['serial']
    except:
        raise Http404
    try:
        recovery_pass = request.POST['recovery_password']
    except:
        raise Http404
    try:
        #try to find the computer
        computer = get_object_or_404(Computer, serial__iexact=serial_num)
    except:
        ##we couldn't find the computer, get it's subnet out of the passed ip
        subnet = ip.rpartition('.')[0] + ".0"
        ##find if there are any subnets with this IP address
        try:
            network = get_object_or_404(Network, network=subnet)
        except:
            raise Http404
        ##get the next name of from the group - if it's not blank carry on
        new_name = next_name(network.computergroup)
        if new_name == "":
            raise Http404
        else:
            ##if there are, create a new computer in that group with the serial
            computer = Computer(name=new_name, serial=serial_num, computergroup=network.computergroup)
            computer.save()
    computer = Computer(recovery_key=recovery_pass, serial=serial_num, last_checkin = datetime.now())
    computer.save()
    
    c ={'revovery_password':computer.recovery_key, 'serial':computer.serial, 'domain':group.domain, }
    return HttpResponse(simplejson.dumps(c), mimetype="application/json")
        