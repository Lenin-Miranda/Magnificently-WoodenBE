#!/usr/bin/env python3
from django.contrib.auth import get_user_model
from users.serializer import UserSerializer

User = get_user_model()

# Obtener usuario lenin
user = User.objects.get(username='lenin')
serializer = UserSerializer(user)

print("=== TESTING is_admin IMPLEMENTATION ===")
print(f"Username: {user.username}")
print(f"is_staff: {user.is_staff}")
print(f"is_superuser: {user.is_superuser}")
print(f"is_admin (serialized): {serializer.data['is_admin']}")
print(f"Full data: {serializer.data}")