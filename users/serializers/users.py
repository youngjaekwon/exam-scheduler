from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm"]
        extra_kwargs = {"id": {"read_only": True}, "email": {"required": True}}

    def validate(self, data):
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 등록된 이메일입니다.")
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)

        user = User.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data.get("email"),
        )
        user.set_password(validated_data.get("password"))
        user.save()

        return user


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"}, required=False)
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"}, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "password", "password_confirm"]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def validate(self, data):
        if "password" in data:
            if not data.get("password_confirm"):
                raise serializers.ValidationError({"password_confirm": "비밀번호 확인이 필요합니다."})
            if data.get("password") != data.get("password_confirm"):
                raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data

    def update(self, instance, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password", None)

        if password:
            instance.set_password(password)

        return super().update(instance, validated_data)
