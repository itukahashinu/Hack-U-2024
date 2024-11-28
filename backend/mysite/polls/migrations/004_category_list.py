from django.db import migrations

def create_categories(apps, schema_editor):
    Category = apps.get_model('polls', 'Category')
    categories = [
        "数学", "統計学", "物理学", "天文学", "地球科学", "化学", "生物学", 
        "工学", "建築学", "デザイン学", "農学", "医学", "歯学", "薬学", 
        "政治学", "法学", "経済学", "経営学", "社会学", "教育学", 
        "心理学", "哲学", "宗教学", "言語学・語学", "人類学・考古学", 
        "歴史学", "地理学", "文学", "芸術", "その他"
    ]
    
    for category_name in categories:
        Category.objects.get_or_create(name=category_name)

class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_alter_survey_status'),  # 依存関係を適切に設定
    ]

    operations = [
        migrations.RunPython(create_categories),
    ]