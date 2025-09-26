from django.conf import settings


class FormsValidator:
    """
    Provides access to settings for ignored classes and validation behavior.
    """
    def __init__(self):
        self.ignored_classes = settings.IGNORED_CLASSES
        self.ignore_validation = settings.IGNORE_VALIDATION
        self.validate_only_on_submit = settings.VALIDATE_ONLY_ON_SUBMIT

    def get_context(self):
        """
        Returns a dictionary for use in template contexts
        """
        return {
            'ignored_classes': self.ignored_classes,
            'ignore_validation': self.ignore_validation,
            'validate_only_on_submit': self.validate_only_on_submit
        }