from rest_framework.serializers import ModelSerializer, FileField
from .models import ExcelFile, Produto, Recorrencia
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class RecorrenciaSerializer(ModelSerializer):
    
    class Meta:
        model = Recorrencia
        fields = '__all__'


class FileSerializer(ModelSerializer):
    file = FileField()
    class Meta:
        model = ExcelFile
        fields = '__all__'


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password',)
        extra_kwargs = {'password':{'write_only': True, 'required': False}}

class ProdutoSerializer(ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'