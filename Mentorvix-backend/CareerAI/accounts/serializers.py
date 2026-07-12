from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    about = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'about', 'skills']

    def get_about(self, obj):
        profile, _ = Profile.objects.get_or_create(user=obj)
        return profile.about

    def get_skills(self, obj):
        profile, _ = Profile.objects.get_or_create(user=obj)
        return profile.skills

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile, _ = Profile.objects.get_or_create(user=instance)
        
        about = self.initial_data.get('about')
        if about is not None:
            profile.about = about

        skills = self.initial_data.get('skills')
        if skills is not None:
            if isinstance(skills, list):
                profile.skills = skills
            elif isinstance(skills, str):
                profile.skills = [s.strip() for s in skills.split(',') if s.strip()]
        
        profile.save()
        return instance