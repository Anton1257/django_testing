import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from app.models import Course, Student
from django_testing.settings import MAX_STUDENTS_PER_COURSE


# Define fixtures
# Заводим фикстуры
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory():
    return baker.make(Course, _quantity=3)


@pytest.fixture
def student_factory():
    return baker.make(Student, _quantity=3)


# Test retrieving the first course
# Тест на получение первого курса
@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    courses = course_factory
    course_to_retrieve = courses[0]
    url = reverse("courses-detail", args=[course_to_retrieve.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == course_to_retrieve.name


# Test listing courses
# Тест на получение списка курсов
@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    courses = course_factory
    url = reverse("courses-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(courses)


# Test filtering courses by id
# Тест на фильтрацию списка курсов по id
@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    courses = course_factory
    target_course = courses[0]
    url = reverse("courses-list")
    response = api_client.get(url, {"id": target_course.id})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == target_course.id


# Test filtering courses by name
# Тест на фильтрацию списка курсов по имени
@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    courses = course_factory
    target_course = courses[0]
    url = reverse("courses-list")
    response = api_client.get(url, {"name": target_course.name})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == target_course.name


# Test successful course creation
# Тест на успешное создание курса
@pytest.mark.django_db
def test_create_course(api_client):
    url = reverse("courses-list")
    data = {"name": "New Course"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.filter(name=data["name"]).exists()


# Test successful course update
# Тест на успешное обновление курса
@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    courses = course_factory
    course_to_update = courses[0]
    url = reverse("courses-detail", args=[course_to_update.id])
    new_name = "Updated Course Name"
    data = {"name": new_name}
    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert Course.objects.get(id=course_to_update.id).name == new_name


# Test successful course deletion
# Тест на успешное удаление курса
@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    courses = course_factory
    course_to_delete = courses[0]
    url = reverse("courses-detail", args=[course_to_delete.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Test limiting the number of students per course
# Тест на ограничение числа студентов на курсе
@pytest.mark.django_db
@pytest.mark.parametrize(
    "num_students,expected_status",
    [
        (19, status.HTTP_201_CREATED),
        (20, status.HTTP_201_CREATED),
        (21, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_limit_students_per_course(api_client, num_students, expected_status):
    url = reverse("courses-list")
    data = {"name": "New Course", "max_students": MAX_STUDENTS_PER_COURSE}
    students = [
        Student.objects.create(name=f"Student {i}", birth_date="1995-01-01")
        for i in range(num_students)
    ]
    students_ids = [student.id for student in students]
    data["students"] = students_ids
    response = api_client.post(url, data, format="json")
    assert response.status_code == expected_status, (
        f"Expected status {expected_status},"
        f"but got {response.status_code}. Response data: {response.data}"
    )
