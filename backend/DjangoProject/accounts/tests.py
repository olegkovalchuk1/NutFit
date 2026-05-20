from django.test import TestCase
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AdminPanelTest(TestCase):
    def setUp(self):
        # 1. Створюємо тестового суперкористувача
        self.username = 'admin_test'
        self.password = 'password123'
        self.user = User.objects.create_superuser(
            username=self.username, 
            email='test@test.com', 
            password=self.password
        )
        self.client = Client()

    def test_admin_login_page_exists(self):
        # Перевірка, чи сторінка логіну адмінки взагалі відкривається
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302) # Має бути редирект на логін

    def test_admin_login_success(self):
        # Тестуємо вхід під адміном
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django administration")

    def test_app_is_registered_in_admin(self):
        # Перевірка, чи додаток видно в адмінці
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, "Authentication and Authorization")