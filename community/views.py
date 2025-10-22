from django.shortcuts import render, redirect, get_object_or_404
# from community.forms import CommunityForm
from community.models import Community
from django.http import HttpResponse
from django.core import serializers


def show_community_page(request):
    communities = Community.objects.all()
    context = {
        'communities': communities,
        'show_navbar': True  # Menambahkan konteks untuk menampilkan navbar
    }
    
    return render(request, 'community.html', context)

def community_detail(request, pk):
    community = get_object_or_404(Community, pk=pk)
    communities = Community.objects.exclude(pk=pk)  # biar gak nampilin dirinya sendiri

    context = {
        'community': community,
        'communities': communities,
        'show_navbar': True  # Menambahkan konteks untuk menampilkan navbar
    }
    return render(request, 'community_detail.html', context)

def search_communities(request):
    query = request.GET.get('q')
    if query:
        communities = Community.objects.filter(community_name__icontains=query)
    else:
        communities = Community.objects.all()
    return render(request, 'community.html', {'communities': communities})

def filter_communities_by_sport(request, sport_type):
    communities = Community.objects.filter(sports_type=sport_type)
    return render(request, 'community.html', {'communities': communities})

def join_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    if community.member_count < community.max_member:
        community.member_count += 1
        community.save()
        return redirect('community_detail', pk=community.pk)
    else:
        return render(request, 'community.html', {'community': community})

def show_xml(request):
    data = serializers.serialize("xml", Community.objects.all())
    return HttpResponse(data, content_type="application/xml")

def show_json(request):
    data = serializers.serialize("json", Community.objects.all())
    return HttpResponse(data, content_type="application/json")

def show_xml_by_id(request, id):
    data = serializers.serialize("xml", Community.objects.filter(pk=id))
    return HttpResponse(data, content_type="application/xml")

def show_json_by_id(request, id):
    data = serializers.serialize("json", Community.objects.filter(pk=id))
    return HttpResponse(data, content_type="application/json")