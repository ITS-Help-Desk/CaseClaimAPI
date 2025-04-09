from django.test import TestCase
from .models import ParentCase
from django.utils import timezone

class ParentCaseModelTest(TestCase):
    def setUp(self):
        self.case = ParentCase.objects.create(
            case_number="11119999",
            description="Help desk gone",
            solution="Yikes",
            user="connor"
        )

    def test_case_created(self):
        self.assertEqual(self.case.case_number, "11119999")
        self.assertEqual(self.case.description, "Help desk gone")
        self.assertEqual(self.case.solution, "Yikes")
        self.assertEqual(self.case.user, "connor")

    def test_active_default_true(self):
        self.assertTrue(self.case.active)

    def test_time_created_auto(self):
        now = timezone.now()
        self.assertLessEqual(self.case.time_created, now)