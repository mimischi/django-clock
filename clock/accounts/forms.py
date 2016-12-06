from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField


class ClockSignUpForm(SignupForm):
    captcha = ReCaptchaField()
