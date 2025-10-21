from django.forms import ModelForm
from main.models import Community 

class CommunityForm(ModelForm):
    class Meta:
        model = Community
        fields = [community_name, description, location, max_member, contact_person, sports_type, contact_phone, profile_image]

