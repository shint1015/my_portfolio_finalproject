from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    query = serializers.CharField(min_length=1)


class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.CharField())