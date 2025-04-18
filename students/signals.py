from django.db.models.signals import post_save, post_delete, m2m_changed, pre_save
from django.dispatch import receiver
from .models import Student
from .utils import send_telegram_message


@receiver(post_save, sender=Student)
def notify_on_student_save(sender, instance, created, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}"
    if created:
        message = f"📥 Новый студент добавлен: {full_name}, {instance.age} лет"
    else:
        message = f"✏️ Студент обновлён: {full_name}, {instance.age} лет"
        if instance.group:
            message += f", группа: {instance.group.name}"
    send_telegram_message(message)


@receiver(post_delete, sender=Student)
def notify_on_student_delete(sender, instance, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}"
    message = f"🗑 Студент удалён: {full_name}"
    send_telegram_message(message)


@receiver(m2m_changed, sender=Student.courses.through)
def notify_on_courses_changed(sender, instance, action, pk_set, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}"
    if action == "post_add":
        message = f"➕ Курсы добавлены для {full_name}: {', '.join(str(pk) for pk in pk_set)}"
    elif action == "post_remove":
        message = f"➖ Курсы удалены для {full_name}: {', '.join(str(pk) for pk in pk_set)}"
    elif action == "post_clear":
        message = f"🧹 Все курсы удалены для {full_name}"
    send_telegram_message(message)


@receiver(pre_save, sender=Student)
def notify_on_group_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Student.objects.get(pk=instance.pk)
            old_group = old_instance.group
            new_group = instance.group
            if old_group != new_group:
                full_name = f"{instance.first_name} {instance.last_name}"
                if new_group:
                    message = f"👥 Студент {full_name} добавлен в группу {new_group.name}"
                else:
                    message = f"👥 Студент {full_name} удалён из группы {old_group.name}"
                send_telegram_message(message)
        except Student.DoesNotExist:
            pass