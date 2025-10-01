from rest_framework import serializers
from ..models import CustomUser, WorkHistory, Skill, SkillsRelevance, CurriculumRelevance, PerceptionFurtherStudies, FeedbackRecommendations, Profile
from .work_history import WorkHistorySerializer
from .skills_relevance import SkillsRelevanceSerializer
from .curriculum_relevance import CurriculumRelevanceSerializer
from .perception_further_studies import PerceptionFurtherStudiesSerializer
from .feedback_recommendations import FeedbackRecommendationsSerializer
from .profile_model import ProfileModelSerializer


class ProfileSerializer(serializers.ModelSerializer):
    work_histories = WorkHistorySerializer(many=True)
    skills_relevance = SkillsRelevanceSerializer()
    curriculum_relevance = CurriculumRelevanceSerializer()
    perception_studies = PerceptionFurtherStudiesSerializer()
    feedback = FeedbackRecommendationsSerializer()
    profile = ProfileModelSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password']

    def update(self, instance, validated_data):
        work_histories_data = validated_data.pop('work_histories', [])
        skills_data = validated_data.pop('skills_relevance', {})
        curriculum_data = validated_data.pop('curriculum_relevance', {})
        perception_data = validated_data.pop('perception_studies', {})
        feedback_data = validated_data.pop('feedback', {})
        profile_data = validated_data.pop('profile', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        SkillsRelevance.objects.update_or_create(user=instance, defaults=skills_data)
        CurriculumRelevance.objects.update_or_create(user=instance, defaults=curriculum_data)
        PerceptionFurtherStudies.objects.update_or_create(user=instance, defaults=perception_data)
        FeedbackRecommendations.objects.update_or_create(user=instance, defaults=feedback_data)
        Profile.objects.update_or_create(user=instance, defaults=profile_data)

        instance.work_histories.all().delete()
        for wh_data in work_histories_data:
            skills = wh_data.pop('skills', [])
            work = WorkHistory.objects.create(user=instance, **wh_data)
            for skill_data in skills:
                skill_obj, _ = Skill.objects.get_or_create(**skill_data)
                work.skills.add(skill_obj)

        return instance