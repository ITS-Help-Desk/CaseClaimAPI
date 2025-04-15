from django.test import TestCase
from parentcase.models import ParentCase
from django.utils import timezone

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User


class ParentCaseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="connor", password="password123")
        self.case = ParentCase.objects.create(
            case_number="11119999",
            description="Help desk gone",
            solution="Yikes",
            user_id=self.user  # ForeignKey → assign User object
        )

    def test_case_created(self):
        self.assertEqual(self.case.case_number, "11119999")
        self.assertEqual(self.case.description, "Help desk gone")
        self.assertEqual(self.case.solution, "Yikes")
        self.assertEqual(self.case.user_id.username, "connor")  # user_id is the FK field name

    def test_active_default_true(self):
        self.assertTrue(self.case.active)

    def test_time_created_auto(self):
        now = timezone.now()
        self.assertLessEqual(self.case.time_created, now)


class ParentCaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.case1 = ParentCase.objects.create(
            case_number="11111111",
            description="Test Case 1",
            solution="Solution 1",
            user_id=self.user,
            active=True
        )
        self.case2 = ParentCase.objects.create(
            case_number="22222222",
            description="Test Case 2",
            solution="Solution 2",
            user_id=self.user,
            active=False
        )

    def test_get_active_parent_cases(self):
        response = self.client.get('/api/parentcase/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['case_number'], '11111111')

    def test_get_all_parent_cases(self):
        response = self.client.get('/api/parentcase/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_set_inactive_parent_case(self):
        response = self.client.post(f'/api/parentcase/set_inactive/{self.case1.case_number}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case1.refresh_from_db()
        self.assertFalse(self.case1.active)

    def test_create_parent_case(self):
        data = {
            'case_number': '33333333',
            'description': 'Test Case 3',
            'solution': 'Solution 3'
        }
        response = self.client.post('/api/parentcase/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ParentCase.objects.count(), 3)
        new_case = ParentCase.objects.get(case_number='33333333')
        self.assertEqual(new_case.description, 'Test Case 3')
        self.assertEqual(new_case.user_id, self.user)

    def test_update_parent_case(self):
        data = {
            'description': 'Updated description',
            'active': False
        }
        response = self.client.post(f'/api/parentcase/update/{self.case1.case_number}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case1.refresh_from_db()
        self.assertEqual(self.case1.description, 'Updated description')
        self.assertEqual(self.case1.solution, 'Solution 1')
        self.assertFalse(self.case1.active)
