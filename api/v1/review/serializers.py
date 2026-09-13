from rest_framework import serializers


class ReviewDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    comment = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('comment'):
            raise serializers.ValidationError({'comment': 'A comment is required when rejecting a submission.'})
        return attrs
