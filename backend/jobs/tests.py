from decimal import Decimal
from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import JobSeekerProfile, Skill
from applications.models import Application
from companies.models import Company, EmployerProfile
from jobs.models import Job, JobCategory, SavedJob

User = get_user_model()


class JobOrderingSecurityTests(TestCase):
    """Verify strict ordering whitelist and protection against FieldError 500s / internal field probing."""

    def setUp(self):
        self.client = APIClient()
        self.emp_user = User.objects.create_user(
            username="job_order_emp",
            email="job_order_emp@example.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.company = Company.objects.create(name="Order Corp", slug="order-corp", created_by=self.emp_user)
        self.emp_profile = EmployerProfile.objects.create(user=self.emp_user, company=self.company, is_company_admin=True)
        self.category = JobCategory.objects.create(name="Software", slug="software")

        self.job_alpha = Job.objects.create(
            title="Alpha Engineer",
            slug="alpha-engineer",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Alpha role",
            responsibilities="Build alpha",
            job_type="full-time",
            salary_min=Decimal("100000.00"),
            views_count=10,
            status="published",
        )
        self.job_zeta = Job.objects.create(
            title="Zeta Engineer",
            slug="zeta-engineer",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Zeta role",
            responsibilities="Build zeta",
            job_type="full-time",
            salary_min=Decimal("300000.00"),
            views_count=50,
            status="published",
        )
        self.job_beta = Job.objects.create(
            title="Beta Engineer",
            slug="beta-engineer",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Beta role",
            responsibilities="Build beta",
            job_type="full-time",
            salary_min=Decimal("200000.00"),
            views_count=30,
            status="published",
        )

    def test_valid_ordering_by_salary_min(self):
        """Whitelisted salary_min ascending and descending ordering works."""
        res_asc = self.client.get("/api/jobs/?ordering=salary_min")
        self.assertEqual(res_asc.status_code, status.HTTP_200_OK)
        titles_asc = [j["title"] for j in res_asc.data["results"]]
        self.assertEqual(titles_asc, ["Alpha Engineer", "Beta Engineer", "Zeta Engineer"])

        res_desc = self.client.get("/api/jobs/?ordering=-salary_min")
        self.assertEqual(res_desc.status_code, status.HTTP_200_OK)
        titles_desc = [j["title"] for j in res_desc.data["results"]]
        self.assertEqual(titles_desc, ["Zeta Engineer", "Beta Engineer", "Alpha Engineer"])

    def test_valid_ordering_by_title_and_views_count(self):
        """Whitelisted title and views_count ordering works as expected."""
        res_title = self.client.get("/api/jobs/?ordering=title")
        self.assertEqual(res_title.status_code, status.HTTP_200_OK)
        self.assertEqual([j["title"] for j in res_title.data["results"]], ["Alpha Engineer", "Beta Engineer", "Zeta Engineer"])

        res_views = self.client.get("/api/jobs/?ordering=-views_count")
        self.assertEqual(res_views.status_code, status.HTTP_200_OK)
        self.assertEqual([j["title"] for j in res_views.data["results"]], ["Zeta Engineer", "Beta Engineer", "Alpha Engineer"])

    def test_invalid_ordering_param_falls_back_safely_without_500(self):
        """Passing ?ordering=foo does NOT raise FieldError 500 and falls back to default ordering."""
        default_res = self.client.get("/api/jobs/")
        invalid_res = self.client.get("/api/jobs/?ordering=foo")
        self.assertEqual(invalid_res.status_code, status.HTTP_200_OK)
        self.assertEqual([j["id"] for j in invalid_res.data["results"]], [j["id"] for j in default_res.data["results"]])

    def test_internal_related_field_ordering_blocked(self):
        """Probing internal/sensitive fields via ?ordering=posted_by__user__password is rejected/ignored."""
        default_res = self.client.get("/api/jobs/")
        for payload in ["posted_by__user__password", "-posted_by__user__email", "id", "company__created_by__password"]:
            res = self.client.get(f"/api/jobs/?ordering={payload}")
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual([j["id"] for j in res.data["results"]], [j["id"] for j in default_res.data["results"]])


class JobLifecycleAndPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.emp_user = User.objects.create_user(
            username="job_emp", email="job_emp@example.com", password="StrongPassword123!", user_type="employer"
        )
        self.other_emp_user = User.objects.create_user(
            username="other_job_emp", email="other_job_emp@example.com", password="StrongPassword123!", user_type="employer"
        )
        self.seeker_user = User.objects.create_user(
            username="job_seeker", email="job_seeker@example.com", password="StrongPassword123!", user_type="jobseeker"
        )
        self.seeker_profile = JobSeekerProfile.objects.create(user=self.seeker_user, full_name="Seeker One")

        self.company = Company.objects.create(name="Job Corp", slug="job-corp", created_by=self.emp_user)
        self.emp_profile = EmployerProfile.objects.create(user=self.emp_user, company=self.company, is_company_admin=True)
        self.other_emp_profile = EmployerProfile.objects.create(user=self.other_emp_user, company=self.company)
        self.category = JobCategory.objects.create(name="Engineering", slug="engineering")
        self.skill = Skill.objects.create(name="Python")

        self.published_job = Job.objects.create(
            title="Backend Developer",
            slug="backend-developer",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Django APIs",
            responsibilities="Build APIs",
            job_type="full-time",
            is_remote=True,
            salary_min=Decimal("120000.00"),
            status="published",
        )
        self.draft_job = Job.objects.create(
            title="Secret Draft Role",
            slug="secret-draft-role",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Unpublished",
            responsibilities="TBD",
            job_type="full-time",
            status="draft",
        )

    def test_only_published_jobs_visible_publicly(self):
        res = self.client.get("/api/jobs/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        slugs = [j["slug"] for j in res.data["results"]]
        self.assertIn("backend-developer", slugs)
        self.assertNotIn("secret-draft-role", slugs)

    def test_job_listing_pagination_page_size_20(self):
        """Published jobs endpoint paginates at 20 items per page using PageNumberPagination."""
        for idx in range(24):
            Job.objects.create(
                title=f"Paginated Role {idx}",
                slug=f"paginated-role-{idx}",
                company=self.company,
                posted_by=self.emp_profile,
                category=self.category,
                description="Desc",
                responsibilities="Resp",
                job_type="full-time",
                status="published",
            )

        res_p1 = self.client.get("/api/jobs/")
        self.assertEqual(res_p1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_p1.data["count"], 25)
        self.assertEqual(len(res_p1.data["results"]), 20)
        self.assertIsNotNone(res_p1.data["next"])
        self.assertIsNone(res_p1.data["previous"])

        res_p2 = self.client.get("/api/jobs/?page=2")
        self.assertEqual(res_p2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_p2.data["count"], 25)
        self.assertEqual(len(res_p2.data["results"]), 5)
        self.assertIsNone(res_p2.data["next"])
        self.assertIsNotNone(res_p2.data["previous"])

        res_invalid = self.client.get("/api/jobs/?page=99")
        self.assertEqual(res_invalid.status_code, status.HTTP_404_NOT_FOUND)

    def test_job_creation_permissions(self):
        payload = {
            "title": "DevOps Engineer",
            "category": self.category.id,
            "description": "Manage cloud infra",
            "responsibilities": "CI/CD and Kubernetes",
            "job_type": "full-time",
            "status": "published",
        }
        # Unauthenticated -> 401
        res_anon = self.client.post("/api/jobs/", payload)
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Jobseeker -> 403
        self.client.force_authenticate(user=self.seeker_user)
        res_seeker = self.client.post("/api/jobs/", payload)
        self.assertEqual(res_seeker.status_code, status.HTTP_403_FORBIDDEN)

        # Employer -> 201
        self.client.force_authenticate(user=self.emp_user)
        res_emp = self.client.post("/api/jobs/", payload)
        self.assertEqual(res_emp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_emp.data["title"], "DevOps Engineer")

    def test_only_posting_employer_can_modify_or_delete_job(self):
        self.client.force_authenticate(user=self.other_emp_user)
        res_patch = self.client.patch(f"/api/jobs/{self.published_job.slug}/", {"title": "Hijacked"})
        self.assertEqual(res_patch.status_code, status.HTTP_403_FORBIDDEN)

        res_del = self.client.delete(f"/api/jobs/{self.published_job.slug}/")
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

        # Owner can update
        self.client.force_authenticate(user=self.emp_user)
        res_owner = self.client.patch(f"/api/jobs/{self.published_job.slug}/", {"title": "Senior Backend Developer"})
        self.assertEqual(res_owner.status_code, status.HTTP_200_OK)
        self.assertEqual(res_owner.data["title"], "Senior Backend Developer")

    def test_job_detail_increments_views_count(self):
        cache.clear()
        initial_views = self.published_job.views_count
        res = self.client.get(f"/api/jobs/{self.published_job.slug}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.published_job.refresh_from_db()
        self.assertEqual(self.published_job.views_count, initial_views + 1)

    def test_job_detail_dedupes_refreshes_and_ignores_bots(self):
        """Atomic views_count skips bots/crawlers and deduplicates rapid refreshes per user/IP."""
        cache.clear()
        start_views = self.published_job.views_count

        # Bot request should not increment
        res_bot = self.client.get(
            f"/api/jobs/{self.published_job.slug}/",
            HTTP_USER_AGENT="Googlebot/2.1 (+http://www.google.com/bot.html)",
            HTTP_X_FORWARDED_FOR="198.51.100.1",
        )
        self.assertEqual(res_bot.status_code, status.HTTP_200_OK)
        self.published_job.refresh_from_db()
        self.assertEqual(self.published_job.views_count, start_views)

        # First human view from IP A increments by 1
        res_human1 = self.client.get(
            f"/api/jobs/{self.published_job.slug}/",
            HTTP_USER_AGENT="Mozilla/5.0",
            HTTP_X_FORWARDED_FOR="198.51.100.10",
        )
        self.assertEqual(res_human1.status_code, status.HTTP_200_OK)
        self.published_job.refresh_from_db()
        self.assertEqual(self.published_job.views_count, start_views + 1)

        # Refresh from same IP A does NOT increment again
        res_refresh = self.client.get(
            f"/api/jobs/{self.published_job.slug}/",
            HTTP_USER_AGENT="Mozilla/5.0",
            HTTP_X_FORWARDED_FOR="198.51.100.10",
        )
        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)
        self.published_job.refresh_from_db()
        self.assertEqual(self.published_job.views_count, start_views + 1)

        # Authenticated user view increments once and dedupes refreshes
        self.client.force_authenticate(user=self.seeker_user)
        self.client.get(f"/api/jobs/{self.published_job.slug}/", HTTP_USER_AGENT="Mozilla/5.0")
        self.client.get(f"/api/jobs/{self.published_job.slug}/", HTTP_USER_AGENT="Mozilla/5.0")
        self.published_job.refresh_from_db()
        self.assertEqual(self.published_job.views_count, start_views + 2)

    def test_job_delete_soft_closes_and_preserves_applications(self):
        """DELETE /api/jobs/<slug>/ sets status='closed' instead of cascading/deleting applications."""
        app = Application.objects.create(job=self.published_job, applicant=self.seeker_profile, status="applied")

        self.client.force_authenticate(user=self.emp_user)
        res_close = self.client.delete(f"/api/jobs/{self.published_job.slug}/")
        self.assertEqual(res_close.status_code, status.HTTP_200_OK)
        self.assertEqual(res_close.data["status"], "closed")

        # Job & application still exist in DB
        self.published_job.refresh_from_db()
        self.assertEqual(self.published_job.status, "closed")
        self.assertTrue(Application.objects.filter(pk=app.pk).exists())

        # Closed job excluded from public /api/jobs/ listing
        res_list = self.client.get("/api/jobs/")
        self.assertNotIn(self.published_job.slug, [j["slug"] for j in res_list.data["results"]])

        # Closing an already closed job returns 400
        res_again = self.client.delete(f"/api/jobs/{self.published_job.slug}/")
        self.assertEqual(res_again.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_and_unsave_job_flow(self):
        self.client.force_authenticate(user=self.seeker_user)
        res_save = self.client.post(f"/api/jobs/{self.published_job.slug}/save/")
        self.assertEqual(res_save.status_code, status.HTTP_201_CREATED)

        # Duplicate save rejected
        res_dup = self.client.post(f"/api/jobs/{self.published_job.slug}/save/")
        self.assertEqual(res_dup.status_code, status.HTTP_400_BAD_REQUEST)

        # List saved jobs
        res_list = self.client.get("/api/jobs/saved/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)

        # Unsave job
        res_unsave = self.client.delete(f"/api/jobs/{self.published_job.slug}/unsave/")
        self.assertEqual(res_unsave.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SavedJob.objects.filter(jobseeker=self.seeker_profile, job=self.published_job).exists())
