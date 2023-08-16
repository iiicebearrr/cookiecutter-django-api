# Create your tests here.
import json

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory, override_settings
from django.core.exceptions import PermissionDenied

from .models import Blogs
from .views import BlogsView, BlogsEditView, BlogsDetailView, publish_post


class TestBlogsApi(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.user, _ = User.objects.get_or_create(
            username="administrator", password="administrator", is_superuser=True
        )
        self.blog_view = BlogsView.as_view()
        self.blog_edit_view = BlogsEditView.as_view()
        self.blog_detail_view = BlogsDetailView.as_view()
        self.factory = RequestFactory()

    def test_get(self):
        inst = Blogs.objects.create(title="test", content="test", author=self.user)
        response = self.client.get("/api/blogs")
        json_resp = json.loads(response.content)
        count, row = json_resp["data"]["count"], json_resp["data"]["list"][0]
        self.assertEqual(count, 1)
        self.assertEqual(row["id"], inst.id)
        self.assertEqual(row["title"], inst.title)

        # test filter by title, contains and exact query
        Blogs.objects.create(title="test2", content="test2", author=self.user)
        response = self.client.get("/api/blogs", {"title__contains": "test"})
        self.assertEqual(json.loads(response.content)["data"]["count"], 2)
        response = self.client.get("/api/blogs", {"title": "test2"})
        self.assertEqual(json.loads(response.content)["data"]["count"], 1)

    @override_settings(DEBUG=False)
    def test_post(self):
        request = self.factory.post(
            "/api/blogs",
            {
                "title": "test",
                "content": "test",
            },
        )

        # test with anonymous user
        request.user = AnonymousUser()

        with self.assertRaisesRegex(PermissionDenied, "Superuser required"):
            self.blog_view(request)

        # test with superuser
        request.user = self.user
        response = self.blog_view(request)
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["data"]["title"], "test")
        self.assertEqual(json_resp["data"]["content"], "test")

    @override_settings(DEBUG=False)
    def test_put(self):
        inst = Blogs.objects.create(title="test", content="test", author=self.user)

        request = self.factory.put(
            f"/api/blogs/{inst.id}/edit",
            {
                "title": "test-update",
                "content": "test",
            },
            content_type="application/json",
        )

        request.user = self.user

        response = self.blog_edit_view(request, id=inst.id)

        json_resp = json.loads(response.content)

        self.assertEqual(json_resp["data"]["title"], "test-update")

    @override_settings(DEBUG=False)
    def test_delete(self):
        inst = Blogs.objects.create(title="test", content="test", author=self.user)

        request = self.factory.delete(f"/api/blogs/{inst.id}/edit")

        request.user = self.user

        self.blog_edit_view(request, id=inst.id)

        self.assertFalse(Blogs.objects.filter(id=inst.id).exists())

    def test_publish(self):
        inst = Blogs.objects.create(title="test", content="test", author=self.user)

        request = self.factory.post(f"/api/blogs/{inst.id}/publish")

        request.user = self.user

        publish_post(request, id=inst.id)

        self.assertTrue(Blogs.objects.get(id=inst.id).published)
