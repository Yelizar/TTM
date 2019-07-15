from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):

    def tutor_list(self):
        """
        Return a list of tutors with status TutorStatus object is_active=true
        """
        return self.filter(tutorstatus__is_active=True)
