from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()
    middle_star = serializers.FloatField()

    class Meta:
        model = Movie
        fields = ('title', 'tagline', 'category', 'rating_user', 'middle_star')


class ReviewCreateSerializer(serializers.ModelSerializer):
    # parent = serializers.SlugRelatedField(slug_field="email", read_only=True)
    # movie = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = Review
        fields = "__all__"


class RecursiveSerializer(serializers.Serializer):
    """Для вывода дерева отзывов"""

    def to_representation(self, value):
        serializers = self.parent.parent.__class__(value, context=self.context)
        return serializers.data


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр комментариев, только parents"""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class ReviewSerializer(serializers.ModelSerializer):
    # parent = serializers.SlugRelatedField(slug_field="email", read_only=True)
    # movie = serializers.SlugRelatedField(slug_field="title", read_only=True)
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ("text", "name", "children")


class ActorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = "__all__"


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полный фильм"""
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)  # вывод форинкей не цифрой, а полем слаг
    actors = ActorListSerializer(read_only=True, many=True)
    directors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    # review_set = ReviewCreateSerializer(many=True) используем reviews, т.к. добавили related_name в модели Review
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ("draft",)


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get("star")}
        )
        return rating
