from django.test import TestCase

from articles.models import Article, Catalog, Comment
from articles.views import _article_to_dict


class ArticleSerializationTest(TestCase):
    def test_article_serialization(self):
        a = Article(id=1, title="Заголовок", text="Текст", rate=5)
        d = {"id": a.id, "title": a.title, "text": a.text, "rate": a.rate}
        self.assertEqual(d["title"], "Заголовок")
        self.assertEqual(d["rate"], 5)


class CatalogModelTest(TestCase):
    def test_catalog_creation(self):
        catalog = Catalog.objects.create(name="Электроника")
        self.assertEqual(str(catalog), "Электроника")

    def test_catalog_list_view(self):
        Catalog.objects.create(name="Книги")
        response = self.client.get("/catalog/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Книги")


class ArticlesListAPITest(TestCase):
    def test_articles_list_empty(self):
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_articles_list_with_data(self):
        Article.objects.create(title="A", text="ta", rate=1)
        Article.objects.create(title="B", text="tb", rate=2)
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertIn("id", data[0])
        self.assertIn("title", data[0])
        self.assertIn("created_at", data[0])

    def test_articles_list_post_not_allowed(self):
        response = self.client.post("/api/articles/")
        self.assertEqual(response.status_code, 405)


class ArticleDetailAPITest(TestCase):
    def test_article_detail_found(self):
        a = Article.objects.create(title="Тест", text="Текст", rate=3)
        response = self.client.get(f"/api/articles/{a.pk}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], a.pk)
        self.assertEqual(data["title"], "Тест")
        self.assertEqual(data["rate"], 3)

    def test_article_detail_not_found(self):
        response = self.client.get("/api/articles/999/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Not found"})


class CommentModelTest(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="Статья", text="Текст статьи", rate=10)

    def test_comment_creation_and_ordering(self):
        c1 = Comment.objects.create(article=self.article, author_name="Иван", text="Первый коммент")
        c2 = Comment.objects.create(article=self.article, author_name="Анна", text="Второй коммент")
        comments = list(self.article.comments.all())
        self.assertEqual(comments, [c1, c2])
        self.assertIn("Иван", str(c1))

    def test_comment_cascade_delete(self):
        Comment.objects.create(article=self.article, author_name="Иван", text="Первый коммент")
        self.assertEqual(Comment.objects.count(), 1)
        self.article.delete()
        self.assertEqual(Comment.objects.count(), 0)


class ArticleDetailViewTest(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="Заголовок статьи", text="Контент статьи", rate=5)

    def test_article_detail_view_success_empty_comments(self):
        response = self.client.get(f"/articles/{self.article.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заголовок статьи")
        self.assertContains(response, "Комментариев пока нет. Будьте первым!")

    def test_article_detail_view_with_comments(self):
        Comment.objects.create(article=self.article, author_name="Алексей", text="Отличный пост")
        response = self.client.get(f"/articles/{self.article.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Алексей")
        self.assertContains(response, "Отличный пост")
        self.assertNotContains(response, "Комментариев пока нет. Будьте первым!")

    def test_article_detail_view_404(self):
        response = self.client.get("/articles/999/")
        self.assertEqual(response.status_code, 404)


class AddCommentViewTest(TestCase):
    def setUp(self):
        self.article = Article.objects.create(title="Тестовая статья", text="Текст", rate=0)

    def test_add_comment_get_method_not_allowed(self):
        response = self.client.get(f"/articles/{self.article.pk}/comment/")
        self.assertEqual(response.status_code, 405)

    def test_add_comment_post_success(self):
        data = {
            "author_name": "Тестировщик",
            "text": "Это тестовый комментарий.",
        }
        response = self.client.post(f"/articles/{self.article.pk}/comment/", data)
        self.assertRedirects(response, f"/articles/{self.article.pk}/")
        self.assertEqual(self.article.comments.count(), 1)
        comment = self.article.comments.first()
        self.assertEqual(comment.author_name, "Тестировщик")
        self.assertEqual(comment.text, "Это тестовый комментарий.")
        self.assertEqual(comment.article, self.article)

    def test_add_comment_post_invalid_renders_errors(self):
        data = {"author_name": "Тестировщик", "text": ""}
        response = self.client.post(f"/articles/{self.article.pk}/comment/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.comments.count(), 0)
        self.assertContains(response, "Обязательное поле")

    def test_add_comment_post_article_not_found(self):
        data = {"author_name": "Тестировщик", "text": "Текст"}
        response = self.client.post("/articles/999/comment/", data)
        self.assertEqual(response.status_code, 404)

