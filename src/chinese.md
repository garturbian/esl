---
layout: layouts/base.njk
title: Chinese Lessons
---

Improve your Chinese with these interactive lessons!

<div class="lessons-grid">
{%- for lesson in collections.chinese -%}
    <a href="{{ lesson.url | url }}" class="lesson-card">
        <h3>{{ lesson.data.title }}</h3>
    </a>
{%- endfor -%}
</div>
