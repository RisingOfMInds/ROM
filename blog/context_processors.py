from django.conf import settings  # import the settings file


def config(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'G_ANALYTICS': settings.G_ANALYTICS}
