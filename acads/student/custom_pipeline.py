# from allauth.socialaccount.models import SocialAccount
#
#
# def validate_email_format(request, sociallogin, **kwargs):
#     email = sociallogin.account.extra_data.get('email', '')
#     if not email.endswith('@pilani.bits-pilani.ac.in'):
#         raise Exception("Only students with BITS Pilani email addresses are allowed to log in.")
