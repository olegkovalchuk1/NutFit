from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ProfileGoalForm
from .models import Profile, Recipe, Workout
from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "age": user.age,
                        "gender": user.gender,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"message": "Registration failed.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "message": "Login failed.",
                    "errors": {"detail": "username and password are required."},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {
                    "message": "Invalid credentials.",
                    "errors": {"detail": "Invalid username or password."},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(
            {
                "message": "Login successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "age": user.age,
                    "gender": user.gender,
                },
            },
            status=status.HTTP_200_OK,
        )
 

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )


class SaveGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = ProfileGoalForm(request.data)
        if not form.is_valid():
            return Response(
                {"message": "Goal save failed.", "errors": form.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile, _ = Profile.objects.update_or_create(
            user=request.user,
            defaults=form.cleaned_data,
        )
        return Response(
            {
                "message": "Goal data saved successfully.",
                "profile": {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "age": profile.age,
                    "weight": profile.weight,
                    "height": profile.height,
                    "activity_level": profile.activity_level,
                    "goal": profile.goal,
                    "date": profile.date,
                },
            },
            status=status.HTTP_200_OK,
        )


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = (
            "id",
            "name",
            "description",
            "category",
            "duration_minutes",
            "difficulty_level",
            "media_url",
        )


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name_recipe",
            "calories",
            "protein",
            "fat",
            "carbs",
            "goal_type",
        )


class RecipeListView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def _as_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get(self, request):
        queryset = Recipe.objects.all()

        queryset = queryset.search(request.query_params.get("q"))
        queryset = queryset.by_goal(request.query_params.get("goal_type"))
        queryset = queryset.by_calories(
            calories_min=self._as_int(request.query_params.get("calories_min")),
            calories_max=self._as_int(request.query_params.get("calories_max")),
        )
        queryset = queryset.by_macros(
            protein_min=self._as_float(request.query_params.get("protein_min")),
            protein_max=self._as_float(request.query_params.get("protein_max")),
            fat_min=self._as_float(request.query_params.get("fat_min")),
            fat_max=self._as_float(request.query_params.get("fat_max")),
            carbs_min=self._as_float(request.query_params.get("carbs_min")),
            carbs_max=self._as_float(request.query_params.get("carbs_max")),
        )

        serializer = RecipeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkoutListView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def _as_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def get(self, request):
        queryset = Workout.objects.all()

        workout_type = request.query_params.get("type") or request.query_params.get(
            "category"
        )
        queryset = queryset.by_type(workout_type)

        duration_mode = request.query_params.get("duration_mode")
        queryset = queryset.by_duration_mode(duration_mode)
        queryset = queryset.by_duration_range(
            duration_min=self._as_int(request.query_params.get("duration_min")),
            duration_max=self._as_int(request.query_params.get("duration_max")),
        )

        difficulty_level = request.query_params.get("difficulty_level")
        if difficulty_level:
            queryset = queryset.filter(difficulty_level__iexact=difficulty_level)

        serializer = WorkoutSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
