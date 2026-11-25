from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from companies.models import Company, EmployerProfile

User = get_user_model()


class CompanyAndEmployerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.emp_user = User.objects.create_user(
            username="comp_emp",
            email="comp_emp@example.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.other_emp_user = User.objects.create_user(
            username="other_comp_emp",
            email="other_comp_emp@example.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.seeker_user = User.objects.create_user(
            username="comp_seeker",
            email="comp_seeker@example.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )
        self.company = Company.objects.create(
            name="Acme Labs",
            slug="acme-labs",
            industry="Technology",
            location="Bengaluru",
            company_size="51-200",
            created_by=self.emp_user,
        )
        self.emp_profile = EmployerProfile.objects.create(
            user=self.emp_user,
            company=self.company,
            designation="VP Engineering",
            is_company_admin=True,
        )

    def test_public_company_list_and_detail(self):
        """Unauthenticated users can browse companies and view company details."""
        res_list = self.client.get("/api/companies/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)
        self.assertEqual(res_list.data[0]["name"], "Acme Labs")

        res_detail = self.client.get(f"/api/companies/{self.company.slug}/")
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data["industry"], "Technology")

    def test_create_company_permissions_and_admin_assignment(self):
        """Only employers can create a company, and creator automatically gets admin EmployerProfile."""
        payload = {
            "name": "Nova Systems",
            "industry": "FinTech",
            "location": "Hyderabad",
            "company_size": "11-50",
        }
        # Anonymous -> 401
        res_anon = self.client.post("/api/companies/", payload)
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Jobseeker -> 403
        self.client.force_authenticate(user=self.seeker_user)
        res_seeker = self.client.post("/api/companies/", payload)
        self.assertEqual(res_seeker.status_code, status.HTTP_403_FORBIDDEN)

        # Employer -> 201
        self.client.force_authenticate(user=self.other_emp_user)
        res_emp = self.client.post("/api/companies/", payload)
        self.assertEqual(res_emp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_emp.data["name"], "Nova Systems")

        profile = EmployerProfile.objects.get(user=self.other_emp_user)
        self.assertTrue(profile.is_company_admin)
        self.assertEqual(profile.company.name, "Nova Systems")

    def test_only_company_creator_can_update_or_delete(self):
        """Non-owner employer receives 403 when modifying or deleting another user's company."""
        self.client.force_authenticate(user=self.other_emp_user)
        res_patch = self.client.patch(f"/api/companies/{self.company.slug}/", {"location": "Mumbai"})
        self.assertEqual(res_patch.status_code, status.HTTP_403_FORBIDDEN)

        res_delete = self.client.delete(f"/api/companies/{self.company.slug}/")
        self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)

        # Creator succeeds
        self.client.force_authenticate(user=self.emp_user)
        res_owner = self.client.patch(f"/api/companies/{self.company.slug}/", {"location": "Pune"})
        self.assertEqual(res_owner.status_code, status.HTTP_200_OK)
        self.assertEqual(res_owner.data["location"], "Pune")

    def test_employer_profile_retrieve_and_update(self):
        """Employer can read and update their own EmployerProfile."""
        self.client.force_authenticate(user=self.emp_user)
        res_get = self.client.get("/api/employer/profile/")
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data["designation"], "VP Engineering")

        res_patch = self.client.patch("/api/employer/profile/", {"designation": "CTO"})
        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data["designation"], "CTO")

    def test_company_recruiters_list_and_admin_guard(self):
        """Company recruiters endpoint allows listing and restricts adding recruiters to company admins."""
        self.client.force_authenticate(user=self.emp_user)
        res_list = self.client.get(f"/api/companies/{self.company.slug}/recruiters/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)

        # Non-admin employer from same company cannot add recruiters
        non_admin_emp = User.objects.create_user(
            username="non_admin_recruiter", email="nonadmin@example.com", password="StrongPassword123!", user_type="employer"
        )
        EmployerProfile.objects.create(user=non_admin_emp, company=self.company, is_company_admin=False)
        self.client.force_authenticate(user=non_admin_emp)
        res_add = self.client.post(f"/api/companies/{self.company.slug}/recruiters/", {"designation": "HR"})
        self.assertEqual(res_add.status_code, status.HTTP_403_FORBIDDEN)
