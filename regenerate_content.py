import json

def generate_faq_html(faqs):
    html = '''{% extends "base.html" %}

{% block title %}FAQ - Chat Online{% endblock %}

{% block content %}
<div class="content-page-container">
    <div class="content-page-header">
        <h1><i class="fas fa-question-circle"></i> Frequently Asked Questions</h1>
        <p>Find answers to common questions</p>
    </div>
    <div class="accordion">
'''
    for faq in faqs:
        html += f'''        <div class="accordion-item">
            <button class="accordion-header">
                <span><i class="fas {faq['icon']}"></i> {faq['question']}</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="accordion-content">
                <div class="accordion-body">
                    <p>{faq['answer']}</p>
                </div>
            </div>
        </div>
'''
    html += '''    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', function() {
        const item = this.parentElement;
        const isActive = item.classList.contains('active');

        document.querySelectorAll('.accordion-item').forEach(otherItem => {
            otherItem.classList.remove('active');
        });

        if (!isActive) {
            item.classList.add('active');
        }
    });
});
</script>
{% endblock %}'''
    return html

def generate_blog_html(blogs):
    html = '''{% extends "base.html" %}

{% block title %}Blog - Chat Online{% endblock %}

{% block content %}
<div class="content-page-container">
    <div class="content-page-header">
        <h1><i class="fas fa-blog"></i> Blog</h1>
        <p>Latest tips, news, and articles</p>
    </div>
    <div class="blog-grid">
'''
    for blog in blogs:
        bg_colors = [
            'linear-gradient(135deg, #0EA5E9, #06B6D4)',
            'linear-gradient(135deg, #8B5CF6, #7C3AED)',
            'linear-gradient(135deg, #10B981, #059669)',
            'linear-gradient(135deg, #F59E0B, #D97706)',
            'linear-gradient(135deg, #EC4899, #DB2777)',
            'linear-gradient(135deg, #6366F1, #4F46E5)'
        ]
        color = bg_colors[hash(blog['title']) % len(bg_colors)]
        icon = 'fa-star' if blog['category'] == 'Safety' else 'fa-user-friends' if blog['category'] == 'Community' else 'fa-lightbulb' if blog['category'] == 'Tips' else 'fa-globe'
        html += f'''
        <div class="blog-card">
            <div class="blog-image" style="background: {color};">
                <i class="fas {icon}"></i>
            </div>
            <div class="blog-content">
                <span class="blog-category">{blog['category']}</span>
                <h3>{blog['title']}</h3>
                <p>{blog['content'][:100]}...</p>
                <span class="blog-meta"><i class="fas fa-calendar"></i> {blog['date']}</span>
            </div>
        </div>
'''
    html += '''    </div>
</div>
{% endblock %}'''
    return html

with open('data/content.json', 'r') as f:
    data = json.load(f)

with open('templates/faq.html', 'w') as f:
    f.write(generate_faq_html(data.get('faqs', [])))

with open('templates/blog.html', 'w') as f:
    f.write(generate_blog_html(data.get('blogs', [])))

print('Files regenerated successfully!')
