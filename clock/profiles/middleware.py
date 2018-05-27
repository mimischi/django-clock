from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.middleware.locale import LocaleMiddleware
from django.utils import translation

from clock.profiles.models import UserProfile


class LocaleMiddlewareExtended(LocaleMiddleware):
    """This middleware extends Djangos normal LocaleMiddleware and looks for the
    language preferred by the user.

    Normally only the current session is searched for the preferred language,
    but the user may want to define it in his profile. This solves the problem
    and therefore keeps the set language across logouts/different devices.
    """

    def get_language_for_user(self, request):
        if request.user.is_authenticated:
            try:
                account = UserProfile.objects.get(user=request.user)
                return account.language
            except UserProfile.DoesNotExist:
                pass
        return translation.get_language_from_request(
            request, check_path=is_language_prefix_patterns_used
        )

    def process_request(self, request):
        language = self.get_language_for_user(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
