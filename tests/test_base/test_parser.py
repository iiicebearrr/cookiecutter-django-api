from django.test import TestCase, RequestFactory
from django.conf import settings
from base.file_handler.parser import StreamFileParser, OssFileParser
from django.core.files.base import File


class TestParser(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.file = settings.BASE_DIR / "tests" / "test.txt"
        self.file_content = "Test file"
        self.file.write_text(self.file_content)

    def test_stream_parser(self):
        request = self.factory.post("/")
        request.FILES["file"] = File(self.file.open("rb"), name=self.file.name)
        parser = StreamFileParser(request)

        f = parser.parse()

        self.assertEqual(b"".join(list(f)).decode(), self.file_content)
        self.file.unlink()

    def test_oss_parser(self):
        pass
