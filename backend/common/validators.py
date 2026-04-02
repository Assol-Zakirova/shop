from datetime import date

from rest_framework import serializers


def ageValidator(request):
    token = getattr(request, 'auth', None)

    if not token:
        return None

    value = token.get('birthdate')
    birthdate = date.fromisoformat(value)

    if birthdate is None:
            raise serializers.ValidationError("Укажите дату рождения, чтобы создать продукт.")

    today = date.today()
    
    age = today.year - birthdate.year
    isNotBirthdayYet = (today.month, today.day) < (birthdate.month, birthdate.day)
    if isNotBirthdayYet:
        age -= 1

    if age >= 18:
        return True
    else:
        raise serializers.ValidationError("Вы должны быть старше 18 лет, чтобы создать продукт.")
