from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
from campaigns.models import CampaignRedirect


class CampaignRedirectMiddleware:
    """
    Middleware to handle 301 redirects for old campaign slugs.
    Checks if the requested URL is an old campaign slug and redirects to the new one.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only process 404 responses
        if response.status_code == 404:
            # Check if this is a campaign detail URL pattern
            # Example: /kampanya-slug/ or /kampanya-slug
            path = request.path.strip('/')
            
            # Try to find a redirect for this slug
            try:
                campaign_redirect = CampaignRedirect.objects.select_related('campaign').get(
                    old_slug=path,
                    is_active=True
                )
                # Perform 301 permanent redirect
                new_url = f'/{campaign_redirect.campaign.slug}/'
                return HttpResponsePermanentRedirect(new_url)
            except CampaignRedirect.DoesNotExist:
                pass
        
        return response
