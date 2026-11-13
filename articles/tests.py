from django.contrib.auth.models import User
from django.test import TestCase

from articles.forms import CommentForm
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
        self.user1 = User.objects.create_user(username="ivan", password="password")
        self.user2 = User.objects.create_user(username="anna", password="password")
        self.article = Article.objects.create(title="Статья", text="Текст статьи", rate=10)

    def test_comment_creation_and_ordering(self):
        c1 = Comment.objects.create(article=self.article, user=self.user1, text="Первый коммент")
        c2 = Comment.objects.create(article=self.article, user=self.user2, text="Второй коммент")
        comments = list(self.article.comments.all())
        self.assertEqual(comments, [c1, c2])
        self.assertIn("ivan", str(c1))

    def test_comment_cascade_delete(self):
        Comment.objects.create(article=self.article, user=self.user1, text="Первый коммент")
        self.assertEqual(Comment.objects.count(), 1)
        self.article.delete()
        self.assertEqual(Comment.objects.count(), 0)


class ArticleDetailViewTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="commenter", password="password")
        self.other_user = User.objects.create_user(username="stranger", password="password")
        self.article = Article.objects.create(title="Заголовок статьи", text="Контент статьи", rate=5)
        self.comment = Comment.objects.create(
            article=self.article, user=self.author, text="Отличный пост"
        )

    def test_article_detail_view_anonymous(self):
        response = self.client.get(f"/articles/{self.article.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заголовок статьи")
        self.assertContains(response, "commenter")
        self.assertContains(response, "Отличный пост")
        self.assertNotContains(response, "Редактировать")
        self.assertNotContains(response, "Удалить")
        self.assertContains(response, "Оставлять комментарии могут только авторизованные")

    def test_article_detail_view_author_sees_actions(self):
        self.client.force_login(self.author)
        response = self.client.get(f"/articles/{self.article.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Редактировать")
        self.assertContains(response, "Удалить")
        self.assertContains(response, "Отправить комментарий")

    def test_article_detail_view_other_user_does_not_see_actions(self):
        self.client.force_login(self.other_user)
        response = self.client.get(f"/articles/{self.article.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Редактировать")
        self.assertNotContains(response, "Удалить")

    def test_article_detail_view_404(self):
        response = self.client.get("/articles/999/")
        self.assertEqual(response.status_code, 404)


class AddCommentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="writer", password="password")
        self.article = Article.objects.create(title="Тестовая статья", text="Текст", rate=0)

    def test_add_comment_anonymous_redirects(self):
        response = self.client.post(
            f"/articles/{self.article.pk}/comment/",
            {"text": "Попытка анонимного комментария"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article.comments.count(), 0)

    def test_add_comment_get_method_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(f"/articles/{self.article.pk}/comment/")
        self.assertEqual(response.status_code, 405)

    def test_add_comment_post_success(self):
        self.client.force_login(self.user)
        data = {"text": "Это тестовый комментарий."}
        response = self.client.post(f"/articles/{self.article.pk}/comment/", data)
        self.assertRedirects(response, f"/articles/{self.article.pk}/")
        self.assertEqual(self.article.comments.count(), 1)
        comment = self.article.comments.first()
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, "Это тестовый комментарий.")
        self.assertEqual(comment.article, self.article)

    def test_add_comment_post_invalid(self):
        self.client.force_login(self.user)
        data = {"text": "123"}
        response = self.client.post(f"/articles/{self.article.pk}/comment/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.article.comments.count(), 0)
        self.assertContains(response, "не менее 5 символов")

    def test_add_comment_post_article_not_found(self):
        self.client.force_login(self.user)
        data = {"text": "Тестовый текст"}
        response = self.client.post("/articles/999/comment/", data)
        self.assertEqual(response.status_code, 404)


class CommentFormValidationTest(TestCase):
    def test_clean_text_too_short(self):
        form = CommentForm(data={"text": "1234"})
        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)
        self.assertIn("не менее 5 символов", form.errors["text"][0])

    def test_clean_text_banned_word(self):
        form = CommentForm(data={"text": "Это чистый СПАМ для всех"})
        self.assertFalse(form.is_valid())
        self.assertIn("text", form.errors)
        self.assertIn("запрещённое слово", form.errors["text"][0])

    def test_clean_valid_form(self):
        form = CommentForm(data={"text": "Отличная статья, спасибо!"})
        self.assertTrue(form.is_valid())


class CommentEditViewTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ivan", password="password")
        self.other_user = User.objects.create_user(username="petr", password="password")
        self.article = Article.objects.create(title="Статья", text="Текст статьи", rate=1)
        self.comment = Comment.objects.create(
            article=self.article, user=self.author, text="Исходный комментарий"
        )

    def test_edit_comment_anonymous_redirects(self):
        response = self.client.get(f"/comments/{self.comment.pk}/edit/")
        self.assertEqual(response.status_code, 302)

    def test_edit_comment_other_user_denied(self):
        self.client.force_login(self.other_user)
        response = self.client.get(f"/comments/{self.comment.pk}/edit/", follow=True)
        self.assertRedirects(response, f"/articles/{self.article.pk}/")
        self.assertContains(response, "Это не ваш комментарий")

    def test_edit_comment_author_get(self):
        self.client.force_login(self.author)
        response = self.client.get(f"/comments/{self.comment.pk}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Исходный комментарий")

    def test_edit_comment_author_post_success(self):
        self.client.force_login(self.author)
        data = {"text": "Обновленный комментарий"}
        response = self.client.post(f"/comments/{self.comment.pk}/edit/", data)
        self.assertRedirects(response, f"/articles/{self.article.pk}/")
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, "Обновленный комментарий")

    def test_edit_comment_author_post_invalid(self):
        self.client.force_login(self.author)
        data = {"text": "12"}
        response = self.client.post(f"/comments/{self.comment.pk}/edit/", data)
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, "Исходный комментарий")
        self.assertContains(response, "не менее 5 символов")

    def test_edit_comment_not_found(self):
        self.client.force_login(self.author)
        response = self.client.get("/comments/999/edit/")
        self.assertEqual(response.status_code, 404)


class CommentDeleteViewTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="password")
        self.other_user = User.objects.create_user(username="other", password="password")
        self.article = Article.objects.create(title="Статья", text="Текст", rate=1)
        self.comment = Comment.objects.create(
            article=self.article, user=self.author, text="Комментарий для удаления"
        )

    def test_delete_comment_anonymous_redirects(self):
        response = self.client.get(f"/comments/{self.comment.pk}/delete/")
        self.assertEqual(response.status_code, 302)

    def test_delete_comment_other_user_denied(self):
        self.client.force_login(self.other_user)
        response = self.client.post(f"/comments/{self.comment.pk}/delete/", follow=True)
        self.assertRedirects(response, f"/articles/{self.article.pk}/")
        self.assertContains(response, "Это не ваш комментарий")
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 1)

    def test_delete_comment_author_get_confirmation(self):
        self.client.force_login(self.author)
        response = self.client.get(f"/comments/{self.comment.pk}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Комментарий для удаления")
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 1)

    def test_delete_comment_author_post_success(self):
        self.client.force_login(self.author)
        response = self.client.post(f"/comments/{self.comment.pk}/delete/")
        self.assertRedirects(response, f"/articles/{self.article.pk}/")
        self.assertEqual(Comment.objects.filter(pk=self.comment.pk).count(), 0)

    def test_delete_comment_not_found(self):
        self.client.force_login(self.author)
        response = self.client.post("/comments/999/delete/")
        self.assertEqual(response.status_code, 404)


class MyCommentsViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")
        self.article = Article.objects.create(title="Интересная статья", text="Текст", rate=1)
        self.c1 = Comment.objects.create(article=self.article, user=self.user1, text="Мой коммент 1")
        self.c2 = Comment.objects.create(article=self.article, user=self.user2, text="Чужой коммент")

    def test_my_comments_anonymous_redirects(self):
        response = self.client.get("/my-comments/")
        self.assertEqual(response.status_code, 302)

    def test_my_comments_logged_in(self):
        self.client.force_login(self.user1)
        response = self.client.get("/my-comments/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Мой коммент 1")
        self.assertContains(response, "Интересная статья")
        self.assertNotContains(response, "Чужой коммент")

    def test_my_comments_empty(self):
        empty_user = User.objects.create_user(username="empty_user", password="password")
        self.client.force_login(empty_user)
        response = self.client.get("/my-comments/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "У вас пока нет комментариев.")
