import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from django.conf import settings
from students.models import Student, Course, Group
from students.utils import send_telegram_message

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(CREATE_STUDENT_NAME, CREATE_STUDENT_AGE, UPDATE_STUDENT_ID, UPDATE_STUDENT_NAME,
 UPDATE_STUDENT_AGE, DELETE_STUDENT_ID, CREATE_COURSE_NAME, CREATE_GROUP_NAME,
 ADD_COURSE_ID, ADD_COURSE_IDS, REMOVE_COURSE_ID, REMOVE_COURSE_IDS, SET_GROUP_ID, SET_GROUP) = range(14)

def start(update, context):
    update.message.reply_text("Привет! Я бот для управления студентами. Используй команды:\n"
                             "/create_student - Создать студента\n"
                             "/update_student - Обновить студента\n"
                             "/delete_student - Удалить студента\n"
                             "/create_course - Создать курс\n"
                             "/create_group - Создать группу\n"
                             "/add_course - Добавить курс студенту\n"
                             "/remove_course - Удалить курс у студента\n"
                             "/set_group - Назначить группу студенту\n"
                             "/list_students - Показать список студентов\n"
                             "/cancel - Отменить действие")
def create_student(update, context):
    update.message.reply_text("Введите имя и фамилию студента (например, John Doe):")
    return CREATE_STUDENT_NAME

def create_student_name(update, context):
    try:
        context.user_data['first_name'], context.user_data['last_name'] = update.message.text.split(maxsplit=1)
        update.message.reply_text("Введите возраст студента:")
        return CREATE_STUDENT_AGE
    except ValueError:
        update.message.reply_text("Введите имя и фамилию через пробел (например, John Doe):")
        return CREATE_STUDENT_NAME

def create_student_age(update, context):
    try:
        age = int(update.message.text)
        student = Student.objects.create(
            first_name=context.user_data['first_name'],
            last_name=context.user_data['last_name'],
            age=age
        )
        update.message.reply_text(f"Студент {student} создан!")
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Пожалуйста, введите корректный возраст (число):")
        return CREATE_STUDENT_AGE

def update_student(update, context):
    update.message.reply_text("Введите ID студента для обновления:")
    return UPDATE_STUDENT_ID

def update_student_id(update, context):
    try:
        student_id = int(update.message.text)
        student = Student.objects.get(id=student_id)
        context.user_data['student_id'] = student_id
        update.message.reply_text(f"Текущие данные: {student.first_name} {student.last_name}, {student.age} лет\n"
                                 "Введите новое имя и фамилию (например, John Smith):")
        return UPDATE_STUDENT_NAME
    except (ValueError, Student.DoesNotExist):
        update.message.reply_text("Неверный ID. Попробуйте снова:")
        return UPDATE_STUDENT_ID

def update_student_name(update, context):
    try:
        context.user_data['first_name'], context.user_data['last_name'] = update.message.text.split(maxsplit=1)
        update.message.reply_text("Введите новый возраст:")
        return UPDATE_STUDENT_AGE
    except ValueError:
        update.message.reply_text("Введите имя и фамилию через пробел (например, John Smith):")
        return UPDATE_STUDENT_NAME

def update_student_age(update, context):
    try:
        age = int(update.message.text)
        student = Student.objects.get(id=context.user_data['student_id'])
        student.first_name = context.user_data['first_name']
        student.last_name = context.user_data['last_name']
        student.age = age
        student.save()
        update.message.reply_text(f"Студент {student} обновлён!")
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Пожалуйста, введите корректный возраст (число):")
        return UPDATE_STUDENT_AGE

def delete_student(update, context):
    update.message.reply_text("Введите ID студента для удаления:")
    return DELETE_STUDENT_ID

def delete_student_id(update, context):
    try:
        student_id = int(update.message.text)
        student = Student.objects.get(id=student_id)
        student.delete()
        update.message.reply_text(f"Студент {student} удалён!")
        return ConversationHandler.END
    except (ValueError, Student.DoesNotExist):
        update.message.reply_text("Неверный ID. Попробуйте снова:")
        return DELETE_STUDENT_ID

def create_course(update, context):
    update.message.reply_text("Введите название курса:")
    return CREATE_COURSE_NAME

def create_course_name(update, context):
    name = update.message.text
    course = Course.objects.create(name=name)
    update.message.reply_text(f"Курс {course} создан!")
    return ConversationHandler.END

def create_group(update, context):
    update.message.reply_text("Введите название группы:")
    return CREATE_GROUP_NAME

def create_group_name(update, context):
    name = update.message.text
    group = Group.objects.create(name=name)
    update.message.reply_text(f"Группа {group} создана!")
    return ConversationHandler.END

def add_course(update, context):
    update.message.reply_text("Введите ID студента:")
    return ADD_COURSE_ID

def add_course_id(update, context):
    try:
        student_id = int(update.message.text)
        Student.objects.get(id=student_id)
        context.user_data['student_id'] = student_id
        update.message.reply_text("Введите ID курсов (через запятую, например, 1,2):")
        return ADD_COURSE_IDS
    except (ValueError, Student.DoesNotExist):
        update.message.reply_text("Неверный ID студента. Попробуйте снова:")
        return ADD_COURSE_ID

def add_course_ids(update, context):
    try:
        course_ids = [int(cid) for cid in update.message.text.split(',')]
        student = Student.objects.get(id=context.user_data['student_id'])
        courses = Course.objects.filter(id__in=course_ids)
        student.courses.add(*courses)
        update.message.reply_text("Курсы добавлены!")
        return ConversationHandler.END
    except (ValueError, Course.DoesNotExist):
        update.message.reply_text("Неверные ID курсов. Попробуйте снова:")
        return ADD_COURSE_IDS

def remove_course(update, context):
    update.message.reply_text("Введите ID студента:")
    return REMOVE_COURSE_ID

def remove_course_id(update, context):
    try:
        student_id = int(update.message.text)
        Student.objects.get(id=student_id)
        context.user_data['student_id'] = student_id
        update.message.reply_text("Введите ID курсов для удаления (через запятую, например, 1,2):")
        return REMOVE_COURSE_IDS
    except (ValueError, Student.DoesNotExist):
        update.message.reply_text("Неверный ID студента. Попробуйте снова:")
        return REMOVE_COURSE_ID

def remove_course_ids(update, context):
    try:
        course_ids = [int(cid) for cid in update.message.text.split(',')]
        student = Student.objects.get(id=context.user_data['student_id'])
        courses = Course.objects.filter(id__in=course_ids)
        student.courses.remove(*courses)
        update.message.reply_text("Курсы удалены!")
        return ConversationHandler.END
    except (ValueError, Course.DoesNotExist):
        update.message.reply_text("Неверные ID курсов. Попробуйте снова:")
        return REMOVE_COURSE_IDS

def set_group(update, context):
    update.message.reply_text("Введите ID студента:")
    return SET_GROUP_ID

def set_group_id(update, context):
    try:
        student_id = int(update.message.text)
        Student.objects.get(id=student_id)
        context.user_data['student_id'] = student_id
        update.message.reply_text("Введите ID группы (или 'none' для удаления группы):")
        return SET_GROUP
    except (ValueError, Student.DoesNotExist):
        update.message.reply_text("Неверный ID студента. Попробуйте снова:")
        return SET_GROUP_ID

def set_group(update, context):
    try:
        group_input = update.message.text
        student = Student.objects.get(id=context.user_data['student_id'])
        if group_input.lower() == 'none':
            student.group = None
        else:
            group_id = int(group_input)
            student.group = Group.objects.get(id=group_id)
        student.save()
        update.message.reply_text("Группа назначена!")
        return ConversationHandler.END
    except (ValueError, Group.DoesNotExist):
        update.message.reply_text("Неверный ID группы. Попробуйте снова:")
        return SET_GROUP

def cancel(update, context):
    update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')
    update.message.reply_text("Произошла ошибка. Попробуйте снова.")

def list_students(update, context):
    students = Student.objects.all()
    if not students:
        update.message.reply_text("Список студентов пуст.")
        return

    message = "📋 Список студентов:\n\n"
    for student in students:
        full_name = f"{student.first_name} {student.last_name}"
        group = student.group.name if student.group else "Без группы"
        courses = ", ".join(course.name for course in student.courses.all()) or "Без курсов"
        message += (f"ID: {student.id}\n"
                   f"Имя: {full_name}\n"
                   f"Возраст: {student.age}\n"
                   f"Группа: {group}\n"
                   f"Курсы: {courses}\n"
                   f"{'-' * 20}\n")

    # Разбиваем сообщение, если оно длиннее 4096 символов
    if len(message) > 4096:
        parts = []
        current_part = "📋 Список студентов (часть {}):\n\n"
        part_number = 1
        lines = message.split('\n')
        current_lines = []
        current_length = len(current_part.format(part_number))

        for line in lines:
            if current_length + len(line) + 1 > 4096:
                parts.append(current_part.format(part_number) + '\n'.join(current_lines))
                part_number += 1
                current_lines = [line]
                current_length = len(current_part.format(part_number)) + len(line) + 1
            else:
                current_lines.append(line)
                current_length += len(line) + 1

        if current_lines:
            parts.append(current_part.format(part_number) + '\n'.join(current_lines))

        for part in parts:
            update.message.reply_text(part)
    else:
        update.message.reply_text(message)

def main():
    updater = Updater(settings.TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # ConversationHandler для создания студента
    create_student_conv = ConversationHandler(
        entry_points=[CommandHandler('create_student', create_student)],
        states={
            CREATE_STUDENT_NAME: [MessageHandler(Filters.text & ~Filters.command, create_student_name)],
            CREATE_STUDENT_AGE: [MessageHandler(Filters.text & ~Filters.command, create_student_age)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для обновления студента
    update_student_conv = ConversationHandler(
        entry_points=[CommandHandler('update_student', update_student)],
        states={
            UPDATE_STUDENT_ID: [MessageHandler(Filters.text & ~Filters.command, update_student_id)],
            UPDATE_STUDENT_NAME: [MessageHandler(Filters.text & ~Filters.command, update_student_name)],
            UPDATE_STUDENT_AGE: [MessageHandler(Filters.text & ~Filters.command, update_student_age)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для удаления студента
    delete_student_conv = ConversationHandler(
        entry_points=[CommandHandler('delete_student', delete_student)],
        states={
            DELETE_STUDENT_ID: [MessageHandler(Filters.text & ~Filters.command, delete_student_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для создания курса
    create_course_conv = ConversationHandler(
        entry_points=[CommandHandler('create_course', create_course)],
        states={
            CREATE_COURSE_NAME: [MessageHandler(Filters.text & ~Filters.command, create_course_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для создания группы
    create_group_conv = ConversationHandler(
        entry_points=[CommandHandler('create_group', create_group)],
        states={
            CREATE_GROUP_NAME: [MessageHandler(Filters.text & ~Filters.command, create_group_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для добавления курсов
    add_course_conv = ConversationHandler(
        entry_points=[CommandHandler('add_course', add_course)],
        states={
            ADD_COURSE_ID: [MessageHandler(Filters.text & ~Filters.command, add_course_id)],
            ADD_COURSE_IDS: [MessageHandler(Filters.text & ~Filters.command, add_course_ids)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для удаления курсов
    remove_course_conv = ConversationHandler(
        entry_points=[CommandHandler('remove_course', remove_course)],
        states={
            REMOVE_COURSE_ID: [MessageHandler(Filters.text & ~Filters.command, remove_course_id)],
            REMOVE_COURSE_IDS: [MessageHandler(Filters.text & ~Filters.command, remove_course_ids)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ConversationHandler для назначения группы
    set_group_conv = ConversationHandler(
        entry_points=[CommandHandler('set_group', set_group)],
        states={
            SET_GROUP_ID: [MessageHandler(Filters.text & ~Filters.command, set_group_id)],
            SET_GROUP: [MessageHandler(Filters.text & ~Filters.command, set_group)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Регистрация хендлеров
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(create_student_conv)
    dp.add_handler(update_student_conv)
    dp.add_handler(delete_student_conv)
    dp.add_handler(create_course_conv)
    dp.add_handler(create_group_conv)
    dp.add_handler(add_course_conv)
    dp.add_handler(remove_course_conv)
    dp.add_handler(set_group_conv)
    dp.add_handler(CommandHandler("list_students", list_students))  # Новая команда
    dp.add_error_handler(error)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()