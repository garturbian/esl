---
layout: layouts/base.njk
title: English Lessons
---

Choose a lesson to begin your English learning journey!

<div class="lessons-grid">
{%- for lesson in collections.lessons -%}
    <a href="{{ lesson.url | url }}" class="lesson-card">
        <h3>{{ lesson.data.title }}</h3>
    </a>
{%- endfor -%}
</div>

We're adding new lessons every week!
