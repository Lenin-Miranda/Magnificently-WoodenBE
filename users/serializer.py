from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    '''return basic user info /me/'''
    role = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    def get_role(self, obj):
        """Return user role as string"""
        if obj.is_superuser:
            return 'superuser'
        elif obj.is_staff:
            return 'staff'
        else:
            return 'user'

    def get_bio(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.bio if profile else ''

    def get_location(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.location if profile else ''
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'bio',
            'location',
            'role',
        ]
    


class RegisterSerializer(serializers.ModelSerializer):
    '''register new user'''

    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'phone_number']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    '''Retrieve or update the authenticated user profile'''
    bio = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'bio',
            'location',
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = getattr(instance, 'profile', None)
        data['bio'] = profile.bio if profile else ''
        data['location'] = profile.location if profile else ''
        return data

    def update(self, instance, validated_data):
        profile_data = {
            'bio': validated_data.pop('bio', None),
            'location': validated_data.pop('location', None),
        }

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if any(value is not None for value in profile_data.values()):
            profile, _ = UserProfile.objects.get_or_create(user=instance)

            if profile_data['bio'] is not None:
                profile.bio = profile_data['bio']

            if profile_data['location'] is not None:
                profile.location = profile_data['location']

            profile.save()

        return instance


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''Custom serializer that allows login with email or username'''
    
    username_field = 'username'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change the field label to make it clear it accepts email or username
        self.fields['username'].help_text = 'Enter your username or email address'
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to get user by email first
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                # If not found by email, try by username (original behavior)
                pass
            
            # Update the username field with the actual username
            attrs['username'] = username
        
        return super().validate(attrs)
