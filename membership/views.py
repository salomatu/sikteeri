# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm

from models import *
from forms import MembershipForm

def new_application(request, template_name='membership/new_application.html'):
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = form.save()
            billing_cycle = BillingCycle(membership=membership)
            billing_cycle.save() # Creating an instance does not touch db and we need and id for the Bill
            bill = Bill(cycle=billing_cycle)
            bill.save()
            bill.send_as_email()
    else:
        form = MembershipForm()

    return render_to_response(template_name, {"form": form},
                              context_instance=RequestContext(request))

def check_alias_availability(request):
    pass

@login_required # XXX Replace with a generic view in URLconf
def membership_list(request, template_name='membership/membership_list.html'):
    return render_to_response(template_name, {'members': Membership.objects.all()},
                              context_instance=RequestContext(request))

@login_required # XXX Replace this too
def membership_list_new(request, template_name='membership/membership_list.html'):
    return render_to_response(template_name,
        {'members': Membership.objects.filter(status__exact='N')},
        context_instance=RequestContext(request))

@login_required
def membership_edit_inline(request, id, template_name='membership/membership_edit_inline.html'):
    membership = get_object_or_404(Membership, id=id)

    # XXX: I hate this. Wasn't there a shortcut for creating a form from instance?
    class Form(ModelForm):
        class Meta:
            model = Membership

    if request.method == 'POST':
        form = Form(request.POST, instance=membership)
        if form.is_valid():
            form.save()
    else:
        form =  Form(instance=membership)
    return render_to_response(template_name, {'form': form, 'membership': membership},
                                  context_instance=RequestContext(request))

def membership_edit(request, id, template_name='membership/membership_edit.html'):
    # XXX: Inline template name is hardcoded in template :/
    return membership_edit_inline(request, id, template_name)